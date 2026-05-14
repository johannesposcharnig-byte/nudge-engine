"""Reward and no-action baseline governance for the Nudge Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .behavioral_methods import (
    action_methods,
    behavioral_fit_score,
    evaluate_behavioral_method,
)
from .behavioral_heuristics import evaluate_heuristics, heuristic_method_bonus


REQUIRED_GUARDRAILS = {
    "consent_required",
    "opt_out_available",
    "frequency_cap",
    "cooldown_window",
    "fatigue_hold_threshold",
    "vulnerability_unknown_hold",
    "protected_state_no_action",
    "manipulation_denylist",
    "no_action_monitoring",
    "harm_monitoring",
}

MANIPULATION_SENSITIVE_METHODS = {
    "default",
    "loss_frame",
    "commitment",
    "social_proof",
    "reciprocity",
    "timely_reminder",
    "just_in_time_intervention",
    "progress_oriented_default",
}

POLICY_ACTION_SET = action_methods()


@dataclass(frozen=True)
class RewardWeights:
    outcome: float = 1.0
    renewal: float = 0.45
    click_proxy: float = 0.08
    fatigue_penalty: float = 0.35
    contact_cost: float = 0.04
    governance_penalty: float = 1.0
    uncertainty_penalty: float = 0.18
    manipulation_penalty: float = 0.25


@dataclass(frozen=True)
class RewardResult:
    action: str
    reward: float
    no_action_reward: float
    baseline_delta: float
    status: str
    reason_codes: list[str]
    evaluated_action: str | None = None
    method_evaluation: dict[str, Any] | None = None
    blocked_reason: str | None = None
    claim_type: str = "hypothesis"

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "evaluated_action": self.evaluated_action or self.action,
            "reward": self.reward,
            "no_action_reward": self.no_action_reward,
            "baseline_delta": self.baseline_delta,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "method_evaluation": dict(self.method_evaluation or {}),
            "blocked_reason": self.blocked_reason,
            "claim_type": self.claim_type,
        }


def normalize_guardrails(guardrails: Any) -> set[str]:
    if isinstance(guardrails, dict):
        return {str(key) for key, value in guardrails.items() if value}
    if isinstance(guardrails, (list, set, tuple)):
        return {str(item) for item in guardrails}
    return set()


def missing_required_guardrails(guardrails: Any) -> list[str]:
    return sorted(REQUIRED_GUARDRAILS - normalize_guardrails(guardrails))


def has_required_guardrails(guardrails: Any) -> bool:
    return not missing_required_guardrails(guardrails)


def validate_no_action_baseline(baseline: Any) -> list[str]:
    """Return missing or invalid no-action baseline fields."""
    if not isinstance(baseline, dict):
        return ["no_action_baseline_object"]
    missing = []
    required = [
        "baseline_action",
        "sample_size",
        "mean_outcome",
        "ci_lower",
        "ci_upper",
        "confidence_level",
        "monitoring_required",
    ]
    for key in required:
        if key not in baseline:
            missing.append(key)
    if baseline.get("baseline_action") != "no_action":
        missing.append("baseline_action_no_action")
    try:
        if int(baseline.get("sample_size", 0)) <= 0:
            missing.append("sample_size_positive")
    except (TypeError, ValueError):
        missing.append("sample_size_positive")
    try:
        if float(baseline.get("ci_lower", 0.0)) > float(baseline.get("ci_upper", 0.0)):
            missing.append("ci_bounds_order")
    except (TypeError, ValueError):
        missing.append("ci_bounds_numeric")
    try:
        if float(baseline.get("confidence_level", 0.0)) < 0.90:
            missing.append("confidence_level_minimum")
    except (TypeError, ValueError):
        missing.append("confidence_level_minimum")
    if baseline.get("monitoring_required") is not True:
        missing.append("monitoring_required_true")
    return sorted(set(missing))


def reward_policy_blockers(context: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not context.get("reward_calibrated"):
        blockers.append("reward_not_calibrated")
    blockers.extend(f"missing_guardrail:{item}" for item in missing_required_guardrails(context.get("guardrails")))
    blockers.extend(f"invalid_no_action_baseline:{item}" for item in validate_no_action_baseline(context.get("no_action_baseline")))

    if context.get("uses_ocean_for_personalization") and context.get("ocean_only_decision"):
        blockers.append("ocean_only_blocked")
    if context.get("heuristic_only_policy"):
        blockers.append("heuristic_only_policy_blocked")
    if context.get("active_nudge_requested") and context.get("consent") is not True:
        blockers.append("missing_consent")
    if context.get("active_nudge_requested") and context.get("opt_out") is True:
        blockers.append("opt_out")
    if context.get("active_nudge_requested") and context.get("consent_withdrawn") is True:
        blockers.append("consent_withdrawn")
    if context.get("active_nudge_requested") and context.get("experiment_group") == "control":
        blockers.append("control_group")
    if context.get("vulnerability_flag") is None and context.get("active_nudge_requested"):
        blockers.append("vulnerability_unknown")
    if context.get("vulnerability_flag") is True and context.get("active_nudge_requested"):
        blockers.append("protected_state_no_action")
    if context.get("fatigue_signal") is not None:
        threshold = float(context.get("fatigue_hold_threshold", 0.75))
        if float(context["fatigue_signal"]) >= threshold and context.get("active_nudge_requested"):
            blockers.append("high_fatigue")
    if int(context.get("recent_nudge_count", 0) or 0) > int(context.get("frequency_cap", 3) or 3):
        blockers.append("frequency_cap_exceeded")
    method = str(context.get("behavioral_method") or context.get("recommended_nudge") or "")
    if method in MANIPULATION_SENSITIVE_METHODS and not context.get("manipulation_governance_review"):
        blockers.append("manipulation_governance_review_missing")
    return sorted(set(blockers))


def estimate_no_action_reward(person: dict[str, Any], weights: RewardWeights = RewardWeights()) -> float:
    base = float(person.get("no_action_expected_outcome", person.get("baseline_activation_score", 0.42)))
    fatigue = float(person.get("fatigue_signal", 0.0))
    return round(base * weights.outcome - 0.05 * fatigue, 4)


def estimate_action_outcome(person: dict[str, Any], action: str) -> float:
    """Estimate action-specific outcome from measured barriers.

    The result is a test-time hypothesis, not a validated treatment effect.
    """
    base = float(person.get("baseline_activation_score", person.get("no_action_expected_outcome", 0.42)))
    max_uplift_by_action = {
        "no_action": 0.0,
        "default": 0.14,
        "cognitive_ease": 0.22,
        "simplification": 0.18,
        "social_proof": 0.16,
        "gain_frame": 0.13,
        "loss_frame": 0.10,
        "commitment": 0.18,
        "reciprocity": 0.15,
        "timely_reminder": 0.12,
        "goal_setting": 0.16,
        "progress_feedback": 0.14,
        "just_in_time_intervention": 0.14,
        "transparency_explanation": 0.08,
        "progress_oriented_default": 0.18,
    }
    fit_score = behavioral_fit_score(action, person)
    uplift = 0.03 + max_uplift_by_action.get(action, 0.0) * fit_score if action != "no_action" else 0.0
    return round(max(0.0, min(1.0, base + uplift)), 4)


def score_action_reward(
    person: dict[str, Any],
    *,
    action: str | None = None,
    weights: RewardWeights = RewardWeights(),
) -> RewardResult:
    action_name = action or str(person.get("recommended_nudge", "no_action"))
    context = {
        **person,
        "active_nudge_requested": action_name != "no_action",
        "behavioral_method": action_name,
        "guardrails": person.get("guardrails", REQUIRED_GUARDRAILS),
        "no_action_baseline": person.get(
            "no_action_baseline",
            {
                "baseline_action": "no_action",
                "sample_size": 100,
                "mean_outcome": person.get("baseline_activation_score", 0.42),
                "ci_lower": 0.35,
                "ci_upper": 0.49,
                "confidence_level": 0.95,
                "monitoring_required": True,
            },
        ),
        "reward_calibrated": person.get("reward_calibrated", True),
    }
    method_evaluation = evaluate_behavioral_method(action_name, context)
    blockers = reward_policy_blockers(context)
    if method_evaluation.status == "blocked":
        blockers.extend(method_evaluation.reason_codes)
    no_action_reward = estimate_no_action_reward(person, weights)
    if blockers:
        blockers = sorted(set(blockers))
        return RewardResult(
            action="no_action",
            reward=no_action_reward,
            no_action_reward=no_action_reward,
            baseline_delta=0.0,
            status="blocked",
            reason_codes=blockers,
            evaluated_action=action_name,
            method_evaluation=method_evaluation.as_dict(),
            blocked_reason=blockers[0],
            claim_type="blocked",
        )

    if action_name == "no_action":
        return RewardResult(
            action="no_action",
            reward=no_action_reward,
            no_action_reward=no_action_reward,
            baseline_delta=0.0,
            status="approve",
            reason_codes=["no_action_baseline"],
            evaluated_action=action_name,
            method_evaluation=method_evaluation.as_dict(),
            claim_type="observed",
        )

    expected_outcome = estimate_action_outcome(person, action_name)
    heuristic_evaluations = evaluate_heuristics(person)
    heuristic_bonus = heuristic_method_bonus(action_name, heuristic_evaluations)
    fatigue = float(person.get("fatigue_signal", 0.0))
    contact_cost = float(person.get("contact_cost", 1.0))
    uncertainty = float(person.get("uncertainty_penalty", 0.0))
    renewed_bonus = weights.renewal if person.get("renewed") is True else 0.0
    click_bonus = weights.click_proxy if person.get("clicked_nudge") is True else 0.0
    manipulation_penalty = weights.manipulation_penalty if action_name in MANIPULATION_SENSITIVE_METHODS else 0.0
    reward = (
        weights.outcome * expected_outcome
        + heuristic_bonus
        + renewed_bonus
        + click_bonus
        - weights.fatigue_penalty * fatigue
        - weights.contact_cost * contact_cost
        - weights.uncertainty_penalty * uncertainty
        - manipulation_penalty
    )
    reward = round(reward, 4)
    delta = round(reward - no_action_reward, 4)
    if delta <= 0:
        return RewardResult(
            action="no_action",
            reward=no_action_reward,
            no_action_reward=no_action_reward,
            baseline_delta=delta,
            status="revise",
            reason_codes=["no_action_wins"],
            evaluated_action=action_name,
            method_evaluation=method_evaluation.as_dict(),
            claim_type="hypothesis",
        )
    return RewardResult(
        action=action_name,
        reward=reward,
        no_action_reward=no_action_reward,
        baseline_delta=delta,
        status="hypothesis",
        reason_codes=["reward_beats_no_action"],
        evaluated_action=action_name,
        method_evaluation=method_evaluation.as_dict(),
        claim_type="hypothesis",
    )


def rank_actions_for_person(person: dict[str, Any], actions: list[str] | None = None) -> list[RewardResult]:
    actions = actions or POLICY_ACTION_SET
    results = [score_action_reward(person, action=action) for action in actions]
    status_priority = {"hypothesis": 3, "approve": 2, "revise": 1, "blocked": 0}
    return sorted(
        results,
        key=lambda item: (item.reward, status_priority.get(item.status, 0), item.baseline_delta),
        reverse=True,
    )


def policy_decision_for_person(
    person: dict[str, Any],
    actions: list[str] | None = None,
) -> dict[str, Any]:
    ranking = rank_actions_for_person(person, actions)
    selected = next(
        (item for item in ranking if item.status in {"hypothesis", "approve"}),
        score_action_reward(person, action="no_action"),
    )
    return {
        "selected_action": selected.action,
        "selected_status": selected.status,
        "selected_reason_codes": list(selected.reason_codes),
        "selected_result": selected.as_dict(),
        "ranking": [item.as_dict() for item in ranking],
        "claim_type": "hypothesis" if selected.action != "no_action" else selected.claim_type,
    }
