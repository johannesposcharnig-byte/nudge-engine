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
- Leonidas security review
- PII Vault redaction summary
- Segment rows using `subject_id`
- Next actions

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
- reason codes
- baseline delta
- no-action reward

Purpose:

- Show what would be recommended, blocked or held per subject.

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

- Leonidas security status
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

### 7. Next Actions

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
- Security and PII status are retained in JSON and visible only in optional system checks.
- Full test suite remains green.
