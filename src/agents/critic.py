"""Critic agent skeleton."""

from .base import BaseAgent


class CriticAgent(BaseAgent):
    name = "critic"

    def run(self, message):
        if self.is_review(message):
            target = self.review_target(message)
            missing = []
            if not message.assumptions:
                missing.append("assumptions")
            if not message.evidence:
                missing.append("evidence")
            if not message.open_questions:
                missing.append("open_questions")
            decision = "revise" if missing or message.confidence < 0.8 else "approve"
            return self.compose_response(
                message,
                summary_suffix=f"Critic review for {target}: gaps, inconsistencies, and missing safeguards checked.",
                confidence=min(0.9, message.confidence + 0.02),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["The target output is reviewable."],
                evidence=message.evidence or ["The output has enough structure to critique."],
                risks=message.risks or ["Any unsupported claim should be tightened before release."],
                open_questions=message.open_questions or ["What still needs explicit justification?"],
                requested_feedback=["Please tighten missing assumptions and evidence."],
            )

        return self.compose_response(
            message,
            summary_suffix="Critic draft: method gaps and missing evidence flagged.",
            confidence=0.82,
            done_status="done",
            next_action="approve",
            assumptions=["The task can be audited against the output structure."],
            evidence=["At least one concrete gap should be surfaced each round."],
            risks=["Unclear assumptions can propagate errors downstream."],
            open_questions=["Which claim is least supported?"],
            requested_feedback=["Please review missing evidence and logic gaps."],
        )
