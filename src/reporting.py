"""Decision reporting for Nudge Engine outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from .agents.base import AgentMessage
from .pii_vault import PII_FIELD_NAMES, analytics_rows_are_pii_safe


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b")
REDACTED = "[REDACTED]"

DIRECT_IDENTIFIER_FIELDS = PII_FIELD_NAMES | {
    "customer_id",
    "user_id",
    "account_id",
    "company_id",
    "crm_id",
    "external_id",
    "pii_payload",
    "vault_records",
}

STATUS_PRIORITY = {
    "reject": 4,
    "blocked": 4,
    "hold": 3,
    "revise": 2,
    "partial": 2,
    "hypothesis": 1,
    "approve": 0,
    "done": 0,
}


@dataclass(frozen=True)
class DecisionReportInput:
    title: str
    orchestrator_result: AgentMessage | dict[str, Any]
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    policy_decisions: list[dict[str, Any]] = field(default_factory=list)
    security_review: dict[str, Any] = field(default_factory=dict)
    pii_redaction_summary: dict[str, Any] = field(default_factory=dict)
    uncertainty: dict[str, Any] = field(default_factory=dict)
    segment_rows: list[dict[str, Any]] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    result_quality: dict[str, Any] = field(default_factory=dict)


def _message_to_dict(message: AgentMessage | dict[str, Any]) -> dict[str, Any]:
    if isinstance(message, dict):
        return dict(message)
    return {
        "agent": message.agent,
        "phase": message.phase,
        "summary": message.summary,
        "done_status": message.done_status,
        "next_action": message.next_action,
        "confidence": message.confidence,
        "claims": list(message.claims),
        "risks": list(message.risks),
        "open_questions": list(message.open_questions),
        "blocked_reason": message.blocked_reason,
        "decision_rationale": message.decision_rationale,
        "context": dict(message.context),
        "uncertainty": dict(message.uncertainty),
    }


def _redact_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    value = EMAIL_PATTERN.sub(REDACTED, value)
    value = PHONE_PATTERN.sub(REDACTED, value)
    return value


def sanitize_for_report(value: Any) -> Any:
    """Remove PII/vault payloads from reportable structures."""

    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            lower_key = str(key).lower()
            if lower_key in DIRECT_IDENTIFIER_FIELDS:
                continue
            sanitized[key] = sanitize_for_report(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_for_report(item) for item in value]
    return _redact_scalar(value)


def _overall_status(*statuses: str | None) -> str:
    normalized = [status for status in statuses if status]
    if not normalized:
        return "hold"
    return max(normalized, key=lambda status: STATUS_PRIORITY.get(status, 2))


def _uncertainty_decision(uncertainty: dict[str, Any]) -> dict[str, Any]:
    if not uncertainty:
        return {
            "status": "hold",
            "summary": "No uncertainty interval available; no significance claim is allowed.",
            "significance_claim_allowed": False,
        }
    required = {"effect_estimate", "ci_lower", "ci_upper", "ci_method", "sample_size", "confidence_level", "contains_null"}
    missing = sorted(required - set(uncertainty))
    if missing:
        return {
            "status": "hold",
            "summary": f"Uncertainty fields are incomplete: {', '.join(missing)}.",
            "significance_claim_allowed": False,
        }
    if uncertainty.get("contains_null") is True:
        return {
            "status": "revise",
            "summary": "Confidence interval contains the null; effect is not decision-stable.",
            "significance_claim_allowed": False,
        }
    confidence_level = float(uncertainty.get("confidence_level", 0.0))
    return {
        "status": "approve" if confidence_level >= 0.95 else "revise",
        "summary": "Confidence interval excludes the null." if confidence_level >= 0.95 else "Exploratory interval excludes the null but is below 0.95.",
        "significance_claim_allowed": confidence_level >= 0.95,
    }


def _policy_summary(policy_decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for decision in policy_decisions:
        selected = decision.get("selected_result", decision)
        summary.append(
            {
                "subject_id": decision.get("subject_id") or selected.get("subject_id"),
                "selected_action": decision.get("selected_action") or selected.get("action"),
                "status": decision.get("selected_status") or selected.get("status"),
                "claim_type": decision.get("claim_type") or selected.get("claim_type", "hypothesis"),
                "reason_codes": list(decision.get("selected_reason_codes") or selected.get("reason_codes", [])),
                "baseline_delta": selected.get("baseline_delta"),
                "no_action_reward": selected.get("no_action_reward"),
            }
        )
    return sanitize_for_report(summary)


def _safe_redaction_summary(summary: dict[str, Any]) -> dict[str, Any]:
    if not summary:
        return {}
    redacted_fields = list(summary.get("redacted_fields", []))
    return {
        "redacted_field_count": len(redacted_fields),
        "records_processed": summary.get("records_processed"),
        "vault_records": summary.get("vault_records"),
        "key_version": summary.get("key_version"),
        "pii_removed_from_analytics": summary.get("pii_removed_from_analytics"),
    }


def build_decision_report(report_input: DecisionReportInput) -> dict[str, Any]:
    orchestrator = sanitize_for_report(_message_to_dict(report_input.orchestrator_result))
    security_review = sanitize_for_report(report_input.security_review or orchestrator.get("context", {}).get("security_review", {}))
    uncertainty = sanitize_for_report(report_input.uncertainty or orchestrator.get("uncertainty", {}))
    uncertainty_gate = _uncertainty_decision(uncertainty)
    policy_summary = _policy_summary(report_input.policy_decisions)
    hypotheses = sanitize_for_report(report_input.hypotheses or orchestrator.get("context", {}).get("hypotheses", []))
    segment_rows = sanitize_for_report(report_input.segment_rows)
    pii_summary = _safe_redaction_summary(sanitize_for_report(report_input.pii_redaction_summary))
    security_status = security_review.get("security_status", "approve") if isinstance(security_review, dict) else "approve"
    final_status = _overall_status(
        orchestrator.get("next_action"),
        security_status,
        uncertainty_gate.get("status"),
        *(item.get("status") for item in policy_summary if isinstance(item, dict)),
    )
    no_pii_in_segments = analytics_rows_are_pii_safe(segment_rows) if isinstance(segment_rows, list) else True

    report = {
        "title": report_input.title,
        "executive_summary": {
            "status": final_status,
            "orchestrator_decision": orchestrator.get("next_action"),
            "security_status": security_status,
            "uncertainty_status": uncertainty_gate.get("status"),
            "summary": orchestrator.get("summary", ""),
            "decision_rationale": orchestrator.get("decision_rationale", ""),
        },
        "evidence_and_uncertainty": {
            "uncertainty": uncertainty,
            "gate": uncertainty_gate,
            "agent_confidence": orchestrator.get("confidence"),
            "confidence_note": "Agent confidence is not statistical confidence_level.",
        },
        "hypotheses": hypotheses,
        "nudge_recommendations": policy_summary,
        "segment_view": segment_rows,
        "security_and_governance": {
            "security_review": security_review,
            "pii_redaction_summary": pii_summary,
            "no_pii_in_segment_view": no_pii_in_segments,
        },
        "result_quality": sanitize_for_report(report_input.result_quality),
        "open_questions": sanitize_for_report(orchestrator.get("open_questions", [])),
        "risks": sanitize_for_report(orchestrator.get("risks", [])),
        "next_actions": sanitize_for_report(report_input.next_actions or _default_next_actions(final_status, uncertainty_gate)),
    }
    return sanitize_for_report(report)


def _default_next_actions(status: str, uncertainty_gate: dict[str, Any]) -> list[str]:
    actions = []
    if status in {"hold", "blocked", "reject"}:
        actions.append("Resolve blockers before any active nudge rollout.")
    if uncertainty_gate.get("significance_claim_allowed") is not True:
        actions.append("Run or complete experiment/CI validation before claiming effect.")
    actions.append("Keep no-action baseline and governance review in the decision loop.")
    return actions


def render_markdown_report(report: dict[str, Any], *, include_system_checks: bool = False) -> str:
    report = sanitize_for_report(report)
    executive = report.get("executive_summary", {})
    evidence = report.get("evidence_and_uncertainty", {})
    uncertainty = evidence.get("uncertainty", {})
    gate = evidence.get("gate", {})

    lines = [
        f"# {report.get('title', 'Nudge Engine Decision Report')}",
        "",
        "## Executive Summary",
        "",
        f"- Status: `{executive.get('status', 'hold')}`",
        f"- Orchestrator Decision: `{executive.get('orchestrator_decision', 'hold')}`",
        f"- Security Status: `{executive.get('security_status', 'unknown')}`",
        f"- Uncertainty Status: `{executive.get('uncertainty_status', 'hold')}`",
        f"- Summary: {executive.get('summary', '')}",
        "",
        "## Evidence & Confidence",
        "",
        f"- Agent confidence: `{evidence.get('agent_confidence')}`",
        f"- Confidence note: {evidence.get('confidence_note')}",
        f"- Effect estimate: `{uncertainty.get('effect_estimate', 'missing')}`",
        f"- CI: `{uncertainty.get('ci_lower', 'missing')} .. {uncertainty.get('ci_upper', 'missing')}`",
        f"- CI method: `{uncertainty.get('ci_method', 'missing')}`",
        f"- Confidence level: `{uncertainty.get('confidence_level', 'missing')}`",
        f"- Significance claim allowed: `{gate.get('significance_claim_allowed', False)}`",
        f"- Gate summary: {gate.get('summary', '')}",
        "",
        "## Hypotheses",
        "",
    ]
    for hypothesis in report.get("hypotheses", []):
        lines.append(
            f"- `{hypothesis.get('id', '-')}` {hypothesis.get('statement', '')} "
            f"Status: `{hypothesis.get('status', 'unknown')}`"
        )
    if not report.get("hypotheses"):
        lines.append("- No hypotheses provided.")

    lines.extend(["", "## Nudge Recommendations", ""])
    for item in report.get("nudge_recommendations", []):
        lines.append(
            f"- `{item.get('subject_id', '-')}` -> `{item.get('selected_action', 'no_action')}` "
            f"Status: `{item.get('status', 'unknown')}` Reasons: `{', '.join(item.get('reason_codes', []))}`"
        )
    if not report.get("nudge_recommendations"):
        lines.append("- No policy recommendations provided.")

    lines.extend(["", "## Segment View", ""])
    for row in report.get("segment_view", [])[:20]:
        lines.append(
            f"- `{row.get('subject_id', '-')}` action=`{row.get('recommended_action', row.get('selected_action', '-'))}` "
            f"status=`{row.get('status', '-')}` reason=`{row.get('reason', '-')}`"
        )
    if not report.get("segment_view"):
        lines.append("- No segment rows provided.")

    if include_system_checks:
        security = report.get("security_and_governance", {})
        security_review = security.get("security_review", {})
        lines.extend(
            [
                "",
                "## System Checks",
                "",
                f"- Security status: `{security_review.get('security_status', 'unknown')}`",
                f"- Risk level: `{security_review.get('risk_level', 'unknown')}`",
                f"- Safe to reason: `{security_review.get('safe_to_reason', 'unknown')}`",
                f"- Safe to execute: `{security_review.get('safe_to_execute', 'unknown')}`",
                f"- No PII in segment view: `{security.get('no_pii_in_segment_view', False)}`",
            ]
        )

    lines.extend(["", "## Next Actions", ""])
    for action in report.get("next_actions", []):
        lines.append(f"- {action}")
    return "\n".join(lines).strip() + "\n"
