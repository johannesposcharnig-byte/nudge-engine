"""Statistical agent skeleton."""

from .base import BaseAgent


class StatisticalAgent(BaseAgent):
    name = "statistical"

    def run(self, message):
        formula_class = message.context.get("formula_class")
        formula_key = message.context.get("formula_key")
        missing_context = self.missing_context(message)

        if self.is_review(message):
            target = self.review_target(message)
            context = message.context.get("target_context", {})
            formula = context.get("formula", message.summary)
            has_formula = "=" in formula or "E[" in formula or "sigma" in formula
            decision = "approve" if has_formula and message.confidence >= 0.75 else "revise"
            return self.compose_response(
                message,
                summary_suffix=f"Statistical review for {target}: notation, identification and estimability checked.",
                confidence=min(0.92, message.confidence + 0.06),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["The model can be identified under the stated assumptions."],
                evidence=message.evidence or ["Notation and inferential structure are inspectable."],
                risks=message.risks or ["Confounding, positivity, or interference may still affect validity."],
                open_questions=message.open_questions or ["What is the identification strategy?"],
                requested_feedback=["Please confirm the estimand and inferential assumptions."],
            )

        if formula_class == "causal":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: CATE estimand, identification, positivity, SUTVA and control condition reviewed.",
                confidence=0.86,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Potential outcomes are meaningful only under a stated identification strategy."],
                evidence=["CATE notation matches a conditional incremental effect."],
                risks=["Confounding, interference, or weak overlap can invalidate causal interpretation."],
                open_questions=missing_context or ["Which design identifies the counterfactual outcome?"],
                requested_feedback=["Please confirm identification, positivity, SUTVA and baseline condition."],
            )

        if formula_class == "aggregation":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: aggregation denominator, windowing and small-sample stability reviewed.",
                confidence=0.82,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Aggregates are interpretable only with a fixed observation window and denominator rule."],
                evidence=["Mean aggregation is mathematically valid when I_ct and N_ct are stable."],
                risks=["Small N_ct or undefined N_ct can make company-level signals unstable."],
                open_questions=missing_context or ["Which rule applies when N_ct equals zero?"],
                requested_feedback=["Please confirm Omega_ct, N_ct and the zero-denominator rule."],
            )

        if formula_class == "outcome":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: outcome model link, lagging, uncertainty and calibration route reviewed.",
                confidence=0.83,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Company features must precede the outcome window."],
                evidence=["Outcome model structure can be evaluated with calibration and uncertainty intervals."],
                risks=["Endogeneity and unlagged features can make the estimated association misleading."],
                open_questions=missing_context or ["Which confidence interval method is used for grouped company data?"],
                requested_feedback=["Please confirm feature lagging and cluster-aware uncertainty."],
            )

        if formula_class == "policy":
            decision = "approve" if message.context.get("reward_calibrated") else "hold"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: policy reward, no-action baseline and estimability reviewed.",
                confidence=0.8,
                done_status="done" if decision == "approve" else "blocked",
                next_action=decision,
                assumptions=["Policy ranking is valid only after reward components are calibrated."],
                evidence=["Argmax policy is mathematically valid once reward and constraints are defined."],
                risks=["Uncalibrated rewards can optimize proxies instead of real impact."],
                open_questions=missing_context or ["How are reward components scaled and calibrated?"],
                requested_feedback=["Please confirm reward calibration and no-action baseline."],
            )

        if formula_class == "constraint":
            decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: constraint threshold and group comparison logic reviewed.",
                confidence=0.82,
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=["Constraint thresholds must be defined before rollout."],
                evidence=["Fairness and contact limits can be evaluated as explicit inequalities."],
                risks=["Exposure parity alone may miss outcome inequality."],
                open_questions=missing_context or ["Which groups and thresholds are in scope?"],
                requested_feedback=["Please confirm group definitions and thresholds."],
            )

        if formula_class == "evaluation":
            if formula_key == "dr_ope" and self.missing_context(message):
                decision = "hold"
            else:
                decision = "approve" if not missing_context else "revise"
            return self.compose_response(
                message,
                summary_suffix="Statistical draft: evaluation estimand, interval method and support assumptions reviewed.",
                confidence=0.84,
                done_status="done" if decision != "hold" else "blocked",
                next_action=decision,
                assumptions=["Evaluation results require an explicit confidence level and valid support."],
                evidence=["A/B, CUPED and DR-OPE each have identifiable uncertainty requirements."],
                risks=["Missing support checks or missing intervals can overstate evidence."],
                open_questions=missing_context or ["Which confidence interval method and level are used?"],
                requested_feedback=["Please confirm uncertainty method and support assumptions."],
            )

        return self.compose_response(
            message,
            summary_suffix="Statistical draft: estimand, assumptions, and testing route prepared.",
            confidence=0.85,
            done_status="done",
            next_action="approve",
            assumptions=["The estimand is identifiable under the current design."],
            evidence=["Identification and inference checks are specified."],
            risks=["Assumptions must be validated against real data and design constraints."],
            open_questions=["Is the estimand estimable with the current data?"],
            requested_feedback=["Please review identification and inferential validity."],
        )
