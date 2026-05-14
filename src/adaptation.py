"""Synthetic adaptation test helpers for the Nudge Engine."""

from __future__ import annotations

import random
from typing import Any

from .behavioral_methods import action_methods
from .ocean import build_ocean_signal
from .reward import REQUIRED_GUARDRAILS, policy_decision_for_person


NUDGE_METHODS = set(action_methods())


def clamp(value: float, *, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def determine_nudge_candidate(person: dict[str, Any]) -> dict[str, Any]:
    """Select a guarded candidate nudge from measured context.

    This is intentionally conservative: it produces a candidate for testing,
    not a final policy decision.
    """
    if person.get("consent") is not True:
        return _nudge_result("no_action", "blocked", "missing_consent")
    if person.get("vulnerability_flag") is True:
        return _nudge_result("no_action", "blocked", "protected_state")
    if float(person.get("fatigue_signal", 0.0)) >= 0.75:
        return _nudge_result("no_action", "hold", "high_fatigue")

    friction = float(person.get("friction_signal", 0.0))
    resistance = float(person.get("resistance_signal", 0.0))
    trust_gap = float(person.get("trust_gap_signal", 0.0))
    peer_norm = float(person.get("peer_norm_signal", 0.0))
    deadline = float(person.get("deadline_pressure", 0.0))
    activation_gap = float(person.get("activation_gap", 0.0))

    if friction >= 0.62 or resistance >= 0.72:
        return _nudge_result("cognitive_ease", "hypothesis", "reduce_friction_or_resistance")
    if trust_gap >= 0.67:
        return _nudge_result("reciprocity", "hypothesis", "trust_gap")
    if peer_norm >= 0.68:
        return _nudge_result("social_proof", "hypothesis", "peer_norm_available")
    if deadline >= 0.72 and float(person.get("fatigue_signal", 0.0)) < 0.55:
        return _nudge_result("timely_reminder", "hypothesis", "deadline_pressure")
    if activation_gap >= 0.62:
        return _nudge_result("commitment", "hypothesis", "follow_through_gap")
    return _nudge_result("gain_frame", "hypothesis", "low_risk_positive_framing")


def _nudge_result(method: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "method": method,
        "status": status,
        "reason": reason,
        "claim_type": "hypothesis" if method != "no_action" else "blocked",
    }


def generate_100_person_adaptation_sample(seed: int = 41) -> list[dict[str, Any]]:
    """Create a deterministic 100-person sample with non-rational patterns."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for index in range(100):
        user_id = f"u{index + 1:03d}"
        consent = index % 17 != 0
        vulnerability = index % 29 == 0
        experiment_group = "control" if index % 2 == 0 else "treatment"

        # TIPI responses are deliberately noisy and not perfectly aligned with behavior.
        tipi = {
            f"tipi_{item}": rng.randint(2, 6)
            for item in range(1, 11)
        }
        if index % 10 == 0:
            tipi["tipi_5"] = 7
            tipi["tipi_10"] = 1
        if index % 13 == 0:
            tipi["tipi_5"] = 2
            tipi["tipi_10"] = 6

        openness_proxy = clamp((float(tipi["tipi_5"]) + (8.0 - float(tipi["tipi_10"]))) / 14.0)
        fatigue = clamp(rng.random() * 0.75 + (0.25 if index % 11 == 0 else 0.0))
        resistance = clamp(rng.random() * 0.65 + (0.30 if index % 10 == 0 else 0.0))
        friction = clamp(rng.random() * 0.85)
        trust_gap = clamp(rng.random() * 0.80)
        peer_norm = clamp(rng.random() * 0.90)
        deadline = clamp(rng.random() * 0.95)
        activation_gap = clamp(rng.random() * 0.90)

        person = {
            "user_id": user_id,
            "company_id": f"c{1 + (index % 8):02d}",
            "event_time": f"2026-05-{1 + (index % 28):02d}T09:00:00Z",
            "experiment_group": experiment_group,
            "consent": consent,
            "vulnerability_flag": vulnerability,
            "fatigue_signal": round(fatigue, 3),
            "resistance_signal": round(resistance, 3),
            "friction_signal": round(friction, 3),
            "trust_gap_signal": round(trust_gap, 3),
            "peer_norm_signal": round(peer_norm, 3),
            "deadline_pressure": round(deadline, 3),
            "activation_gap": round(activation_gap, 3),
            "openness_proxy": round(openness_proxy, 3),
            "default_available": index % 7 == 0,
            "goal_feasibility_known": activation_gap >= 0.45,
            "peer_reference_group_valid": peer_norm >= 0.68,
            "trigger_event_available": deadline >= 0.72,
            **tipi,
        }
        candidate = determine_nudge_candidate(person)
        if experiment_group == "control" and candidate["method"] != "no_action":
            candidate = _nudge_result("no_action", "control", "control_group")

        method_effect = {
            "no_action": 0.0,
            "cognitive_ease": 0.24,
            "social_proof": 0.15,
            "gain_frame": 0.12,
            "loss_frame": 0.04,
            "commitment": 0.17,
            "reciprocity": 0.14,
            "timely_reminder": 0.11,
            "progress_feedback": 0.13,
        }[candidate["method"]]
        noise = rng.gauss(0.0, 0.08)
        activation_score = clamp(
            0.44
            + method_effect
            - 0.12 * fatigue
            - 0.08 * resistance
            + 0.04 * openness_proxy
            + noise
        )
        clicked_nudge = experiment_group == "treatment" and rng.random() < activation_score
        renewed = rng.random() < clamp(activation_score + 0.08)

        person.update(
            {
                "recommended_nudge": candidate["method"],
                "nudge_status": candidate["status"],
                "nudge_reason": candidate["reason"],
                "clicked_nudge": clicked_nudge,
                "renewed": renewed,
                "activation_score": round(activation_score, 4),
                "baseline_activation_score": round(0.44 - 0.05 * fatigue + noise / 2.0, 4),
                "guardrails": sorted(REQUIRED_GUARDRAILS),
                "reward_calibrated": True,
                "no_action_baseline": {
                    "baseline_action": "no_action",
                    "sample_size": 100,
                    "mean_outcome": 0.42,
                    "ci_lower": 0.35,
                    "ci_upper": 0.49,
                    "confidence_level": 0.95,
                    "monitoring_required": True,
                },
            }
        )
        if consent:
            person["ocean_signal"] = build_ocean_signal(tipi, consent=True)
        else:
            person["ocean_signal"] = build_ocean_signal(tipi, consent=False)
        policy_decision = policy_decision_for_person(person)
        person["policy_ranking"] = policy_decision["ranking"]
        person["policy_decision"] = policy_decision
        person["reward_result"] = policy_decision["selected_result"]
        rows.append(person)
    return rows


def split_activation_scores(rows: list[dict[str, Any]]) -> tuple[list[float], list[float]]:
    treatment = [
        float(row["activation_score"])
        for row in rows
        if row["experiment_group"] == "treatment"
    ]
    control = [
        float(row["activation_score"])
        for row in rows
        if row["experiment_group"] == "control"
    ]
    return treatment, control
