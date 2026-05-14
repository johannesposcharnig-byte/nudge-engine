"""Data agent skeleton."""

from .base import BaseAgent


class DataAgent(BaseAgent):
    name = "data"

    def run(self, message):
        formula_class = message.context.get("formula_class")
        formula_key = message.context.get("formula_key")
        missing_context = self.missing_context(message)

        if self.is_review(message):
            target = self.review_target(message)
            context = message.context.get("target_context", {})
            variables = context.get("variables", [])
            measurable = bool(variables) or bool(context.get("schema"))
            decision = "approve" if measurable and message.confidence >= 0.7 else "revise"
            risks = list(message.risks) or ["Potential leakage or unmeasured terms need to be ruled out."]
            return self.compose_response(
                message,
                summary_suffix=f"Data review for {target}: measurability and leakage check completed.",
                confidence=min(0.9, message.confidence + 0.03),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["Variables can be operationalized from available tables."],
                evidence=message.evidence or ["Schema and timestamp logic inspected."],
                risks=risks,
                open_questions=message.open_questions or ["Which variables are still unobserved?"],
                requested_feedback=["Please confirm variable definitions and leakage safety."],
            )

        if formula_class == "aggregation":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Data draft: aggregation fields, Omega_ct, N_ct and zero-denominator handling reviewed.",
                confidence=0.83,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Company aggregation requires stable user membership and a fixed observation window."],
                evidence=["Required aggregation inputs are explicitly listed in the formula registry."],
                risks=["Missing window logic or N_ct = 0 handling can break reproducibility."],
                open_questions=missing_context or ["Which snapshot defines I_ct?"],
                requested_feedback=["Please confirm window, membership and denominator policy."],
            )

        if formula_class == "causal":
            decision = "approve" if message.context.get("variables") else "revise"
            return self.compose_response(
                message,
                summary_suffix="Data draft: treatment, outcome, context variables and leakage timing reviewed.",
                confidence=0.84,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Treatment, context and outcome timestamps can be logged separately."],
                evidence=["Causal review variables are available in the formula context."],
                risks=["Post-treatment features in X_it would create leakage."],
                open_questions=missing_context or ["Which fields are guaranteed pre-treatment?"],
                requested_feedback=["Please confirm treatment assignment and pre-treatment features."],
            )

        if formula_class == "outcome":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Data draft: W_ct, feature lagging and company outcome availability reviewed.",
                confidence=0.82,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["W_ct must be computed before the target outcome window."],
                evidence=["Outcome inputs are listed and can be checked against a data contract."],
                risks=["Unlagged company features can leak future outcomes."],
                open_questions=missing_context or ["Which data table owns W_ct and outcome timestamps?"],
                requested_feedback=["Please confirm feature lag and outcome windows."],
            )

        if formula_class == "policy":
            decision = "approve" if not missing_context else "hold"
            return self.compose_response(
                message,
                summary_suffix="Data draft: reward inputs, no-action baseline and guardrail observability reviewed.",
                confidence=0.8,
                done_status="done" if decision == "approve" else "blocked",
                next_action=decision,
                assumptions=["All reward components must be observable or explicitly modeled."],
                evidence=["Policy context declares required reward and guardrail inputs."],
                risks=["Missing reward fields can silently change action ranking."],
                open_questions=missing_context or ["Which reward components are measured versus modeled?"],
                requested_feedback=["Please confirm reward and guardrail observability."],
            )

        if formula_class == "constraint":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Data draft: fairness groups, thresholds and contact counts reviewed.",
                confidence=0.82,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Group labels and contact events are observable with stable timestamps."],
                evidence=["Constraint inputs are explicit in the formula registry."],
                risks=["Missing or noisy group labels can invalidate fairness checks."],
                open_questions=missing_context or ["Which group definitions are approved for use?"],
                requested_feedback=["Please confirm group variables and thresholds."],
            )

        if formula_class == "evaluation":
            has_ci = self.has_ci(message)
            support_required = formula_key == "dr_ope"
            support_ready = not support_required or all(
                key in message.context for key in ["overlap_check", "propensity_clipping", "cross_fitting", "support_check"]
            )
            decision = "approve" if has_ci and support_ready and not missing_context else "hold"
            return self.compose_response(
                message,
                summary_suffix="Data draft: evaluation inputs, CI fields and support requirements reviewed.",
                confidence=0.83,
                done_status="done" if decision == "approve" else "blocked",
                next_action=decision,
                assumptions=["Evaluation can proceed only with comparable groups and explicit uncertainty fields."],
                evidence=["Required variables and uncertainty fields are checked in the message context."],
                risks=["Missing CI fields or weak support should block effect claims."],
                open_questions=missing_context or ([] if has_ci else ["Where are effect_estimate, ci_lower, ci_upper and ci_method?"]),
                requested_feedback=["Please confirm CI fields, sample size and support checks."],
            )

        return self.compose_response(
            message,
            summary_suffix="Data draft: schema, logging, and leakage controls reviewed.",
            confidence=0.82,
            done_status="done",
            next_action="approve",
            assumptions=["Inputs can be logged with stable IDs and timestamps."],
            evidence=["Data contract and feature pipeline assumptions are explicit."],
            risks=["Any missing field can still break downstream formulas."],
            open_questions=["Are all formula variables observable?"],
            requested_feedback=["Please review field definitions and time windows."],
        )
