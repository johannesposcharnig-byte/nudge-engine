import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"


class DashboardAssetTests(unittest.TestCase):
    def test_dashboard_assets_exist(self) -> None:
        for relative in [
            "index.html",
            "styles.css",
            "app.js",
            "data/sample-report.json",
        ]:
            self.assertTrue((DASHBOARD / relative).exists(), relative)

    def test_dashboard_contains_required_sections(self) -> None:
        html = (DASHBOARD / "index.html").read_text()
        for section in [
            "analyze",
            "overview",
            "quality",
            "experiment",
            "evidence",
            "nudges",
            "chat",
        ]:
            self.assertIn(f'id="{section}"', html)
        self.assertNotIn('href="#security"', html)

    def test_sample_report_contains_no_direct_pii(self) -> None:
        report_text = (DASHBOARD / "data/sample-report.json").read_text()
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", report_text))
        self.assertNotIn("customer_id", report_text)
        self.assertNotIn("user_id", report_text)
        self.assertNotIn("phone", report_text.lower())
        report = json.loads(report_text)
        self.assertTrue(report["security_and_governance"]["no_pii_in_segment_view"])

    def test_dashboard_chat_is_report_grounded_preview(self) -> None:
        script = (DASHBOARD / "app.js").read_text()
        self.assertIn("answerQuestion", script)
        self.assertIn("loaded analysis", script)
        self.assertIn("report-grounded LLM endpoint", script)

    def test_dashboard_supports_question_and_json_upload(self) -> None:
        html = (DASHBOARD / "index.html").read_text()
        self.assertIn('id="analysis-question"', html)
        self.assertIn('id="report-upload"', html)
        self.assertIn("Run engine preview", html)

    def test_dashboard_surfaces_result_quality_and_audit_lineage(self) -> None:
        html = (DASHBOARD / "index.html").read_text()
        script = (DASHBOARD / "app.js").read_text()
        report = json.loads((DASHBOARD / "data/sample-report.json").read_text())

        self.assertIn('id="quality"', html)
        self.assertIn('id="quality-state"', html)
        self.assertIn('id="audit-lineage"', html)
        self.assertIn("renderResultQuality", script)
        self.assertIn("renderExperimentAndApproval", script)
        self.assertIn('id="approval-status"', html)
        self.assertIn("effect_evidence", script)
        self.assertIn("http://127.0.0.1:8765/analyze", script)
        self.assertIn("looksLikeEngineInput", script)
        self.assertIn("result_quality", report)
        self.assertIn("audit_lineage", report)


if __name__ == "__main__":
    unittest.main()
