"""Evidence ladder and claim permission rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


EVIDENCE_LEVELS = {
    "unknown": 0,
    "descriptive": 1,
    "correlational": 2,
    "predictive": 3,
    "quasi_causal": 4,
    "experimental": 5,
    "replicated": 6,
}

ALLOWED_WORDING = {
    "unknown": "insufficient evidence",
    "hypothesis": "is consistent with",
    "descriptive": "we observe",
    "correlational": "is associated with",
    "predictive": "predicts",
    "quasi_causal": "suggests an effect under assumptions",
    "experimental": "measured effect in experiment",
    "replicated": "replicated measured effect",
}

PROHIBITED_WORDING = (
    "proves",
    "guarantees",
    "will increase",
    "the user has bias",
    "best intervention",
    "significant",
)


@dataclass(frozen=True)
class ClaimPermission:
    evidence_level: str
    significance_claim_allowed: bool
    causal_claim_allowed: bool
    recommendation_claim_allowed: bool
    effect_wording: str
    blocked_claims: list[str]
    required_next_evidence: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_level": self.evidence_level,
            "significance_claim_allowed": self.significance_claim_allowed,
            "causal_claim_allowed": self.causal_claim_allowed,
            "recommendation_claim_allowed": self.recommendation_claim_allowed,
            "effect_wording": self.effect_wording,
            "blocked_claims": list(self.blocked_claims),
            "required_next_evidence": list(self.required_next_evidence),
            "prohibited_wording": list(PROHIBITED_WORDING),
        }


def infer_evidence_level(
    *,
    uncertainty: dict[str, Any] | None = None,
    has_treatment_control: bool = False,
    identification_strategy: str | None = None,
    replicated: bool = False,
) -> str:
    uncertainty = uncertainty or {}
    if replicated and uncertainty:
        return "replicated"
    if uncertainty and has_treatment_control:
        return "experimental"
    if identification_strategy:
        return "quasi_causal"
    if uncertainty:
        return "descriptive"
    return "unknown"


def evaluate_claim_permission(
    *,
    uncertainty: dict[str, Any] | None,
    has_treatment_control: bool,
    has_no_action_baseline: bool,
    identification_strategy: str | None = None,
    replicated: bool = False,
) -> ClaimPermission:
    evidence_level = infer_evidence_level(
        uncertainty=uncertainty,
        has_treatment_control=has_treatment_control,
        identification_strategy=identification_strategy,
        replicated=replicated,
    )
    uncertainty = uncertainty or {}
    ci_complete = all(
        key in uncertainty
        for key in ["effect_estimate", "ci_lower", "ci_upper", "ci_method", "sample_size", "confidence_level", "contains_null"]
    )
    significance_allowed = (
        ci_complete
        and uncertainty.get("contains_null") is False
        and float(uncertainty.get("confidence_level", 0.0)) >= 0.95
    )
    causal_allowed = EVIDENCE_LEVELS.get(evidence_level, 0) >= 4
    recommendation_allowed = has_no_action_baseline and evidence_level != "unknown"

    blocked: list[str] = []
    required: list[str] = []
    if not significance_allowed:
        blocked.append("significance_claim")
        required.append("complete_95_ci_excluding_null")
    if not causal_allowed:
        blocked.append("causal_claim")
        required.append("treatment_control_or_identification_strategy")
    if not recommendation_allowed:
        blocked.append("best_nudge_claim")
        required.append("measured_no_action_baseline")

    return ClaimPermission(
        evidence_level=evidence_level,
        significance_claim_allowed=significance_allowed,
        causal_claim_allowed=causal_allowed,
        recommendation_claim_allowed=recommendation_allowed,
        effect_wording=ALLOWED_WORDING.get(evidence_level, "is consistent with"),
        blocked_claims=sorted(set(blocked)),
        required_next_evidence=sorted(set(required)),
    )
