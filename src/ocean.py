"""OCEAN / Big Five signal helpers based on the TIPI instrument.

The Ten-Item Personality Inventory is useful as a brief self-report signal.
It is intentionally treated as low-precision and hypothesis-only here; it must
not be used as a standalone basis for policy approval or behavioral claims.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TIPI_ITEM_KEYS = tuple(f"tipi_{index}" for index in range(1, 11))
OCEAN_TRAITS = (
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
)
TIPI_REVERSE_ITEMS = {2, 4, 6, 8, 10}


@dataclass(frozen=True)
class OceanScores:
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    emotional_stability: float
    instrument: str = "TIPI"
    source: str = "self_report"
    precision: str = "low_precision"
    hypothesis_only: bool = True
    consent: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def reverse_score(value: float) -> float:
    """Reverse a 1-7 Likert score."""
    _validate_item_value(value)
    return 8.0 - float(value)


def _validate_item_value(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("TIPI items must be numeric values from 1 to 7.") from exc
    if numeric < 1 or numeric > 7:
        raise ValueError("TIPI items must be in the inclusive range 1..7.")
    return numeric


def normalize_tipi_responses(responses: dict[str | int, Any]) -> dict[int, float]:
    """Return TIPI responses keyed by item number 1..10."""
    normalized: dict[int, float] = {}
    for index in range(1, 11):
        candidates = (index, str(index), f"tipi_{index}", f"TIPI_{index}")
        found = next((key for key in candidates if key in responses), None)
        if found is None:
            raise ValueError(f"Missing TIPI item {index}.")
        normalized[index] = _validate_item_value(responses[found])
    return normalized


def score_tipi(
    responses: dict[str | int, Any],
    *,
    consent: bool,
    source: str = "self_report",
) -> OceanScores:
    """Score TIPI into Big Five traits.

    Consent is required because the result is a psychological signal. Without
    consent the caller must not compute or use trait scores.
    """
    if consent is not True:
        raise PermissionError("OCEAN/TIPI scoring requires explicit user consent.")

    items = normalize_tipi_responses(responses)
    extraversion = (items[1] + reverse_score(items[6])) / 2.0
    agreeableness = (reverse_score(items[2]) + items[7]) / 2.0
    conscientiousness = (items[3] + reverse_score(items[8])) / 2.0
    emotional_stability = (reverse_score(items[4]) + items[9]) / 2.0
    openness = (items[5] + reverse_score(items[10])) / 2.0
    neuroticism = 8.0 - emotional_stability

    return OceanScores(
        openness=round(openness, 3),
        conscientiousness=round(conscientiousness, 3),
        extraversion=round(extraversion, 3),
        agreeableness=round(agreeableness, 3),
        neuroticism=round(neuroticism, 3),
        emotional_stability=round(emotional_stability, 3),
        source=source,
        consent=consent,
    )


def build_ocean_signal(
    responses: dict[str | int, Any],
    *,
    consent: bool,
    source: str = "self_report",
) -> dict[str, Any]:
    """Build a governance-safe psychological signal payload."""
    base = {
        "instrument": "TIPI",
        "source": source,
        "precision": "low_precision",
        "hypothesis_only": True,
        "usable_for_personalization": False,
        "allowed_claim_type": "hypothesis",
    }
    if consent is not True:
        return {
            **base,
            "consent": False,
            "blocked_reason": "ocean_consent_required",
            "scores": None,
        }

    scores = score_tipi(responses, consent=True, source=source)
    return {
        **base,
        "consent": True,
        "usable_for_personalization": True,
        "scores": scores.as_dict(),
        "blocked_reason": None,
    }


def ocean_context_requires_hold(context: dict[str, Any]) -> str | None:
    """Return a hold reason when OCEAN context is unsafe for decisions."""
    has_ocean_signal = any(
        context.get(key)
        for key in [
            "ocean_scores",
            "ocean_signal",
            "tipi_responses",
            "psychological_signal",
            "uses_ocean_for_personalization",
        ]
    )
    if not has_ocean_signal:
        return None
    if context.get("ocean_consent") is not True:
        return "ocean_consent_required"
    if context.get("ocean_only_decision"):
        return "ocean_cannot_be_standalone_decision_basis"
    return None
