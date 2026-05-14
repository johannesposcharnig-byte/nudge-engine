"""PII vault boundary for pseudonymized customer analytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import re
from typing import Any


PII_FIELD_NAMES = {
    "email",
    "email_address",
    "full_name",
    "name",
    "phone",
    "phone_number",
    "mobile",
    "address",
    "street",
    "customer_name",
}

IDENTITY_FIELD_NAMES = {
    "user_id",
    "customer_id",
    "account_id",
    "company_id",
    "crm_id",
    "external_id",
}

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b")


@dataclass(frozen=True)
class VaultAuditEvent:
    action: str
    subject_id: str
    actor: str
    reason: str
    timestamp: str
    key_version: str
    fields: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "subject_id": self.subject_id,
            "actor": self.actor,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "key_version": self.key_version,
            "fields": list(self.fields),
        }


@dataclass(frozen=True)
class PseudonymizationResult:
    analytics_rows: list[dict[str, Any]]
    vault_records: list[dict[str, Any]]
    audit_events: list[VaultAuditEvent]
    redaction_summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "analytics_rows": [dict(row) for row in self.analytics_rows],
            "vault_records": [dict(record) for record in self.vault_records],
            "audit_events": [event.as_dict() for event in self.audit_events],
            "redaction_summary": dict(self.redaction_summary),
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _canonical_identity(row: dict[str, Any], identity_fields: list[str]) -> str:
    parts = []
    for field_name in identity_fields:
        value = row.get(field_name)
        if value not in {None, ""}:
            parts.append(f"{field_name}={str(value).strip().lower()}")
    if not parts:
        raise ValueError("At least one identity field is required for pseudonymization.")
    return "|".join(parts)


def stable_subject_id(identity_value: str, *, secret_key: str, key_version: str = "v1") -> str:
    digest = hmac.new(
        secret_key.encode("utf-8"),
        f"{key_version}:{identity_value}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sub_{digest[:16]}"


def _field_contains_pii(field_name: str, value: Any) -> bool:
    lower_field = field_name.lower()
    if lower_field in PII_FIELD_NAMES:
        return True
    if value is None:
        return False
    text = str(value)
    return bool(EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text))


def _vault_record_for_row(
    row: dict[str, Any],
    *,
    subject_id: str,
    identity_fields: list[str],
    key_version: str,
) -> dict[str, Any]:
    pii_payload = {}
    for field_name, value in row.items():
        if field_name in identity_fields or _field_contains_pii(field_name, value):
            pii_payload[field_name] = value
    return {
        "subject_id": subject_id,
        "key_version": key_version,
        "pii_fields": sorted(pii_payload),
        "pii_payload": pii_payload,
        "created_at": _now_iso(),
        "storage_class": "vault_only",
    }


def pseudonymize_customer_rows(
    rows: list[dict[str, Any]],
    *,
    secret_key: str,
    identity_fields: list[str] | None = None,
    key_version: str = "v1",
    actor: str = "orchestrator",
    reason: str = "customer_data_intake",
) -> PseudonymizationResult:
    """Split raw customer rows into vault records and agent-safe analytics rows.

    This boundary is intentionally deterministic for repeatable tests. In production,
    the vault records must be stored in a separate encrypted vault and the analytics
    rows are the only rows allowed to enter agent context.
    """

    if not secret_key:
        raise ValueError("secret_key is required for pseudonymization.")
    identity_fields = identity_fields or ["customer_id", "user_id", "account_id"]
    analytics_rows: list[dict[str, Any]] = []
    vault_by_subject: dict[str, dict[str, Any]] = {}
    audit_events: list[VaultAuditEvent] = []
    redacted_fields: set[str] = set()

    for row in rows:
        identity_value = _canonical_identity(row, identity_fields)
        subject_id = stable_subject_id(identity_value, secret_key=secret_key, key_version=key_version)
        vault_record = _vault_record_for_row(
            row,
            subject_id=subject_id,
            identity_fields=identity_fields,
            key_version=key_version,
        )
        existing = vault_by_subject.get(subject_id, {})
        merged_payload = {**existing.get("pii_payload", {}), **vault_record["pii_payload"]}
        vault_by_subject[subject_id] = {
            **vault_record,
            "pii_payload": merged_payload,
            "pii_fields": sorted(merged_payload),
        }

        analytics_row = {"subject_id": subject_id}
        for field_name, value in row.items():
            if field_name in identity_fields or _field_contains_pii(field_name, value):
                redacted_fields.add(field_name)
                continue
            analytics_row[field_name] = value
        analytics_rows.append(analytics_row)
        audit_events.append(
            VaultAuditEvent(
                action="pseudonymize",
                subject_id=subject_id,
                actor=actor,
                reason=reason,
                timestamp=_now_iso(),
                key_version=key_version,
                fields=sorted(vault_record["pii_fields"]),
            )
        )

    return PseudonymizationResult(
        analytics_rows=analytics_rows,
        vault_records=list(vault_by_subject.values()),
        audit_events=audit_events,
        redaction_summary={
            "redacted_fields": sorted(redacted_fields),
            "records_processed": len(rows),
            "vault_records": len(vault_by_subject),
            "key_version": key_version,
            "pii_removed_from_analytics": True,
        },
    )


def analytics_rows_are_pii_safe(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        for field_name, value in row.items():
            if field_name.lower() in PII_FIELD_NAMES:
                return False
            if value is not None and (EMAIL_PATTERN.search(str(value)) or PHONE_PATTERN.search(str(value))):
                return False
    return True
