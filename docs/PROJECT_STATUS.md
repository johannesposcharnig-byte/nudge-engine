# Project Status

## Summary

The Nudge Engine is currently a local-first, pilot-stage behavioral decision support prototype. It can analyze structured customer activation rows, produce guarded decision reports, expose a local API and display results in a dashboard preview.

It is not production-ready.

## Implemented

- Engine core entrypoint: `src/analysis_service.py`
- Local API: `src/api.py`
- API smoke test: `scripts/smoke_test_api.py`
- Canonical local API payload: `tests/fixtures/api_activation_payload.json`
- Dashboard preview: `dashboard/index.html`
- PII pseudonymization: `src/pii_vault.py`
- Security & Integrity Gate: `src/security.py`
- Data Contract and Data Readiness: `src/data_contracts.py`
- Evidence and Claim Permission: `src/claim_permissions.py`
- Reward and no-action policy logic: `src/reward.py`
- Result Quality: `src/result_quality.py`
- Audit Lineage: `src/audit_lineage.py`
- Reporting: `src/reporting.py`
- GitHub validation workflow: `.github/workflows/validate.yml`

## Tested

- Full unit test discovery
- Python compile check
- Local API function tests
- Local HTTP API smoke test
- Dashboard static asset checks
- PII report redaction checks
- Security and prompt-injection checks
- Claim permission and CI checks
- Data contract checks
- Audit lineage checks

## Connected

- `run_analysis()` connects security, PII pseudonymization, data readiness, hypotheses, uncertainty, policy, result quality, audit lineage and reporting.
- `POST /analyze` calls the guarded analysis service.
- The dashboard can load existing Decision Reports or send `customer_rows` payloads to the local API.

## Blocked Before Pilot

- A real pilot data contract must be agreed for the first customer/use case.
- Dashboard live run should be tested manually with representative local payloads.
- Human approval workflow is still lightweight and config-based.
- Experiment design assistant is not yet a complete runtime layer.

## Blocked Before Production

- Authentication
- Encrypted production PII vault
- Persistent audit store
- Access control
- Deployment monitoring
- Secrets management
- Data retention policy
- Incident response process
- Legal/privacy review
- Production data processing agreement

