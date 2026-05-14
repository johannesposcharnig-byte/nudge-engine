"""Policy agent skeleton."""

from .base import BaseAgent


class PolicyAgent(BaseAgent):
    name = "policy"

    def run(self, message):
        if self.is_review(message):
            target = self.review_target(message)
            decision = "approve" if "risk" not in " ".join(message.risks).lower() and message.confidence >= 0.7 else "revise"
            return self.compose_response(
                message,
                summary_suffix=f"Policy review for {target}: reward, guardrails, and no-action baseline checked.",
                confidence=min(0.9, message.confidence + 0.04),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["A safe no-action option remains available."],
                evidence=message.evidence or ["Reward structure and guardrail logic are explicit."],
                risks=message.risks or ["Policy should not outpace evaluation evidence."],
                open_questions=message.open_questions or ["Is the contact budget compatible with the policy?"],
                requested_feedback=["Please confirm guardrails and decision ranking."],
            )

        return self.compose_response(
            message,
            summary_suffix="Policy draft: action ranking, reward, and guardrails prepared.",
            confidence=0.83,
            done_status="done",
            next_action="approve",
            assumptions=["No-action is always a valid fallback."],
            evidence=["Reward and guardrail logic can be traced."],
            risks=["Policy quality depends on the upstream effect estimates."],
            open_questions=["Are all operational constraints encoded?"],
            requested_feedback=["Please review reward design and guardrails."],
        )
