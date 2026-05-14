"""Devil's advocate agent skeleton."""

from .base import BaseAgent
from ..reward import reward_policy_blockers


class DevilsAdvocateAgent(BaseAgent):
    name = "devils_advocate"

    def run(self, message):
        formula_class = message.context.get("formula_class")
        formula_key = message.context.get("formula_key")

        if self.is_review(message):
            target = self.review_target(message)
            decision = "revise" if message.confidence >= 0.75 else "hold"
            return self.compose_response(
                message,
                summary_suffix=f"Devil's advocate review for {target}: strongest counterposition and failure mode drafted.",
                confidence=min(0.9, message.confidence + 0.02),
                done_status="done" if decision == "revise" else "blocked",
                next_action=decision,
                assumptions=message.assumptions or ["A realistic counter-argument can be built from the current output."],
                evidence=message.evidence or ["Counterfactual failure modes and edge cases can be stated."],
                risks=message.risks or ["The favored direction may fail under alternative assumptions."],
                open_questions=message.open_questions or ["What is the strongest reason this should not work?"],
                requested_feedback=["Please verify whether the counterposition changes the decision."],
            )

        if formula_class:
            missing_context = self.missing_context(message)
            risks_by_class = {
                "causal": "Hidden confounding, interference, or weak overlap can make the causal effect look stronger than it is.",
                "aggregation": "Small companies, changing membership, or N_ct = 0 can make aggregates noisy or misleading.",
                "index": "Composite indices can be gamed if weights or audited inputs are not locked.",
                "outcome": "Outcome models can confuse correlation with causal impact if feature timing is not strict.",
                "policy": "The policy can optimize a proxy reward and produce contact fatigue or unfair exposure.",
                "constraint": "Exposure fairness can hide outcome inequality or threshold gaming.",
                "evaluation": "Evaluation can overstate certainty when confidence intervals, support, or propensities are weak.",
            }
            risk = risks_by_class.get(str(formula_class), "The formula may fail under alternative assumptions.")
            if formula_key == "reward_policy" and not reward_policy_blockers(message.context):
                decision = "approve"
            elif formula_key in {"dr_ope", "reward_policy"}:
                decision = "hold"
            elif missing_context:
                decision = "revise"
            else:
                decision = "approve"
            return self.compose_response(
                message,
                summary_suffix=f"Devil's advocate draft: formula-specific failure mode for {formula_class} prepared.",
                confidence=0.82,
                done_status="blocked" if decision == "hold" else "done",
                next_action=decision,
                assumptions=["A credible counter-position must be cleared before final approval."],
                evidence=["Failure mode is derived from the formula class and required assumptions."],
                risks=[risk],
                open_questions=missing_context or ["What concrete evidence would falsify the current approval path?"],
                requested_feedback=["Please verify whether this failure mode changes the orchestrator decision."],
            )

        return self.compose_response(
            message,
            summary_suffix="Devil's advocate draft: strongest counterposition prepared.",
            confidence=0.8,
            done_status="done",
            next_action="revise",
            assumptions=["At least one credible failure mode exists."],
            evidence=["Counterposition and downside risks identified."],
            risks=["Optimistic assumptions may hide failure conditions."],
            open_questions=["What evidence would falsify the current direction?"],
            requested_feedback=["Please review the counterposition and failure modes."],
        )
