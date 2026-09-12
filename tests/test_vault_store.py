from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from src.pii_vault import pseudonymize_customer_rows
from src.vault_store import LocalVaultStore


class VaultStoreTests(unittest.TestCase):
    def make_store(self) -> tuple[LocalVaultStore, str]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "vault.json"
        result = pseudonymize_customer_rows(
            [
                {
                    "customer_id": "c1",
                    "email": "person@example.com",
                    "crm_id": "crm-1",
                    "event_time": "2026-05-01T09:00:00Z",
                }
            ],
            secret_key="vault-secret",
            identity_fields=["customer_id"],
            actor="test",
            reason="unit_test",
        )
        store = LocalVaultStore(path)
        store.add_records(result.vault_records, audit_events=result.audit_events)
        return store, result.analytics_rows[0]["subject_id"]

    def test_vault_records_persist_locally(self) -> None:
        store, subject_id = self.make_store()
        loaded = json.loads(store.path.read_text(encoding="utf-8"))

        self.assertIn(subject_id, loaded["vault_records"])
        self.assertEqual(loaded["vault_records"][subject_id]["status"], "active")
        self.assertEqual(loaded["vault_records"][subject_id]["storage_class"], "vault_only")
        self.assertIn("retention_until", loaded["vault_records"][subject_id])

    def test_reidentify_requires_explicit_approval(self) -> None:
        store, subject_id = self.make_store()

        rejected = store.resolve_subject_identity(
            subject_id,
            actor="pilot_admin",
            reason="support_followup",
            approval=False,
        )
        approved = store.resolve_subject_identity(
            subject_id,
            actor="pilot_admin",
            reason="support_followup",
            approval=True,
        )

        self.assertEqual(rejected.status, "rejected")
        self.assertEqual(rejected.blocked_reason, "approval_required")
        self.assertEqual(rejected.audit_event.action, "reidentify_rejected")
        self.assertEqual(approved.status, "approved")
        self.assertEqual(approved.identity["customer_id"], "c1")
        self.assertEqual(approved.audit_event.action, "reidentify")

    def test_missing_actor_or_reason_blocks_reidentification(self) -> None:
        store, subject_id = self.make_store()

        missing_actor = store.resolve_subject_identity(subject_id, actor="", reason="support", approval=True)
        missing_reason = store.resolve_subject_identity(subject_id, actor="admin", reason="", approval=True)

        self.assertEqual(missing_actor.blocked_reason, "missing_actor")
        self.assertEqual(missing_reason.blocked_reason, "missing_reason")

    def test_deleted_subject_cannot_be_resolved(self) -> None:
        store, subject_id = self.make_store()

        deleted = store.delete_subject(subject_id, actor="privacy_admin", reason="deletion_request", approval=True)
        resolved = store.resolve_subject_identity(subject_id, actor="pilot_admin", reason="support", approval=True)

        self.assertEqual(deleted.status, "deleted")
        self.assertFalse(store.subject_is_resolvable(subject_id))
        self.assertEqual(resolved.status, "rejected")
        self.assertEqual(resolved.blocked_reason, "subject_deleted")

    def test_expired_subject_cannot_be_resolved(self) -> None:
        store, subject_id = self.make_store()
        future = (datetime.now(timezone.utc) + timedelta(days=120)).isoformat(timespec="seconds")

        events = store.apply_retention_policy(now=future)
        resolved = store.resolve_subject_identity(subject_id, actor="pilot_admin", reason="support", approval=True)

        self.assertTrue(events)
        self.assertEqual(events[0].action, "retention_expire")
        self.assertFalse(store.subject_is_resolvable(subject_id))
        self.assertEqual(resolved.blocked_reason, "subject_expired")


if __name__ == "__main__":
    unittest.main()
