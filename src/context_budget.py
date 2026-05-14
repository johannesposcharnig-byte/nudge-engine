"""Context minimization and evidence-pack rules for agent runs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .security import PROMPT_INJECTION_PATTERNS, leonidas_security_review


TOKEN_BUDGET_RULE = (
    "Agents must use the smallest sufficient context. Default is Evidence Pack only; "
    "full context requires an explicit full_context_required flag and a missing-question reason."
)

DEFAULT_MAX_DOCUMENTS = 3
DEFAULT_MAX_SECTIONS_PER_DOCUMENT = 2
DEFAULT_OWNER = "orchestrator"

VALIDATION_STATUSES = {"draft", "revise", "approved", "deprecated", "blocked"}
EVIDENCE_LEVELS = {"low", "medium", "high", "experimentally_validated"}
LIFECYCLE_STATUSES = {"active", "stale", "archived", "deprecated", "blocked"}
BLOCKED_SOURCE_STATUSES = {"blocked", "deprecated"}
GOVERNANCE_CRITICAL_DOCUMENTS = {
    "behavioral_method_matrix",
    "claims",
    "governance",
    "policy_spec",
    "reward_model",
    "run_state",
    "validation_acceptance",
}

LARGE_CONTEXT_KEYS = {
    "all_documents",
    "conversation_history",
    "documents",
    "file_contents",
    "full_context",
    "raw_context",
    "raw_documents",
}

AGENT_SOURCE_POLICY: dict[str, dict[str, Any]] = {
    "data": {
        "documents": ["schema", "formula_registry", "validation_acceptance"],
        "sections": ["data_contract", "variables", "uncertainty"],
    },
    "statistical": {
        "documents": ["formula_registry", "validation_acceptance", "formula_spec"],
        "sections": ["formula_definition", "assumptions", "ci_rule"],
    },
    "evaluation": {
        "documents": ["validation_acceptance", "formula_registry", "simulation"],
        "sections": ["ci_rule", "support_check", "effect_interval"],
    },
    "research": {
        "documents": ["behavioral_method_matrix", "formula_registry", "run_state"],
        "sections": ["mechanism", "behavioral_method", "evidence_strength"],
    },
    "policy": {
        "documents": ["formula_registry", "policy_spec", "run_state"],
        "sections": ["reward", "guardrails", "no_action"],
    },
    "ml": {
        "documents": ["formula_registry", "run_state", "validation_acceptance"],
        "sections": ["features", "model_metrics", "calibration"],
    },
    "critic": {
        "documents": ["claims", "risks", "run_state"],
        "sections": ["unsupported_claims", "open_questions", "blockers"],
    },
    "devils_advocate": {
        "documents": ["claims", "risks", "run_state"],
        "sections": ["failure_modes", "proxy_risks", "counter_assumptions"],
    },
    "governance": {
        "documents": ["claims", "behavioral_method_matrix", "run_state"],
        "sections": ["fairness", "consent", "autonomy"],
    },
}

ESSENTIAL_CONTEXT_KEYS = {
    "agent",
    "analysis_depth",
    "available_columns",
    "behavioral_method",
    "behavioral_methods",
    "B_F",
    "ci_method",
    "ci_required",
    "confidence_level",
    "consent_field",
    "context_summary",
    "control_condition",
    "control_group",
    "core_agent_roles",
    "customer_data_profile",
    "entity_fields",
    "evidence_gate_required",
    "exploratory_confidence_level",
    "formula",
    "formula_assumptions",
    "formula_class",
    "formula_key",
    "formula_review_stage",
    "formula_review_stage_index",
    "G",
    "governance_blocked",
    "governance_review",
    "guardrails",
    "hypotheses",
    "hypotheses_mece_ready",
    "identification_strategy",
    "mece_groups",
    "missing_required_fields",
    "model",
    "no_action_baseline",
    "null_value",
    "outcome_candidates",
    "outcome_variable",
    "ocean_consent",
    "ocean_instrument",
    "ocean_scores",
    "ocean_signal",
    "ocean_source",
    "ocean_only_decision",
    "overlap_check",
    "previous_stage_agent",
    "previous_stage_summary",
    "propensity_clipping",
    "psychological_fields",
    "psychological_signal",
    "required_context",
    "required_review_agents",
    "requires_causal_claim",
    "reward_calibrated",
    "routing_phase",
    "segment_fields",
    "simulation_result",
    "support_check",
    "target_behavior",
    "time_fields",
    "tipi_responses",
    "treatment_candidates",
    "treatment_group",
    "uncertainty",
    "variables",
    "X_pre",
    "cross_fitting",
    "conflicts",
    "lifecycle_metadata",
    "retrieval_query",
    "security_warnings",
    "security_review",
    "security_agent",
    "source_metadata",
    "uses_ocean_for_personalization",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_iso(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _default_source_metadata(source_id: str, *, agent: str, retrieval_query: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "relevance_score": 0.75,
        "selection_reason": f"Selected by source policy for {agent}.",
        "retrieval_timestamp": _now_iso(),
        "retrieval_method": "agent_source_policy",
        "retrieval_query": retrieval_query,
        "source_confidence": 0.7,
        "validation_status": "approved",
        "evidence_level": "medium",
        "owner": DEFAULT_OWNER,
        "last_reviewed": _now_iso(),
        "created_at": _now_iso(),
        "expires_at": None,
        "lifecycle_status": "active",
        "trusted": True,
    }


def normalize_source_metadata(
    source_id: str,
    metadata: dict[str, Any] | None,
    *,
    agent: str,
    retrieval_query: str,
) -> dict[str, Any]:
    normalized = _default_source_metadata(source_id, agent=agent, retrieval_query=retrieval_query)
    if metadata:
        normalized.update(metadata)
    if normalized.get("validation_status") not in VALIDATION_STATUSES:
        normalized["validation_status"] = "draft"
    if normalized.get("evidence_level") not in EVIDENCE_LEVELS:
        normalized["evidence_level"] = "low"
    if normalized.get("lifecycle_status") not in LIFECYCLE_STATUSES:
        normalized["lifecycle_status"] = "stale"
    normalized.setdefault("retrieval_timestamp", _now_iso())
    normalized.setdefault("retrieval_method", "agent_source_policy")
    normalized.setdefault("retrieval_query", retrieval_query)
    normalized.setdefault("owner", DEFAULT_OWNER)
    normalized.setdefault("last_reviewed", _now_iso())
    return normalized


def selected_sources_for_agent(
    agent: str,
    *,
    source_metadata: dict[str, Any] | None = None,
    retrieval_query: str = "",
) -> dict[str, Any]:
    policy = AGENT_SOURCE_POLICY.get(agent, {"documents": ["run_state"], "sections": ["summary"]})
    documents = list(policy["documents"])[:DEFAULT_MAX_DOCUMENTS]
    metadata = {
        document: normalize_source_metadata(
            document,
            (source_metadata or {}).get(document, {}),
            agent=agent,
            retrieval_query=retrieval_query or f"{agent} evidence pack",
        )
        for document in documents
    }
    return {
        "documents": documents,
        "sections": list(policy["sections"])[:DEFAULT_MAX_SECTIONS_PER_DOCUMENT],
        "max_documents": DEFAULT_MAX_DOCUMENTS,
        "max_sections_per_document": DEFAULT_MAX_SECTIONS_PER_DOCUMENT,
        "source_metadata": metadata,
    }


def security_scan(context: dict[str, Any]) -> list[dict[str, Any]]:
    return leonidas_security_review(context).as_warnings()


def evaluate_retrieval_governance(
    context: dict[str, Any],
    *,
    agent: str,
    selected_sources: dict[str, Any],
) -> dict[str, Any]:
    metadata = selected_sources.get("source_metadata", {})
    blocked_sources = []
    stale_sources = []
    warnings = []
    for source_id, source in metadata.items():
        validation_status = source.get("validation_status")
        lifecycle_status = source.get("lifecycle_status")
        expires_at = _parse_iso(source.get("expires_at"))
        if expires_at and expires_at < datetime.now(timezone.utc):
            lifecycle_status = "stale"
            source["lifecycle_status"] = "stale"
        if validation_status in BLOCKED_SOURCE_STATUSES or lifecycle_status in BLOCKED_SOURCE_STATUSES:
            blocked_sources.append(source_id)
        if lifecycle_status == "stale":
            stale_sources.append(source_id)
            if source_id in GOVERNANCE_CRITICAL_DOCUMENTS:
                warnings.append(
                    {
                        "source_id": source_id,
                        "severity": "high",
                        "reason": "Governance-critical context is stale.",
                    }
                )
        if not source.get("owner") or not source.get("last_reviewed"):
            warnings.append(
                {
                    "source_id": source_id,
                    "severity": "medium",
                    "reason": "Source is missing owner or last_reviewed metadata.",
                }
            )
        if validation_status == "draft" and agent in {"policy", "governance", "evaluation"}:
            warnings.append(
                {
                    "source_id": source_id,
                    "severity": "medium",
                    "reason": "Draft evidence cannot support final policy, governance, or evaluation approval.",
                }
            )
    return {
        "blocked_sources": blocked_sources,
        "stale_sources": stale_sources,
        "warnings": warnings,
        "passed": not blocked_sources and not any(w.get("severity") == "high" for w in warnings),
    }


def detect_conflicts(context: dict[str, Any]) -> list[dict[str, Any]]:
    conflicts = list(context.get("conflicts", []))
    normalized = []
    for conflict in conflicts:
        if conflict.get("conflict_detected"):
            normalized.append(
                {
                    "conflict_detected": True,
                    "conflicting_sources": list(conflict.get("conflicting_sources", [])),
                    "conflict_reason": conflict.get("conflict_reason", "Unspecified evidence conflict."),
                    "escalation_target": conflict.get("escalation_target", "orchestrator"),
                    "resolution_status": conflict.get("resolution_status", "unresolved"),
                }
            )
    return normalized


def compare_evidence_strength(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {"low": 1, "medium": 2, "high": 3, "experimentally_validated": 4}
    approved_strong = [
        source
        for source in sources.values()
        if source.get("validation_status") == "approved" and rank.get(source.get("evidence_level"), 0) >= 3
    ]
    weak_unapproved = [
        source
        for source in sources.values()
        if source.get("validation_status") in {"draft", "revise"} or rank.get(source.get("evidence_level"), 0) <= 1
    ]
    if approved_strong and weak_unapproved:
        return [
            {
                "severity": "medium",
                "reason": "Weak or unvalidated evidence is present and must not override approved high evidence.",
                "strong_sources": [source["source_id"] for source in approved_strong],
                "weak_sources": [source["source_id"] for source in weak_unapproved],
            }
        ]
    return []


def minimize_context(context: dict[str, Any], *, agent: str) -> dict[str, Any]:
    allowed_extra = set(context.get("allowed_context_keys", []))
    full_context_allowed = bool(context.get("full_context_required") and context.get("full_context_reason"))
    minimized = {}
    for key, value in context.items():
        if key == "external_content":
            continue
        if key in LARGE_CONTEXT_KEYS and not full_context_allowed and key not in allowed_extra:
            continue
        if key in ESSENTIAL_CONTEXT_KEYS or key in allowed_extra or key.startswith("formula_"):
            minimized[key] = value
    source_metadata = context.get("source_metadata", {})
    retrieval_query = str(context.get("retrieval_query", f"{agent} evidence pack"))
    selected_sources = selected_sources_for_agent(
        agent,
        source_metadata=source_metadata,
        retrieval_query=retrieval_query,
    )
    retrieval_governance = evaluate_retrieval_governance(
        context,
        agent=agent,
        selected_sources=selected_sources,
    )
    security_review = leonidas_security_review(context)
    security_warnings = security_review.as_warnings()
    conflicts = detect_conflicts(context)
    evidence_strength_warnings = compare_evidence_strength(selected_sources["source_metadata"])
    minimized["selected_sources"] = selected_sources
    minimized["context_minimized"] = True
    minimized["full_context_used"] = full_context_allowed
    minimized["token_budget_rule"] = TOKEN_BUDGET_RULE
    minimized["retrieval_governance"] = retrieval_governance
    minimized["blocked_sources"] = retrieval_governance["blocked_sources"]
    minimized["stale_sources"] = retrieval_governance["stale_sources"]
    minimized["security_warnings"] = security_warnings
    minimized["security_review"] = security_review.as_dict()
    minimized["security_agent"] = security_review.agent
    minimized["conflicts"] = conflicts
    minimized["evidence_strength_warnings"] = evidence_strength_warnings
    minimized["source_metadata"] = selected_sources["source_metadata"]
    if security_warnings:
        minimized["external_content_redacted"] = True
    return minimized


def build_evidence_pack(
    *,
    task_phase: str,
    agent: str,
    prompt: str,
    context: dict[str, Any],
    run_state: dict[str, Any],
) -> dict[str, Any]:
    selected_sources = context.get("selected_sources") or selected_sources_for_agent(
        agent,
        source_metadata=context.get("source_metadata", {}),
        retrieval_query=str(context.get("retrieval_query", f"{agent} evidence pack")),
    )
    return {
        "task_phase": task_phase,
        "agent": agent,
        "prompt": prompt,
        "selected_sources": selected_sources,
        "source_metadata": selected_sources.get("source_metadata", {}),
        "retrieval_governance": context.get("retrieval_governance", {}),
        "security_warnings": list(context.get("security_warnings", [])),
        "security_review": dict(context.get("security_review", {})),
        "security_agent": context.get("security_agent", "Leonidas"),
        "conflicts": list(context.get("conflicts", [])),
        "lifecycle_warnings": list(context.get("stale_sources", [])),
        "evidence_strength_warnings": list(context.get("evidence_strength_warnings", [])),
        "run_state": dict(run_state),
        "formula": {
            key: context.get(key)
            for key in [
                "formula_key",
                "formula_class",
                "formula",
                "variables",
                "required_context",
                "ci_required",
                "ci_method",
                "confidence_level",
            ]
            if key in context
        },
        "hypotheses": list(context.get("hypotheses", []))[:7],
        "uncertainty": dict(context.get("uncertainty", {})),
        "missing_required_fields": list(context.get("missing_required_fields", [])),
        "open_questions": list(context.get("open_questions", [])),
        "claims_policy": [
            "Classify each central statement as observed, inferred, hypothesis, unknown, or blocked.",
            "Do not claim effect, significance, causality, or recommendation without supporting data.",
            "Ask for missing evidence instead of reading broad context.",
        ],
    }


def estimate_context_reduction(original: dict[str, Any], minimized: dict[str, Any]) -> float:
    original_size = max(1, len(str(original)))
    minimized_size = len(str(minimized))
    return max(0.0, min(1.0, 1.0 - (minimized_size / original_size)))
