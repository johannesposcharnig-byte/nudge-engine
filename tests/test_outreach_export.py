from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.outreach_export import build_outreach_export, outreach_rows_are_pii_safe, write_outreach_csv, write_outreach_json
from src.pii_vault import pseudonymize_customer_rows
from src.reporting import DecisionReportInput, build_decision_report
from src.vault_store import LocalVaultStore


class OutreachExportTests(unittest.TestCase):
    def make_report_and_store(self) -> tuple[dict, LocalVaultStore, dict[str, str]]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raw_rows = [
            {
                "customer_id": "c1",
                "email": "person1@example.com",
                "event_time": "2026-05-01T09:00:00Z",
                "consent": True,
            },
            {
                "customer_id": "c2",
                "email": "person2@example.com",
                "event_time": "2026-05-01T09:00:00Z",
                "consent": False,
            },
            {
                "customer_id": "c3",
                "email": "person3@example.com",
                "event_time": "2026-05-01T09:00:00Z",
                "consent": True,
            },
        ]
        vault = pseudonymize_customer_rows(raw_rows, secret_key="vault-secret", identity_fields=["customer_id"])
        store = LocalVaultStore(Path(tmp.name) / "vault.json")
        store.add_records(vault.vault_records, audit_events=vault.audit_events)
        ids = {
            "active": vault.analytics_rows[0]["subject_id"],
            "missing_consent": vault.analytics_rows[1]["subject_id"],
            "blocked": vault.analytics_rows[2]["subject_id"],
        }
        report = build_decision_report(
            DecisionReportInput(
                title="Outreach Report",
                orchestrator_result={"next_action": "approve", "summary": "ok", "confidence": 0.8},
                policy_decisions=[
                    {
                        "subject_id": ids["active"],
                        "selected_result": {
                            "subject_id": ids["active"],
                            "action": "cognitive_ease",
                            "status": "hypothesis",
                            "claim_type": "hypothesis",
                            "reason_codes": ["high_friction"],
                            "method_evaluation": {
                                "risk_tier": "low",
                                "human_review_required": False,
                                "status": "eligible",
                                "fit_score": 0.8,
                            },
                        },
                    },
                    {
                        "subject_id": ids["missing_consent"],
                        "selected_result": {
                            "subject_id": ids["missing_consent"],
                            "action": "cognitive_ease",
                            "status": "hypothesis",
                            "claim_type": "hypothesis",
                            "reason_codes": ["high_friction"],
                            "method_evaluation": {"risk_tier": "low", "human_review_required": False},
                        },
                    },
                    {
                        "subject_id": ids["blocked"],
                        "selected_result": {
                            "subject_id": ids["blocked"],
                            "action": "no_action",
                            "status": "blocked",
                            "claim_type": "blocked",
                            "reason_codes": ["high_fatigue"],
                            "method_evaluation": {"risk_tier": "baseline", "human_review_required": False},
                        },
                    },
                ],
                segment_rows=vault.analytics_rows,
                pii_redaction_summary=vault.redaction_summary,
            )
        )
        return report, store, ids

    def test_outreach_export_includes_only_approved_active_candidates(self) -> None:
        report, store, ids = self.make_report_and_store()

        rows = build_outreach_export(
            report,
            store,
            actor="pilot_admin",
            reason="activation_pilot_export",
            approval=True,
            include_identity=False,
        )

        by_subject = {row["subject_id"]: row for row in rows}
        self.assertEqual(by_subject[ids["active"]]["export_status"], "ready")
        self.assertEqual(by_subject[ids["missing_consent"]]["export_status"], "skipped_missing_consent")
        self.assertEqual(by_subject[ids["blocked"]]["export_status"], "skipped_blocked")
        self.assertTrue(outreach_rows_are_pii_safe(rows))
        self.assertNotIn("person1@example.com", str(rows))

    def test_identity_resolution_in_export_requires_approval(self) -> None:
        report, store, ids = self.make_report_and_store()

        rejected = build_outreach_export(
            report,
            store,
            actor="pilot_admin",
            reason="activation_pilot_export",
            approval=False,
            include_identity=True,
        )
        approved = build_outreach_export(
            report,
            store,
            actor="pilot_admin",
            reason="activation_pilot_export",
            approval=True,
            include_identity=True,
        )

        rejected_active = next(row for row in rejected if row["subject_id"] == ids["active"])
        approved_active = next(row for row in approved if row["subject_id"] == ids["active"])
        self.assertEqual(rejected_active["export_status"], "skipped_approval_required")
        self.assertEqual(approved_active["resolved_customer_id"], "c1")
        self.assertNotIn("email", approved_active)

    def test_deleted_subject_is_skipped(self) -> None:
        report, store, ids = self.make_report_and_store()
        store.delete_subject(ids["active"], actor="privacy_admin", reason="deletion_request", approval=True)

        rows = build_outreach_export(
            report,
            store,
            actor="pilot_admin",
            reason="activation_pilot_export",
            approval=True,
            include_identity=True,
        )

        active = next(row for row in rows if row["subject_id"] == ids["active"])
        self.assertEqual(active["export_status"], "skipped_not_resolvable")

    def test_expired_subject_is_skipped(self) -> None:
        report, store, ids = self.make_report_and_store()
        store.apply_retention_policy(now="2200-01-01T00:00:00+00:00")

        rows = build_outreach_export(
            report,
            store,
            actor="pilot_admin",
            reason="activation_pilot_export",
            approval=True,
            include_identity=True,
        )

        active = next(row for row in rows if row["subject_id"] == ids["active"])
        self.assertEqual(active["export_status"], "skipped_not_resolvable")

    def test_export_writers_create_csv_and_json(self) -> None:
        report, store, _ = self.make_report_and_store()
        rows = build_outreach_export(report, store, actor="pilot_admin", reason="export", approval=True)
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "export.csv"
            json_path = Path(tmp) / "export.json"
            write_outreach_csv(rows, csv_path)
            write_outreach_json(rows, json_path)

            self.assertTrue(csv_path.exists())
            self.assertTrue(json_path.exists())
            self.assertIn("subject_id", csv_path.read_text(encoding="utf-8"))
            self.assertIn("subject_id", json_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
