"""Evaluation agent skeleton."""

from .base import BaseAgent


class EvaluationAgent(BaseAgent):
    name = "evaluation"

    def run(self, message):
        formula_class = message.context.get("formula_class")
        formula_key = message.context.get("formula_key")
        missing_context = self.missing_context(message)

        if self.is_review(message):
            target = self.review_target(message)
            decision = "approve" if message.confidence >= 0.7 else "revise"
            return self.compose_response(
                message,
                summary_suffix=f"Evaluation review for {target}: lift, drift, and stability check completed.",
                confidence=min(0.9, message.confidence + 0.03),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["Evaluation windows match the decision windows."],
                evidence=message.evidence or ["Offline or online metrics can be compared to baselines."],
                risks=message.risks or ["The comparison may be unstable across segments or time."],
                open_questions=message.open_questions or ["Which metric is the primary success measure?"],
                requested_feedback=["Please confirm the evaluation criterion and stability."],
            )

        if formula_class == "evaluation" or message.context.get("ci_required"):
            has_ci = self.has_ci(message)
            if has_ci:
                contains_null = self.ci_contains_null(message)
                decision = "revise" if contains_null else "approve"
                open_questions = ["The interval contains the null value. Treat as not yet stable."] if contains_null else []
            else:
                decision = "hold"
                open_questions = ["CI fields are required before claiming effect stability."]

            if formula_key == "dr_ope":
                support_missing = [
                    key for key in ["overlap_check", "propensity_clipping", "cross_fitting", "support_check"]
                    if key not in message.context
                ]
                if support_missing:
                    decision = "hold"
                    open_questions.extend(support_missing)

            return self.compose_response(
                message,
                summary_suffix="Evaluation draft: confidence interval, stability and support checks reviewed.",
                confidence=0.84,
                done_status="done" if decision != "hold" else "blocked",
                next_action=decision,
                assumptions=["95% is the default confidence level; 90% is exploratory."],
                evidence=["Effect decisions require estimate, CI bounds, method and sample size when available."],
                risks=["A missing or null-crossing interval should not be treated as a confirmed effect."],
                open_questions=open_questions or missing_context or ["Which rollout threshold applies to the interval width?"],
                requested_feedback=["Please confirm CI method, confidence level and rollout threshold."],
                uncertainty=dict(message.uncertainty),
            )

        return self.compose_response(
            message,
            summary_suffix="Evaluation draft: offline and online monitoring plan prepared.",
            confidence=0.82,
            done_status="done",
            next_action="approve",
            assumptions=["A baseline or comparison path exists."],
            evidence=["Evaluation metrics and monitoring criteria are specified."],
            risks=["Segment drift can still invalidate conclusions."],
            open_questions=["Which acceptance threshold applies to rollout?"],
            requested_feedback=["Please review evaluation design and thresholds."],
        )
