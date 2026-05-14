# Local API Testing

## Purpose

This file defines the minimum local test path for the Nudge Engine API.

The goal is not production readiness. The goal is to prove that the local API can receive customer-row input, run the guarded engine, and return a report with Result Quality and Audit Lineage.

## What This Tests

- API health endpoint
- `POST /analyze`
- Customer rows input path
- Security & Integrity Gate
- PII pseudonymization
- Data Contract and Data Readiness
- Claim Permission and CI gate
- Reward/Policy ranking
- Result Quality
- Audit Lineage
- Dashboard-compatible JSON output

## Start The API

From the project root:

```bash
python3 -m src.api
```

Expected console output:

```text
Nudge Engine local API running at http://127.0.0.1:8765
```

## Healthcheck

In a second terminal:

```bash
curl http://127.0.0.1:8765/health
```

Expected:

```json
{"status":"ok","service":"nudge-engine-local-api"}
```

## Analyze Smoke Test

Run:

```bash
python3 scripts/smoke_test_api.py
```

This uses:

```text
tests/fixtures/api_activation_payload.json
```

Expected output includes:

```text
Local API smoke test OK
```

## Manual Analyze Request

```bash
curl -X POST http://127.0.0.1:8765/analyze \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/api_activation_payload.json
```

Expected response includes:

- `executive_summary`
- `result_quality`
- `audit_lineage`
- `nudge_recommendations`
- `security_and_governance`

## Dashboard Live Test

1. Start the API:

```bash
python3 -m src.api
```

2. Open:

```text
dashboard/index.html
```

3. Upload:

```text
tests/fixtures/api_activation_payload.json
```

4. Confirm that the dashboard shows:

- Result Quality
- Pilot Readiness
- Decision State
- Trust Warnings
- Audit Lineage
- Nudge table

## Local Acceptance Criteria

- Healthcheck returns `ok`.
- Smoke test exits successfully.
- `/analyze` returns HTTP 200 for the fixture.
- API response contains no direct email addresses or raw user IDs.
- `result_quality.data_readiness.status` is `ready`.
- `audit_lineage.stored_raw_rows` is `false`.
- Dashboard can display either uploaded Decision Reports or API-generated reports from `customer_rows`.

## Known Limits

- No authentication yet.
- No production vault.
- No persistent audit store.
- No deployment monitoring.
- API is local-only.
- Dashboard requires the local API process to be running for live customer-row analysis.
