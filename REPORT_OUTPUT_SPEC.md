# Report Output Specification

## Purpose

The Reporting Layer turns Nudge Engine outputs into decision-ready reports.

The report must be understandable for humans and safe for API use. It must not leak PII, overclaim significance, or hide governance blockers.

## Supported Outputs

Current:

- Python `dict` / JSON-compatible Decision Report
- Markdown Decision Report

Future:

- CSV / XLSX segment export
- PDF / deck export
- dashboard API payload

## Report Inputs

The report can consume:

- Orchestrator result
- Hypotheses
- Formula uncertainty fields
- Policy decisions and reward rankings
- Security & Integrity Gate review
- PII Vault redaction summary
- Segment rows using `subject_id`
- Next actions
- Result Quality object
- Audit Lineage object

## Hard Reporting Rules

- No direct PII in report output.
- No vault payload in report output.
- No raw customer ID, user ID, account ID or company ID in report output.
- Reports use `subject_id`.
- Agent confidence is never presented as statistical confidence.
- Significance is only allowed when required CI fields exist, CI excludes null and `confidence_level >= 0.95`.
- If uncertainty is missing, report status must be `hold`.
- If CI contains null, uncertainty status must be `revise`.
- Security and governance status must be retained in JSON and available on request, but not dominate the default human report.
- Policy output must separate `action_fit` from `effect_evidence`.
- Reports must not imply that a ranked action has proven effect unless the Evidence/Claim Permission Layer allows that wording.
- Audit lineage must not store raw rows.

## Report Sections

### 1. Executive Summary

Contains:

- overall status
- orchestrator decision
- uncertainty status
- short summary
- decision rationale

Purpose:

- Give a fast decision view.

### 2. Evidence & Confidence

Contains:

- agent confidence
- confidence note
- effect estimate
- CI lower and upper
- CI method
- confidence level
- significance claim allowed
- uncertainty gate summary

Purpose:

- Prevent false significance or causal claims.

### 3. Hypotheses

Contains:

- hypothesis ID
- statement
- status
- MECE group

Purpose:

- Keep hypotheses separate from validated evidence.

### 4. Nudge Recommendations

Contains:

- `subject_id`
- selected action
- status
- claim type
- action fit status and fit score
- effect evidence status
- intervention risk tier
- human review requirement
- reason codes
- baseline delta
- no-action reward

Purpose:

- Show what would be recommended, blocked or held per subject without confusing theoretical fit with measured effect.

### 5. Segment View

Contains:

- pseudonymous row-level summary
- `subject_id`
- recommended action
- status
- reason

Purpose:

- Support operational review without exposing identity.

### 6. System Checks

Contains:

- Security & Integrity Gate status
- risk level
- safe to reason
- safe to execute
- PII redaction summary without raw field names
- no-PII check result

Purpose:

- Keep security and privacy review auditable without dominating the business result view.

Default Markdown behavior:

- Hidden from the main human report.
- Available through `include_system_checks=true`.
- Always retained in the JSON-compatible report.

### 7. Result Quality

Contains:

- formal decision state
- data readiness
- claim permission
- pilot readiness
- trust warnings

Purpose:

- Prevent the dashboard or report from over-presenting weak evidence as pilot-ready output.

### 8. Audit Lineage

Contains:

- run ID
- engine, policy and report versions
- schema hash
- input row count
- decision state
- blockers
- security status
- human override status
- raw-row persistence flag

Purpose:

- Make every run reproducible and auditable without storing raw customer rows.

### 9. Next Actions

Contains:

- concrete next steps
- blocker resolution
- experiment or CI validation
- governance/no-action reminders

Purpose:

- Make the report actionable.

## Implemented Module

File:

- `src/reporting.py`

Main functions:

- `build_decision_report()`
- `render_markdown_report()`
- `sanitize_for_report()`

Tests:

- `tests/test_reporting.py`

## Acceptance Criteria

- Markdown report contains all required sections.
- Markdown report hides system/security checks by default.
- Markdown report can include system checks explicitly.
- Report dict contains no raw PII.
- Segment rows expose `subject_id`, not direct identifiers.
- Redaction summary does not list direct identifier field names.
- Missing uncertainty produces `hold`.
- CI containing null blocks significance claims.
- Policy recommendations include no-action context.
- Policy recommendations include `action_fit` and `effect_evidence`.
- Security and PII status are retained in JSON and visible only in optional system checks.
- Result Quality is retained in JSON and visible in the dashboard.
- Audit Lineage is retained in JSON and does not store raw rows.
- Full test suite remains green.
