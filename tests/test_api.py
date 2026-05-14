from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.api import analyze_payload


ROOT = Path(__file__).resolve().parents[1]
API_FIXTURE = ROOT / "tests" / "fixtures" / "api_activation_payload.json"


class ApiTests(unittest.TestCase):
    def test_analyze_payload_returns_report_for_valid_customer_rows(self) -> None:
        status, body = analyze_payload(
            {
                "question": "Which nudge should we test?",
                "identity_fields": ["user_id"],
                "customer_rows": [
                    {
                        "user_id": f"u{index}",
                        "event_time": f"2026-05-{(index % 28) + 1:02d}T09:00:00Z",
                        "activation_score": 1 if index % 2 else 0,
                        "consent": True,
                        "experiment_group": "treatment" if index % 2 else "control",
                        "friction_signal": 0.4,
                        "resistance_signal": 0.2,
                        "reward_calibrated": True,
                        "guardrails": ["consent", "frequency_cap", "protected_state_check", "no_dark_patterns"],
                        "no_action_baseline": {
                            "baseline_action": "no_action",
                            "sample_size": 20,
                            "mean_outcome": 0.4,
                            "ci_lower": 0.3,
                            "ci_upper": 0.5,
                            "confidence_level": 0.95,
                            "monitoring_required": True,
                        },
                    }
                    for index in range(40)
                ],
            }
        )

        self.assertEqual(status, 200)
        self.assertIn("executive_summary", body)
        self.assertIn("result_quality", body)
        self.assertIn("audit_lineage", body)

    def test_analyze_payload_returns_structured_error_for_bad_payload(self) -> None:
        status, body = analyze_payload({"question": "Analyze"})

        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "missing_customer_rows")
        self.assertNotIn("Traceback", str(body))

    def test_api_activation_fixture_is_valid_engine_input(self) -> None:
        payload = json.loads(API_FIXTURE.read_text(encoding="utf-8"))

        status, body = analyze_payload(payload)

        self.assertEqual(status, 200)
        self.assertEqual(body["result_quality"]["data_readiness"]["status"], "ready")
        self.assertTrue(body["security_and_governance"]["no_pii_in_segment_view"])
        self.assertFalse(body["audit_lineage"]["stored_raw_rows"])
        self.assertNotIn("user001@example.com", json.dumps(body))


if __name__ == "__main__":
    unittest.main()
