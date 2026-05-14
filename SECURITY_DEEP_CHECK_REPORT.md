# Security Deep Check Report

## Snapshot

- Date: 2026-05-14
- Scope: local source code, security gate, orchestration gate, context budget, reward/policy blockers, data-integrity checks and adversarial security tests
- Primary security owner: Leonidas
- Orchestration owner: Orchestrator
- Result: passed after Security Hardening v2

## Who Performs The Deep Security Check

Leonidas performs the technical security and integrity check.

For deep checks, Leonidas is coordinated by the Orchestrator with these review perspectives:

- Leonidas: prompt injection, governance bypass, reward/policy override, unsafe sources, secrets, PII, data poisoning and data integrity
- Orchestrator: confirms that `safe_to_reason` and `safe_to_execute` are enforced
- Critic & Governance: evaluates manipulation, consent, dark-pattern and protected-state risks
- Data & Measurement: validates schema, ranges, source quality, duplicate IDs, timestamp integrity and contamination risks
- Policy & Reward: validates no-action baseline, reward calibration and guardrails

Leonidas is a mandatory security gate, not a sixth core agent. This keeps the 5-agent architecture simple while making security non-optional.

## Code Areas Reviewed

- `src/security.py`
- `src/context_budget.py`
- `src/orchestrator.py`
- `src/reward.py`
- `src/agents/base.py`
- `tests/test_security.py`
- `tests/test_backward_validation.py`
- `tests/test_orchestrator.py`
- `tests/test_reward.py`

## Checks Performed

### 1. Prompt Injection

Reviewed:

- Pattern list in Leonidas
- Text normalization for punctuation and repeated whitespace
- Flattening of external text fields
- Scan of `prompt`, `retrieval_query`, `external_content`, `source_metadata`, `conflicts`, `raw_context`, `raw_documents`, `full_context`, `all_documents`, `documents`, `file_contents`, `conversation_history`
- Scan of customer-row fields such as notes, feedback and CSV-like text cells
- Pre-dispatch block in Orchestrator

Hardening:

- Added normalized phrase matching.
- Added row-level scanning for customer data.
- Added adversarial tests for obfuscated and row-level prompt injection.

Status:

- Passed.

### 2. Secrets And PII Exposure

Reviewed:

- OpenAI-style API keys
- GitHub tokens
- Slack tokens
- AWS access key pattern
- Generic `api_key`, `secret`, `token`, `password`, `credential` assignments
- Emails
- Phone-number-like strings

Hardening:

- Added secret-pattern detection with `action=block`.
- Added PII-pattern detection with `action=hold`.
- Added tests for API-key exposure and email exposure.

Security rule:

- Secrets block reasoning because credentials must be removed and rotated.
- Direct PII holds execution until pseudonymized.

Status:

- Passed.

### 3. Governance Bypass

Reviewed:

- `bypass_governance`
- `ignore_guardrails`
- `unsafe_override`
- `force_approve`
- Prompt injection phrases such as `disable governance` and `override governance`

Finding:

- Explicit bypass flags and prompt-level bypass attempts are blocked.

Status:

- Passed.

### 4. Reward And Policy Override

Reviewed:

- `reward_override_request`
- `heuristic_only_policy`
- `ocean_only_decision`
- `disable_no_action_baseline`
- Orchestrator enforcement of `safe_to_execute=false`
- Reward blockers for guardrails and no-action baseline

Finding:

- Reward shortcut attempts do not block reasoning, but block execution and approval.
- This is correct because some contexts can still be analyzed safely, but cannot be approved.

Status:

- Passed.

### 5. Data Poisoning And Schema Integrity

Reviewed:

- Normalized behavioral signal ranges
- Numeric values and CSV-style numeric strings
- `customer_rows`, `data_sample`, `records`, `rows`
- Signal keys such as `fatigue_signal`, `resistance_signal`, `friction_signal`, `trust_gap_signal`

Hardening:

- Added numeric coercion for string values.
- Added handling for `NaN` and infinite values.
- Added adversarial test for CSV-style value `"1.4"`.

Status:

- Passed.

### 6. Data Integrity

Reviewed:

- Duplicate unique event IDs
- Invalid timestamp-like fields
- Label leakage fields such as `future_`, `post_treatment`, `post_nudge`, `after_treatment`, `after_nudge`, `label`, `target`
- Treatment/control contamination where the same entity appears in multiple groups

Hardening:

- Added duplicate unique-ID scanner.
- Added timestamp parser check.
- Added label-leakage scanner.
- Added treatment/control contamination scanner.
- Added adversarial tests for all four cases.

Status:

- Passed.

### 7. Source Integrity

Reviewed:

- `trusted=false`
- `validation_status=blocked`
- `validation_status=deprecated`
- `lifecycle_status=blocked`
- `lifecycle_status=deprecated`
- Retrieval governance in `context_budget.py`

Finding:

- Blocked sources create hard blocks.
- Deprecated or untrusted sources hold execution.
- Retrieval governance also blocks selected blocked/deprecated sources.

Status:

- Passed.

### 8. Full Context And External Content

Reviewed:

- `external_content` redaction
- Large context keys
- `full_context_required`
- `full_context_reason`
- `allowed_context_keys`

Finding:

- `external_content` is scanned before minimization and then stripped.
- Full context remains an explicit exception requiring a reason.
- Large context fields are scanned by Leonidas.

Status:

- Passed.

### 9. Orchestrator Enforcement

Reviewed:

- `dispatch()`
- `evaluate_evidence_gate()`
- `preflight_blocked_message()`
- `update_run_state()`

Finding:

- `safe_to_reason=false` blocks before agent reasoning.
- `safe_to_execute=false` blocks approval attempts.
- Last security review is stored in compact run state.

Status:

- Passed.

## Fixes Implemented

### Fix 1: Obfuscated Prompt Injection Detection

File:

- `src/security.py`

Change:

- Added `_normalize_text()`.
- Added `NORMALIZED_PROMPT_INJECTION_PATTERNS`.
- Prompt injection scan checks original lower-case text and normalized text.

Security improvement:

- Blocks simple obfuscations like `IGNORE---previous   instructions!!!`.

### Fix 2: Row-Level Prompt Injection Detection

File:

- `src/security.py`

Change:

- Added `customer_rows`, `data_sample`, `records` and `rows` to scanned external text values.

Security improvement:

- Blocks hostile instructions hidden in customer notes, feedback or CSV cells.

### Fix 3: Secrets And PII Detection

File:

- `src/security.py`

Change:

- Added `SECRET_PATTERNS`.
- Added `PII_PATTERNS`.
- Added `_scan_secrets_and_pii()`.

Security improvement:

- Secrets block reasoning.
- Direct PII holds execution until pseudonymized.

### Fix 4: CSV-Style Data Poisoning Detection

File:

- `src/security.py`

Change:

- Added `_coerce_number()`.
- Data poisoning scan handles numeric strings, `NaN` and infinite values.

Security improvement:

- Blocks poisoned behavioral signals such as `"1.4"` for fields expected in `[0, 1]`.

### Fix 5: Data Integrity Scanner

File:

- `src/security.py`

Change:

- Added duplicate unique-ID check.
- Added invalid timestamp check.
- Added label leakage check.
- Added treatment/control contamination check.

Security improvement:

- Prevents unsafe causal evaluation and model training from contaminated or leaky data.

### Fix 6: Adversarial Security Tests

File:

- `tests/test_security.py`

Change:

- Added tests for row-level injection.
- Added tests for secrets and PII.
- Added tests for duplicate event IDs, invalid timestamps, label leakage and treatment/control contamination.

Security improvement:

- Prevents regression of Security Hardening v2.

## Test Results

Security-specific tests:

```bash
python3 -m unittest discover -s 'Nudge Engine/tests' -p 'test_security.py'
```

Observed:

- `Ran 16 tests`
- `OK`

Full regression suite:

```bash
python3 -m unittest discover -s 'Nudge Engine/tests' -p 'test_*.py'
```

Observed:

- `Ran 106 tests`
- `OK`

Compile check:

```bash
PYTHONPYCACHEPREFIX='/tmp/nudge_engine_pycache' python3 -m compileall -q 'Nudge Engine/src' 'Nudge Engine/tests'
```

Observed:

- Passed.

## Remaining Security Risks

### 1. Pattern-Based Prompt Injection Is Still Limited

Leonidas now handles simple obfuscation and row-level injection, but not advanced semantic attacks.

Examples:

- indirect policy override phrasing
- multilingual attacks
- encoded instructions
- instruction smuggling inside long documents

Recommended next step:

- Add an adversarial prompt-injection fixture pack with paraphrases, multilingual variants and encoded examples.

### 2. Data Integrity Is Stronger But Not Yet Statistical

Leonidas now detects structural problems, but does not yet perform statistical anomaly detection.

Missing:

- suspicious distribution shifts
- adversarially perfect outcomes
- unnatural class balance
- impossible correlations
- sudden source-level drift

Recommended next step:

- Add statistical anomaly checks for production-like datasets.

### 3. Secrets Scanning Is Pattern-Based

The current scanner covers common token and credential patterns.

Missing:

- custom enterprise secret formats
- entropy-based secret detection
- automatic redaction
- rotation workflow

Recommended next step:

- Add entropy-based secret detection and redaction before Evidence Pack creation.

### 4. Runtime Tool Security Is Minimal

The engine currently does not execute external tools as part of its runtime, but future integrations may.

Recommended next step:

- Add explicit tool-allowlist and tool-call audit schema before connecting external systems.

### 5. No Git Audit Trail

The folder is not a Git repository.

Impact:

- no commit history
- no diff-based review
- harder change audit

Recommended next step:

- Initialize or move into a versioned repository before production-like validation.

## Final Security Status

Current local security status:

- `accepted for next development iteration`

Not yet:

- `production security approved`

Reason:

- The current checks are now strong for local orchestration, prompt injection, governance bypass, reward shortcut, secrets, PII, structural data integrity and basic data poisoning.
- Production approval requires multilingual/semantic adversarial fixtures, entropy-based secrets detection, statistical anomaly detection, runtime tool security and versioned audit trail.
