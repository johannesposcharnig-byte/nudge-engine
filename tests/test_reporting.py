import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.base import AgentMessage
from src.pii_vault import pseudonymize_customer_rows
from src.reporting import DecisionReportInput, build_decision_report, render_markdown_report
from src.reward import policy_decision_for_person
from src.security import leonidas_security_review


class ReportingTests(unittest.TestCase):
    def make_message(self, *, uncertainty: dict | None = None, next_action: str = "approve") -> AgentMessage:
        return AgentMessage(
            agent="orchestrator",
            phase="formula_review",
            jtbd="Create decision report",
            summary="Formula review completed.",
            done_status="done",
            confidence=0.88,
            context={
                "evidence_gate_required": True,
                "security_review": leonidas_security_review({"pii_pseudonymized": True}).as_dict(),
                "hypotheses": [
                    {
                        "id": "H4",
                        "statement": "Treatment can improve activation.",
                        "status": "testable",
                        "mece_group": "effect",
                    }
                ],
            },
            assumptions=["Report must distinguish hypotheses from validated effects."],
            evidence=["A/B simulation result is available."],
            risks=[],
            open_questions=[],
            requested_feedback=[],
            feedback_to=[],
            next_action=next_action,
            uncertainty=uncertainty or {},
            claims=[
                {
                    "statement": "Formula review decision is based on staged evidence.",
                    "claim_type": "observed",
                    "category": "process",
                    "evidence_available": ["stage summaries"],
                }
            ],
            claim_type="observed",
            evidence_available=["stage summaries"],
            decision_rationale="Formula gate passed.",
        )

    def test_report_redacts_pii_and_uses_subject_id(self) -> None:
        vault = pseudonymize_customer_rows(
            [
                {
                    "customer_id": "c1",
                    "email": "person@example.com",
                    "event_time": "2026-05-01T09:00:00Z",
                    "fatigue_signal": "0.2",
                }
            ],
            secret_key="vault-secret",
            identity_fields=["customer_id"],
        )
        subject_id = vault.analytics_rows[0]["subject_id"]
        message = self.make_message(
            uncertainty={
                "effect_estimate": 0.12,
                "ci_lower": 0.04,
                "ci_upper": 0.2,
                "ci_method": "bootstrap",
                "sample_size": 120,
                "confidence_level": 0.95,
                "contains_null": False,
            }
        )
        report = build_decision_report(
            DecisionReportInput(
                title="Activation Nudge Report",
                orchestrator_result=message,
                segment_rows=[
                    {
                        "subject_id": subject_id,
                        "email": "person@example.com",
                        "recommended_action": "cognitive_ease",
                        "status": "hypothesis",
                        "reason": "high friction",
                    }
                ],
                pii_redaction_summary=vault.redaction_summary,
            )
        )
        markdown = render_markdown_report(report)

        self.assertIn(subject_id, markdown)
        self.assertNotIn("person@example.com", markdown)
        self.assertNotIn("customer_id", str(report))
        self.assertTrue(report["security_and_governance"]["no_pii_in_segment_view"])

    def test_report_blocks_significance_claim_when_ci_contains_null(self) -> None:
        message = self.make_message(
            uncertainty={
                "effect_estimate": 0.02,
                "ci_lower": -0.03,
                "ci_upper": 0.07,
                "ci_method": "bootstrap",
                "sample_size": 80,
                "confidence_level": 0.95,
                "contains_null": True,
            }
        )

        report = build_decision_report(DecisionReportInput(title="CI Report", orchestrator_result=message))

        self.assertEqual(report["evidence_and_uncertainty"]["gate"]["status"], "revise")
        self.assertFalse(report["evidence_and_uncertainty"]["gate"]["significance_claim_allowed"])

    def test_report_holds_without_uncertainty(self) -> None:
        report = build_decision_report(
            DecisionReportInput(
                title="Missing CI Report",
                orchestrator_result=self.make_message(uncertainty={}, next_action="approve"),
            )
        )

        self.assertEqual(report["executive_summary"]["status"], "hold")
        self.assertFalse(report["evidence_and_uncertainty"]["gate"]["significance_claim_allowed"])

    def test_report_includes_policy_and_no_action_context(self) -> None:
        person = {
            "subject_id": "sub_demo",
            "recommended_nudge": "cognitive_ease",
            "consent": True,
            "vulnerability_flag": False,
            "fatigue_signal": 0.2,
            "friction_signal": 0.8,
            "resistance_signal": 0.7,
            "baseline_activation_score": 0.4,
            "reward_calibrated": True,
            "manipulation_governance_review": True,
        }
        policy = policy_decision_for_person(person, actions=["no_action", "cognitive_ease"])
        policy["subject_id"] = "sub_demo"
        message = self.make_message(
            uncertainty={
                "effect_estimate": 0.12,
                "ci_lower": 0.04,
                "ci_upper": 0.2,
                "ci_method": "bootstrap",
                "sample_size": 120,
                "confidence_level": 0.95,
                "contains_null": False,
            }
        )

        report = build_decision_report(
            DecisionReportInput(
                title="Policy Report",
                orchestrator_result=message,
                policy_decisions=[policy],
            )
        )

        self.assertEqual(report["nudge_recommendations"][0]["subject_id"], "sub_demo")
        self.assertIn("no_action_reward", report["nudge_recommendations"][0])
        self.assertEqual(report["nudge_recommendations"][0]["claim_type"], "hypothesis")
        self.assertIn("action_fit", report["nudge_recommendations"][0])
        self.assertEqual(report["nudge_recommendations"][0]["effect_evidence"], "hypothesis_only")
        self.assertIn("human_review_required", report["nudge_recommendations"][0])

    def test_markdown_contains_required_sections(self) -> None:
        report = build_decision_report(
            DecisionReportInput(
                title="Required Sections",
                orchestrator_result=self.make_message(),
            )
        )
        markdown = render_markdown_report(report)

        for section in [
            "Executive Summary",
            "Evidence & Confidence",
            "Hypotheses",
            "Nudge Recommendations",
            "Segment View",
            "Next Actions",
        ]:
            self.assertIn(section, markdown)
        self.assertNotIn("Security & Governance", markdown)

    def test_markdown_can_include_optional_system_checks(self) -> None:
        report = build_decision_report(
            DecisionReportInput(
                title="System Check Report",
                orchestrator_result=self.make_message(),
            )
        )
        markdown = render_markdown_report(report, include_system_checks=True)

        self.assertIn("System Checks", markdown)
        self.assertIn("Security status", markdown)


if __name__ == "__main__":
    unittest.main()
