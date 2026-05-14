"""Governance agent skeleton."""

from .base import BaseAgent


class GovernanceAgent(BaseAgent):
    name = "governance"

    def run(self, message):
        formula_class = message.context.get("formula_class")
        formula_key = message.context.get("formula_key")
        sensitive_methods = {"loss_frame", "social_proof", "reciprocity", "fairness", "reward_policy"}

        if self.is_review(message):
            target = self.review_target(message)
            risk_text = " ".join(message.risks).lower()
            high_risk = any(token in risk_text for token in ["dark", "consent", "harm", "risk", "manip"])
            decision = "hold" if high_risk else "approve"
            return self.compose_response(
                message,
                summary_suffix=f"Governance review for {target}: transparency, consent, and fairness checked.",
                confidence=min(0.88, message.confidence + 0.03),
                done_status="done" if decision == "approve" else "blocked",
                next_action=decision,
                assumptions=message.assumptions or ["The intervention can be communicated transparently."],
                evidence=message.evidence or ["Consent, fairness, and user choice considerations were inspected."],
                risks=message.risks or ["Governance concerns must be escalated before rollout."],
                open_questions=message.open_questions or ["Does the flow preserve user autonomy?"],
                requested_feedback=["Please confirm ethics, transparency, and approval constraints."],
            )

        if formula_class in {"policy", "constraint"} or formula_key in sensitive_methods:
            missing = self.missing_context(message)
            high_risk = bool(message.context.get("governance_blocked"))
            decision = "hold" if high_risk or missing else "approve"
            return self.compose_response(
                message,
                summary_suffix="Governance draft: autonomy, transparency, fairness and contact-pressure safeguards reviewed.",
                confidence=0.84,
                done_status="done" if decision == "approve" else "blocked",
                next_action=decision,
                assumptions=["User autonomy and a no-action path must remain available."],
                evidence=["Governance-sensitive formula classes require explicit guardrails."],
                risks=["Opaque or manipulative nudges must not be released."],
                open_questions=missing or ["Are vulnerable groups affected by this policy or constraint?"],
                requested_feedback=["Please confirm transparency, consent and fairness safeguards."],
            )

        return self.compose_response(
            message,
            summary_suffix="Governance draft: transparency, choice, and risk constraints prepared.",
            confidence=0.84,
            done_status="done",
            next_action="approve",
            assumptions=["The workflow preserves user choice."],
            evidence=["Guardrails and consent checks are part of the design."],
            risks=["Any manipulative pattern must be blocked before deployment."],
            open_questions=["Are any vulnerable groups affected?"],
            requested_feedback=["Please review consent and autonomy safeguards."],
        )
