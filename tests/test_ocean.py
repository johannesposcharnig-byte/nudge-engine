from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.base import AgentMessage
from src.evidence import build_mece_hypotheses, infer_customer_data_profile
from src.ocean import build_ocean_signal, reverse_score, score_tipi
from src.orchestrator import Orchestrator


FIXTURE = ROOT / "tests" / "fixtures" / "synthetic_tipi_responses.csv"


class OceanModelTests(unittest.TestCase):
    def test_reverse_score_uses_one_to_seven_scale(self) -> None:
        self.assertEqual(reverse_score(1), 7)
        self.assertEqual(reverse_score(7), 1)
        self.assertEqual(reverse_score(4), 4)

    def test_tipi_scoring_returns_ocean_traits(self) -> None:
        responses = {
            "tipi_1": 6,
            "tipi_2": 2,
            "tipi_3": 6,
            "tipi_4": 5,
            "tipi_5": 7,
            "tipi_6": 2,
            "tipi_7": 6,
            "tipi_8": 2,
            "tipi_9": 5,
            "tipi_10": 1,
        }

        scores = score_tipi(responses, consent=True)

        self.assertEqual(scores.extraversion, 6.0)
        self.assertEqual(scores.agreeableness, 6.0)
        self.assertEqual(scores.conscientiousness, 6.0)
        self.assertEqual(scores.emotional_stability, 4.0)
        self.assertEqual(scores.neuroticism, 4.0)
        self.assertEqual(scores.openness, 7.0)
        self.assertTrue(scores.hypothesis_only)
        self.assertEqual(scores.precision, "low_precision")

    def test_tipi_rejects_missing_or_out_of_range_items(self) -> None:
        incomplete = {f"tipi_{index}": 4 for index in range(1, 10)}
        with self.assertRaises(ValueError):
            score_tipi(incomplete, consent=True)

        invalid = {f"tipi_{index}": 4 for index in range(1, 11)}
        invalid["tipi_5"] = 8
        with self.assertRaises(ValueError):
            score_tipi(invalid, consent=True)

    def test_tipi_requires_consent(self) -> None:
        responses = {f"tipi_{index}": 4 for index in range(1, 11)}
        with self.assertRaises(PermissionError):
            score_tipi(responses, consent=False)

        signal = build_ocean_signal(responses, consent=False)
        self.assertFalse(signal["usable_for_personalization"])
        self.assertEqual(signal["blocked_reason"], "ocean_consent_required")
        self.assertIsNone(signal["scores"])

    def test_orchestrator_blocks_ocean_personalization_without_consent(self) -> None:
        orchestrator = Orchestrator()
        message = AgentMessage(
            agent="policy",
            phase="policy_design",
            jtbd="Use OCEAN for policy routing",
            summary="Policy routes based on OCEAN.",
            done_status="done",
            confidence=0.8,
            context={
                "evidence_gate_required": True,
                "uses_ocean_for_personalization": True,
                "ocean_consent": False,
                "ocean_scores": {"openness": 6.5},
            },
            evidence=["tipi_responses"],
            claims=[
                {
                    "statement": "OCEAN scores can route the policy.",
                    "claim_type": "inferred",
                    "category": "psychological_trait",
                    "evidence_available": ["tipi_responses"],
                }
            ],
            claim_type="inferred",
            evidence_available=["tipi_responses"],
            next_action="approve",
        )

        self.assertEqual(orchestrator.evaluate_evidence_gate(message), "hold")

    def test_orchestrator_blocks_ocean_only_policy_approval(self) -> None:
        orchestrator = Orchestrator()
        message = AgentMessage(
            agent="policy",
            phase="policy_design",
            jtbd="Approve policy from OCEAN only",
            summary="OCEAN only policy approval.",
            done_status="done",
            confidence=0.8,
            context={
                "evidence_gate_required": True,
                "uses_ocean_for_personalization": True,
                "ocean_consent": True,
                "ocean_only_decision": True,
                "ocean_scores": {"openness": 6.5},
            },
            evidence=["tipi_responses"],
            claims=[
                {
                    "statement": "OCEAN alone is enough to approve the policy.",
                    "claim_type": "inferred",
                    "category": "ocean",
                    "evidence_available": ["tipi_responses"],
                }
            ],
            claim_type="inferred",
            evidence_available=["tipi_responses"],
            next_action="approve",
        )

        self.assertEqual(orchestrator.evaluate_evidence_gate(message), "hold")

    def test_customer_profile_detects_ocean_and_tipi_fields(self) -> None:
        profile = infer_customer_data_profile(
            {
                "available_columns": [
                    "user_id",
                    "event_time",
                    "renewal",
                    "tipi_1",
                    "openness_signal",
                    "neuroticism_signal",
                ]
            }
        )

        self.assertIn("tipi_1", profile["psychological_fields"])
        self.assertIn("openness_signal", profile["psychological_fields"])
        hypotheses = build_mece_hypotheses({"customer_data_profile": profile})
        h3 = next(item for item in hypotheses if item["id"] == "H3")
        h5 = next(item for item in hypotheses if item["id"] == "H5")
        self.assertIn("psychological_signal", h3["evidence"])
        self.assertIn("psychological_fields", h5["evidence"])

    def test_synthetic_tipi_fixture_contains_non_rational_trait_patterns(self) -> None:
        with FIXTURE.open(newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertGreaterEqual(len(rows), 6)
        no_consent = [row for row in rows if row["ocean_consent"] == "false"]
        high_open_resistant = [
            row for row in rows
            if float(row["tipi_5"]) >= 6 and row["observed_resistance"] == "high"
        ]
        low_open_exploratory = [
            row for row in rows
            if float(row["tipi_5"]) <= 3 and row["clicked_new_feature"] == "true"
        ]

        self.assertTrue(no_consent)
        self.assertTrue(high_open_resistant)
        self.assertTrue(low_open_exploratory)


if __name__ == "__main__":
    unittest.main()
