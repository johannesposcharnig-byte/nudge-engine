"""Unified analysis entrypoint for the Nudge Engine.

This module stitches the existing guarded components into one narrow runtime
flow. It is intentionally conservative: missing data produces `hold`, not an
invented effect or recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .agents.base import AgentMessage
from .claim_permissions import evaluate_claim_permission
from .data_contracts import evaluate_activation_data_contract
from .evidence import (
    build_mece_hypotheses,
    clarification_questions_for_missing,
    customer_data_missing_fields,
    infer_customer_data_profile,
)
from .orchestrator import Orchestrator, Task
from .pii_vault import (
    IDENTITY_FIELD_NAMES,
    PII_FIELD_NAMES,
    analytics_rows_are_pii_safe,
    pseudonymize_customer_rows,
)
from .reporting import DecisionReportInput, build_decision_report
from .result_quality import evaluate_result_quality
from .reward import policy_decision_for_person
from .security import SecurityReview, leonidas_security_review
from .simulation import ab_mean_difference_ci


DEFAULT_VAULT_SECRET = "development-only-nudge-engine-vault-secret"
DEFAULT_CONFIDENCE_LEVEL = 0.95
MAX_POLICY_ROWS = 25


@dataclass(frozen=True)
class AnalysisRequest:
    """Customer-facing analysis request before API transport exists."""

    question: str
    customer_rows: list[dict[str, Any]]
    config: dict[str, Any] = field(default_factory=dict)
    identity_fields: list[str] | None = None
    vault_secret: str = DEFAULT_VAULT_SECRET
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL


def run_analysis(request: AnalysisRequest | dict[str, Any]) -> dict[str, Any]:
    """Run a guarded analysis pipeline and return a dashboard-ready report."""

    parsed = _coerce_request(request)
    raw_security = leonidas_security_review(
        {
            "external_content": parsed.question,
            "customer_rows": parsed.customer_rows,
            "unique_id_field": _first_available_identity_field(parsed),
        }
    )
    if _must_block_before_pseudonymization(raw_security):
        return _blocked_report(parsed, raw_security)

    if not parsed.customer_rows:
        security_review = raw_security.as_dict()
        result = _service_message(
            request=parsed,
            summary="No customer rows were provided; analysis cannot start.",
            next_action="hold",
            blocked_reason="missing_customer_rows",
            security_review=security_review,
            clarification_questions=["Bitte lade Kundendaten mit mindestens einer Zeile hoch."],
        )
        return build_decision_report(
            DecisionReportInput(
                title="Nudge Engine Analysis",
                orchestrator_result=result,
                security_review=security_review,
                next_actions=["Upload customer data before running analysis."],
            )
        )

    identity_fields = _identity_fields(parsed)
    if not _has_identity_values(parsed.customer_rows, identity_fields):
        security_review = raw_security.as_dict()
        result = _service_message(
            request=parsed,
            summary="No usable customer identity field was found; pseudonymization cannot start safely.",
            next_action="hold",
            blocked_reason="missing_identity_field",
            security_review=security_review,
            clarification_questions=[
                "Welches Feld identifiziert User, Kunde, Company oder Account eindeutig?"
            ],
        )
        return build_decision_report(
            DecisionReportInput(
                title="Nudge Engine Analysis",
                orchestrator_result=result,
                security_review=security_review,
                next_actions=["Provide a stable identity field before analysis."],
            )
        )

    vault = pseudonymize_customer_rows(
        parsed.customer_rows,
        secret_key=parsed.vault_secret,
        identity_fields=identity_fields,
        actor="analysis_service",
        reason="run_analysis",
    )
    analytics_rows = vault.analytics_rows
    analytics_security = leonidas_security_review(
        {
            "customer_rows": analytics_rows,
            "pii_pseudonymized": True,
            "unique_id_field": "subject_id",
            "entity_field": "subject_id",
        }
    )
    if not analytics_security.safe_to_reason:
        return _blocked_report(
            parsed,
            analytics_security,
            pii_redaction_summary=vault.redaction_summary,
            segment_rows=analytics_rows[:MAX_POLICY_ROWS],
        )

    context = _build_analysis_context(parsed, analytics_rows, analytics_security, vault.redaction_summary)
    data_readiness = evaluate_activation_data_contract(analytics_rows).as_dict()
    orchestrator = Orchestrator()
    intake_result = orchestrator.run_orchestration(
        Task(
            phase="customer_data_intake",
            agent="data",
            prompt=f"Validate customer data before answering: {parsed.question}",
            context=context,
        )
    )

    hypotheses = build_mece_hypotheses({**context, "customer_data_profile": infer_customer_data_profile(context)})
    uncertainty = _calculate_ab_uncertainty(analytics_rows, context, parsed.confidence_level)
    claim_permission = evaluate_claim_permission(
        uncertainty=uncertainty,
        has_treatment_control=bool(context.get("treatment_group") and context.get("control_group")),
        has_no_action_baseline=_has_measured_no_action_baseline(analytics_rows),
        identification_strategy=parsed.config.get("identification_strategy"),
        replicated=bool(parsed.config.get("replicated_evidence")),
    ).as_dict()
    formula_result = _maybe_review_formula(orchestrator, parsed, context, uncertainty)
    final_result = formula_result or _with_uncertainty(intake_result, uncertainty)

    policy_decisions = _policy_decisions(analytics_rows, parsed.config)
    result_quality = evaluate_result_quality(
        data_readiness=data_readiness,
        claim_permission=claim_permission,
        security_review=analytics_security.as_dict(),
        privacy_safe=analytics_rows_are_pii_safe(analytics_rows),
        policy_decisions=policy_decisions,
        human_approved=bool(parsed.config.get("human_approved")),
    ).as_dict()
    next_actions = _next_actions(final_result, uncertainty, policy_decisions)
    return build_decision_report(
        DecisionReportInput(
            title="Nudge Engine Analysis",
            orchestrator_result=final_result,
            hypotheses=hypotheses,
            policy_decisions=policy_decisions,
            security_review=analytics_security.as_dict(),
            pii_redaction_summary=vault.redaction_summary,
            uncertainty=uncertainty,
            segment_rows=_segment_rows(analytics_rows),
            next_actions=next_actions,
            result_quality=result_quality,
        )
    )


def _coerce_request(request: AnalysisRequest | dict[str, Any]) -> AnalysisRequest:
    if isinstance(request, AnalysisRequest):
        return request
    return AnalysisRequest(
        question=str(request.get("question", "")),
        customer_rows=list(request.get("customer_rows", [])),
        config=dict(request.get("config", {})),
        identity_fields=request.get("identity_fields"),
        vault_secret=str(request.get("vault_secret", DEFAULT_VAULT_SECRET)),
        confidence_level=float(request.get("confidence_level", DEFAULT_CONFIDENCE_LEVEL)),
    )


def _must_block_before_pseudonymization(security_review: SecurityReview) -> bool:
    for risk in security_review.detected_risks:
        if risk.action == "block":
            return True
        if risk.risk_type in {"secret_exposure", "prompt_injection", "governance_bypass"}:
            return True
    return False


def _identity_fields(request: AnalysisRequest) -> list[str]:
    if request.identity_fields:
        return list(request.identity_fields)
    available = set(_columns(request.customer_rows))
    detected = [field for field in ["customer_id", "user_id", "account_id", "company_id"] if field in available]
    if detected:
        return detected[:1]
    fallback = next((field for field in available if field in IDENTITY_FIELD_NAMES), None)
    return [fallback] if fallback else ["customer_id"]


def _has_identity_values(rows: list[dict[str, Any]], identity_fields: list[str]) -> bool:
    return any(
        any(row.get(field) not in {None, ""} for field in identity_fields)
        for row in rows
    )


def _first_available_identity_field(request: AnalysisRequest) -> str | None:
    fields = _identity_fields(request)
    return fields[0] if fields else None


def _columns(rows: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                ordered.append(str(key))
                seen.add(str(key))
    return ordered


def _build_analysis_context(
    request: AnalysisRequest,
    analytics_rows: list[dict[str, Any]],
    security_review: SecurityReview,
    pii_redaction_summary: dict[str, Any],
) -> dict[str, Any]:
    available_columns = _columns(analytics_rows)
    config = dict(request.config)
    outcome_variable = config.get("outcome_variable") or _infer_outcome(available_columns)
    treatment_field = config.get("treatment_field") or _infer_treatment_field(available_columns)
    context = {
        "question": request.question,
        "available_columns": available_columns,
        "outcome_variable": outcome_variable,
        "behavioral_method": config.get("behavioral_method"),
        "consent_field": config.get("consent_field", "consent" if "consent" in available_columns else None),
        "customer_rows": analytics_rows,
        "pii_pseudonymized": True,
        "security_review": security_review.as_dict(),
        "pii_redaction_summary": pii_redaction_summary,
        "requires_causal_claim": bool(config.get("requires_causal_claim", True)),
    }
    if treatment_field:
        context["treatment_group"] = f"{treatment_field}=treatment"
        context["control_group"] = f"{treatment_field}=control"
    missing = customer_data_missing_fields(context)
    context["customer_data_profile"] = infer_customer_data_profile(context)
    context["clarification_questions"] = clarification_questions_for_missing(missing)
    context["missing_fields"] = missing
    return context


def _infer_outcome(columns: list[str]) -> str | None:
    preferred = [
        "activation_score",
        "renewed",
        "renewal",
        "conversion",
        "converted",
        "churn",
        "outcome",
    ]
    lower_to_original = {column.lower(): column for column in columns}
    for candidate in preferred:
        if candidate in lower_to_original:
            return lower_to_original[candidate]
    return None


def _infer_treatment_field(columns: list[str]) -> str | None:
    preferred = ["experiment_group", "treatment_group", "nudge_variant", "variant"]
    lower_to_original = {column.lower(): column for column in columns}
    for candidate in preferred:
        if candidate in lower_to_original:
            return lower_to_original[candidate]
    return None


def _calculate_ab_uncertainty(
    rows: list[dict[str, Any]],
    context: dict[str, Any],
    confidence_level: float,
) -> dict[str, Any]:
    outcome = context.get("outcome_variable")
    treatment_field = _infer_treatment_field(context.get("available_columns", []))
    if not outcome or not treatment_field:
        return {}
    treatment: list[float] = []
    control: list[float] = []
    for row in rows:
        if outcome not in row or treatment_field not in row:
            continue
        numeric_outcome = _coerce_float(row.get(outcome))
        if numeric_outcome is None:
            continue
        group = str(row.get(treatment_field, "")).lower()
        if group == "treatment":
            treatment.append(numeric_outcome)
        elif group == "control":
            control.append(numeric_outcome)
    if not treatment or not control:
        return {}
    return ab_mean_difference_ci(treatment, control, confidence_level=confidence_level).as_uncertainty()


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _has_measured_no_action_baseline(rows: list[dict[str, Any]]) -> bool:
    return any(isinstance(row.get("no_action_baseline"), dict) for row in rows)


def _maybe_review_formula(
    orchestrator: Orchestrator,
    request: AnalysisRequest,
    context: dict[str, Any],
    uncertainty: dict[str, Any],
) -> AgentMessage | None:
    if not uncertainty:
        return None
    formula_context = {
        "formula_key": "ab_test",
        "treatment_group": context.get("treatment_group"),
        "control_group": context.get("control_group"),
        "outcome_variable": context.get("outcome_variable"),
        "uncertainty": uncertainty,
        "customer_data_profile": context.get("customer_data_profile"),
        "hypotheses": build_mece_hypotheses(context),
    }
    return orchestrator.run_orchestration(
        Task(
            phase="formula_review",
            agent="statistical",
            prompt=f"Review calculable A/B effect before answering: {request.question}",
            context=formula_context,
        )
    )


def _with_uncertainty(message: AgentMessage, uncertainty: dict[str, Any]) -> AgentMessage:
    message.uncertainty.update(uncertainty)
    message.context["uncertainty"] = uncertainty
    return message


def _policy_decisions(rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    actions = config.get("actions")
    decisions = []
    for row in rows[: int(config.get("max_policy_rows", MAX_POLICY_ROWS))]:
        decisions.append(policy_decision_for_person(row, actions=actions))
    return decisions


def _segment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = [
        "subject_id",
        "experiment_group",
        "activation_score",
        "renewed",
        "consent",
        "fatigue_signal",
        "friction_signal",
        "resistance_signal",
        "recommended_nudge",
        "nudge_status",
    ]
    segments = []
    for row in rows[:MAX_POLICY_ROWS]:
        segments.append({key: row[key] for key in allowed if key in row and key not in PII_FIELD_NAMES})
    return segments


def _next_actions(
    result: AgentMessage,
    uncertainty: dict[str, Any],
    policy_decisions: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    if result.next_action != "approve":
        actions.append("Resolve engine blockers before connecting this result to rollout.")
    if not uncertainty:
        actions.append("Provide treatment/control and a numeric outcome before any effect claim.")
    if any(decision.get("selected_action") == "no_action" for decision in policy_decisions):
        actions.append("Review no-action selections; many are expected when consent, fatigue, or governance blocks exist.")
    if not actions:
        actions.append("Review the generated report with governance before dashboard/API rollout.")
    return actions


def _service_message(
    *,
    request: AnalysisRequest,
    summary: str,
    next_action: str,
    blocked_reason: str,
    security_review: dict[str, Any],
    clarification_questions: list[str] | None = None,
) -> AgentMessage:
    return AgentMessage(
        agent="analysis_service",
        phase="analysis",
        jtbd=request.question,
        summary=summary,
        done_status="blocked",
        confidence=0.9,
        context={"security_review": security_review},
        risks=[blocked_reason],
        open_questions=list(clarification_questions or []),
        next_action=next_action,  # type: ignore[arg-type]
        claims=[
            {
                "statement": summary,
                "claim_type": "blocked",
                "evidence_available": ["Leonidas security review" if security_review else "service input"],
            }
        ],
        claim_type="blocked",
        clarification_questions=list(clarification_questions or []),
        blocked_reason=blocked_reason,
        security_warnings=list(security_review.get("detected_risks", [])),
        decision_rationale=summary,
    )


def _blocked_report(
    request: AnalysisRequest,
    security_review: SecurityReview,
    *,
    pii_redaction_summary: dict[str, Any] | None = None,
    segment_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    security = security_review.as_dict()
    result = _service_message(
        request=request,
        summary="Leonidas blocked or held the analysis before engine reasoning.",
        next_action="hold",
        blocked_reason="security_blocker",
        security_review=security,
    )
    return build_decision_report(
        DecisionReportInput(
            title="Nudge Engine Analysis",
            orchestrator_result=result,
            security_review=security,
            pii_redaction_summary=pii_redaction_summary or {},
            segment_rows=segment_rows or [],
            next_actions=["Resolve security or data integrity blocker before analysis."],
        )
    )
