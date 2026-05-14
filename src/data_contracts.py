"""Data contracts and readiness scoring for pilot analysis runs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from datetime import datetime
from typing import Any


ACTIVATION_REQUIRED_FIELDS = {
    "identity": ("subject_id", "user_id", "customer_id", "account_id", "company_id"),
    "timestamp": ("event_time", "timestamp", "created_at", "date"),
    "outcome": ("activation_score", "activated", "conversion", "converted", "outcome"),
    "consent": ("consent", "user_consent", "marketing_consent"),
}

ACTIVATION_OPTIONAL_FIELDS = {
    "treatment": ("experiment_group", "treatment_group", "nudge_variant", "variant"),
    "fatigue": ("fatigue_signal",),
    "friction": ("friction_signal",),
    "resistance": ("resistance_signal",),
    "trust": ("trust_gap_signal",),
    "peer_norm": ("peer_norm_signal", "peer_reference_group_valid"),
}

PROHIBITED_FIELD_HINTS = (
    "email",
    "phone",
    "full_name",
    "customer_name",
    "address",
    "post_treatment",
    "post_nudge",
    "future_",
    "after_treatment",
    "after_nudge",
    "label",
    "target",
)


@dataclass(frozen=True)
class DataReadiness:
    use_case: str
    status: str
    score: float
    schema_hash: str
    available_columns: list[str]
    missing_required_groups: list[str]
    detected_groups: dict[str, list[str]]
    prohibited_fields: list[str]
    clarification_questions: list[str]
    causal_ready: bool
    row_count: int
    field_profiles: list[dict[str, Any]]
    treatment_balance: dict[str, int]
    outcome_profile: dict[str, Any]
    readiness_warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "use_case": self.use_case,
            "status": self.status,
            "score": self.score,
            "schema_hash": self.schema_hash,
            "available_columns": list(self.available_columns),
            "missing_required_groups": list(self.missing_required_groups),
            "detected_groups": {key: list(value) for key, value in self.detected_groups.items()},
            "prohibited_fields": list(self.prohibited_fields),
            "clarification_questions": list(self.clarification_questions),
            "causal_ready": self.causal_ready,
            "row_count": self.row_count,
            "field_profiles": [dict(profile) for profile in self.field_profiles],
            "treatment_balance": dict(self.treatment_balance),
            "outcome_profile": dict(self.outcome_profile),
            "readiness_warnings": list(self.readiness_warnings),
        }


def schema_hash(columns: list[str]) -> str:
    canonical = "|".join(sorted(str(column).lower() for column in columns))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def columns_from_rows(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    columns: list[str] = []
    for row in rows:
        for column in row:
            if column not in seen:
                seen.add(str(column))
                columns.append(str(column))
    return columns


def _non_empty_values(rows: list[dict[str, Any]], column: str) -> list[Any]:
    values = []
    for row in rows:
        value = row.get(column)
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        values.append(value)
    return values


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True


def _is_timestamp(value: Any) -> bool:
    if isinstance(value, (int, float)):
        return True
    if not isinstance(value, str):
        return False
    candidate = value.strip()
    if not candidate:
        return False
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _infer_field_type(values: list[Any]) -> str:
    if not values:
        return "empty"
    if all(isinstance(value, bool) for value in values):
        return "boolean"
    if all(_is_number(value) for value in values):
        return "numeric"
    if all(_is_timestamp(value) for value in values):
        return "timestamp"
    if all(isinstance(value, str) for value in values):
        return "string"
    return "mixed"


def _field_profiles(rows: list[dict[str, Any]], columns: list[str]) -> list[dict[str, Any]]:
    row_count = len(rows)
    profiles = []
    for column in columns:
        values = _non_empty_values(rows, column)
        missing_count = row_count - len(values)
        profiles.append(
            {
                "field": column,
                "inferred_type": _infer_field_type(values),
                "missing_count": missing_count,
                "missing_ratio": round(missing_count / row_count, 3) if row_count else 1.0,
                "unique_count": len({str(value) for value in values}),
            }
        )
    return profiles


def _first_detected(detected: dict[str, list[str]], group: str) -> str | None:
    fields = detected.get(group, [])
    return fields[0] if fields else None


def _treatment_balance(rows: list[dict[str, Any]], treatment_field: str | None) -> dict[str, int]:
    if not treatment_field:
        return {}
    balance: dict[str, int] = {}
    for row in rows:
        value = row.get(treatment_field)
        if value in {None, ""}:
            continue
        key = str(value).strip().lower()
        balance[key] = balance.get(key, 0) + 1
    return balance


def _has_treatment_and_control(balance: dict[str, int]) -> bool:
    if not balance:
        return False
    keys = set(balance)
    has_treatment = bool(keys & {"treatment", "treated", "variant", "nudge", "test", "b"})
    has_control = bool(keys & {"control", "holdout", "baseline", "no_action", "a"})
    if has_treatment and has_control:
        return True
    return len([count for count in balance.values() if count > 0]) >= 2


def _outcome_profile(rows: list[dict[str, Any]], outcome_field: str | None) -> dict[str, Any]:
    if not outcome_field:
        return {}
    values = _non_empty_values(rows, outcome_field)
    numeric_values = [float(value) for value in values if _is_number(value)]
    unique_values = sorted({str(value).lower() for value in values})
    profile: dict[str, Any] = {
        "field": outcome_field,
        "non_empty_count": len(values),
        "numeric_count": len(numeric_values),
        "unique_count": len(unique_values),
        "binary_like": set(unique_values).issubset({"0", "1", "false", "true", "no", "yes"}),
    }
    if numeric_values:
        profile["min"] = min(numeric_values)
        profile["max"] = max(numeric_values)
    return profile


def _readiness_warnings(
    *,
    rows: list[dict[str, Any]],
    detected: dict[str, list[str]],
    field_profiles: list[dict[str, Any]],
    treatment_balance: dict[str, int],
    outcome_profile: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if not rows:
        warnings.append("no_rows")
    if len(rows) < 30:
        warnings.append("small_sample_under_30")
    if len(rows) < 100:
        warnings.append("pilot_sample_under_100")
    for profile in field_profiles:
        if float(profile["missing_ratio"]) >= 0.2:
            warnings.append(f"high_missingness:{profile['field']}")
    timestamp_field = _first_detected(detected, "timestamp")
    if timestamp_field:
        timestamp_values = _non_empty_values(rows, timestamp_field)
        invalid_timestamp_count = sum(1 for value in timestamp_values if not _is_timestamp(value))
        if invalid_timestamp_count:
            warnings.append(f"invalid_timestamp_values:{timestamp_field}:{invalid_timestamp_count}")
    if treatment_balance and not _has_treatment_and_control(treatment_balance):
        warnings.append("treatment_without_usable_control")
    if outcome_profile and outcome_profile.get("non_empty_count", 0) == 0:
        warnings.append("outcome_empty")
    if outcome_profile and not outcome_profile.get("binary_like") and outcome_profile.get("numeric_count") == 0:
        warnings.append("outcome_not_numeric_or_binary")
    return sorted(set(warnings))


def evaluate_activation_data_contract(rows: list[dict[str, Any]]) -> DataReadiness:
    columns = columns_from_rows(rows)
    lower_to_original = {column.lower(): column for column in columns}
    detected: dict[str, list[str]] = {}
    missing: list[str] = []

    for group, candidates in ACTIVATION_REQUIRED_FIELDS.items():
        found = [lower_to_original[candidate] for candidate in candidates if candidate in lower_to_original]
        detected[group] = found
        if not found:
            missing.append(group)

    for group, candidates in ACTIVATION_OPTIONAL_FIELDS.items():
        detected[group] = [lower_to_original[candidate] for candidate in candidates if candidate in lower_to_original]

    prohibited = [
        column
        for column in columns
        if any(hint == column.lower() or hint in column.lower() for hint in PROHIBITED_FIELD_HINTS)
        and column.lower() not in {"target_behavior"}
    ]
    profiles = _field_profiles(rows, columns)
    treatment_field = _first_detected(detected, "treatment")
    balance = _treatment_balance(rows, treatment_field)
    causal_ready = _has_treatment_and_control(balance)
    outcome = _outcome_profile(rows, _first_detected(detected, "outcome"))
    warnings = _readiness_warnings(
        rows=rows,
        detected=detected,
        field_profiles=profiles,
        treatment_balance=balance,
        outcome_profile=outcome,
    )
    required_score = (len(ACTIVATION_REQUIRED_FIELDS) - len(missing)) / len(ACTIVATION_REQUIRED_FIELDS)
    optional_score = min(1.0, sum(1 for group in ACTIVATION_OPTIONAL_FIELDS if detected.get(group)) / 3.0)
    penalty = 0.25 if prohibited else 0.0
    score = max(0.0, min(1.0, round(required_score * 0.75 + optional_score * 0.25 - penalty, 3)))

    if prohibited:
        status = "reject"
    elif missing:
        status = "hold"
    elif "outcome_empty" in warnings or any(warning.startswith("invalid_timestamp_values") for warning in warnings):
        status = "hold"
    elif not causal_ready:
        status = "experiment_required"
    else:
        status = "ready"

    questions = []
    if "identity" in missing:
        questions.append("Welches Feld identifiziert User, Kunde, Company oder Account eindeutig?")
    if "timestamp" in missing:
        questions.append("Welches Feld definiert die zeitliche Reihenfolge der Events?")
    if "outcome" in missing:
        questions.append("Welche Aktivierungs-Zielvariable soll analysiert werden?")
    if "consent" in missing:
        questions.append("Welches Feld dokumentiert Consent fuer Analyse und Nudges?")
    if not causal_ready:
        questions.append("Gibt es Treatment, Kontrollgruppe, Variant oder eine andere Identifikationsstrategie?")
    if treatment_field and not causal_ready:
        questions.append("Wie sind Treatment und Kontrollgruppe im Experiment-/Variant-Feld codiert?")
    if any(warning.startswith("invalid_timestamp_values") for warning in warnings):
        questions.append("Bitte korrigiere ungueltige Zeitwerte, bevor zeitliche Effekte oder Leakage geprueft werden.")
    if "outcome_empty" in warnings:
        questions.append("Bitte liefere nicht-leere Outcome-Werte fuer die Aktivierungsanalyse.")
    if prohibited:
        questions.append("Bitte entferne PII, post-treatment Felder, Labels oder Leakage-Felder aus den Analytics-Daten.")

    return DataReadiness(
        use_case="activation",
        status=status,
        score=score,
        schema_hash=schema_hash(columns),
        available_columns=columns,
        missing_required_groups=missing,
        detected_groups=detected,
        prohibited_fields=prohibited,
        clarification_questions=questions,
        causal_ready=causal_ready,
        row_count=len(rows),
        field_profiles=profiles,
        treatment_balance=balance,
        outcome_profile=outcome,
        readiness_warnings=warnings,
    )
