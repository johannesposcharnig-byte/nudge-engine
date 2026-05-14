# Engine Functionality Check

## Executive Result

Status: `service_entrypoint_functional`

The Nudge Engine is functionally testable as a backend library with a unified analysis service, validated modules, synthetic end-to-end-like runs, guarded formula review, reward/policy checks, PII handling, reporting, and a static dashboard preview.

It is not yet fully operational as a product flow because there is no backend/API connection between the dashboard and the engine.

## What Is Functional Now

### 1. Test Stability

Latest local validation:

- Unit and integration-style tests: `125 tests OK`
- Python syntax check: passed for `src` and `tests`

This means the existing modules are internally consistent and currently executable.

### 2. Security Gate

Functional components:

- Leonidas security checks
- Prompt-injection detection
- source validation
- lifecycle blocker handling
- governance-critical stale-source hold logic
- policy/reward integrity checks

Functional meaning:

The engine can block unsafe or untrusted inputs before agent reasoning or formula review continues.

Remaining limitation:

Security is implemented as a code gate, but not yet exposed as a production ingestion boundary behind an API.

### 3. PII Boundary

Functional components:

- customer rows can be pseudonymized
- analytics rows can be separated from vault records
- report rendering avoids direct PII in tested outputs

Functional meaning:

The engine has a working privacy boundary for testable local processing.

Remaining limitation:

The PII vault is still a local implementation pattern. A production-grade setup needs encrypted storage, key management, access controls, and audit logging outside the normal agent runtime.

### 4. Customer Data Intake

Functional components:

- schema checks
- required fields
- consent checks
- outcome variable checks
- security and source checks
- clarification questions when data is incomplete

Functional meaning:

The engine can decide whether customer data is ready for analysis or whether it must hold and ask questions.

Runtime entrypoint:

- `src/analysis_service.py`
- `run_analysis(AnalysisRequest | dict)`

Functional meaning:

Customer-like rows can now enter one service function and receive a dashboard-ready report object.

Remaining limitation:

This is a local Python service entrypoint, not yet an HTTP API.

### 5. Hypothesis-First Workflow

Functional components:

- MECE hypothesis generation
- testable vs. not-testable-yet status
- evidence gate fields
- blocker logic for unsupported claims

Functional meaning:

The engine can prevent agents from jumping straight to recommendations without first structuring hypotheses.

Runtime integration:

The analysis service builds MECE hypotheses from the uploaded row schema and structured context.

Remaining limitation:

Natural-language question interpretation is still conservative. The service does not invent hidden outcomes or causal designs from vague wording.

### 6. Formula Review

Functional components:

- formula registry
- formula review sequence
- statistical, data, devil's advocate, research, evaluation, and governance review modes
- confidence interval rules
- `hold` when uncertainty or identification is missing

Functional meaning:

The engine can review formula families and block claims when statistical requirements are missing.

Runtime integration:

The analysis service calculates an A/B mean-difference confidence interval when it finds a numeric outcome plus treatment/control groups.

Remaining limitation:

Formula calculation is not yet universal for every formula family and arbitrary dataset shape. Unsupported data still produces `hold` instead of a causal claim.

### 7. Reward And Policy Logic

Functional components:

- action vs. no-action comparison
- guardrails
- reward calibration checks
- protected-state handling
- fatigue and vulnerability checks
- heuristic support as explanation, not standalone approval

Functional meaning:

The engine can rank candidate actions conservatively and block policy approval when reward, no-action baseline, or governance is insufficient.

Remaining limitation:

Policy learning is not yet a live learning system. It is a guarded decision and validation layer, not a deployed adaptive policy loop.

### 8. Synthetic End-To-End-Like Validation

Functional components:

- 100-person synthetic test dataset
- non-perfect, noisy behavioral signals
- OCEAN/TIPI-derived signals with consent gates
- A/B confidence interval calculation
- nudge candidate generation
- policy decision checks
- formula review

Functional meaning:

The engine can be exercised through a realistic test-like pipeline.

Remaining limitation:

Synthetic data proves that the pipeline works structurally. It does not prove real customer effect, real significance, or causal validity.

### 9. Reporting

Functional components:

- structured decision report
- executive summary
- uncertainty and CI gate
- hypotheses
- nudge recommendations
- segment view
- next actions
- optional system checks

Functional meaning:

The engine can transform outputs into a user-facing report format.

Runtime integration:

The report builder is now fed by the analysis service.

Remaining limitation:

Report quality still depends on the data fields available to the service.

### 10. Dashboard Preview

Functional components:

- static dashboard
- sample report rendering
- JSON upload preview
- local rule-based report chat
- result sections for overview, results, evidence, nudges, and chat

Functional meaning:

The dashboard can display engine-style results.

Remaining limitation:

The dashboard is not connected to the engine. It currently loads `dashboard/data/sample-report.json` or user-uploaded JSON and does not call a backend.

## What Is Not Yet Fully Functional

### 1. No Backend API

Missing:

- HTTP endpoint for dashboard submissions
- file upload handling
- request validation
- report response
- secure runtime boundary

Impact:

The dashboard cannot trigger the real engine yet.

### 2. No Dashboard-To-Engine Connection

Missing:

- frontend `fetch()` to an analysis endpoint
- loading states for real execution
- error handling from engine holds/blockers
- report hydration from live engine response

Impact:

The dashboard is a presentation shell, not the operational UI yet.

### 3. No Real Customer Causality Without Data Design

Missing unless customer data provides it:

- treatment/control logic
- time ordering
- sufficient sample size
- confidence interval
- identification assumptions
- experiment or quasi-experiment design

Impact:

The engine can define and enforce causal rules, but it cannot honestly claim causal effect unless the data supports it.

### 4. No Production PII Vault

Missing:

- encryption at rest
- key management
- access policy
- audit trail for identity lookup
- separation from agent runtime

Impact:

The current vault is a development architecture pattern, not a production privacy system.

## Functional Classification

### Current State

`service_entrypoint_validated`

The codebase has working modules, a single local analysis service, and tests for happy path, PII safety, security blocking, missing outcome, and missing identity.

### Not Yet

`operational_product_flow`

This requires an API plus dashboard integration.

## Recommended Next Step

Build a narrow API around `run_analysis()` before connecting the dashboard.

Reason:

The service now proves the engine can run as one coherent local process. The next step is exposing that process through a controlled HTTP boundary.

Implemented service flow:

1. Accept `question`, `customer_rows`, and optional `config`.
2. Run Leonidas preflight on raw external content.
3. Pseudonymize identity fields before analysis.
4. Run customer data intake.
5. Generate MECE hypotheses.
6. Run only calculations supported by available data.
7. Evaluate nudges and reward/policy guardrails.
8. Build a decision report.
9. Return `approve`, `revise`, `hold`, or `reject` with reasons.

## Acceptance Criteria Before Dashboard/API Connection

- A test can pass raw customer-like rows into one service function: done.
- The service returns a complete report object: done.
- PII does not appear in the report: done.
- Missing outcome or missing treatment/control creates `hold` or clarification questions: done.
- Prompt injection in uploaded rows blocks before reasoning: done.
- No causal or significance claim is produced without valid uncertainty fields.
- Nudge recommendations include evidence status and no-action reasoning.
- Existing and new tests remain green: `125 tests OK`.

## Bottom Line

The Nudge Engine is not "only static" anymore at the code level.

But it is not yet a live operational engine behind the dashboard.

The correct next move is to implement a small API around `run_analysis()`, then connect the dashboard to that API.
