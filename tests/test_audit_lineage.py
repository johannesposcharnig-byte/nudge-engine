from __future__ import annotations

import unittest

from src.audit_lineage import build_audit_lineage


class AuditLineageTests(unittest.TestCase):
    def test_audit_lineage_stores_run_metadata_not_raw_rows(self) -> None:
        lineage = build_audit_lineage(
            rows=[{"subject_id": "sub_1", "activation_score": 1}],
            data_readiness={
                "schema_hash": "abc123",
                "available_columns": ["subject_id", "activation_score"],
            },
            result_quality={
                "decision_state": {
                    "state": "pilot_candidate",
                    "blockers": [],
                }
            },
            security_review={"security_status": "approve"},
        )

        self.assertTrue(lineage["run_id"].startswith("run_"))
        self.assertEqual(lineage["input_schema_hash"], "abc123")
        self.assertEqual(lineage["input_row_count"], 1)
        self.assertEqual(lineage["decision_state"], "pilot_candidate")
        self.assertFalse(lineage["stored_raw_rows"])
        self.assertNotIn("sub_1", str(lineage))


if __name__ == "__main__":
    unittest.main()
