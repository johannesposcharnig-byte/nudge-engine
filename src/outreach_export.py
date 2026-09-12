"""Governed outreach export for approved nudge candidates."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .approval import evaluate_approval, legacy_approval_context
from .pii_vault import analytics_rows_are_pii_safe
from .vault_store import LocalVaultStore


EXPORTABLE_STATUSES = {"approve", "approved", "hypothesis", "pilot_candidate"}
BLOCKED_STATUSES = {"blocked", "reject", "hold"}


def build_outreach_export(
    report: dict[str, Any],
    vault: LocalVaultStore,
    *,
    actor: str,
    reason: str,
    approval: bool,
    include_identity: bool = False,
    approval_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Create governed outreach rows from a decision report.

    Identity resolution is optional and still requires explicit approval. Rows
    that are blocked, expired, deleted, missing consent or unresolved are skipped
    with an explicit export status.
    """

    run_id = report.get("audit_lineage", {}).get("run_id") or "legacy_local_export"
    if approval_context is None:
        approval_context = legacy_approval_context(
            approval=approval,
            actor=actor,
            reason=reason,
            linked_run_id=run_id,
            scopes=["outreach_export", "identity_resolution"],
        )
    decision_blockers = report.get("result_quality", {}).get("decision_state", {}).get("blockers", [])
    outreach_approval = evaluate_approval(
        approval_context,
        required_scope="outreach_export",
        linked_run_id=run_id,
        active_blockers=decision_blockers,
    )
    identity_approval = evaluate_approval(
        approval_context,
        required_scope="identity_resolution",
        linked_run_id=run_id,
        active_blockers=decision_blockers,
    )
    segment_by_subject = {
        row.get("subject_id"): row for row in report.get("segment_view", []) if row.get("subject_id")
    }
    exports: list[dict[str, Any]] = []
    for item in report.get("nudge_recommendations", []):
        subject_id = item.get("subject_id")
        if not subject_id:
            continue
        segment = segment_by_subject.get(subject_id, {})
        base = _base_export_row(item)
        if not outreach_approval.valid:
            exports.append({**base, "export_status": "skipped_approval_required"})
            continue
        if str(item.get("status")) in BLOCKED_STATUSES:
            exports.append({**base, "export_status": "skipped_blocked"})
            continue
        if item.get("selected_action") == "no_action":
            exports.append({**base, "export_status": "skipped_no_action"})
            continue
        if segment.get("consent") is not True:
            exports.append({**base, "export_status": "skipped_missing_consent"})
            continue
        if not vault.subject_is_resolvable(subject_id):
            exports.append({**base, "export_status": "skipped_not_resolvable"})
            continue

        export_row = {
            **base,
            "message_variant": _message_variant(str(item.get("selected_action", "no_action"))),
            "human_review_status": "approved" if item.get("human_review_required") else "not_required",
            "export_status": "ready",
        }
        if include_identity:
            if not identity_approval.valid:
                exports.append({**base, "export_status": "skipped_approval_required"})
                continue
            resolution = vault.resolve_subject_identity(
                subject_id,
                actor=actor,
                reason=reason,
                approval=identity_approval.valid,
                fields=["customer_id", "user_id", "crm_id", "external_id"],
            )
            if resolution.status != "approved":
                exports.append({**base, "export_status": f"skipped_{resolution.blocked_reason}"})
                continue
            export_row.update(_resolved_identity_fields(resolution.identity))
        exports.append(export_row)
    return exports


def write_outreach_csv(rows: list[dict[str, Any]], path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_outreach_json(rows: list[dict[str, Any]], path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def outreach_rows_are_pii_safe(rows: list[dict[str, Any]]) -> bool:
    return analytics_rows_are_pii_safe(rows)


def _base_export_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "subject_id": item.get("subject_id"),
        "selected_action": item.get("selected_action"),
        "reason_codes": ",".join(item.get("reason_codes", [])),
        "claim_type": item.get("claim_type", "hypothesis"),
        "effect_evidence": item.get("effect_evidence", "hypothesis_only"),
        "risk_tier": item.get("risk_tier"),
        "human_review_status": "required" if item.get("human_review_required") else "not_required",
    }


def _message_variant(action: str) -> str:
    variants = {
        "cognitive_ease": "simplify_next_step",
        "simplification": "reduce_steps",
        "progress_feedback": "show_progress",
        "commitment": "ask_commitment",
        "social_proof": "validated_reference_group_required",
    }
    return variants.get(action, f"{action}_pilot_message")


def _resolved_identity_fields(identity: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "customer_id": "resolved_customer_id",
        "user_id": "resolved_user_id",
        "crm_id": "resolved_crm_id",
        "external_id": "resolved_external_id",
    }
    return {target: identity[source] for source, target in mapping.items() if source in identity}
