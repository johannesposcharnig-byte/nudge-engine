"""Base agent contracts."""

from dataclasses import dataclass, field, replace
from typing import Any, Literal, Optional


Decision = Literal["approve", "revise", "reject", "hold"]
DoneStatus = Literal["done", "partial", "blocked"]
ClaimType = Literal["observed", "inferred", "hypothesis", "unknown", "blocked"]
HypothesisStatus = Literal["testable", "not_testable_yet", "out_of_scope"]


@dataclass
class AgentMessage:
    agent: str
    phase: str
    jtbd: str
    summary: str
    done_status: DoneStatus
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    requested_feedback: list[str] = field(default_factory=list)
    feedback_to: list[str] = field(default_factory=list)
    next_action: Decision = "hold"
    uncertainty: dict[str, Any] = field(default_factory=dict)
    claims: list[dict[str, Any]] = field(default_factory=list)
    claim_type: ClaimType = "unknown"
    evidence_required: list[str] = field(default_factory=list)
    evidence_available: list[str] = field(default_factory=list)
    hypothesis_id: Optional[str] = None
    hypothesis_status: Optional[HypothesisStatus] = None
    clarification_questions: list[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    readiness_flags: dict[str, bool] = field(default_factory=dict)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    security_warnings: list[dict[str, Any]] = field(default_factory=list)
    lifecycle_status: Optional[str] = None
    compressed_memory: str = ""
    decision_rationale: str = ""


class BaseAgent:
    name: str = "base"
    default_model: str = "GPT-5.4-Mini"

    def run(self, message: AgentMessage) -> AgentMessage:
        raise NotImplementedError

    def is_review(self, message: AgentMessage) -> bool:
        return message.context.get("mode") == "review"

    def review_target(self, message: AgentMessage) -> str:
        return str(message.context.get("target_agent", message.agent))

    def self_check(self, message: AgentMessage) -> dict[str, Any]:
        missing = []
        if not message.summary.strip():
            missing.append("summary")
        if not message.assumptions:
            missing.append("assumptions")
        if not message.evidence:
            missing.append("evidence")
        if message.context.get("evidence_gate_required"):
            if not message.claims:
                missing.append("claims")
            if message.claim_type in {"observed", "inferred"} and not (
                message.evidence_available or message.evidence
            ):
                missing.append("evidence_available")
            if message.next_action == "approve" and message.blocked_reason:
                missing.append("blocked_reason_resolution")

        if message.done_status == "blocked":
            quality = "blocked"
        elif missing or message.confidence < 0.7:
            quality = "insufficient"
        else:
            quality = "good"

        return {
            "quality": quality,
            "missing": missing,
            "confidence": message.confidence,
            "agent": self.name,
        }

    def missing_context(self, message: AgentMessage) -> list[str]:
        required = message.context.get("required_context", [])
        return [key for key in required if key not in message.context]

    def has_ci(self, message: AgentMessage) -> bool:
        uncertainty = message.uncertainty or message.context.get("uncertainty", {})
        return all(key in uncertainty for key in ["effect_estimate", "ci_lower", "ci_upper", "ci_method"])

    def ci_contains_null(self, message: AgentMessage) -> bool:
        uncertainty = message.uncertainty or message.context.get("uncertainty", {})
        if not all(key in uncertainty for key in ["ci_lower", "ci_upper"]):
            return False
        null_value = float(message.context.get("null_value", 0.0))
        return float(uncertainty["ci_lower"]) <= null_value <= float(uncertainty["ci_upper"])

    def unsupported_claims(self, message: AgentMessage) -> list[dict[str, Any]]:
        unsupported = []
        for claim in message.claims:
            claim_type = claim.get("claim_type", "unknown")
            evidence = claim.get("evidence_available") or message.evidence_available or message.evidence
            if claim_type in {"observed", "inferred"} and not evidence:
                unsupported.append(claim)
            if claim_type == "blocked":
                unsupported.append(claim)
        return unsupported

    def compose_response(
        self,
        message: AgentMessage,
        *,
        summary_suffix: str,
        confidence: Optional[float] = None,
        done_status: Optional[DoneStatus] = None,
        next_action: Optional[Decision] = None,
        assumptions: Optional[list[str]] = None,
        evidence: Optional[list[str]] = None,
        risks: Optional[list[str]] = None,
        open_questions: Optional[list[str]] = None,
        requested_feedback: Optional[list[str]] = None,
        feedback_to: Optional[list[str]] = None,
        uncertainty: Optional[dict[str, Any]] = None,
        claims: Optional[list[dict[str, Any]]] = None,
        claim_type: Optional[ClaimType] = None,
        evidence_required: Optional[list[str]] = None,
        evidence_available: Optional[list[str]] = None,
        hypothesis_id: Optional[str] = None,
        hypothesis_status: Optional[HypothesisStatus] = None,
        clarification_questions: Optional[list[str]] = None,
        blocked_reason: Optional[str] = None,
        readiness_flags: Optional[dict[str, bool]] = None,
        source_metadata: Optional[dict[str, Any]] = None,
        conflicts: Optional[list[dict[str, Any]]] = None,
        security_warnings: Optional[list[dict[str, Any]]] = None,
        lifecycle_status: Optional[str] = None,
        compressed_memory: Optional[str] = None,
        decision_rationale: Optional[str] = None,
        context_updates: Optional[dict[str, Any]] = None,
    ) -> AgentMessage:
        context = dict(message.context)
        if context_updates:
            context.update(context_updates)
        next_evidence = evidence if evidence is not None else message.evidence
        next_claim_type = claim_type if claim_type is not None else (
            "observed" if next_evidence else message.claim_type
        )
        next_evidence_available = (
            evidence_available if evidence_available is not None else message.evidence_available
        )
        if not next_evidence_available and next_evidence:
            next_evidence_available = list(next_evidence)
        next_claims = claims if claims is not None else message.claims
        if not next_claims and context.get("evidence_gate_required"):
            next_claims = [
                {
                    "statement": summary_suffix,
                    "claim_type": next_claim_type,
                    "evidence_available": list(next_evidence_available),
                    "hypothesis_id": hypothesis_id if hypothesis_id is not None else message.hypothesis_id,
                }
            ]

        return replace(
            message,
            summary=(message.summary + "\n" + summary_suffix).strip(),
            confidence=confidence if confidence is not None else message.confidence,
            done_status=done_status if done_status is not None else message.done_status,
            next_action=next_action if next_action is not None else message.next_action,
            assumptions=assumptions if assumptions is not None else message.assumptions,
            evidence=evidence if evidence is not None else message.evidence,
            risks=risks if risks is not None else message.risks,
            open_questions=open_questions if open_questions is not None else message.open_questions,
            requested_feedback=requested_feedback
            if requested_feedback is not None
            else message.requested_feedback,
            feedback_to=feedback_to if feedback_to is not None else message.feedback_to,
            uncertainty=uncertainty if uncertainty is not None else message.uncertainty,
            claims=next_claims,
            claim_type=next_claim_type,
            evidence_required=evidence_required
            if evidence_required is not None
            else message.evidence_required,
            evidence_available=next_evidence_available,
            hypothesis_id=hypothesis_id if hypothesis_id is not None else message.hypothesis_id,
            hypothesis_status=hypothesis_status
            if hypothesis_status is not None
            else message.hypothesis_status,
            clarification_questions=clarification_questions
            if clarification_questions is not None
            else message.clarification_questions,
            blocked_reason=blocked_reason if blocked_reason is not None else message.blocked_reason,
            readiness_flags=readiness_flags if readiness_flags is not None else message.readiness_flags,
            source_metadata=source_metadata if source_metadata is not None else message.source_metadata,
            conflicts=conflicts if conflicts is not None else message.conflicts,
            security_warnings=security_warnings
            if security_warnings is not None
            else message.security_warnings,
            lifecycle_status=lifecycle_status if lifecycle_status is not None else message.lifecycle_status,
            compressed_memory=compressed_memory
            if compressed_memory is not None
            else message.compressed_memory,
            decision_rationale=decision_rationale
            if decision_rationale is not None
            else message.decision_rationale,
            context=context,
        )
