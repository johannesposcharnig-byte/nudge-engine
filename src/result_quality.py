"""Result quality gate for decision reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .decision_states import evaluate_decision_state


@dataclass(frozen=True)
class ResultQuality:
    decision_state: dict[str, Any]
    data_readiness: dict[str, Any]
    claim_permission: dict[str, Any]
    pilot_readiness: str
    trust_warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision_state": dict(self.decision_state),
            "data_readiness": dict(self.data_readiness),
            "claim_permission": dict(self.claim_permission),
            "pilot_readiness": self.pilot_readiness,
            "trust_warnings": list(self.trust_warnings),
        }


def evaluate_result_quality(
    *,
    data_readiness: dict[str, Any],
    claim_permission: dict[str, Any],
    security_review: dict[str, Any],
    privacy_safe: bool,
    policy_decisions: list[dict[str, Any]],
    human_approved: bool = False,
) -> ResultQuality:
    high_risk_or_review_required = any(
        decision.get("selected_result", {}).get("method_evaluation", {}).get("human_review_required")
        or decision.get("selected_result", {}).get("method_evaluation", {}).get("risk_tier") == "high"
        for decision in policy_decisions
    )
    decision_state = evaluate_decision_state(
        security_status=str(security_review.get("security_status", "hold")),
        data_status=str(data_readiness.get("status", "hold")),
        privacy_safe=privacy_safe,
        claim_permission=claim_permission,
        high_risk_or_review_required=high_risk_or_review_required,
        human_approved=human_approved,
    ).as_dict()

    warnings = []
    if data_readiness.get("status") != "ready":
        warnings.append("data_not_pilot_ready")
    if claim_permission.get("significance_claim_allowed") is not True:
        warnings.append("no_significance_claim_allowed")
    if claim_permission.get("causal_claim_allowed") is not True:
        warnings.append("no_causal_claim_allowed")
    if high_risk_or_review_required:
        warnings.append("human_review_required_for_intervention")
    if security_review.get("security_status") != "approve":
        warnings.append("security_not_approved")
    if not privacy_safe:
        warnings.append("privacy_not_safe")

    pilot_readiness = "pilot_candidate" if decision_state["state"] == "pilot_candidate" else "not_ready"
    if decision_state["state"] == "pilot_approved":
        pilot_readiness = "pilot_approved"

    return ResultQuality(
        decision_state=decision_state,
        data_readiness=data_readiness,
        claim_permission=claim_permission,
        pilot_readiness=pilot_readiness,
        trust_warnings=sorted(set(warnings)),
    )
