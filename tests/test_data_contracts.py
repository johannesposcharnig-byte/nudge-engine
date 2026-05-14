from __future__ import annotations

import unittest

from src.data_contracts import evaluate_activation_data_contract


class DataContractTests(unittest.TestCase):
    def test_ready_dataset_includes_deep_readiness_profile(self) -> None:
        rows = [
            {
                "subject_id": f"sub_{index}",
                "event_time": f"2026-05-{(index % 28) + 1:02d}T09:00:00Z",
                "activation_score": 1 if index % 2 else 0,
                "consent": True,
                "experiment_group": "treatment" if index % 2 else "control",
                "friction_signal": 0.2,
            }
            for index in range(120)
        ]

        readiness = evaluate_activation_data_contract(rows).as_dict()

        self.assertEqual(readiness["status"], "ready")
        self.assertTrue(readiness["causal_ready"])
        self.assertEqual(readiness["row_count"], 120)
        self.assertIn("treatment", readiness["treatment_balance"])
        self.assertIn("control", readiness["treatment_balance"])
        self.assertEqual(readiness["outcome_profile"]["field"], "activation_score")
        self.assertTrue(readiness["outcome_profile"]["binary_like"])
        self.assertTrue(readiness["field_profiles"])

    def test_invalid_timestamp_holds_before_time_based_claims(self) -> None:
        rows = [
            {
                "subject_id": "sub_1",
                "event_time": "not-a-date",
                "activation_score": 1,
                "consent": True,
                "experiment_group": "treatment",
            },
            {
                "subject_id": "sub_2",
                "event_time": "2026-05-01T09:00:00Z",
                "activation_score": 0,
                "consent": True,
                "experiment_group": "control",
            },
        ]

        readiness = evaluate_activation_data_contract(rows).as_dict()

        self.assertEqual(readiness["status"], "hold")
        self.assertTrue(any(warning.startswith("invalid_timestamp_values") for warning in readiness["readiness_warnings"]))
        self.assertIn("ungueltige Zeitwerte", " ".join(readiness["clarification_questions"]))

    def test_treatment_without_control_requires_experiment_design(self) -> None:
        rows = [
            {
                "subject_id": f"sub_{index}",
                "event_time": "2026-05-01T09:00:00Z",
                "activation_score": 1,
                "consent": True,
                "experiment_group": "treatment",
            }
            for index in range(40)
        ]

        readiness = evaluate_activation_data_contract(rows).as_dict()

        self.assertEqual(readiness["status"], "experiment_required")
        self.assertFalse(readiness["causal_ready"])
        self.assertIn("treatment_without_usable_control", readiness["readiness_warnings"])


if __name__ == "__main__":
    unittest.main()
