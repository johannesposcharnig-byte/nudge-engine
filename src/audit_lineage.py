"""Lightweight audit lineage for local and pilot analysis runs."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any
from uuid import uuid4


ENGINE_VERSION = "0.1.0-local"
POLICY_VERSION = "0.1.0-policy"
REPORT_VERSION = "0.1.0-report"


def _hash_columns(columns: list[str]) -> str:
    canonical = "|".join(sorted(str(column).lower() for column in columns))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def build_audit_lineage(
    *,
    rows: list[dict[str, Any]],
    data_readiness: dict[str, Any],
    result_quality: dict[str, Any],
    security_review: dict[str, Any],
    human_override_status: str = "none",
) -> dict[str, Any]:
    """Create an audit-friendly run record without persisting raw row content."""

    available_columns = list(data_readiness.get("available_columns", []))
    decision_state = result_quality.get("decision_state", {})
    return {
        "run_id": f"run_{uuid4().hex[:12]}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_version": ENGINE_VERSION,
        "policy_version": POLICY_VERSION,
        "report_version": REPORT_VERSION,
        "input_row_count": len(rows),
        "input_schema_hash": data_readiness.get("schema_hash") or _hash_columns(available_columns),
        "decision_state": decision_state.get("state", "unknown"),
        "blockers": list(decision_state.get("blockers", [])),
        "security_status": security_review.get("security_status", "unknown"),
        "privacy_state": "pii_safe_context",
        "human_override_status": human_override_status,
        "stored_raw_rows": False,
    }
