from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.behavioral_methods import (
    BEHAVIORAL_METHOD_REGISTRY,
    action_methods,
    evaluate_behavioral_method,
    human_review_required_for_method,
    intervention_risk_tier,
    intervention_risk_tier_coverage,
    meta_methods,
)


class BehavioralMethodRegistryTests(unittest.TestCase):
    def test_registry_contains_full_scientific_starting_set(self) -> None:
        expected_actions = {
            "no_action",
            "default",
            "cognitive_ease",
            "simplification",
            "social_proof",
            "gain_frame",
            "loss_frame",
            "commitment",
            "reciprocity",
            "timely_reminder",
            "goal_setting",
            "progress_feedback",
            "just_in_time_intervention",
            "transparency_explanation",
            "progress_oriented_default",
        }

        self.assertTrue(expected_actions.issubset(set(action_methods())))
        self.assertIn("personalization", meta_methods())

    def test_every_action_has_mechanism_and_hypothesis_claim_type(self) -> None:
        for method_name in action_methods():
            with self.subTest(method_name=method_name):
                method = BEHAVIORAL_METHOD_REGISTRY[method_name]
                self.assertTrue(method.mechanism)
                self.assertIn(method.allowed_claim_type, {"hypothesis", "observed"})
                if method.kind == "action":
                    self.assertEqual(method.allowed_claim_type, "hypothesis")

    def test_social_proof_requires_peer_norm_and_valid_reference_group(self) -> None:
        missing = evaluate_behavioral_method("social_proof", {"peer_norm_signal": 0.8})
        self.assertEqual(missing.status, "blocked")
        self.assertIn("missing_signal:peer_reference_group_valid", missing.reason_codes)

        eligible = evaluate_behavioral_method(
            "social_proof",
            {"peer_norm_signal": 0.8, "peer_reference_group_valid": True},
        )
        self.assertEqual(eligible.status, "eligible")
        self.assertGreater(eligible.fit_score, 0.0)

    def test_loss_frame_blocks_when_fatigue_is_elevated(self) -> None:
        result = evaluate_behavioral_method(
            "loss_frame",
            {"deadline_pressure": 0.9, "fatigue_signal": 0.65},
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn("method_blocked_by_fatigue", result.reason_codes)

    def test_cognitive_ease_is_eligible_for_high_friction_and_resistance(self) -> None:
        result = evaluate_behavioral_method(
            "cognitive_ease",
            {"friction_signal": 0.9, "resistance_signal": 0.8},
        )

        self.assertEqual(result.status, "eligible")
        self.assertGreaterEqual(result.fit_score, 0.8)

    def test_unknown_method_is_blocked(self) -> None:
        result = evaluate_behavioral_method("scarcity_pressure", {})

        self.assertEqual(result.status, "blocked")
        self.assertIn("unknown_behavioral_method", result.reason_codes)
        self.assertEqual(result.claim_type, "blocked")

    def test_all_registered_methods_have_intervention_risk_tiers(self) -> None:
        coverage = intervention_risk_tier_coverage()

        self.assertEqual(coverage["missing"], [])
        self.assertEqual(coverage["extra"], [])
        self.assertEqual(intervention_risk_tier("loss_frame"), "high")
        self.assertEqual(intervention_risk_tier("no_action"), "baseline")
        self.assertEqual(intervention_risk_tier("personalization"), "meta")
        self.assertEqual(intervention_risk_tier("fake_scarcity"), "prohibited")

    def test_human_review_required_for_sensitive_methods(self) -> None:
        self.assertTrue(human_review_required_for_method("loss_frame"))
        self.assertTrue(human_review_required_for_method("social_proof"))
        self.assertFalse(human_review_required_for_method("cognitive_ease"))

        result = evaluate_behavioral_method(
            "social_proof",
            {"peer_norm_signal": 0.8, "peer_reference_group_valid": True},
        )
        self.assertTrue(result.as_dict()["human_review_required"])
        self.assertEqual(result.as_dict()["risk_tier"], "medium")


if __name__ == "__main__":
    unittest.main()
