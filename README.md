# Nudge Engine

Developer-first repository for a governed behavioral decision support engine.

The Nudge Engine analyzes activation and engagement data, creates testable behavioral hypotheses, evaluates evidence and uncertainty, and produces governance-aware nudge recommendations. It is intentionally conservative: if the data cannot support a claim, the engine must say so.

## What This Project Is

- A local-first behavioral decision support system.
- A guarded analysis pipeline for customer activation data.
- A hypothesis-first engine with evidence, privacy, security and governance gates.
- A developer prototype that already includes a local API, dashboard preview, tests, PII pseudonymization, result quality checks and audit lineage.

## What This Project Is Not

- Not an autonomous nudge execution system.
- Not a production personalization platform.
- Not a reinforcement-learning rollout engine.
- Not a system that can claim causal impact without experiment or identification evidence.
- Not production-ready for real customer PII without additional security, auth, vault and deployment controls.

## Core Principles

- Hypotheses before recommendations.
- Evidence before claims.
- Recommendation ranking is not proof of effect.
- `action_fit` and `effect_evidence` stay separate.
- No direct PII should enter agent context, reports or dashboard views.
- Significance requires complete CI fields, CI excluding null, and `confidence_level >= 0.95`.
- Security and governance may block analysis or rollout.

## Current Architecture

The local runtime follows this path:

```text
Customer rows
  -> Security & Integrity Gate
  -> PII pseudonymization
  -> Data Contract / Data Readiness
  -> MECE hypotheses
  -> Evidence / Claim Permission
  -> Calculation layer
  -> Reward / Policy layer
  -> Result Quality
  -> Decision Report
  -> Dashboard / API response
  -> Audit Lineage
```

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Quickstart

Run from the repository root.

### 1. Run Tests

```bash
PYTHONPYCACHEPREFIX=/tmp/nudge_engine_pycache python3 -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/tmp/nudge_engine_pycache python3 -m compileall src tests scripts
```

### 2. Start Local API

```bash
python3 -m src.api
```

The API runs at:

```text
http://127.0.0.1:8765
```

### 3. Run API Smoke Test

In a second terminal:

```bash
python3 scripts/smoke_test_api.py
```

The smoke test uses:

```text
tests/fixtures/api_activation_payload.json
```

### 4. Open Dashboard

Open:

```text
dashboard/index.html
```

Upload either:

- a Decision Report JSON, or
- a `customer_rows` JSON payload while the local API is running.

## Local API

Available endpoints:

- `GET /health`
- `POST /analyze`

Example:

```bash
curl -X POST http://127.0.0.1:8765/analyze \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/api_activation_payload.json
```

See [docs/API.md](./docs/API.md) and [LOCAL_API_TESTING.md](./LOCAL_API_TESTING.md).

## Documentation

Start here:

- [Documentation Index](./docs/README.md)
- [Project Status](./docs/PROJECT_STATUS.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Local Development](./docs/LOCAL_DEVELOPMENT.md)
- [API](./docs/API.md)
- [Security and Privacy](./docs/SECURITY_AND_PRIVACY.md)
- [Evidence and Claims](./docs/EVIDENCE_AND_CLAIMS.md)
- [Dashboard](./docs/DASHBOARD.md)
- [Roadmap](./docs/ROADMAP.md)
- [Human Changelog](./docs/CHANGELOG.md)

## Current Status

Implemented and tested locally:

- Engine entrypoint: `run_analysis()`
- Local API: `POST /analyze`
- Local API smoke test
- Dashboard preview and API upload flow
- PII pseudonymization boundary
- Security & Integrity Gate
- Data Contract and Data Readiness
- MECE hypothesis generation
- Evidence and Claim Permission
- Reward and no-action policy logic
- Result Quality
- Audit Lineage
- Unit tests and GitHub validation workflow

Still blocked for production:

- Authentication
- Encrypted production PII vault
- Persistent audit store
- Deployment and monitoring
- Access control
- Data retention policy
- Incident process
- Legal/privacy review

## Safety Notice

This repository is pilot-stage. Do not commit raw customer data, vault files, exported private reports or production secrets. The `.gitignore` excludes common sensitive paths, but developers remain responsible for checking staged changes before pushing.

Use the safe checkpoint workflow:

```bash
bash scripts/safe_checkpoint_push.sh "checkpoint: describe the change"
```

See [GITHUB_AUTOMATION.md](./GITHUB_AUTOMATION.md).
