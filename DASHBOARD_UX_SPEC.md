# Dashboard UX Specification

## Purpose

The dashboard is the front door for Nudge Engine analysis.

The intended flow is:

```text
Question or customer data
  -> Engine run
  -> Decision report
  -> Dashboard result
  -> Optional chat with the result
```

It is designed for:

- executive review
- model/evidence review
- nudge recommendation review
- background system-check review when needed
- future chat-based exploration of report results

## Current Implementation

Files:

- `dashboard/index.html`
- `dashboard/styles.css`
- `dashboard/app.js`
- `dashboard/data/sample-report.json`

The dashboard is intentionally static and dependency-free for this stage.

## Visual Direction

- Bright, high-trust interface
- Warm paper background with light grid texture
- Glass-like panels
- Strong typographic hierarchy
- Green/blue governance palette with amber uncertainty accents
- Mobile-responsive layout

## Sections

### Overview

Shows:

- report title
- executive summary
- overall decision status

### Analyze

Shows:

- business question input
- JSON report upload
- run preview button
- clear note that the current mode is local preview until connected to the Python engine/API

### KPI Cards

Shows:

- security status
- uncertainty status
- significance availability
- PII/Vault cleanliness

### Evidence

Shows:

- confidence interval
- effect estimate marker
- null marker
- significance gate result

### Hypotheses

Shows:

- hypothesis ID
- MECE group
- statement
- status

### Nudge Recommendations

Shows:

- `subject_id`
- selected action
- status
- reason codes
- baseline delta
- no-action reward

### Background System Checks

Shows:

- Leonidas status
- risk level
- safe-to-reason
- safe-to-execute
- PII status
- redaction count
- vault record count

This section is collapsed behind a small system strip by default. Security is essential, but it should not dominate the business result view.

### Report Chat Preview

Current:

- local rule-based questions over loaded report JSON
- answers status, CI, security, PII, nudges and next actions

Future:

- connect to report-grounded chat endpoint
- cite exact report fields
- prevent answers from using non-report context

## Privacy Rules

- Dashboard data must use `subject_id`.
- Dashboard must not show email, phone, names or raw IDs.
- Redaction summary must show counts, not sensitive field names.
- Vault payload must never be loaded into dashboard data.

## Acceptance Criteria

- Dashboard contains all required sections.
- Dashboard starts with question/data input.
- Dashboard sample data contains no direct PII.
- Security is not a primary navigation item.
- Chat preview is report-grounded and does not claim production LLM behavior.
- Dashboard remains dependency-free and can be opened as static HTML.
- Full Python test suite remains green.
