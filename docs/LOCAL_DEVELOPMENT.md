# Local Development

## Requirements

- Python 3.12 recommended
- No external Python dependencies are required for the current local test path

Run all commands from the repository root.

## Run Tests

```bash
PYTHONPYCACHEPREFIX=/tmp/nudge_engine_pycache python3 -m unittest discover -s tests
```

## Compile Check

```bash
PYTHONPYCACHEPREFIX=/tmp/nudge_engine_pycache python3 -m compileall src tests scripts
```

## Start Local API

```bash
python3 -m src.api
```

Expected:

```text
Nudge Engine local API running at http://127.0.0.1:8765
```

## Run Local API Smoke Test

In another terminal:

```bash
python3 scripts/smoke_test_api.py
```

Expected output includes:

```text
Local API smoke test OK
```

## Test Payload

Use:

```text
tests/fixtures/api_activation_payload.json
```

The payload contains synthetic activation rows with:

- identity fields for pseudonymization
- email fields to test PII removal
- consent
- timestamp
- treatment/control assignment
- activation outcome
- friction/resistance/fatigue signals
- no-action baseline
- guardrails

## Dashboard Preview

Open:

```text
dashboard/index.html
```

The dashboard can load:

- a generated Decision Report JSON
- a `customer_rows` JSON payload if the local API is running

## Safe GitHub Push

Use:

```bash
bash scripts/safe_checkpoint_push.sh "checkpoint: describe the change"
```

The script runs tests, compile check, updates `CHANGELOG_AUTO.md`, commits and pushes.

