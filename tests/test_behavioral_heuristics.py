from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.behavioral_heuristics import (
    active_heuristics,
    correlation_support,
    evaluate_heuristic,
    excluded_heuristics,
    heuristic_method_bonus,
    reference_only_heuristics,
)
from src.reward import REQUIRED_GUARDRAILS, policy_decision_for_person, reward_policy_blockers


VALID_NO_ACTION_BASELINE = {
    "baseline_action": "no_action",
    "sample_size": 100,
    "mean_outcome": 0.42,
    "ci_lower": 0.35,
    "ci_upper": 0.49,
    "confidence_level": 0.95,
    "monitoring_required": True,
}


class BehavioralHeuristicLayerTests(unittest.TestCase):
    def test_active_reference_and_excluded_lists_are_separate(self) -> None:
        self.assertIn("availability_heuristic", active_heuristics())
        self.assertIn("present_bias", active_heuristics())
        self.assertIn("wysiati", active_heuristics())
        self.assertIn("dunning_kruger_effect", reference_only_heuristics())
        self.assertIn("cashless_effect", excluded_heuristics())
        self.assertTrue(set(active_heuristics()).isdisjoint(reference_only_heuristics()))
        self.assertTrue(set(active_heuristics()).isdisjoint(excluded_heuristics()))

    def test_availability_heuristic_requires_recent_salient_event_signals(self) -> None:
        result = evaluate_heuristic("availability_heuristic", {"recent_salient_event": True})

        self.assertEqual(result.status, "not_testable_yet")
        self.assertIn("event_recency", result.missing_signals)
        self.assertIn("behavior_change_after_event", result.missing_signals)
        self.assertEqual(result.claim_type, "hypothesis")

    def test_present_bias_maps_to_commitment_goal_and_reminder_methods(self) -> None:
        result = evaluate_heuristic(
            "present_bias",
            {"activation_gap": 0.8, "delayed_benefit_signal": 0.7},
        )

        self.assertEqual(result.status, "moderate_support")
        self.assertIn("commitment", result.compatible_methods)
        self.assertIn("goal_setting", result.compatible_methods)
        self.assertIn("timely_reminder", result.compatible_methods)
        self.assertEqual(result.claim_type, "hypothesis")

    def test_reference_only_heuristics_do_not_influence_ranking(self) -> None:
        result = evaluate_heuristic("dunning_kruger_effect", {"confidence_signal": 0.9})

        self.assertEqual(result.status, "reference_only")
        self.assertEqual(result.compatible_methods, [])
        self.assertEqual(heuristic_method_bonus("commitment", [result]), 0.0)

    def test_excluded_heuristics_are_blocked_governance_risks(self) -> None:
        result = evaluate_heuristic("cashless_effect", {"purchase_signal": 0.8})

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.claim_type, "blocked")
        self.assertIn("excluded_governance_risk", result.reason_codes)

    def test_loss_aversion_penalizes_loss_frame_under_supported_heuristic(self) -> None:
        result = evaluate_heuristic(
            "loss_aversion",
            {"loss_salience": 0.8, "deadline_pressure": 0.8},
        )

        self.assertEqual(result.status, "moderate_support")
        self.assertGreater(heuristic_method_bonus("loss_frame", [result]), 0.0)

    def test_decision_fatigue_blocks_pressure_methods_and_supports_no_action(self) -> None:
        result = evaluate_heuristic(
            "decision_fatigue",
            {"fatigue_signal": 0.9, "decision_count": 0.8},
        )

        self.assertEqual(result.status, "moderate_support")
        self.assertIn("no_action", result.compatible_methods)
        self.assertIn("timely_reminder", result.blocked_methods)
        self.assertLess(heuristic_method_bonus("timely_reminder", [result]), 0.0)

    def test_heuristic_only_policy_is_blocked(self) -> None:
        blockers = reward_policy_blockers(
            {
                "reward_calibrated": True,
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "heuristic_only_policy": True,
            }
        )

        self.assertIn("heuristic_only_policy_blocked", blockers)

    def test_correlation_support_never_creates_causal_claim(self) -> None:
        result = correlation_support([0.1, 0.4, 0.9, 1.0], [0.0, 0.2, 0.8, 1.0])

        self.assertEqual(result["status"], "moderate_support")
        self.assertEqual(result["claim_type"], "hypothesis")
        self.assertFalse(result["causal_claim"])
        self.assertEqual(result["reason"], "correlation_is_not_causation")

    def test_heuristic_bonus_can_change_ranking_only_when_policy_is_otherwise_allowed(self) -> None:
        decision = policy_decision_for_person(
            {
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.1,
                "activation_gap": 0.9,
                "delayed_benefit_signal": 0.8,
                "goal_feasibility_known": True,
                "baseline_activation_score": 0.30,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
                "manipulation_governance_review": True,
            }
        )

        self.assertIn(decision["selected_action"], {"commitment", "goal_setting", "progress_feedback"})
        self.assertEqual(decision["claim_type"], "hypothesis")


if __name__ == "__main__":
    unittest.main()
