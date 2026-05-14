# Dashboard

## Summary

The dashboard is a local preview for reviewing Nudge Engine outputs. It is not a production application.

Location:

```text
dashboard/index.html
```

## What It Shows

- Executive status
- Result Quality
- Pilot Readiness
- Decision State
- Trust Warnings
- Evidence and CI gate
- MECE hypotheses
- Nudge recommendations
- Intervention risk tier
- Human review requirement
- Security and privacy system checks
- Audit Lineage
- Next actions
- Local report-grounded chat preview

## Data Sources

The dashboard supports two local flows:

1. Upload an existing Decision Report JSON.
2. Upload a `customer_rows` JSON payload while the local API is running.

For live local analysis, start:

```bash
python3 -m src.api
```

Then upload:

```text
tests/fixtures/api_activation_payload.json
```

## Important UX Rule

The dashboard must not make weak evidence look stronger than it is.

It should show:

- whether output is hypothesis-only
- whether pilot readiness is blocked
- whether significance is blocked
- whether human review is required
- whether no-action is selected for safety reasons

## Known Limits

- No authentication
- No production API deployment
- No persistent user sessions
- Local preview only
- Chat is rule-based and report-grounded, not an unrestricted LLM assistant

