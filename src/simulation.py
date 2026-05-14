"""Small simulation and confidence-interval helpers for acceptance tests."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from statistics import NormalDist
from typing import Any


@dataclass(frozen=True)
class EffectInterval:
    effect_estimate: float
    ci_lower: float
    ci_upper: float
    ci_method: str
    sample_size: int
    confidence_level: float

    @property
    def contains_null(self) -> bool:
        return self.ci_lower <= 0.0 <= self.ci_upper

    def as_uncertainty(self) -> dict[str, Any]:
        return {
            "effect_estimate": self.effect_estimate,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "ci_method": self.ci_method,
            "sample_size": self.sample_size,
            "confidence_level": self.confidence_level,
            "contains_null": self.contains_null,
        }


def simulate_ab_outcomes(
    *,
    sample_size: int = 200,
    treatment_effect: float = 0.5,
    baseline: float = 1.0,
    noise_sd: float = 1.0,
    seed: int = 7,
) -> tuple[list[float], list[float]]:
    rng = random.Random(seed)
    control = [rng.gauss(baseline, noise_sd) for _ in range(sample_size // 2)]
    treatment = [rng.gauss(baseline + treatment_effect, noise_sd) for _ in range(sample_size - len(control))]
    return treatment, control


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    value_mean = mean(values)
    return sum((value - value_mean) ** 2 for value in values) / (len(values) - 1)


def ab_mean_difference_ci(
    treatment: list[float],
    control: list[float],
    *,
    confidence_level: float = 0.95,
) -> EffectInterval:
    if not treatment or not control:
        raise ValueError("Treatment and control samples must be non-empty.")

    estimate = mean(treatment) - mean(control)
    se = math.sqrt(sample_variance(treatment) / len(treatment) + sample_variance(control) / len(control))
    alpha = 1.0 - confidence_level
    z_value = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    margin = z_value * se
    return EffectInterval(
        effect_estimate=estimate,
        ci_lower=estimate - margin,
        ci_upper=estimate + margin,
        ci_method="normal_approximation",
        sample_size=len(treatment) + len(control),
        confidence_level=confidence_level,
    )


def bootstrap_mean_difference_ci(
    treatment: list[float],
    control: list[float],
    *,
    confidence_level: float = 0.90,
    iterations: int = 500,
    seed: int = 11,
) -> EffectInterval:
    if not treatment or not control:
        raise ValueError("Treatment and control samples must be non-empty.")

    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sampled_treatment = [rng.choice(treatment) for _ in treatment]
        sampled_control = [rng.choice(control) for _ in control]
        estimates.append(mean(sampled_treatment) - mean(sampled_control))

    estimates.sort()
    lower_q = (1.0 - confidence_level) / 2.0
    upper_q = 1.0 - lower_q
    lower_index = max(0, min(len(estimates) - 1, int(lower_q * len(estimates))))
    upper_index = max(0, min(len(estimates) - 1, int(upper_q * len(estimates)) - 1))
    return EffectInterval(
        effect_estimate=mean(treatment) - mean(control),
        ci_lower=estimates[lower_index],
        ci_upper=estimates[upper_index],
        ci_method="bootstrap",
        sample_size=len(treatment) + len(control),
        confidence_level=confidence_level,
    )
