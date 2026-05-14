# API

## Summary

The API is a local development API for guarded analysis. It is not production-ready and has no authentication.

Base URL:

```text
http://127.0.0.1:8765
```

Start:

```bash
python3 -m src.api
```

## GET /health

Checks whether the local API is running.

Example:

```bash
curl http://127.0.0.1:8765/health
```

Response:

```json
{
  "status": "ok",
  "service": "nudge-engine-local-api"
}
```

## POST /analyze

Runs the guarded analysis pipeline.

Example:

```bash
curl -X POST http://127.0.0.1:8765/analyze \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/api_activation_payload.json
```

Minimum request shape:

```json
{
  "question": "Which low-risk activation nudge should we test next?",
  "identity_fields": ["user_id"],
  "confidence_level": 0.95,
  "config": {
    "outcome_variable": "activation_score",
    "actions": ["no_action", "cognitive_ease", "simplification"]
  },
  "customer_rows": []
}
```

Expected response sections:

- `executive_summary`
- `evidence_and_uncertainty`
- `hypotheses`
- `nudge_recommendations`
- `segment_view`
- `security_and_governance`
- `result_quality`
- `audit_lineage`
- `next_actions`

## Structured Errors

Errors are returned as JSON:

```json
{
  "error": {
    "code": "missing_customer_rows",
    "message": "Payload must include customer_rows."
  }
}
```

The API should not expose raw tracebacks in responses.

## Local Limits

- Local-only host: `127.0.0.1`
- Default port: `8765`
- Maximum request size: 2 MB
- No authentication
- No production vault
- No persistent audit store
- No production monitoring

