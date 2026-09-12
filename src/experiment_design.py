"""Evidence-aware experiment plans for hypotheses that cannot yet support effect claims."""

from __future__ import annotations

from typing import Any


DEFAULT_GUARDRAILS = [
    "consent_required",
    "opt_out_available",
    "frequency_cap",
    "fatigue_monitoring",
    "harm_monitoring",
    "no_action_baseline",
]


def build_experiment_design(
    *,
    data_readiness: dict[str, Any],
    context: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    uncertainty: dict[str, Any],
    confidence_level: float = 0.95,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a test plan or clarification request without inventing an effect."""

    config = dict(config or {})
    outcome = context.get("outcome_variable")
    missing_groups = set(data_readiness.get("missing_required_groups", []))
    available_columns = set(data_readiness.get("available_columns", []))
    if not outcome or "outcome" in missing_groups or (available_columns and outcome not in available_columns):
        return {
            "status": "clarification_required",
            "experiment_required": False,
            "blocked_reason": "outcome_variable_missing",
            "clarification_questions": ["Welche Aktivierungs-Zielvariable soll im Experiment gemessen werden?"],
            "claim_permission": "No effect, significance or causal claim is allowed.",
        }

    ci_complete = all(
        field in uncertainty
        for field in ["effect_estimate", "ci_lower", "ci_upper", "confidence_level", "contains_null"]
    )
    stable_effect = (
        ci_complete
        and uncertainty.get("contains_null") is False
        and float(uncertainty.get("confidence_level", 0.0)) >= 0.95
    )
    requires_experiment = data_readiness.get("status") == "experiment_required" or not stable_effect
    if not requires_experiment:
        return {
            "status": "not_required",
            "experiment_required": False,
            "claim_permission": "Existing evidence passed the configured interval gate; governance review still applies.",
        }

    method = _recommended_method(config)
    primary = _primary_hypothesis(hypotheses)
    treatment_field = _first_detected(data_readiness, "treatment")
    measurement_window = config.get("measurement_window")
    open_assumptions = [
        "Randomization integrity and treatment contamination must be checked.",
        "Sample size and power must be calculated before enrollment.",
    ]
    blockers = []
    if not treatment_field:
        blockers.append("treatment_assignment_missing")
    if not measurement_window:
        blockers.append("measurement_window_requires_domain_input")
    if method == "cuped" and not config.get("pre_period_covariate"):
        blockers.append("cuped_pre_period_covariate_missing")

    return {
        "status": "experiment_required",
        "experiment_required": True,
        "hypothesis": primary,
        "outcome_variable": outcome,
        "treatment": {
            "field": treatment_field,
            "condition": config.get("treatment_condition", "treatment"),
        },
        "control_condition": config.get("control_condition", "control_or_no_action"),
        "primary_metric": config.get("primary_metric", outcome),
        "guardrails": list(config.get("experiment_guardrails", DEFAULT_GUARDRAILS)),
        "measurement_window": measurement_window or "clarification_required",
        "required_data": sorted(
            set(["subject_id", "event_time", outcome, "consent", treatment_field or "treatment_assignment"])
        ),
        "recommended_method": method,
        "confidence_level": max(0.95, float(confidence_level)),
        "open_assumptions": open_assumptions,
        "blockers": blockers,
        "claim_permission": "This is a measurement plan, not evidence that the intervention works.",
    }


def _recommended_method(config: dict[str, Any]) -> str:
    if config.get("pre_period_covariate"):
        return "cuped"
    if config.get("existing_rollout") or config.get("holdout_available"):
        return "holdout"
    return "ab_test"


def _primary_hypothesis(hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    for hypothesis in hypotheses:
        if hypothesis.get("status") == "testable":
            return {
                "id": hypothesis.get("id"),
                "statement": hypothesis.get("statement"),
                "status": hypothesis.get("status"),
            }
    return {
        "id": None,
        "statement": "The intervention may change the configured outcome relative to no action.",
        "status": "hypothesis",
    }


def _first_detected(data_readiness: dict[str, Any], group: str) -> str | None:
    detected = data_readiness.get("detected_groups", {}).get(group, [])
    return str(detected[0]) if detected else None
