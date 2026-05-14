"""Data contracts and readiness scoring for pilot analysis runs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
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
    causal_ready = bool(detected.get("treatment"))
    required_score = (len(ACTIVATION_REQUIRED_FIELDS) - len(missing)) / len(ACTIVATION_REQUIRED_FIELDS)
    optional_score = min(1.0, sum(1 for group in ACTIVATION_OPTIONAL_FIELDS if detected.get(group)) / 3.0)
    penalty = 0.25 if prohibited else 0.0
    score = max(0.0, min(1.0, round(required_score * 0.75 + optional_score * 0.25 - penalty, 3)))

    if prohibited:
        status = "reject"
    elif missing:
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
    )
