"""Behavioral method registry and eligibility rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


MethodKind = Literal["baseline", "action", "meta"]
MethodStatus = Literal["eligible", "blocked"]


@dataclass(frozen=True)
class BehavioralMethod:
    method: str
    kind: MethodKind
    mechanism: str
    required_signals: tuple[str, ...] = ()
    best_fit: tuple[str, ...] = ()
    governance_required: bool = False
    manipulation_risk: str = "low"
    allowed_claim_type: str = "hypothesis"
    outcome_metrics: tuple[str, ...] = ("activation_score",)
    formula_layers: tuple[str, ...] = ("tau_a(x)", "pi*(x)")


@dataclass(frozen=True)
class MethodEvaluation:
    method: str
    status: MethodStatus
    fit_score: float
    reason_codes: list[str]
    required_signals: list[str]
    governance_required: bool
    manipulation_risk: str
    claim_type: str = "hypothesis"

    def as_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "status": self.status,
            "fit_score": self.fit_score,
            "reason_codes": list(self.reason_codes),
            "required_signals": list(self.required_signals),
            "governance_required": self.governance_required,
            "manipulation_risk": self.manipulation_risk,
            "claim_type": self.claim_type,
        }


BEHAVIORAL_METHOD_REGISTRY: dict[str, BehavioralMethod] = {
    "no_action": BehavioralMethod(
        method="no_action",
        kind="baseline",
        mechanism="baseline comparison and harm avoidance",
        allowed_claim_type="observed",
        outcome_metrics=("activation_score", "fatigue_signal", "harm_monitoring"),
    ),
    "default": BehavioralMethod(
        method="default",
        kind="action",
        mechanism="status quo bias and reduced choice effort",
        required_signals=("default_available",),
        best_fit=("activation", "onboarding", "completion"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "cognitive_ease": BehavioralMethod(
        method="cognitive_ease",
        kind="action",
        mechanism="processing fluency and effort reduction",
        required_signals=("friction_signal", "resistance_signal"),
        best_fit=("completion", "activation", "feature_adoption"),
        manipulation_risk="low",
    ),
    "simplification": BehavioralMethod(
        method="simplification",
        kind="action",
        mechanism="cognitive load reduction",
        required_signals=("friction_signal",),
        best_fit=("onboarding", "task_completion"),
        manipulation_risk="low",
    ),
    "social_proof": BehavioralMethod(
        method="social_proof",
        kind="action",
        mechanism="descriptive norms and social comparison",
        required_signals=("peer_norm_signal", "peer_reference_group_valid"),
        best_fit=("activation", "adoption", "renewal"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "gain_frame": BehavioralMethod(
        method="gain_frame",
        kind="action",
        mechanism="positive outcome salience",
        required_signals=("fatigue_signal",),
        best_fit=("activation", "feature_adoption"),
        governance_required=False,
        manipulation_risk="low",
    ),
    "loss_frame": BehavioralMethod(
        method="loss_frame",
        kind="action",
        mechanism="loss aversion",
        required_signals=("deadline_pressure",),
        best_fit=("deadline_behavior", "renewal"),
        governance_required=True,
        manipulation_risk="high",
    ),
    "commitment": BehavioralMethod(
        method="commitment",
        kind="action",
        mechanism="precommitment and consistency",
        required_signals=("activation_gap",),
        best_fit=("follow_through", "retention"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "reciprocity": BehavioralMethod(
        method="reciprocity",
        kind="action",
        mechanism="reciprocity norm and trust building",
        required_signals=("trust_gap_signal",),
        best_fit=("engagement", "trust", "response_rate"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "timely_reminder": BehavioralMethod(
        method="timely_reminder",
        kind="action",
        mechanism="cueing and present-bias support",
        required_signals=("deadline_pressure", "trigger_event_available"),
        best_fit=("follow_up", "deadline_behavior", "inaction_recovery"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "goal_setting": BehavioralMethod(
        method="goal_setting",
        kind="action",
        mechanism="self-regulation and goal-gradient effects",
        required_signals=("activation_gap", "goal_feasibility_known"),
        best_fit=("activation", "ongoing_use", "team_performance"),
        manipulation_risk="low",
    ),
    "progress_feedback": BehavioralMethod(
        method="progress_feedback",
        kind="action",
        mechanism="feedback loops and competence signals",
        required_signals=("activation_gap",),
        best_fit=("habit_building", "completion", "retention"),
        manipulation_risk="low",
    ),
    "just_in_time_intervention": BehavioralMethod(
        method="just_in_time_intervention",
        kind="action",
        mechanism="event-triggered context-dependent support",
        required_signals=("trigger_event_available", "deadline_pressure"),
        best_fit=("inaction_recovery", "deadline_support"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "transparency_explanation": BehavioralMethod(
        method="transparency_explanation",
        kind="action",
        mechanism="trust calibration and informed choice",
        required_signals=("trust_gap_signal",),
        best_fit=("legitimacy", "trust", "high_risk_methods"),
        governance_required=False,
        manipulation_risk="low",
    ),
    "progress_oriented_default": BehavioralMethod(
        method="progress_oriented_default",
        kind="action",
        mechanism="default effect plus progress salience",
        required_signals=("default_available", "activation_gap"),
        best_fit=("activation", "next_best_action"),
        governance_required=True,
        manipulation_risk="medium",
    ),
    "personalization": BehavioralMethod(
        method="personalization",
        kind="meta",
        mechanism="heterogeneous treatment effects and contextual relevance",
        required_signals=("segment_fields",),
        best_fit=("selection_layer",),
        governance_required=True,
        manipulation_risk="medium",
        formula_layers=("tau_a(x)", "pi*(x)", "V_hat_DR(pi)"),
    ),
}


def action_methods() -> list[str]:
    return [
        method.method
        for method in BEHAVIORAL_METHOD_REGISTRY.values()
        if method.kind in {"baseline", "action"}
    ]


def meta_methods() -> list[str]:
    return [
        method.method
        for method in BEHAVIORAL_METHOD_REGISTRY.values()
        if method.kind == "meta"
    ]


def get_behavioral_method(method: str) -> BehavioralMethod | None:
    return BEHAVIORAL_METHOD_REGISTRY.get(method)


def _missing_required_signals(method: BehavioralMethod, context: dict[str, Any]) -> list[str]:
    missing = []
    for signal in method.required_signals:
        if signal not in context or context.get(signal) in {None, ""}:
            missing.append(signal)
        if isinstance(context.get(signal), bool) and context.get(signal) is False:
            missing.append(signal)
    return sorted(set(missing))


def evaluate_behavioral_method(method_name: str, context: dict[str, Any]) -> MethodEvaluation:
    method = get_behavioral_method(method_name)
    if method is None:
        return MethodEvaluation(
            method=method_name,
            status="blocked",
            fit_score=0.0,
            reason_codes=["unknown_behavioral_method"],
            required_signals=[],
            governance_required=True,
            manipulation_risk="unknown",
            claim_type="blocked",
        )
    if method.kind == "baseline":
        return MethodEvaluation(
            method=method.method,
            status="eligible",
            fit_score=0.0,
            reason_codes=["baseline_action"],
            required_signals=list(method.required_signals),
            governance_required=method.governance_required,
            manipulation_risk=method.manipulation_risk,
            claim_type="observed",
        )

    missing = _missing_required_signals(method, context)
    reason_codes = [f"missing_signal:{signal}" for signal in missing]
    fatigue = float(context.get("fatigue_signal", 0.0) or 0.0)
    if method.method in {"loss_frame", "timely_reminder", "just_in_time_intervention"} and fatigue >= 0.55:
        reason_codes.append("method_blocked_by_fatigue")
    if method.method == "social_proof" and float(context.get("peer_norm_signal", 0.0) or 0.0) < 0.2:
        reason_codes.append("weak_peer_norm_signal")
    if method.method == "commitment" and float(context.get("activation_gap", 0.0) or 0.0) < 0.2:
        reason_codes.append("weak_commitment_gap")
    if method.method in {"default", "progress_oriented_default"} and context.get("default_available") is not True:
        reason_codes.append("default_not_available")

    status: MethodStatus = "blocked" if reason_codes else "eligible"
    return MethodEvaluation(
        method=method.method,
        status=status,
        fit_score=0.0 if status == "blocked" else behavioral_fit_score(method.method, context),
        reason_codes=sorted(set(reason_codes)) or ["method_eligible"],
        required_signals=list(method.required_signals),
        governance_required=method.governance_required,
        manipulation_risk=method.manipulation_risk,
        claim_type=method.allowed_claim_type if status == "eligible" else "blocked",
    )


def behavioral_fit_score(method: str, context: dict[str, Any]) -> float:
    fatigue = float(context.get("fatigue_signal", 0.0) or 0.0)
    resistance = float(context.get("resistance_signal", 0.0) or 0.0)
    friction = float(context.get("friction_signal", 0.0) or 0.0)
    trust_gap = float(context.get("trust_gap_signal", 0.0) or 0.0)
    peer_norm = float(context.get("peer_norm_signal", 0.0) or 0.0)
    deadline = float(context.get("deadline_pressure", 0.0) or 0.0)
    activation_gap = float(context.get("activation_gap", 0.0) or 0.0)

    scores = {
        "no_action": 0.0,
        "default": 0.55 + 0.15 * friction,
        "cognitive_ease": max(friction, resistance),
        "simplification": 0.75 * friction + 0.10 * resistance,
        "social_proof": peer_norm - 0.15 * resistance,
        "gain_frame": 0.55 + 0.20 * (1.0 - fatigue),
        "loss_frame": deadline - 0.35 * fatigue,
        "commitment": activation_gap - 0.10 * friction,
        "reciprocity": trust_gap,
        "timely_reminder": deadline - 0.25 * fatigue,
        "goal_setting": activation_gap - 0.10 * fatigue,
        "progress_feedback": 0.70 * activation_gap - 0.15 * resistance,
        "just_in_time_intervention": deadline - 0.20 * fatigue,
        "transparency_explanation": trust_gap + 0.15 * resistance,
        "progress_oriented_default": 0.45 + 0.35 * activation_gap,
    }
    return round(max(0.0, min(1.0, scores.get(method, 0.0))), 4)
