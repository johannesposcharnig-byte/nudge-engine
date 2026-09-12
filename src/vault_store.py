"""Local protected vault store for controlled identity resolution.

This module is intentionally local-first. It is not a production vault: records
are stored in a git-ignored file and all identity resolution requires explicit
actor, reason and approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from .pii_vault import VaultAuditEvent


DEFAULT_RETENTION_DAYS = 90
DEFAULT_VAULT_PATH = Path("vault/local_vault.json")
ACTIVE = "active"
DELETED = "deleted"
EXPIRED = "expired"


@dataclass(frozen=True)
class VaultResolution:
    subject_id: str
    status: str
    identity: dict[str, Any]
    audit_event: VaultAuditEvent
    blocked_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "status": self.status,
            "identity": dict(self.identity),
            "audit_event": self.audit_event.as_dict(),
            "blocked_reason": self.blocked_reason,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def retention_until(created_at: str, retention_days: int = DEFAULT_RETENTION_DAYS) -> str:
    return (parse_iso(created_at) + timedelta(days=retention_days)).isoformat(timespec="seconds")


class LocalVaultStore:
    """Tiny local vault store for development and pilot simulation."""

    def __init__(self, path: Path | str = DEFAULT_VAULT_PATH, *, retention_days: int = DEFAULT_RETENTION_DAYS) -> None:
        self.path = Path(path)
        self.retention_days = retention_days
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"vault_records": {}, "audit_events": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8")

    def add_records(
        self,
        records: list[dict[str, Any]],
        *,
        audit_events: list[VaultAuditEvent] | None = None,
        persist: bool = True,
    ) -> None:
        for record in records:
            created_at = str(record.get("created_at") or now_iso())
            prepared = {
                **record,
                "created_at": created_at,
                "retention_until": record.get("retention_until") or retention_until(created_at, self.retention_days),
                "status": record.get("status") or ACTIVE,
                "storage_class": "vault_only",
            }
            self._data["vault_records"][prepared["subject_id"]] = prepared
        for event in audit_events or []:
            self._append_event(event)
        if persist:
            self.save()

    def resolve_subject_identity(
        self,
        subject_id: str,
        *,
        actor: str,
        reason: str,
        approval: bool,
        fields: list[str] | None = None,
    ) -> VaultResolution:
        record = self._data["vault_records"].get(subject_id)
        blocked_reason = self._resolution_blocker(subject_id, actor=actor, reason=reason, approval=approval)
        if blocked_reason:
            event = self._audit("reidentify_rejected", subject_id, actor, reason, record, fields or [], blocked_reason)
            return VaultResolution(subject_id, "rejected", {}, event, blocked_reason)

        payload = dict(record.get("pii_payload", {}))
        selected_fields = fields or sorted(payload)
        identity = {field: payload[field] for field in selected_fields if field in payload}
        event = self._audit("reidentify", subject_id, actor, reason, record, sorted(identity))
        return VaultResolution(subject_id, "approved", identity, event)

    def delete_subject(self, subject_id: str, *, actor: str, reason: str, approval: bool) -> VaultResolution:
        record = self._data["vault_records"].get(subject_id)
        blocked_reason = self._approval_blocker(actor=actor, reason=reason, approval=approval)
        if not record:
            blocked_reason = "unknown_subject"
        if blocked_reason:
            event = self._audit("delete_subject_rejected", subject_id, actor, reason, record, [], blocked_reason)
            return VaultResolution(subject_id, "rejected", {}, event, blocked_reason)
        record["status"] = DELETED
        event = self._audit("delete_subject", subject_id, actor, reason, record, sorted(record.get("pii_fields", [])))
        self.save()
        return VaultResolution(subject_id, "deleted", {}, event)

    def apply_retention_policy(self, *, now: str | None = None, actor: str = "system", reason: str = "retention_policy") -> list[VaultAuditEvent]:
        current = parse_iso(now or now_iso())
        events = []
        for subject_id, record in self._data["vault_records"].items():
            if record.get("status") != ACTIVE:
                continue
            expires_at = parse_iso(str(record.get("retention_until")))
            if expires_at <= current:
                record["status"] = EXPIRED
                events.append(self._audit("retention_expire", subject_id, actor, reason, record, []))
        if events:
            self.save()
        return events

    def subject_is_resolvable(self, subject_id: str) -> bool:
        record = self._data["vault_records"].get(subject_id)
        return bool(record and record.get("status") == ACTIVE)

    def get_record(self, subject_id: str) -> dict[str, Any] | None:
        record = self._data["vault_records"].get(subject_id)
        return dict(record) if record else None

    @property
    def audit_events(self) -> list[dict[str, Any]]:
        return [dict(event) for event in self._data["audit_events"]]

    def _approval_blocker(self, *, actor: str, reason: str, approval: bool) -> str | None:
        if not actor:
            return "missing_actor"
        if not reason:
            return "missing_reason"
        if approval is not True:
            return "approval_required"
        return None

    def _resolution_blocker(self, subject_id: str, *, actor: str, reason: str, approval: bool) -> str | None:
        approval_blocker = self._approval_blocker(actor=actor, reason=reason, approval=approval)
        if approval_blocker:
            return approval_blocker
        record = self._data["vault_records"].get(subject_id)
        if not record:
            return "unknown_subject"
        if record.get("status") == DELETED:
            return "subject_deleted"
        if record.get("status") == EXPIRED:
            return "subject_expired"
        if record.get("status") != ACTIVE:
            return "subject_not_active"
        return None

    def _audit(
        self,
        action: str,
        subject_id: str,
        actor: str,
        reason: str,
        record: dict[str, Any] | None,
        fields: list[str],
        blocked_reason: str | None = None,
    ) -> VaultAuditEvent:
        event = VaultAuditEvent(
            action=action,
            subject_id=subject_id,
            actor=actor or "unknown",
            reason=reason or blocked_reason or "missing_reason",
            timestamp=now_iso(),
            key_version=str((record or {}).get("key_version", "unknown")),
            fields=fields,
        )
        payload = event.as_dict()
        if blocked_reason:
            payload["blocked_reason"] = blocked_reason
        self._data["audit_events"].append(payload)
        return event

    def _append_event(self, event: VaultAuditEvent) -> None:
        self._data["audit_events"].append(event.as_dict())
