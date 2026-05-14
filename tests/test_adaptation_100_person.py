from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adaptation import (
    NUDGE_METHODS,
    generate_100_person_adaptation_sample,
    split_activation_scores,
)
from src.evidence import MECE_HYPOTHESIS_GROUPS, build_mece_hypotheses, infer_customer_data_profile, mece_groups_complete
from src.orchestrator import Orchestrator, Task
from src.reward import REQUIRED_GUARDRAILS
from src.simulation import ab_mean_difference_ci


VALID_NO_ACTION_BASELINE = {
    "baseline_action": "no_action",
    "sample_size": 100,
    "mean_outcome": 0.42,
    "ci_lower": 0.35,
    "ci_upper": 0.49,
    "confidence_level": 0.95,
    "monitoring_required": True,
}


class Adaptation100PersonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = generate_100_person_adaptation_sample(seed=41)

    def test_step_1_sample_has_100_people_and_realistic_edge_cases(self) -> None:
        self.assertEqual(len(self.rows), 100)
        self.assertTrue(any(row["experiment_group"] == "treatment" for row in self.rows))
        self.assertTrue(any(row["experiment_group"] == "control" for row in self.rows))
        self.assertTrue(any(row["consent"] is False for row in self.rows))
        self.assertTrue(any(row["vulnerability_flag"] is True for row in self.rows))

        high_open_resistant = [
            row for row in self.rows
            if float(row["openness_proxy"]) >= 0.70 and float(row["resistance_signal"]) >= 0.70
        ]
        low_open_clicking = [
            row for row in self.rows
            if float(row["openness_proxy"]) <= 0.35 and row["clicked_nudge"] is True
        ]

        self.assertTrue(high_open_resistant)
        self.assertTrue(low_open_clicking)

    def test_step_2_calculations_produce_valid_95_percent_ci_and_consent_safe_ocean(self) -> None:
        treatment, control = split_activation_scores(self.rows)
        interval = ab_mean_difference_ci(treatment, control, confidence_level=0.95)
        uncertainty = interval.as_uncertainty()

        self.assertEqual(uncertainty["sample_size"], 100)
        self.assertEqual(uncertainty["confidence_level"], 0.95)
        self.assertLessEqual(uncertainty["ci_lower"], uncertainty["effect_estimate"])
        self.assertGreaterEqual(uncertainty["ci_upper"], uncertainty["effect_estimate"])
        self.assertIn("contains_null", uncertainty)
        self.assertGreater(uncertainty["effect_estimate"], 0.0)

        consented = [row for row in self.rows if row["consent"] is True]
        no_consent = [row for row in self.rows if row["consent"] is False]
        self.assertTrue(consented)
        self.assertTrue(no_consent)
        self.assertTrue(all(row["ocean_signal"]["scores"] for row in consented))
        self.assertTrue(all(row["ocean_signal"]["scores"] is None for row in no_consent))
        self.assertTrue(
            all(row["ocean_signal"]["blocked_reason"] == "ocean_consent_required" for row in no_consent)
        )

    def test_step_3_hypothesis_generation_detects_data_effect_and_psychological_signals(self) -> None:
        available_columns = list(self.rows[0].keys())
        context = {
            "available_columns": available_columns,
            "outcome_variable": "activation_score",
            "treatment_group": "experiment_group=treatment",
            "control_group": "experiment_group=control",
            "behavioral_method": "adaptive_candidate_nudge",
            "target_behavior": "activation",
            "segment_fields": ["company_id", "openness_proxy", "resistance_signal"],
            "consent_field": "consent",
        }
        profile = infer_customer_data_profile(context)
        hypotheses = build_mece_hypotheses({**context, "customer_data_profile": profile})

        self.assertTrue(mece_groups_complete(hypotheses))
        self.assertEqual(
            sorted({hypothesis["mece_group"] for hypothesis in hypotheses}),
            sorted(MECE_HYPOTHESIS_GROUPS),
        )
        by_id = {hypothesis["id"]: hypothesis for hypothesis in hypotheses}
        self.assertEqual(by_id["H1"]["status"], "testable")
        self.assertEqual(by_id["H2"]["status"], "testable")
        self.assertEqual(by_id["H3"]["status"], "testable")
        self.assertEqual(by_id["H4"]["status"], "testable")
        self.assertEqual(by_id["H5"]["status"], "testable")
        self.assertIn("psychological_signal", by_id["H3"]["evidence"])
        self.assertIn("psychological_fields", by_id["H5"]["evidence"])

    def test_step_4_nudge_candidates_are_guarded_and_from_approved_method_set(self) -> None:
        for row in self.rows:
            self.assertIn(row["recommended_nudge"], NUDGE_METHODS)
            self.assertIn("policy_ranking", row)
            self.assertIn("policy_decision", row)
            self.assertEqual(row["reward_result"], row["policy_decision"]["selected_result"])
            evaluated_actions = {item["evaluated_action"] for item in row["policy_ranking"]}
            self.assertIn("no_action", evaluated_actions)
            rewards = [item["reward"] for item in row["policy_ranking"]]
            self.assertEqual(rewards, sorted(rewards, reverse=True))
            if row["experiment_group"] == "control":
                self.assertEqual(row["policy_decision"]["selected_action"], "no_action")
            if row["consent"] is False:
                self.assertEqual(row["recommended_nudge"], "no_action")
                self.assertEqual(row["nudge_reason"], "missing_consent")
                self.assertEqual(row["policy_decision"]["selected_action"], "no_action")
            if row["vulnerability_flag"] is True and row["consent"] is True:
                self.assertEqual(row["recommended_nudge"], "no_action")
                self.assertEqual(row["nudge_reason"], "protected_state")
                self.assertEqual(row["policy_decision"]["selected_action"], "no_action")
            if float(row["fatigue_signal"]) >= 0.75 and row["consent"] is True and row["vulnerability_flag"] is False:
                self.assertEqual(row["recommended_nudge"], "no_action")
                self.assertEqual(row["nudge_reason"], "high_fatigue")
                self.assertEqual(row["policy_decision"]["selected_action"], "no_action")

        active_candidates = [
            row for row in self.rows
            if row["experiment_group"] == "treatment" and row["policy_decision"]["selected_action"] != "no_action"
        ]
        self.assertTrue(active_candidates)
        self.assertTrue(all(row["policy_decision"]["claim_type"] == "hypothesis" for row in active_candidates))

    def test_step_5_orchestrator_reviews_calculation_and_blocks_ocean_only_policy(self) -> None:
        treatment, control = split_activation_scores(self.rows)
        interval = ab_mean_difference_ci(treatment, control, confidence_level=0.95)
        orchestrator = Orchestrator()

        formula_result = orchestrator.run_orchestration(
            Task(
                phase="formula_review",
                agent="statistical",
                prompt="Review 100-person adaptive nudge A/B calculation",
                context={
                    "formula_key": "ab_test",
                    "treatment_group": "experiment_group=treatment",
                    "control_group": "experiment_group=control",
                    "outcome_variable": "activation_score",
                    "uncertainty": interval.as_uncertainty(),
                },
            )
        )
        self.assertIn(formula_result.next_action, {"approve", "revise"})
        self.assertNotEqual(formula_result.next_action, "hold")

        policy_result = orchestrator.run_orchestration(
            Task(
                phase="formula_review",
                agent="statistical",
                prompt="Review OCEAN-only policy blocker",
                context={
                    "formula_key": "reward_policy",
                    "reward_calibrated": True,
                    "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                    "guardrails": sorted(REQUIRED_GUARDRAILS),
                    "uses_ocean_for_personalization": True,
                    "ocean_consent": True,
                    "ocean_only_decision": True,
                    "ocean_scores": {"openness": 6.2},
                },
            )
        )
        self.assertEqual(policy_result.next_action, "hold")


if __name__ == "__main__":
    unittest.main()
