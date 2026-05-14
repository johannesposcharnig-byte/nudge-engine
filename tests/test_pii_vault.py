import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pii_vault import (
    analytics_rows_are_pii_safe,
    pseudonymize_customer_rows,
    stable_subject_id,
)
from src.security import leonidas_security_review


class PiiVaultTests(unittest.TestCase):
    def test_stable_subject_id_uses_key_version_and_hmac(self) -> None:
        first = stable_subject_id("customer_id=c1", secret_key="vault-secret", key_version="v1")
        second = stable_subject_id("customer_id=c1", secret_key="vault-secret", key_version="v1")
        rotated = stable_subject_id("customer_id=c1", secret_key="vault-secret", key_version="v2")

        self.assertEqual(first, second)
        self.assertNotEqual(first, rotated)
        self.assertTrue(first.startswith("sub_"))
        self.assertNotIn("c1", first)

    def test_pseudonymization_splits_pii_from_analytics_rows(self) -> None:
        result = pseudonymize_customer_rows(
            [
                {
                    "customer_id": "c1",
                    "email": "person@example.com",
                    "phone": "+43 660 1234567",
                    "event_time": "2026-05-01T09:00:00Z",
                    "fatigue_signal": "0.2",
                }
            ],
            secret_key="vault-secret",
            identity_fields=["customer_id"],
            key_version="v1",
            actor="test",
            reason="unit_test",
        )

        self.assertEqual(len(result.analytics_rows), 1)
        self.assertEqual(len(result.vault_records), 1)
        analytics_row = result.analytics_rows[0]
        vault_record = result.vault_records[0]
        self.assertIn("subject_id", analytics_row)
        self.assertNotIn("customer_id", analytics_row)
        self.assertNotIn("email", analytics_row)
        self.assertNotIn("phone", analytics_row)
        self.assertEqual(vault_record["subject_id"], analytics_row["subject_id"])
        self.assertIn("email", vault_record["pii_payload"])
        self.assertIn("phone", vault_record["pii_payload"])
        self.assertTrue(analytics_rows_are_pii_safe(result.analytics_rows))
        self.assertTrue(result.audit_events)
        self.assertEqual(result.audit_events[0].action, "pseudonymize")

    def test_leonidas_accepts_pseudonymized_analytics_rows(self) -> None:
        result = pseudonymize_customer_rows(
            [
                {
                    "customer_id": "c1",
                    "email": "person@example.com",
                    "event_time": "2026-05-01T09:00:00Z",
                    "fatigue_signal": "0.2",
                }
            ],
            secret_key="vault-secret",
            identity_fields=["customer_id"],
        )

        review = leonidas_security_review(
            {
                "customer_rows": result.analytics_rows,
                "pii_pseudonymized": True,
            }
        )

        self.assertEqual(review.security_status, "approve")
        self.assertTrue(review.safe_to_reason)
        self.assertTrue(review.safe_to_execute)

    def test_raw_pii_still_holds_without_pseudonymization(self) -> None:
        review = leonidas_security_review(
            {
                "customer_rows": [
                    {
                        "customer_id": "c1",
                        "email": "person@example.com",
                        "event_time": "2026-05-01T09:00:00Z",
                    }
                ]
            }
        )

        self.assertEqual(review.security_status, "hold")
        self.assertFalse(review.safe_to_execute)
        self.assertTrue(any(risk.risk_type == "pii_exposure" for risk in review.detected_risks))


if __name__ == "__main__":
    unittest.main()
