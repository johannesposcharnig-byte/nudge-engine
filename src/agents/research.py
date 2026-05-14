"""Research agent skeleton."""

from .base import BaseAgent


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, message):
        formula_class = message.context.get("formula_class")

        if self.is_review(message):
            target = self.review_target(message)
            risks = list(message.risks) or ["Evidence base may be thin or theory-to-formula mapping may be incomplete."]
            decision = "approve" if message.confidence >= 0.75 and message.evidence else "revise"
            return self.compose_response(
                message,
                summary_suffix=f"Research review for {target}: theory and evidence check completed.",
                confidence=min(0.9, message.confidence + 0.05),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["The theory is consistent with the stated use case."],
                evidence=message.evidence or ["Literature alignment and mechanism plausibility need explicit confirmation."],
                risks=risks,
                open_questions=message.open_questions or ["Which mechanism is empirically strongest?"],
                requested_feedback=["Please confirm theoretical fit and evidence strength."],
            )

        if formula_class:
            mechanism = {
                "causal": "causal effect logic is compatible with intervention evaluation.",
                "aggregation": "company aggregation links individual behavior to organizational signals.",
                "index": "index construction must reflect a defensible behavioral or operational construct.",
                "outcome": "business outcomes should be tied to lagged behavioral mechanisms.",
                "policy": "policy decisions must preserve autonomy and use the least intrusive effective action.",
                "constraint": "constraints support fairness, transparency and bounded contact pressure.",
                "evaluation": "evaluation formulas test whether observed effects are stable enough to learn from.",
            }.get(str(formula_class), "mechanism requires explicit theory mapping.")
            return self.compose_response(
                message,
                summary_suffix=f"Research draft: {mechanism}",
                confidence=0.82,
                done_status="done",
                next_action="approve",
                assumptions=["The formula is only scientifically grounded when its mechanism is explicit."],
                evidence=["Mechanism and formula class are linked in the review context."],
                risks=["A plausible mechanism still needs empirical validation."],
                open_questions=["Which behavioral mechanism is primary for this formula or intervention?"],
                requested_feedback=["Please confirm theoretical mechanism and evidence strength."],
            )

        topic = message.context.get("topic", message.summary)
        return self.compose_response(
            message,
            summary_suffix=f"Research draft for {topic}: mechanism, evidence and theoretical fit reviewed.",
            confidence=0.8,
            done_status="done",
            next_action="approve",
            assumptions=["The use case can be grounded in behavioral theory."],
            evidence=["Mechanism plausibility and literature direction identified."],
            risks=["Empirical strength still requires formula-level and data-level validation."],
            open_questions=["Which evidence source is primary for the target behavior?"],
            requested_feedback=["Please review theoretical fit and intervention plausibility."],
        )
