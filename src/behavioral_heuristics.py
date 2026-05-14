"""Cognitive heuristic hypothesis layer for the Nudge Engine.

This layer explains behavior as testable hypotheses. It must not diagnose a
customer or approve actions by itself.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal


HeuristicStatus = Literal[
    "not_testable_yet",
    "weak_support",
    "moderate_support",
    "contradicted",
    "validated_experimentally",
    "reference_only",
    "excluded",
]


@dataclass(frozen=True)
class BehavioralHeuristic:
    heuristic_id: str
    source_url: str
    codex_group: str
    required_signals: tuple[str, ...]
    evidence_patterns: tuple[str, ...]
    alternative_explanations: tuple[str, ...]
    compatible_methods: tuple[str, ...]
    blocked_methods: tuple[str, ...]
    governance_risk: str
    claim_type: str = "hypothesis"
    mode: str = "active"


@dataclass(frozen=True)
class HeuristicEvaluation:
    heuristic_id: str
    status: HeuristicStatus
    support_score: float
    evidence_available: list[str]
    missing_signals: list[str]
    compatible_methods: list[str]
    blocked_methods: list[str]
    alternative_explanations: list[str]
    governance_risk: str
    reason_codes: list[str]
    claim_type: str = "hypothesis"

    def as_dict(self) -> dict[str, Any]:
        return {
            "heuristic_id": self.heuristic_id,
            "status": self.status,
            "support_score": self.support_score,
            "evidence_available": list(self.evidence_available),
            "missing_signals": list(self.missing_signals),
            "compatible_methods": list(self.compatible_methods),
            "blocked_methods": list(self.blocked_methods),
            "alternative_explanations": list(self.alternative_explanations),
            "governance_risk": self.governance_risk,
            "reason_codes": list(self.reason_codes),
            "claim_type": self.claim_type,
        }


TDL = "https://thedecisionlab.com/biases"
CODEX = "https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg"


ACTIVE_HEURISTICS: dict[str, BehavioralHeuristic] = {
    "availability_heuristic": BehavioralHeuristic(
        "availability_heuristic",
        f"{TDL}/availability-heuristic",
        "too_much_information",
        ("recent_salient_event", "event_recency", "behavior_change_after_event"),
        ("recent_event_overweighted", "salient_event_precedes_behavior_change"),
        ("real_need_change", "support_issue", "seasonality", "pricing_change"),
        ("transparency_explanation", "cognitive_ease", "progress_feedback"),
        ("loss_frame",),
        "medium",
    ),
    "present_bias": BehavioralHeuristic(
        "present_bias",
        f"{TDL}/present-bias",
        "need_to_act_fast",
        ("activation_gap", "delayed_benefit_signal"),
        ("short_term_cost_blocks_long_term_benefit",),
        ("unclear_value", "missing_capability", "product_friction"),
        ("commitment", "goal_setting", "timely_reminder", "progress_feedback"),
        ("loss_frame",),
        "medium",
    ),
    "hyperbolic_discounting": BehavioralHeuristic(
        "hyperbolic_discounting",
        f"{TDL}/hyperbolic-discounting",
        "need_to_act_fast",
        ("delayed_benefit_signal", "immediate_cost_signal"),
        ("immediate_rewards_overweighted",),
        ("budget_constraint", "unclear_value", "low_trust"),
        ("commitment", "goal_setting", "progress_feedback"),
        ("loss_frame",),
        "medium",
    ),
    "status_quo_bias": BehavioralHeuristic(
        "status_quo_bias",
        f"{TDL}/status-quo-bias",
        "need_to_act_fast",
        ("default_available", "switching_cost_signal"),
        ("current_option_persisted_despite_better_alternative",),
        ("migration_risk", "hidden_costs", "low_capability"),
        ("default", "progress_oriented_default", "commitment"),
        (),
        "medium",
    ),
    "loss_aversion": BehavioralHeuristic(
        "loss_aversion",
        f"{TDL}/loss-aversion",
        "need_to_act_fast",
        ("loss_salience", "deadline_pressure"),
        ("losses_weighted_more_than_gains",),
        ("real_risk", "pricing_change", "support_issue"),
        ("loss_frame", "transparency_explanation"),
        (),
        "high",
    ),
    "framing_effect": BehavioralHeuristic(
        "framing_effect",
        f"{TDL}/framing-effect",
        "not_enough_meaning",
        ("message_frame", "frame_response_difference"),
        ("same_offer_changes_behavior_by_frame",),
        ("audience_mismatch", "channel_effect", "copy_quality"),
        ("gain_frame", "transparency_explanation"),
        ("deceptive_urgency",),
        "medium",
    ),
    "choice_overload": BehavioralHeuristic(
        "choice_overload",
        f"{TDL}/choice-overload",
        "too_much_information",
        ("option_count", "dropoff_after_choice_set"),
        ("more_options_reduce_completion",),
        ("poor_information_architecture", "missing_recommendation", "low_intent"),
        ("simplification", "default", "cognitive_ease"),
        (),
        "low",
    ),
    "anchoring_bias": BehavioralHeuristic(
        "anchoring_bias",
        f"{TDL}/anchoring-bias",
        "not_enough_meaning",
        ("anchor_value", "subsequent_choice_shift"),
        ("first_value_shapes_later_choice",),
        ("price_sensitivity", "segment_difference", "copy_effect"),
        ("transparency_explanation", "gain_frame"),
        ("deceptive_anchoring",),
        "medium",
    ),
    "social_norms": BehavioralHeuristic(
        "social_norms",
        f"{TDL}/social-norms",
        "not_enough_meaning",
        ("peer_norm_signal", "peer_reference_group_valid"),
        ("peer_behavior_predicts_action",),
        ("selection_effect", "segment_confounding", "network_effect"),
        ("social_proof",),
        (),
        "medium",
    ),
    "bandwagon_effect": BehavioralHeuristic(
        "bandwagon_effect",
        f"{TDL}/bandwagon-effect",
        "not_enough_meaning",
        ("peer_norm_signal", "adoption_trend_signal"),
        ("rising_adoption_increases_following",),
        ("marketing_campaign", "seasonality", "network_effect"),
        ("social_proof",),
        (),
        "medium",
    ),
    "ambiguity_effect": BehavioralHeuristic(
        "ambiguity_effect",
        f"{TDL}/ambiguity-effect",
        "not_enough_meaning",
        ("uncertainty_signal", "information_gap"),
        ("unknown_option_avoided",),
        ("low_trust", "missing_value", "unclear_pricing"),
        ("transparency_explanation", "simplification", "default"),
        (),
        "low",
    ),
    "planning_fallacy": BehavioralHeuristic(
        "planning_fallacy",
        f"{TDL}/planning-fallacy",
        "need_to_act_fast",
        ("estimated_completion_time", "actual_completion_time"),
        ("tasks_take_longer_than_expected",),
        ("scope_change", "missing_capability", "external_dependency"),
        ("goal_setting", "progress_feedback", "commitment"),
        (),
        "low",
    ),
    "confirmation_bias": BehavioralHeuristic(
        "confirmation_bias",
        f"{TDL}/confirmation-bias",
        "too_much_information",
        ("belief_signal", "contradictory_information_ignored"),
        ("confirming_information_preferred",),
        ("irrelevant_message", "source_trust_issue", "identity_threat"),
        ("transparency_explanation",),
        ("social_proof", "loss_frame"),
        "high",
    ),
    "salience_bias": BehavioralHeuristic(
        "salience_bias",
        f"{TDL}/salience-bias",
        "too_much_information",
        ("salient_feature_exposure", "behavior_change_after_exposure"),
        ("prominent_information_drives_action",),
        ("novelty_effect", "copy_quality", "channel_effect"),
        ("transparency_explanation", "progress_feedback"),
        ("loss_frame",),
        "medium",
    ),
    "decision_fatigue": BehavioralHeuristic(
        "decision_fatigue",
        f"{TDL}/decision-fatigue",
        "need_to_act_fast",
        ("fatigue_signal", "decision_count"),
        ("later_decisions_have_lower_quality",),
        ("low_intent", "complex_task", "missing_capability"),
        ("no_action", "simplification", "cognitive_ease"),
        ("loss_frame", "timely_reminder", "just_in_time_intervention"),
        "high",
    ),
    "base_rate_fallacy": BehavioralHeuristic(
        "base_rate_fallacy",
        f"{TDL}/base-rate-fallacy",
        "too_much_information",
        ("base_rate_available", "case_specific_signal"),
        ("specific_story_overweights_base_rate",),
        ("true_segment_difference", "outlier_case", "data_quality_issue"),
        ("transparency_explanation",),
        ("social_proof",),
        "medium",
    ),
    "attentional_bias": BehavioralHeuristic(
        "attentional_bias",
        f"{TDL}/attentional-bias",
        "too_much_information",
        ("attention_signal", "ignored_relevant_information"),
        ("attention_clustered_on_subset",),
        ("layout_issue", "content_relevance", "device_context"),
        ("cognitive_ease", "simplification"),
        (),
        "low",
    ),
    "mere_exposure_effect": BehavioralHeuristic(
        "mere_exposure_effect",
        f"{TDL}/mere-exposure-effect",
        "too_much_information",
        ("exposure_count", "preference_shift"),
        ("repeated_exposure_increases_preference",),
        ("learning_effect", "campaign_effect", "selection_bias"),
        ("progress_feedback", "transparency_explanation"),
        (),
        "medium",
    ),
    "endowment_effect": BehavioralHeuristic(
        "endowment_effect",
        f"{TDL}/endowment-effect",
        "not_enough_meaning",
        ("ownership_signal", "reluctance_to_switch"),
        ("owned_option_overvalued",),
        ("switching_cost", "contract_lock_in", "habit"),
        ("progress_oriented_default", "transparency_explanation"),
        (),
        "medium",
    ),
    "regret_aversion": BehavioralHeuristic(
        "regret_aversion",
        f"{TDL}/regret-aversion",
        "need_to_act_fast",
        ("anticipated_regret_signal", "inaction_after_risk"),
        ("anticipated_regret_blocks_choice",),
        ("real_risk", "low_trust", "unclear_consequence"),
        ("transparency_explanation", "gain_frame"),
        ("loss_frame",),
        "high",
    ),
    "optimism_bias": BehavioralHeuristic(
        "optimism_bias",
        f"{TDL}/optimism-bias",
        "not_enough_meaning",
        ("risk_underestimation_signal", "missed_deadline_history"),
        ("future_success_overestimated",),
        ("low_capability", "external_dependency", "poor_estimate"),
        ("goal_setting", "progress_feedback"),
        (),
        "medium",
    ),
    "normalcy_bias": BehavioralHeuristic(
        "normalcy_bias",
        f"{TDL}/normalcy-bias",
        "not_enough_meaning",
        ("risk_alert_ignored", "status_quo_persistence"),
        ("warning_ignored_due_to_normal_expectation",),
        ("low_trust", "alert_fatigue", "irrelevant_alert"),
        ("transparency_explanation", "cognitive_ease"),
        ("loss_frame",),
        "high",
    ),
    "omission_bias": BehavioralHeuristic(
        "omission_bias",
        f"{TDL}/omission-bias",
        "need_to_act_fast",
        ("inaction_after_prompt", "action_cost_signal"),
        ("harm_from_inaction_overlooked",),
        ("low_intent", "missing_capability", "unclear_value"),
        ("commitment", "goal_setting", "transparency_explanation"),
        (),
        "medium",
    ),
    "wysiati": BehavioralHeuristic(
        "wysiati",
        CODEX,
        "not_enough_meaning",
        ("information_gap", "decision_with_limited_information"),
        ("visible_information_overweighted",),
        ("missing_data", "low_intent", "product_complexity"),
        ("transparency_explanation", "simplification", "cognitive_ease"),
        ("loss_frame",),
        "medium",
    ),
}


REFERENCE_ONLY_HEURISTICS = {
    "barnum_effect",
    "dunning_kruger_effect",
    "halo_effect",
    "fundamental_attribution_error",
    "just_world_hypothesis",
    "naive_realism",
    "self_serving_bias",
    "spotlight_effect",
    "illusion_of_transparency",
    "illusion_of_control",
    "illusion_of_validity",
    "hindsight_bias",
    "peak_end_rule",
    "source_confusion",
    "rosy_retrospection",
    "nostalgia_effect",
    "telescoping_effect",
    "serial_position_effect",
    "primacy_effect",
    "recency_effect",
    "google_effect",
    "ikea_effect",
    "benjamin_franklin_effect",
    "observer_expectancy_effect",
    "pygmalion_effect",
    "outcome_bias",
    "look_elsewhere_effect",
}


EXCLUDED_HEURISTICS = {
    "sexual_overperception_bias",
    "parasocial_trust_in_ai",
    "bye_now_effect",
    "cashless_effect",
    "bottom_dollar_effect",
    "scarcity_pressure",
    "deceptive_urgency",
}


def active_heuristics() -> list[str]:
    return list(ACTIVE_HEURISTICS)


def reference_only_heuristics() -> list[str]:
    return sorted(REFERENCE_ONLY_HEURISTICS)


def excluded_heuristics() -> list[str]:
    return sorted(EXCLUDED_HEURISTICS)


def get_heuristic(heuristic_id: str) -> BehavioralHeuristic | None:
    return ACTIVE_HEURISTICS.get(heuristic_id)


def evaluate_heuristic(heuristic_id: str, context: dict[str, Any]) -> HeuristicEvaluation:
    if heuristic_id in EXCLUDED_HEURISTICS:
        return HeuristicEvaluation(
            heuristic_id=heuristic_id,
            status="excluded",
            support_score=0.0,
            evidence_available=[],
            missing_signals=[],
            compatible_methods=[],
            blocked_methods=[],
            alternative_explanations=["governance_excluded"],
            governance_risk="critical",
            reason_codes=["excluded_governance_risk"],
            claim_type="blocked",
        )
    if heuristic_id in REFERENCE_ONLY_HEURISTICS:
        return HeuristicEvaluation(
            heuristic_id=heuristic_id,
            status="reference_only",
            support_score=0.0,
            evidence_available=[],
            missing_signals=[],
            compatible_methods=[],
            blocked_methods=[],
            alternative_explanations=["reference_only_not_operationalized"],
            governance_risk="unknown",
            reason_codes=["reference_only"],
            claim_type="hypothesis",
        )
    heuristic = get_heuristic(heuristic_id)
    if heuristic is None:
        return HeuristicEvaluation(
            heuristic_id=heuristic_id,
            status="excluded",
            support_score=0.0,
            evidence_available=[],
            missing_signals=[],
            compatible_methods=[],
            blocked_methods=[],
            alternative_explanations=["unknown_heuristic"],
            governance_risk="unknown",
            reason_codes=["unknown_heuristic"],
            claim_type="blocked",
        )

    evidence_available = [
        signal
        for signal in heuristic.required_signals
        if signal in context and context.get(signal) not in {None, "", False}
    ]
    missing_signals = sorted(set(heuristic.required_signals) - set(evidence_available))
    if missing_signals:
        return HeuristicEvaluation(
            heuristic_id=heuristic_id,
            status="not_testable_yet",
            support_score=0.0,
            evidence_available=evidence_available,
            missing_signals=missing_signals,
            compatible_methods=list(heuristic.compatible_methods),
            blocked_methods=list(heuristic.blocked_methods),
            alternative_explanations=list(heuristic.alternative_explanations),
            governance_risk=heuristic.governance_risk,
            reason_codes=[f"missing_signal:{signal}" for signal in missing_signals],
            claim_type="hypothesis",
        )

    support_score = heuristic_support_score(heuristic_id, context)
    contradicted = context.get(f"{heuristic_id}_contradicted") is True
    experimentally_validated = context.get(f"{heuristic_id}_experiment_validated") is True
    if contradicted:
        status: HeuristicStatus = "contradicted"
        reason_codes = ["heuristic_contradicted"]
    elif experimentally_validated:
        status = "validated_experimentally"
        reason_codes = ["experimentally_validated"]
    elif support_score >= 0.65:
        status = "moderate_support"
        reason_codes = ["moderate_heuristic_support"]
    else:
        status = "weak_support"
        reason_codes = ["weak_heuristic_support"]

    return HeuristicEvaluation(
        heuristic_id=heuristic_id,
        status=status,
        support_score=support_score,
        evidence_available=evidence_available,
        missing_signals=[],
        compatible_methods=list(heuristic.compatible_methods),
        blocked_methods=list(heuristic.blocked_methods),
        alternative_explanations=list(heuristic.alternative_explanations),
        governance_risk=heuristic.governance_risk,
        reason_codes=reason_codes,
        claim_type="hypothesis",
    )


def evaluate_heuristics(context: dict[str, Any]) -> list[HeuristicEvaluation]:
    return [evaluate_heuristic(heuristic_id, context) for heuristic_id in active_heuristics()]


def heuristic_support_score(heuristic_id: str, context: dict[str, Any]) -> float:
    value_map = {
        "availability_heuristic": _mean(context, ["recent_salient_event", "event_recency", "behavior_change_after_event"]),
        "present_bias": _mean(context, ["activation_gap", "delayed_benefit_signal"]),
        "hyperbolic_discounting": _mean(context, ["delayed_benefit_signal", "immediate_cost_signal"]),
        "status_quo_bias": _mean(context, ["default_available", "switching_cost_signal"]),
        "loss_aversion": _mean(context, ["loss_salience", "deadline_pressure"]),
        "framing_effect": _mean(context, ["message_frame", "frame_response_difference"]),
        "choice_overload": _mean(context, ["option_count", "dropoff_after_choice_set"]),
        "anchoring_bias": _mean(context, ["anchor_value", "subsequent_choice_shift"]),
        "social_norms": _mean(context, ["peer_norm_signal", "peer_reference_group_valid"]),
        "bandwagon_effect": _mean(context, ["peer_norm_signal", "adoption_trend_signal"]),
        "ambiguity_effect": _mean(context, ["uncertainty_signal", "information_gap"]),
        "planning_fallacy": _completion_gap(context),
        "confirmation_bias": _mean(context, ["belief_signal", "contradictory_information_ignored"]),
        "salience_bias": _mean(context, ["salient_feature_exposure", "behavior_change_after_exposure"]),
        "decision_fatigue": _mean(context, ["fatigue_signal", "decision_count"]),
        "base_rate_fallacy": _mean(context, ["base_rate_available", "case_specific_signal"]),
        "attentional_bias": _mean(context, ["attention_signal", "ignored_relevant_information"]),
        "mere_exposure_effect": _mean(context, ["exposure_count", "preference_shift"]),
        "endowment_effect": _mean(context, ["ownership_signal", "reluctance_to_switch"]),
        "regret_aversion": _mean(context, ["anticipated_regret_signal", "inaction_after_risk"]),
        "optimism_bias": _mean(context, ["risk_underestimation_signal", "missed_deadline_history"]),
        "normalcy_bias": _mean(context, ["risk_alert_ignored", "status_quo_persistence"]),
        "omission_bias": _mean(context, ["inaction_after_prompt", "action_cost_signal"]),
        "wysiati": _mean(context, ["information_gap", "decision_with_limited_information"]),
    }
    return round(max(0.0, min(1.0, value_map.get(heuristic_id, 0.0))), 4)


def heuristic_method_bonus(method: str, evaluations: list[HeuristicEvaluation]) -> float:
    bonus = 0.0
    for evaluation in evaluations:
        if evaluation.status not in {"weak_support", "moderate_support", "validated_experimentally"}:
            continue
        if method in evaluation.compatible_methods:
            bonus += 0.01 if evaluation.status == "weak_support" else 0.03
        if method in evaluation.blocked_methods:
            bonus -= 0.05
    return round(max(-0.08, min(0.08, bonus)), 4)


def correlation_support(
    signal: list[float],
    outcome: list[float],
    *,
    method: str = "pearson",
) -> dict[str, Any]:
    if len(signal) != len(outcome) or len(signal) < 3:
        return {
            "status": "not_testable_yet",
            "correlation": 0.0,
            "claim_type": "hypothesis",
            "reason": "correlation_requires_equal_vectors_with_at_least_three_rows",
        }
    if method not in {"pearson", "spearman", "phi"}:
        return {
            "status": "not_testable_yet",
            "correlation": 0.0,
            "claim_type": "hypothesis",
            "reason": "unsupported_correlation_method",
        }
    left = _rank(signal) if method == "spearman" else signal
    right = _rank(outcome) if method == "spearman" else outcome
    correlation = _pearson(left, right)
    status = "moderate_support" if abs(correlation) >= 0.3 else "weak_support"
    return {
        "status": status,
        "correlation": round(correlation, 4),
        "claim_type": "hypothesis",
        "causal_claim": False,
        "reason": "correlation_is_not_causation",
    }


def _mean(context: dict[str, Any], keys: list[str]) -> float:
    values = [_scale(context.get(key)) for key in keys]
    return sum(values) / len(values) if values else 0.0


def _scale(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if numeric > 1.0:
        return min(1.0, numeric / 10.0)
    return max(0.0, min(1.0, numeric))


def _completion_gap(context: dict[str, Any]) -> float:
    estimated = float(context.get("estimated_completion_time", 0.0) or 0.0)
    actual = float(context.get("actual_completion_time", 0.0) or 0.0)
    if estimated <= 0 or actual <= estimated:
        return 0.0
    return min(1.0, (actual - estimated) / max(actual, 1.0))


def _pearson(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_denominator = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_denominator = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    denominator = left_denominator * right_denominator
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _rank(values: list[float]) -> list[float]:
    order = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    for rank, (_, index) in enumerate(order, start=1):
        ranks[index] = float(rank)
    return ranks
