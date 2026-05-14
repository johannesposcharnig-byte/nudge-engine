from __future__ import annotations

import csv
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import Orchestrator, Task


FIXTURE = ROOT / "tests" / "fixtures" / "synthetic_customer_events.csv"


def load_rows() -> list[dict[str, str]]:
    with FIXTURE.open(newline="") as handle:
        return list(csv.DictReader(handle))


class SyntheticCustomerFixtureTests(unittest.TestCase):
    def test_fixture_has_required_intake_columns(self) -> None:
        rows = load_rows()
        self.assertGreaterEqual(len(rows), 18)
        columns = set(rows[0])
        required = {
            "user_id",
            "company_id",
            "event_time",
            "nudge_variant",
            "nudge_method",
            "consent",
            "renewal",
            "openness_signal",
            "resistance_signal",
            "fatigue_signal",
            "vulnerability_flag",
        }
        self.assertTrue(required.issubset(columns))

    def test_fixture_is_not_rational_persona_shaped(self) -> None:
        rows = load_rows()
        high_openness_no_action = [
            row for row in rows
            if float(row["openness_signal"]) >= 0.60 and row["opened_nudge"] == "false"
        ]
        low_openness_action = [
            row for row in rows
            if float(row["openness_signal"]) <= 0.25 and row["clicked_nudge"] == "true"
        ]
        loss_frame_backfire = [
            row for row in rows
            if row["nudge_method"] == "loss_frame" and row["renewal"] == "false"
        ]
        control_renewals = [
            row for row in rows
            if row["nudge_variant"] == "control" and row["renewal"] == "true"
        ]

        self.assertTrue(high_openness_no_action)
        self.assertTrue(low_openness_action)
        self.assertTrue(loss_frame_backfire)
        self.assertTrue(control_renewals)

    def test_fixture_contains_governance_sensitive_rows(self) -> None:
        rows = load_rows()
        no_consent_treatment = [
            row for row in rows
            if row["consent"] == "false" and row["nudge_variant"] == "treatment"
        ]
        vulnerable_rows = [
            row for row in rows
            if row["vulnerability_flag"] == "true"
        ]
        high_fatigue_treatment = [
            row for row in rows
            if row["nudge_variant"] == "treatment" and float(row["fatigue_signal"]) >= 0.65
        ]

        self.assertTrue(no_consent_treatment)
        self.assertTrue(vulnerable_rows)
        self.assertTrue(high_fatigue_treatment)

    def test_fixture_schema_passes_customer_data_intake(self) -> None:
        rows = load_rows()
        orchestrator = Orchestrator()
        result = orchestrator.run_orchestration(
            Task(
                phase="customer_data_intake",
                agent="data",
                prompt="Validate synthetic customer fixture",
                context={
                    "available_columns": list(rows[0]),
                    "outcome_variable": "renewal",
                    "behavioral_method": "commitment",
                    "consent_field": "consent",
                    "time_fields": ["event_time", "signup_date"],
                    "entity_fields": ["user_id", "company_id"],
                    "treatment_group": "nudge_variant=treatment",
                    "control_group": "nudge_variant=control",
                },
            )
        )

        self.assertEqual(result.next_action, "approve")
        self.assertTrue(result.readiness_flags["data_ready"])


if __name__ == "__main__":
    unittest.main()
