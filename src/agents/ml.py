"""ML agent skeleton."""

from .base import BaseAgent


class MLAgent(BaseAgent):
    name = "ml"

    def run(self, message):
        if self.is_review(message):
            target = self.review_target(message)
            decision = "approve" if message.confidence >= 0.7 else "revise"
            return self.compose_response(
                message,
                summary_suffix=f"ML review for {target}: score stability and calibration check completed.",
                confidence=min(0.9, message.confidence + 0.04),
                done_status="done" if decision == "approve" else "partial",
                next_action=decision,
                assumptions=message.assumptions or ["The model can be trained reproducibly."],
                evidence=message.evidence or ["Score behavior, calibration, and prediction signal were examined."],
                risks=message.risks or ["Model drift or uncalibrated scores may reduce decision quality."],
                open_questions=message.open_questions or ["Which features dominate the signal?"],
                requested_feedback=["Please confirm model stability and calibration."],
            )

        return self.compose_response(
            message,
            summary_suffix="ML draft: model training, calibration, and score generation prepared.",
            confidence=0.84,
            done_status="done",
            next_action="approve",
            assumptions=["Model features are available and stable."],
            evidence=["Training and calibration paths are specified."],
            risks=["Poor feature quality can weaken uplift and forecasting."],
            open_questions=["Are the target labels consistent across windows?"],
            requested_feedback=["Please review model readiness and calibration strategy."],
        )
