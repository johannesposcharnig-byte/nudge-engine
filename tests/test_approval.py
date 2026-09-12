from __future__ import annotations

from datetime import datetime, timezone
import unittest

from src.approval import evaluate_approval


class ApprovalTests(unittest.TestCase):
    def valid_context(self) -> dict:
        return {
            "status": "approved",
            "actor": "pilot_owner",
            "reason": "reviewed synthetic activation run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "approved_scopes": ["pilot_review", "outreach_export"],
            "linked_run_id": "run_test",
            "intervention_risk_tier": "low",
        }

    def test_complete_approval_is_valid_for_its_scope_and_run(self) -> None:
        result = evaluate_approval(self.valid_context(), required_scope="pilot_review", linked_run_id="run_test")
        self.assertTrue(result.valid)

    def test_approval_is_rejected_for_wrong_run_or_missing_actor(self) -> None:
        context = self.valid_context()
        context["actor"] = ""
        result = evaluate_approval(context, required_scope="pilot_review", linked_run_id="run_other")
        self.assertFalse(result.valid)
        self.assertIn("approval_actor_missing", result.blockers)
        self.assertIn("approval_run_mismatch", result.blockers)

    def test_security_and_privacy_blockers_are_not_overridable(self) -> None:
        result = evaluate_approval(
            self.valid_context(),
            required_scope="pilot_review",
            linked_run_id="run_test",
            active_blockers=["security_blocked", "privacy_not_safe"],
        )
        self.assertFalse(result.valid)
        self.assertIn("non_overridable:security_blocked", result.blockers)
        self.assertIn("non_overridable:privacy_not_safe", result.blockers)


if __name__ == "__main__":
    unittest.main()
