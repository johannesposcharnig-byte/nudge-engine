from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import Orchestrator, Task
from src.reward import (
    POLICY_ACTION_SET,
    REQUIRED_GUARDRAILS,
    has_required_guardrails,
    missing_required_guardrails,
    policy_decision_for_person,
    rank_actions_for_person,
    reward_policy_blockers,
    score_action_reward,
    validate_no_action_baseline,
)


VALID_NO_ACTION_BASELINE = {
    "baseline_action": "no_action",
    "sample_size": 100,
    "mean_outcome": 0.42,
    "ci_lower": 0.35,
    "ci_upper": 0.49,
    "confidence_level": 0.95,
    "monitoring_required": True,
}


class RewardGovernanceTests(unittest.TestCase):
    def test_policy_guardrails_must_include_required_safety_keys(self) -> None:
        guardrails = ["consent_required", "frequency_cap"]

        self.assertFalse(has_required_guardrails(guardrails))
        self.assertIn("opt_out_available", missing_required_guardrails(guardrails))
        self.assertFalse(missing_required_guardrails(sorted(REQUIRED_GUARDRAILS)))

    def test_reward_policy_requires_measured_no_action_baseline_object(self) -> None:
        self.assertIn("no_action_baseline_object", validate_no_action_baseline(True))
        self.assertFalse(validate_no_action_baseline(dict(VALID_NO_ACTION_BASELINE)))

    def test_reward_policy_blockers_include_missing_guardrails_and_baseline(self) -> None:
        blockers = reward_policy_blockers(
            {
                "formula_key": "reward_policy",
                "reward_calibrated": True,
                "no_action_baseline": True,
                "guardrails": ["frequency_cap"],
            }
        )

        self.assertIn("invalid_no_action_baseline:no_action_baseline_object", blockers)
        self.assertIn("missing_guardrail:consent_required", blockers)

    def test_missing_vulnerability_status_holds_active_nudge(self) -> None:
        blockers = reward_policy_blockers(
            {
                "reward_calibrated": True,
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "active_nudge_requested": True,
                "vulnerability_flag": None,
            }
        )

        self.assertIn("vulnerability_unknown", blockers)

    def test_high_cumulative_exposure_holds_even_if_current_fatigue_low(self) -> None:
        blockers = reward_policy_blockers(
            {
                "reward_calibrated": True,
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "active_nudge_requested": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.2,
                "recent_nudge_count": 5,
                "frequency_cap": 3,
            }
        )

        self.assertIn("frequency_cap_exceeded", blockers)

    def test_loss_frame_requires_manipulation_governance_review(self) -> None:
        blockers = reward_policy_blockers(
            {
                "reward_calibrated": True,
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "active_nudge_requested": True,
                "vulnerability_flag": False,
                "behavioral_method": "loss_frame",
            }
        )

        self.assertIn("manipulation_governance_review_missing", blockers)

    def test_no_action_can_win_against_active_nudge(self) -> None:
        result = score_action_reward(
            {
                "recommended_nudge": "gain_frame",
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.72,
                "activation_score": 0.45,
                "baseline_activation_score": 0.44,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
                "manipulation_governance_review": True,
            },
            action="gain_frame",
        )

        self.assertEqual(result.action, "no_action")
        self.assertIn("no_action_wins", result.reason_codes)

    def test_policy_ranking_includes_no_action_and_all_policy_actions(self) -> None:
        ranking = rank_actions_for_person(
            {
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.2,
                "friction_signal": 0.8,
                "resistance_signal": 0.5,
                "baseline_activation_score": 0.35,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
                "manipulation_governance_review": True,
            }
        )

        evaluated_actions = {item.evaluated_action for item in ranking}
        rewards = [item.reward for item in ranking]
        self.assertEqual(evaluated_actions, set(POLICY_ACTION_SET))
        self.assertIn("no_action", evaluated_actions)
        self.assertEqual(rewards, sorted(rewards, reverse=True))

    def test_policy_decision_selects_cognitive_ease_for_high_friction_when_allowed(self) -> None:
        decision = policy_decision_for_person(
            {
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.1,
                "friction_signal": 0.95,
                "resistance_signal": 0.88,
                "trust_gap_signal": 0.1,
                "peer_norm_signal": 0.1,
                "deadline_pressure": 0.1,
                "activation_gap": 0.2,
                "baseline_activation_score": 0.30,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
            }
        )

        self.assertEqual(decision["selected_action"], "cognitive_ease")
        self.assertEqual(decision["claim_type"], "hypothesis")

    def test_policy_ranking_blocks_active_actions_without_consent(self) -> None:
        decision = policy_decision_for_person(
            {
                "consent": False,
                "vulnerability_flag": False,
                "fatigue_signal": 0.1,
                "friction_signal": 0.95,
                "baseline_activation_score": 0.30,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
            }
        )

        self.assertEqual(decision["selected_action"], "no_action")
        blocked_actions = [
            item for item in decision["ranking"]
            if item["evaluated_action"] != "no_action"
        ]
        self.assertTrue(all(item["status"] == "blocked" for item in blocked_actions))
        self.assertTrue(all("missing_consent" in item["reason_codes"] for item in blocked_actions))

    def test_policy_ranking_keeps_control_group_on_no_action(self) -> None:
        decision = policy_decision_for_person(
            {
                "experiment_group": "control",
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.1,
                "friction_signal": 0.95,
                "baseline_activation_score": 0.30,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
            }
        )

        self.assertEqual(decision["selected_action"], "no_action")
        active_results = [
            item for item in decision["ranking"]
            if item["evaluated_action"] != "no_action"
        ]
        self.assertTrue(all("control_group" in item["reason_codes"] for item in active_results))

    def test_policy_ranking_blocks_social_proof_without_manipulation_review(self) -> None:
        decision = policy_decision_for_person(
            {
                "consent": True,
                "vulnerability_flag": False,
                "fatigue_signal": 0.1,
                "peer_norm_signal": 0.95,
                "peer_reference_group_valid": True,
                "baseline_activation_score": 0.30,
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                "reward_calibrated": True,
            }
        )

        social_proof = next(
            item for item in decision["ranking"]
            if item["evaluated_action"] == "social_proof"
        )
        self.assertEqual(social_proof["status"], "blocked")
        self.assertIn("manipulation_governance_review_missing", social_proof["reason_codes"])

    def test_orchestrator_holds_reward_policy_without_semantic_guardrails(self) -> None:
        result = Orchestrator().run_orchestration(
            Task(
                phase="formula_review",
                agent="statistical",
                prompt="Review policy with weak guardrails",
                context={
                    "formula_key": "reward_policy",
                    "reward_calibrated": True,
                    "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                    "guardrails": ["frequency_cap"],
                },
            )
        )

        self.assertEqual(result.next_action, "hold")

    def test_orchestrator_approves_policy_with_measured_baseline_and_full_guardrails(self) -> None:
        result = Orchestrator().run_orchestration(
            Task(
                phase="formula_review",
                agent="statistical",
                prompt="Review policy with full reward governance",
                context={
                    "formula_key": "reward_policy",
                    "reward_calibrated": True,
                    "no_action_baseline": dict(VALID_NO_ACTION_BASELINE),
                    "guardrails": sorted(REQUIRED_GUARDRAILS),
                    "vulnerability_flag": False,
                },
            )
        )

        self.assertEqual(result.next_action, "approve")


if __name__ == "__main__":
    unittest.main()
