from __future__ import annotations

import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.simulation import ab_mean_difference_ci, bootstrap_mean_difference_ci, simulate_ab_outcomes


class SimulationTests(unittest.TestCase):
    def test_ab_simulation_ci_contains_known_effect(self) -> None:
        treatment, control = simulate_ab_outcomes(sample_size=400, treatment_effect=0.5, seed=2)
        interval = ab_mean_difference_ci(treatment, control, confidence_level=0.95)

        self.assertLess(interval.ci_lower, 0.5)
        self.assertGreater(interval.ci_upper, 0.5)
        self.assertEqual(interval.confidence_level, 0.95)
        self.assertFalse(interval.contains_null)

    def test_bootstrap_ci_marks_exploratory_confidence_level(self) -> None:
        treatment, control = simulate_ab_outcomes(sample_size=80, treatment_effect=0.4, seed=3)
        interval = bootstrap_mean_difference_ci(treatment, control, confidence_level=0.90, iterations=200)

        self.assertEqual(interval.confidence_level, 0.90)
        self.assertEqual(interval.ci_method, "bootstrap")
        self.assertEqual(interval.sample_size, 80)
        self.assertIn("ci_lower", interval.as_uncertainty())


if __name__ == "__main__":
    unittest.main()
