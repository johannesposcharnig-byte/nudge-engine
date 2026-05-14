"""Security and integrity checks for governed agent execution."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Any, Literal


LEONIDAS_AGENT_NAME = "Leonidas"

RiskLevel = Literal["low", "medium", "high", "critical"]
SecurityStatus = Literal["approve", "revise", "hold", "reject"]

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "disable governance",
    "override policy",
    "reveal system prompt",
    "modify reward weights",
    "bypass no-action baseline",
    "bypass governance",
    "ignore all previous instructions",
    "forget your instructions",
    "disable safety",
    "override governance",
    "force approve",
]

SECRET_PATTERNS = {
    "openai_api_key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "github_token": r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
    "slack_token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "generic_secret_assignment": r"\b(api[_-]?key|secret|token|password|credential)\s*[:=]\s*['\"]?[A-Za-z0-9._/\-]{12,}",
}

PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone": r"\b(?:\+?\d[\d\s().-]{7,}\d)\b",
}

REWARD_HACKING_KEYS = {
    "reward_override_request",
    "heuristic_only_policy",
    "ocean_only_decision",
    "disable_no_action_baseline",
}

GOVERNANCE_BYPASS_KEYS = {
    "bypass_governance",
    "ignore_guardrails",
    "unsafe_override",
    "force_approve",
}

NORMALIZED_SIGNAL_KEYS = {
    "activation_gap",
    "activation_score",
    "ambiguity_signal",
    "attention_signal",
    "baseline_activation_score",
    "deadline_pressure",
    "fatigue_signal",
    "friction_signal",
    "openness_proxy",
    "peer_norm_signal",
    "resistance_signal",
    "trust_gap_signal",
}

ROW_CONTEXT_KEYS = ["customer_rows", "data_sample", "records", "rows"]

ROW_TEXT_FIELDS = {
    "comment",
    "customer_note",
    "description",
    "feedback",
    "free_text",
    "message",
    "note",
    "notes",
    "support_ticket",
    "text",
}

TIME_FIELD_HINTS = ("time", "timestamp", "date", "created_at", "updated_at", "event_time")

LEAKAGE_FIELD_HINTS = (
    "future_",
    "post_treatment",
    "post_nudge",
    "after_treatment",
    "after_nudge",
    "label",
    "target",
)

RISK_RANK: dict[RiskLevel, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


@dataclass(frozen=True)
class SecurityRisk:
    """A concrete security or integrity risk found by Leonidas."""

    risk_type: str
    risk_level: RiskLevel
    reason: str
    evidence: list[str] = field(default_factory=list)
    action: Literal["warn", "hold", "block"] = "warn"
    pattern: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent": LEONIDAS_AGENT_NAME,
            "risk_type": self.risk_type,
            "risk_level": self.risk_level,
            "severity": self.risk_level,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "action": self.action,
            "pattern": self.pattern or self.risk_type,
        }


@dataclass(frozen=True)
class SecurityReview:
    """Leonidas review result used by the orchestrator gate."""

    agent: str = LEONIDAS_AGENT_NAME
    security_status: SecurityStatus = "approve"
    risk_level: RiskLevel = "low"
    detected_risks: list[SecurityRisk] = field(default_factory=list)
    blocked_content: list[str] = field(default_factory=list)
    required_mitigations: list[str] = field(default_factory=list)
    safe_to_reason: bool = True
    safe_to_execute: bool = True
    decision_rationale: str = "No critical security or integrity risk detected."

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "security_status": self.security_status,
            "risk_level": self.risk_level,
            "detected_risks": [risk.as_dict() for risk in self.detected_risks],
            "blocked_content": list(self.blocked_content),
            "required_mitigations": list(self.required_mitigations),
            "safe_to_reason": self.safe_to_reason,
            "safe_to_execute": self.safe_to_execute,
            "decision_rationale": self.decision_rationale,
        }

    def as_warnings(self) -> list[dict[str, Any]]:
        return [risk.as_dict() for risk in self.detected_risks]


def _flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    alphanumeric = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(alphanumeric.split())


NORMALIZED_PROMPT_INJECTION_PATTERNS = [
    _normalize_text(pattern) for pattern in PROMPT_INJECTION_PATTERNS
]


def _external_text_values(context: dict[str, Any]) -> list[tuple[str, str]]:
    keys = [
        "prompt",
        "retrieval_query",
        "external_content",
        "source_metadata",
        "conflicts",
        "raw_context",
        "raw_documents",
        "full_context",
        "all_documents",
        "documents",
        "file_contents",
        "conversation_history",
        *ROW_CONTEXT_KEYS,
    ]
    values = []
    for key in keys:
        if key in context:
            values.append((key, _flatten_text(context.get(key))))
    return values


def _compile_findings(patterns: dict[str, str], text_values: list[tuple[str, str]]) -> list[tuple[str, str]]:
    findings = []
    for source_key, value in text_values:
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, value, flags=re.IGNORECASE):
                findings.append((pattern_name, source_key))
    return findings


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        numeric = float(value)
    elif isinstance(value, str):
        try:
            numeric = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return numeric
    return numeric


def _iter_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ROW_CONTEXT_KEYS:
        value = context.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _add_highest(levels: list[RiskLevel]) -> RiskLevel:
    if not levels:
        return "low"
    return max(levels, key=lambda level: RISK_RANK[level])


def _scan_prompt_injection(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    for source_key, value in _external_text_values(context):
        lowered = value.lower()
        normalized = _normalize_text(value)
        for pattern, normalized_pattern in zip(PROMPT_INJECTION_PATTERNS, NORMALIZED_PROMPT_INJECTION_PATTERNS):
            if pattern in lowered or normalized_pattern in normalized:
                risks.append(
                    SecurityRisk(
                        risk_type="prompt_injection",
                        risk_level="critical",
                        reason="External content attempted to override governance, policy, reward, or system rules.",
                        evidence=[source_key],
                        action="block",
                        pattern=pattern,
                    )
                )
    return risks


def _scan_secrets_and_pii(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    if context.get("pii_pseudonymized") is True:
        return risks
    text_values = _external_text_values(context)
    for pattern_name, source_key in _compile_findings(SECRET_PATTERNS, text_values):
        risks.append(
            SecurityRisk(
                risk_type="secret_exposure",
                risk_level="critical",
                reason="Context appears to contain credentials, tokens, API keys, or secrets.",
                evidence=[source_key],
                action="block",
                pattern=pattern_name,
            )
        )
    for pattern_name, source_key in _compile_findings(PII_PATTERNS, text_values):
        risks.append(
            SecurityRisk(
                risk_type="pii_exposure",
                risk_level="high",
                reason="Context appears to contain directly identifying personal data and should be pseudonymized before reasoning.",
                evidence=[source_key],
                action="hold",
                pattern=pattern_name,
            )
        )
    return risks


def _scan_reward_and_policy_integrity(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    for key in sorted(REWARD_HACKING_KEYS):
        if context.get(key):
            risks.append(
                SecurityRisk(
                    risk_type="reward_policy_integrity",
                    risk_level="high",
                    reason=f"Context contains a policy/reward shortcut flag: {key}.",
                    evidence=[key],
                    action="hold",
                    pattern=key,
                )
            )
    for key in sorted(GOVERNANCE_BYPASS_KEYS):
        if context.get(key):
            risks.append(
                SecurityRisk(
                    risk_type="governance_bypass",
                    risk_level="critical",
                    reason=f"Context attempts to bypass or force governance: {key}.",
                    evidence=[key],
                    action="block",
                    pattern=key,
                )
            )
    return risks


def _parse_iso_datetime(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        from datetime import datetime

        datetime.fromisoformat(text)
        return True
    except ValueError:
        return False


def _scan_data_integrity(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    rows = _iter_rows(context)
    if not rows:
        return risks

    unique_fields = []
    if context.get("unique_id_field"):
        unique_fields.append(str(context["unique_id_field"]))
    if any("event_id" in row for row in rows):
        unique_fields.append("event_id")

    for field in sorted(set(unique_fields)):
        seen: set[str] = set()
        duplicates: set[str] = set()
        for row in rows:
            if field not in row:
                continue
            value = str(row[field])
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        if duplicates:
            risks.append(
                SecurityRisk(
                    risk_type="data_integrity_duplicate_id",
                    risk_level="high",
                    reason="A field expected to be unique contains duplicate values.",
                    evidence=[field, *sorted(duplicates)[:5]],
                    action="hold",
                    pattern="duplicate_unique_id",
                )
            )

    for row_index, row in enumerate(rows):
        for key, value in row.items():
            lower_key = str(key).lower()
            if any(hint == lower_key or hint in lower_key for hint in TIME_FIELD_HINTS):
                if value and not _parse_iso_datetime(value):
                    risks.append(
                        SecurityRisk(
                            risk_type="data_integrity_invalid_timestamp",
                            risk_level="high",
                            reason="Timestamp-like field is not parseable as an ISO datetime/date.",
                            evidence=[f"row={row_index}", str(key), str(value)],
                            action="hold",
                            pattern="invalid_timestamp",
                        )
                    )
            if any(hint in lower_key for hint in LEAKAGE_FIELD_HINTS):
                if lower_key not in {"target_behavior"}:
                    risks.append(
                        SecurityRisk(
                            risk_type="label_leakage_risk",
                            risk_level="high",
                            reason="Feature set appears to contain future, post-treatment, label, or target fields.",
                            evidence=[str(key)],
                            action="hold",
                            pattern="label_leakage_field",
                        )
                    )

    treatment_by_entity: dict[str, set[str]] = {}
    entity_field = str(context.get("entity_field", ""))
    if not entity_field:
        for candidate in ["user_id", "customer_id", "account_id", "company_id"]:
            if any(candidate in row for row in rows):
                entity_field = candidate
                break
    for row in rows:
        if not entity_field or entity_field not in row:
            continue
        group = row.get("experiment_group") or row.get("treatment_group") or row.get("variant")
        if group is None:
            continue
        treatment_by_entity.setdefault(str(row[entity_field]), set()).add(str(group))
    contaminated = sorted(entity for entity, groups in treatment_by_entity.items() if len(groups) > 1)
    if contaminated:
        risks.append(
            SecurityRisk(
                risk_type="treatment_control_contamination",
                risk_level="high",
                reason="The same entity appears in multiple treatment/control groups.",
                evidence=[entity_field, *contaminated[:5]],
                action="hold",
                pattern="treatment_control_contamination",
            )
        )

    return risks


def _scan_source_integrity(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    source_metadata = context.get("source_metadata", {})
    if not isinstance(source_metadata, dict):
        return risks
    for source_id, source in source_metadata.items():
        if not isinstance(source, dict):
            continue
        validation_status = source.get("validation_status")
        lifecycle_status = source.get("lifecycle_status")
        if source.get("trusted") is False:
            risks.append(
                SecurityRisk(
                    risk_type="untrusted_source",
                    risk_level="high",
                    reason="Source is explicitly marked as untrusted.",
                    evidence=[str(source_id)],
                    action="hold",
                    pattern="untrusted_source",
                )
            )
        if validation_status == "blocked" or lifecycle_status == "blocked":
            risks.append(
                SecurityRisk(
                    risk_type="blocked_source",
                    risk_level="critical",
                    reason="Blocked evidence source must not enter reasoning.",
                    evidence=[str(source_id)],
                    action="block",
                    pattern="blocked_source",
                )
            )
        if validation_status == "deprecated" or lifecycle_status == "deprecated":
            risks.append(
                SecurityRisk(
                    risk_type="deprecated_source",
                    risk_level="high",
                    reason="Deprecated evidence source must not support a decision.",
                    evidence=[str(source_id)],
                    action="hold",
                    pattern="deprecated_source",
                )
            )
    return risks


def _scan_data_poisoning(context: dict[str, Any]) -> list[SecurityRisk]:
    risks = []
    rows = _iter_rows(context)
    for row_index, row in enumerate(rows):
        for key, value in row.items():
            normalized_key = str(key)
            if normalized_key not in NORMALIZED_SIGNAL_KEYS and not normalized_key.endswith("_signal"):
                continue
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            if math.isnan(numeric_value) or math.isinf(numeric_value) or numeric_value < 0 or numeric_value > 1:
                risks.append(
                    SecurityRisk(
                        risk_type="data_poisoning_or_schema_violation",
                        risk_level="high",
                        reason="Normalized behavioral signal is outside the expected [0, 1] range.",
                        evidence=[f"row={row_index}", normalized_key, str(value)],
                        action="hold",
                        pattern="out_of_range_behavioral_signal",
                    )
                )
    return risks


def leonidas_security_review(context: dict[str, Any]) -> SecurityReview:
    """Run Leonidas security checks before agent reasoning or execution."""

    risks = [
        *_scan_prompt_injection(context),
        *_scan_secrets_and_pii(context),
        *_scan_reward_and_policy_integrity(context),
        *_scan_source_integrity(context),
        *_scan_data_poisoning(context),
        *_scan_data_integrity(context),
    ]
    risk_level = _add_highest([risk.risk_level for risk in risks])
    blocked_content = [
        evidence
        for risk in risks
        if risk.action == "block"
        for evidence in risk.evidence
    ]
    mitigations = []
    if any(risk.risk_type == "prompt_injection" for risk in risks):
        mitigations.append("Remove or quarantine hostile external instructions before retrying.")
    if any(risk.risk_type == "secret_exposure" for risk in risks):
        mitigations.append("Remove secrets and rotate exposed credentials before retrying.")
    if any(risk.risk_type == "pii_exposure" for risk in risks):
        mitigations.append("Pseudonymize direct identifiers before agent reasoning.")
    if any(risk.risk_type == "data_poisoning_or_schema_violation" for risk in risks):
        mitigations.append("Validate schema ranges and sanitize anomalous behavioral signals.")
    if any(risk.risk_type.startswith("data_integrity") for risk in risks):
        mitigations.append("Repair duplicate IDs, timestamp formats, and schema integrity issues.")
    if any(risk.risk_type == "label_leakage_risk" for risk in risks):
        mitigations.append("Remove future, post-treatment, target, or label leakage fields from model inputs.")
    if any(risk.risk_type == "treatment_control_contamination" for risk in risks):
        mitigations.append("Resolve treatment/control contamination before causal evaluation.")
    if any(risk.risk_type == "reward_policy_integrity" for risk in risks):
        mitigations.append("Re-run reward, no-action baseline, and governance calibration.")
    if any(risk.risk_type in {"blocked_source", "deprecated_source", "untrusted_source"} for risk in risks):
        mitigations.append("Replace unsafe evidence sources with active approved sources.")
    if any(risk.risk_type == "governance_bypass" for risk in risks):
        mitigations.append("Remove governance bypass flags and route to governance review.")

    has_block = any(risk.action == "block" for risk in risks)
    has_hold = any(risk.action == "hold" for risk in risks)
    if has_block:
        status: SecurityStatus = "reject"
    elif has_hold:
        status = "hold"
    elif risks:
        status = "revise"
    else:
        status = "approve"

    return SecurityReview(
        security_status=status,
        risk_level=risk_level,
        detected_risks=risks,
        blocked_content=blocked_content,
        required_mitigations=mitigations,
        safe_to_reason=not has_block,
        safe_to_execute=not (has_block or has_hold),
        decision_rationale=(
            "Leonidas blocked unsafe context before reasoning."
            if has_block
            else "Leonidas held execution until integrity risks are mitigated."
            if has_hold
            else "Leonidas found non-blocking warnings."
            if risks
            else "Leonidas found no security or integrity blockers."
        ),
    )
