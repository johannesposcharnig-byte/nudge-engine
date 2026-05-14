"""Hypothesis and evidence helpers for the Nudge Engine."""

from __future__ import annotations

from typing import Any


MECE_HYPOTHESIS_GROUPS = [
    "data_quality",
    "target_behavior",
    "behavioral_mechanism",
    "effect",
    "segment_heterogeneity",
    "reward_policy",
    "governance_risk",
]


def _available(context: dict[str, Any], keys: list[str]) -> list[str]:
    return [key for key in keys if context.get(key)]


def infer_customer_data_profile(context: dict[str, Any]) -> dict[str, Any]:
    columns = list(context.get("available_columns", []))
    lower_columns = {str(column).lower(): column for column in columns}

    def detect(*tokens: str) -> list[str]:
        return [
            original
            for lower, original in lower_columns.items()
            if any(token in lower for token in tokens)
        ]

    time_fields = list(context.get("time_fields", [])) or detect("time", "date", "created", "updated")
    entity_fields = list(context.get("entity_fields", [])) or detect("user", "customer", "company", "account")
    outcome_candidates = list(context.get("outcome_candidates", [])) or detect(
        "churn",
        "renewal",
        "conversion",
        "nps",
        "upsell",
        "outcome",
    )
    treatment_candidates = list(context.get("treatment_candidates", [])) or detect(
        "treatment",
        "intervention",
        "nudge",
        "variant",
        "action",
    )
    psychological_fields = list(context.get("psychological_fields", [])) or detect(
        "tipi_",
        "ocean",
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
        "personality",
        "psychological",
    )

    return {
        "available_columns": columns,
        "time_fields": time_fields,
        "entity_fields": entity_fields,
        "outcome_candidates": outcome_candidates,
        "treatment_candidates": treatment_candidates,
        "psychological_fields": psychological_fields,
    }


def customer_data_missing_fields(context: dict[str, Any]) -> list[str]:
    profile = context.get("customer_data_profile") or infer_customer_data_profile(context)
    missing = []
    if not profile.get("available_columns"):
        missing.append("available_columns")
    if not profile.get("entity_fields"):
        missing.append("entity_fields")
    if not profile.get("time_fields"):
        missing.append("time_fields")
    if not (context.get("outcome_variable") or profile.get("outcome_candidates")):
        missing.append("outcome_variable")
    if context.get("requires_causal_claim") and not (
        context.get("identification_strategy")
        or context.get("treatment_group")
        or profile.get("treatment_candidates")
    ):
        missing.append("treatment_or_identification")
    return missing


def clarification_questions_for_missing(missing: list[str]) -> list[str]:
    questions = {
        "available_columns": "Welche Spalten und Datenquellen liegen fuer diesen Kunden vor?",
        "entity_fields": "Welche ID identifiziert User, Kunde, Company oder Account eindeutig?",
        "time_fields": "Welches Feld definiert die zeitliche Reihenfolge der Events?",
        "outcome_variable": "Welche Zielvariable soll optimiert oder erklaert werden?",
        "treatment_or_identification": "Gibt es Treatment, Kontrollgruppe, Randomisierung oder eine andere Identifikationsstrategie?",
    }
    return [questions[key] for key in missing if key in questions]


def build_mece_hypotheses(context: dict[str, Any]) -> list[dict[str, Any]]:
    profile = context.get("customer_data_profile") or infer_customer_data_profile(context)
    enriched = {**context, "customer_data_profile": profile}
    specs = [
        (
            "H1",
            "Die Kundendaten sind vollstaendig genug, um Analyse und Calculation zu starten.",
            "data_quality",
            ["available_columns", "entity_fields", "time_fields"],
            "schema_and_missingness_check",
        ),
        (
            "H2",
            "Das Zielverhalten oder Outcome ist eindeutig operationalisiert.",
            "target_behavior",
            ["outcome_variable"],
            "outcome_definition_check",
        ),
        (
            "H3",
            "Der vermutete Behavioral Mechanism passt zum Zielverhalten und Kontext.",
            "behavioral_mechanism",
            ["behavioral_method", "target_behavior"],
            "behavioral_science_review",
        ),
        (
            "H4",
            "Ein beobachteter Effekt kann mit Treatment, Vergleich und Unsicherheit geprueft werden.",
            "effect",
            ["treatment_group", "control_group", "outcome_variable", "uncertainty"],
            "ab_cuped_cate_or_ci_check",
        ),
        (
            "H5",
            "Segmente oder Archetypen sind datenbasiert unterscheidbar.",
            "segment_heterogeneity",
            ["segment_fields"],
            "segment_support_check",
        ),
        (
            "H6",
            "Reward und Policy sind kalibriert und haben No-Action plus Guardrails.",
            "reward_policy",
            ["reward_calibrated", "no_action_baseline", "guardrails"],
            "policy_reward_check",
        ),
        (
            "H7",
            "Governance-Risiken sind bekannt, begrenzt und freigabefaehig.",
            "governance_risk",
            ["consent_field", "governance_review"],
            "governance_risk_check",
        ),
    ]

    hypotheses = []
    for hypothesis_id, statement, group, required_data, test_method in specs:
        evidence = _available(enriched, required_data)
        if group == "data_quality":
            evidence = []
            if profile.get("available_columns"):
                evidence.append("available_columns")
            if profile.get("entity_fields"):
                evidence.append("entity_fields")
            if profile.get("time_fields"):
                evidence.append("time_fields")
        if group == "target_behavior" and profile.get("outcome_candidates"):
            evidence.append("outcome_candidates")
        if group == "effect" and profile.get("treatment_candidates"):
            evidence.append("treatment_candidates")
        if group == "behavioral_mechanism" and (
            profile.get("psychological_fields")
            or enriched.get("ocean_scores")
            or enriched.get("ocean_signal")
            or enriched.get("tipi_responses")
            or enriched.get("psychological_signal")
        ):
            evidence.append("psychological_signal")
        if group == "segment_heterogeneity" and profile.get("psychological_fields"):
            evidence.append("psychological_fields")

        status = "testable" if evidence else "not_testable_yet"
        hypotheses.append(
            {
                "id": hypothesis_id,
                "statement": statement,
                "category": group,
                "mece_group": group,
                "required_data": required_data,
                "test_method": test_method,
                "status": status,
                "evidence": sorted(set(evidence)),
                "decision_impact": "blocks approval" if status != "testable" else "can inform next gate",
            }
        )
    return hypotheses


def mece_groups_complete(hypotheses: list[dict[str, Any]]) -> bool:
    return sorted({item.get("mece_group") for item in hypotheses}) == sorted(MECE_HYPOTHESIS_GROUPS)
