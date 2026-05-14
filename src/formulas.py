"""Formula registry and review metadata for the Nudge Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class FormulaDefinition:
    key: str
    name: str
    formula_class: str
    formula: str
    variables: list[str]
    assumptions: list[str]
    required_context: list[str] = field(default_factory=list)
    ci_required: bool = False
    default_confidence_level: float = 0.95
    exploratory_confidence_level: float = 0.90
    null_value: float = 0.0
    ci_method: Optional[str] = None
    required_review_agents: list[str] = field(default_factory=list)


FORMULA_REGISTRY: dict[str, FormulaDefinition] = {
    "cate": FormulaDefinition(
        key="cate",
        name="Conditional Average Treatment Effect",
        formula_class="causal",
        formula="tau_a(x) = E[Y_it^u(a) - Y_it^u(0) | X_it = x]",
        variables=["tau_a", "Y_it^u(a)", "Y_it^u(0)", "X_it"],
        assumptions=["identification_strategy", "positivity", "sutva", "control_condition"],
        required_context=["identification_strategy", "control_condition"],
        required_review_agents=["statistical", "data", "devils_advocate", "research"],
    ),
    "aggregation": FormulaDefinition(
        key="aggregation",
        name="Company Aggregations",
        formula_class="aggregation",
        formula="U_ct, F_ct, C_ct, E_ct over I_ct and Omega_ct",
        variables=["U_ct", "F_ct", "C_ct", "E_ct", "I_ct", "N_ct", "Omega_ct"],
        assumptions=["window_definition", "n_zero_rule", "snapshot_logic"],
        required_context=["Omega_ct", "N_ct", "n_zero_rule"],
        required_review_agents=["statistical", "data", "devils_advocate", "research"],
    ),
    "hr_burden": FormulaDefinition(
        key="hr_burden",
        name="HR Burden Index",
        formula_class="index",
        formula="H_ct = w_h1 * z(tickets_ct) + w_h2 * z(manual_tasks_ct) + w_h3 * z(escalations_ct)",
        variables=["H_ct", "tickets_ct", "manual_tasks_ct", "escalations_ct"],
        assumptions=["standardization", "weighting_rule"],
        required_context=["standardization"],
        required_review_agents=["statistical", "data", "devils_advocate", "research"],
    ),
    "justifiability": FormulaDefinition(
        key="justifiability",
        name="Justifiability Index",
        formula_class="index",
        formula="J_ct = w_j1 * U_ct + w_j2 * F_ct - w_j3 * C_ct - w_j4 * E_ct + w_j5 * R_ct_report",
        variables=["J_ct", "U_ct", "F_ct", "C_ct", "E_ct", "R_ct_report"],
        assumptions=["audited_report_score", "weighting_rule", "gaming_check"],
        required_context=["R_ct_report", "weighting_rule"],
        required_review_agents=["statistical", "data", "devils_advocate", "research"],
    ),
    "renewal": FormulaDefinition(
        key="renewal",
        name="Renewal Model",
        formula_class="outcome",
        formula="P(Renewal_ct = 1 | W_ct) = sigma(...)",
        variables=["Renewal_ct", "W_ct"],
        assumptions=["feature_lag", "calibration", "cluster_structure"],
        required_context=["W_ct", "feature_lag"],
        ci_required=True,
        ci_method="cluster_robust_or_bootstrap",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
    "nps": FormulaDefinition(
        key="nps",
        name="NPS Model",
        formula_class="outcome",
        formula="NPS_ct = alpha_0 + alpha^T W_ct + v_c + epsilon_ct",
        variables=["NPS_ct", "W_ct"],
        assumptions=["feature_lag", "bounded_outcome", "calibration"],
        required_context=["W_ct", "feature_lag"],
        ci_required=True,
        ci_method="cluster_robust_or_bootstrap",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
    "upsell": FormulaDefinition(
        key="upsell",
        name="Upsell Model",
        formula_class="outcome",
        formula="P(Upsell_ct = 1 | W_ct) = sigma(...)",
        variables=["Upsell_ct", "W_ct", "PriceNew_ct", "product_fit_ct"],
        assumptions=["feature_lag", "product_fit_definition", "calibration"],
        required_context=["W_ct", "PriceNew_ct", "product_fit_ct", "feature_lag"],
        ci_required=True,
        ci_method="cluster_robust_or_bootstrap",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
    "reward_policy": FormulaDefinition(
        key="reward_policy",
        name="Reward and Policy",
        formula_class="policy",
        formula="pi*(x) = argmax_{a in A} E[r_it(a) | X_it = x]",
        variables=["pi", "r_it(a)", "A", "X_it"],
        assumptions=["reward_calibration", "no_action_baseline", "guardrails"],
        required_context=["reward_calibrated", "no_action_baseline", "guardrails"],
        required_review_agents=["statistical", "data", "devils_advocate", "research", "governance"],
    ),
    "fairness": FormulaDefinition(
        key="fairness",
        name="Fairness Constraints",
        formula_class="constraint",
        formula="max_{g1,g2 in G} FairnessGap(a; g1, g2) <= B_F",
        variables=["FairnessGap", "G", "B_F", "A"],
        assumptions=["group_definition", "threshold_definition", "outcome_gap_check"],
        required_context=["G", "B_F"],
        required_review_agents=["statistical", "data", "devils_advocate", "research", "governance"],
    ),
    "ab_test": FormulaDefinition(
        key="ab_test",
        name="A/B Test Effect",
        formula_class="evaluation",
        formula="Delta_a = E[Y | A = a] - E[Y | A = 0]",
        variables=["Delta_a", "Y", "A"],
        assumptions=["randomization_or_identification", "same_window"],
        required_context=["treatment_group", "control_group"],
        ci_required=True,
        ci_method="standard_or_robust",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
    "cuped": FormulaDefinition(
        key="cuped",
        name="CUPED",
        formula_class="evaluation",
        formula="Y_CUPED = Y - theta * (X_pre - E[X_pre])",
        variables=["Y_CUPED", "Y", "theta", "X_pre"],
        assumptions=["pre_treatment_covariate", "covariate_predictive"],
        required_context=["X_pre"],
        ci_required=True,
        ci_method="standard_or_bootstrap",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
    "dr_ope": FormulaDefinition(
        key="dr_ope",
        name="Doubly Robust Off-Policy Evaluation",
        formula_class="evaluation",
        formula="V_hat_DR(pi) = (1/n) * sum_i [q_hat(X_i, pi(X_i)) + 1{A_i = pi(X_i)} / p_hat(A_i | X_i) * (Y_i - q_hat(X_i, A_i))]",
        variables=["V_hat_DR", "q_hat", "p_hat", "X_i", "A_i", "Y_i"],
        assumptions=["overlap", "propensity_clipping", "cross_fitting", "support_check"],
        required_context=["overlap_check", "propensity_clipping", "cross_fitting", "support_check"],
        ci_required=True,
        ci_method="bootstrap_or_crossfit",
        required_review_agents=["statistical", "data", "devils_advocate", "research", "evaluation"],
    ),
}


def get_formula_definition(context: dict[str, Any]) -> Optional[FormulaDefinition]:
    key = context.get("formula_key")
    if isinstance(key, str) and key in FORMULA_REGISTRY:
        return FORMULA_REGISTRY[key]

    formula_text = str(context.get("formula", "")).lower()
    for definition in FORMULA_REGISTRY.values():
        if definition.key in formula_text or definition.name.lower() in formula_text:
            return definition
    if "tau" in formula_text and "y^u" in formula_text:
        return FORMULA_REGISTRY["cate"]
    if "v_hat_dr" in formula_text or "p_hat" in formula_text:
        return FORMULA_REGISTRY["dr_ope"]
    if "cuped" in formula_text or "x_pre" in formula_text:
        return FORMULA_REGISTRY["cuped"]
    if "delta_a" in formula_text:
        return FORMULA_REGISTRY["ab_test"]
    if "fairnessgap" in formula_text:
        return FORMULA_REGISTRY["fairness"]
    if "pi*" in formula_text or "argmax" in formula_text or "r_it" in formula_text:
        return FORMULA_REGISTRY["reward_policy"]
    if "j_ct" in formula_text:
        return FORMULA_REGISTRY["justifiability"]
    if "h_ct" in formula_text:
        return FORMULA_REGISTRY["hr_burden"]
    if any(token in formula_text for token in ["u_ct", "f_ct", "c_ct", "e_ct"]):
        return FORMULA_REGISTRY["aggregation"]
    return None


def formula_context(context: dict[str, Any]) -> dict[str, Any]:
    definition = get_formula_definition(context)
    if definition is None:
        return dict(context)

    enriched = dict(context)
    enriched.setdefault("formula_key", definition.key)
    enriched.setdefault("formula_class", definition.formula_class)
    enriched.setdefault("formula", definition.formula)
    enriched.setdefault("variables", list(definition.variables))
    enriched.setdefault("formula_assumptions", list(definition.assumptions))
    enriched.setdefault("required_context", list(definition.required_context))
    enriched.setdefault("ci_required", definition.ci_required)
    enriched.setdefault("confidence_level", definition.default_confidence_level)
    enriched.setdefault("exploratory_confidence_level", definition.exploratory_confidence_level)
    enriched.setdefault("null_value", definition.null_value)
    if definition.ci_method:
        enriched.setdefault("ci_method", definition.ci_method)
    enriched.setdefault("required_review_agents", list(definition.required_review_agents))
    return enriched
