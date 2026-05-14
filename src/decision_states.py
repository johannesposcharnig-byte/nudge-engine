"""Formal decision state model for pilot readiness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DECISION_STATES = [
    "not_started",
    "data_required",
    "security_blocked",
    "privacy_hold",
    "data_invalid",
    "hypothesis_only",
    "experiment_required",
    "evidence_insufficient",
    "exploratory_result",
    "pilot_candidate",
    "human_review_required",
    "pilot_approved",
    "rejected",
]


@dataclass(frozen=True)
class DecisionState:
    state: str
    blockers: list[str]
    escalation_required: bool
    human_review_required: bool
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "blockers": list(self.blockers),
            "escalation_required": self.escalation_required,
            "human_review_required": self.human_review_required,
            "rationale": self.rationale,
        }


def evaluate_decision_state(
    *,
    security_status: str,
    data_status: str,
    privacy_safe: bool,
    claim_permission: dict[str, Any],
    high_risk_or_review_required: bool,
    human_approved: bool = False,
) -> DecisionState:
    blockers: list[str] = []

    if security_status in {"reject", "blocked"}:
        return DecisionState(
            state="security_blocked",
            blockers=["security_blocked"],
            escalation_required=True,
            human_review_required=True,
            rationale="Security or integrity gate blocked reasoning or execution.",
        )
    if security_status == "hold":
        blockers.append("security_hold")
    if not privacy_safe:
        return DecisionState(
            state="privacy_hold",
            blockers=["privacy_not_safe"],
            escalation_required=True,
            human_review_required=True,
            rationale="Direct PII or unsafe privacy state prevents analysis output.",
        )
    if data_status == "reject":
        return DecisionState(
            state="data_invalid",
            blockers=["data_contract_rejected"],
            escalation_required=True,
            human_review_required=False,
            rationale="Data contract rejected the dataset due to prohibited or invalid fields.",
        )
    if data_status == "hold":
        return DecisionState(
            state="data_required",
            blockers=["required_data_missing"],
            escalation_required=False,
            human_review_required=False,
            rationale="Required activation data fields are missing.",
        )
    if data_status == "experiment_required":
        blockers.append("experiment_required")

    blocked_claims = list(claim_permission.get("blocked_claims", []))
    if "causal_claim" in blocked_claims and "significance_claim" in blocked_claims:
        state = "hypothesis_only" if data_status != "experiment_required" else "experiment_required"
        return DecisionState(
            state=state,
            blockers=sorted(set([*blockers, *blocked_claims])),
            escalation_required=False,
            human_review_required=False,
            rationale="Current data can support hypotheses or experiment planning, not causal effect claims.",
        )
    if "significance_claim" in blocked_claims:
        return DecisionState(
            state="evidence_insufficient",
            blockers=sorted(set([*blockers, *blocked_claims])),
            escalation_required=False,
            human_review_required=False,
            rationale="Evidence is insufficient for statistical significance claims.",
        )
    if high_risk_or_review_required and not human_approved:
        return DecisionState(
            state="human_review_required",
            blockers=sorted(set([*blockers, "human_review_required"])),
            escalation_required=True,
            human_review_required=True,
            rationale="At least one intervention requires human review before pilot approval.",
        )
    if blockers:
        return DecisionState(
            state="exploratory_result",
            blockers=sorted(set(blockers)),
            escalation_required=False,
            human_review_required=False,
            rationale="Result is informative but not yet pilot-approved.",
        )
    return DecisionState(
        state="pilot_approved" if human_approved else "pilot_candidate",
        blockers=[],
        escalation_required=not human_approved,
        human_review_required=not human_approved,
        rationale="Data, evidence and privacy gates are sufficient for pilot candidate status.",
    )
