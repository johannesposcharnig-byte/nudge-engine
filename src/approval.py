"""Structured human approval validation for pilot and outreach actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


APPROVAL_SCOPES = {"pilot_review", "outreach_export", "identity_resolution", "high_risk_intervention"}
NON_OVERRIDABLE_BLOCKERS = {"security_blocked", "security_hold", "privacy_not_safe", "data_contract_rejected"}


@dataclass(frozen=True)
class ApprovalDecision:
    valid: bool
    status: str
    actor: str | None
    reason: str | None
    approved_scopes: list[str]
    linked_run_id: str | None
    risk_tier: str | None
    blockers: list[str]
    override_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "status": self.status,
            "actor": self.actor,
            "reason": self.reason,
            "approved_scopes": list(self.approved_scopes),
            "linked_run_id": self.linked_run_id,
            "risk_tier": self.risk_tier,
            "blockers": list(self.blockers),
            "override_reason": self.override_reason,
        }


def evaluate_approval(
    approval: dict[str, Any] | None,
    *,
    required_scope: str,
    linked_run_id: str | None,
    active_blockers: list[str] | None = None,
) -> ApprovalDecision:
    """Validate an approval without allowing security/privacy overrides."""

    payload = dict(approval or {})
    if not payload:
        return ApprovalDecision(
            valid=False,
            status="not_provided",
            actor=None,
            reason=None,
            approved_scopes=[],
            linked_run_id=None,
            risk_tier=None,
            blockers=["approval_not_provided"],
        )
    blockers: list[str] = []
    actor = _clean(payload.get("actor") or payload.get("approver"))
    reason = _clean(payload.get("reason"))
    status = str(payload.get("status", "not_provided")).lower()
    scopes = _scopes(payload.get("approved_scope") or payload.get("approved_scopes"))
    approval_run_id = _clean(payload.get("linked_run_id"))
    timestamp = _clean(payload.get("timestamp"))
    risk_tier = _clean(payload.get("intervention_risk_tier") or payload.get("risk_tier"))
    override_reason = _clean(payload.get("override_reason"))

    if required_scope not in APPROVAL_SCOPES:
        blockers.append("unsupported_approval_scope")
    if status != "approved":
        blockers.append("approval_not_granted")
    if not actor:
        blockers.append("approval_actor_missing")
    if not reason:
        blockers.append("approval_reason_missing")
    if required_scope not in scopes:
        blockers.append("approval_scope_missing")
    if not timestamp or not _valid_timestamp(timestamp):
        blockers.append("approval_timestamp_invalid")
    if not linked_run_id or approval_run_id != linked_run_id:
        blockers.append("approval_run_mismatch")

    non_overridable = sorted(set(active_blockers or []) & NON_OVERRIDABLE_BLOCKERS)
    blockers.extend(f"non_overridable:{item}" for item in non_overridable)
    return ApprovalDecision(
        valid=not blockers,
        status="approved" if not blockers else "rejected",
        actor=actor,
        reason=reason,
        approved_scopes=scopes,
        linked_run_id=approval_run_id,
        risk_tier=risk_tier,
        blockers=sorted(set(blockers)),
        override_reason=override_reason,
    )


def legacy_approval_context(
    *,
    approval: bool,
    actor: str,
    reason: str,
    linked_run_id: str,
    scopes: list[str],
) -> dict[str, Any]:
    """Adapt the local v1 boolean API without using it inside the gate."""

    return {
        "status": "approved" if approval is True else "rejected",
        "actor": actor,
        "reason": reason,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "approved_scopes": scopes,
        "linked_run_id": linked_run_id,
        "intervention_risk_tier": "unknown",
    }


def _scopes(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return sorted({str(item) for item in value if str(item).strip()})
    return []


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _valid_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False
