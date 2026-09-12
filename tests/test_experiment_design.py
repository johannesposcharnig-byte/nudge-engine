from __future__ import annotations

import unittest

from src.experiment_design import build_experiment_design


class ExperimentDesignTests(unittest.TestCase):
    def test_missing_outcome_requests_clarification_without_inventing_plan(self) -> None:
        plan = build_experiment_design(
            data_readiness={"status": "hold"},
            context={"outcome_variable": None},
            hypotheses=[],
            uncertainty={},
        )

        self.assertEqual(plan["status"], "clarification_required")
        self.assertFalse(plan["experiment_required"])
        self.assertIn("outcome", plan["blocked_reason"])

    def test_treatment_without_control_creates_safe_ab_plan(self) -> None:
        plan = build_experiment_design(
            data_readiness={
                "status": "experiment_required",
                "detected_groups": {"treatment": ["experiment_group"]},
            },
            context={"outcome_variable": "activation_score"},
            hypotheses=[{"id": "H1", "statement": "Treatment may change activation.", "status": "testable"}],
            uncertainty={},
            confidence_level=0.9,
        )

        self.assertTrue(plan["experiment_required"])
        self.assertEqual(plan["recommended_method"], "ab_test")
        self.assertEqual(plan["confidence_level"], 0.95)
        self.assertEqual(plan["measurement_window"], "clarification_required")
        self.assertIn("not evidence", plan["claim_permission"])

    def test_pre_period_covariate_selects_cuped(self) -> None:
        plan = build_experiment_design(
            data_readiness={"status": "experiment_required", "detected_groups": {"treatment": []}},
            context={"outcome_variable": "activation_score"},
            hypotheses=[],
            uncertainty={},
            config={"pre_period_covariate": "activation_pre"},
        )

        self.assertEqual(plan["recommended_method"], "cuped")


if __name__ == "__main__":
    unittest.main()
