# Full Validation Test Protocol

## Purpose

This protocol documents the current end-to-end validation of the Nudge Engine.

It verifies whether the engine is technically runnable, scientifically guarded, hypothesis-first, evidence-gated, security-aware and safe enough for the next development iteration.

## Validation Snapshot

- Date: 2026-05-10 19:17:01 CEST
- Workspace: `/Users/johannesposcharnig/Desktop/Nudge Engine/Nudge Engine`
- Test command: `python3 -m unittest discover -s 'Nudge Engine/tests' -p 'test_*.py'`
- Compile command: `PYTHONPYCACHEPREFIX='/tmp/nudge_engine_pycache' python3 -m compileall -q 'Nudge Engine/src' 'Nudge Engine/tests'`
- Test result: `97 tests OK`
- Compile result: successful
- Git status: not available because the folder is not a Git repository

## Acceptance Basis

The validation is based on:

- [Validation Acceptance Criteria](./VALIDATION_ACCEPTANCE.md)
- [README](./README.md)
- [Agent Message Schema](./AGENT_MESSAGE_SCHEMA.md)
- [Security & Integrity Layer](./SECURITY_INTEGRITY_LAYER.md)
- [Behavioral Method Matrix](./BEHAVIORAL_METHOD_MATRIX.md)
- [Heuristic Layer Plan](./HEURISTIC_LAYER_PLAN.md)
- [OCEAN Signal Model](./OCEAN_SIGNAL_MODEL.md)
- [Formula Spec](./FORMULA_SPEC_CLEAN.md)

## Definition Of Done

The full validation is accepted only if:

- All unit tests pass.
- Python source and test files compile.
- Every formula can be routed through the orchestrator.
- Evidence Gate blocks unsupported claims.
- Confidence and statistical confidence level are not confused.
- CI-dependent formulas hold or revise when uncertainty is missing or weak.
- Policy and reward approval requires reward calibration, measured no-action baseline and semantic guardrails.
- Leonidas blocks unsafe context before agent reasoning.
- OCEAN/TIPI remains consent-gated and hypothesis-only.
- Heuristic/Bias layer cannot create causal claims or approve policy alone.
- Synthetic data contains realistic non-rational edge cases, not only rational personas.

## Test Layers

### 1. Syntax And Import Integrity

Goal:
Ensure all Python modules and tests are syntactically valid.

Command:

```bash
PYTHONPYCACHEPREFIX='/tmp/nudge_engine_pycache' python3 -m compileall -q 'Nudge Engine/src' 'Nudge Engine/tests'
```

Expected:

- Compile exits successfully.
- No syntax errors.
- No import-time failures.

Observed:

- Passed.

### 2. Full Regression Suite

Goal:
Run the complete automated test suite.

Command:

```bash
python3 -m unittest discover -s 'Nudge Engine/tests' -p 'test_*.py'
```

Expected:

- All tests pass.

Observed:

- `Ran 97 tests in 0.593s`
- `OK`

## Coverage Matrix

| Layer | Test File | What Is Tested | Current Result |
|---|---|---|---|
| Orchestration | `tests/test_orchestrator.py` | model selection, formula routing, Evidence Pack, source metadata, evidence gate, formula gate, CI rules, compact run state | Passed |
| Backward Validation | `tests/test_backward_validation.py` | backwards workflow from intake to calculation, prompt injection block, blocked sources, policy governance, stale evidence | Passed |
| Security | `tests/test_security.py` | Leonidas security review, prompt injection, reward shortcut, governance bypass, data poisoning, Evidence Pack integration | Passed |
| Reward And Policy | `tests/test_reward.py` | guardrails, no-action baseline, vulnerability hold, fatigue, exposure cap, manipulation review, action ranking | Passed |
| Behavioral Methods | `tests/test_behavioral_methods.py` | approved method registry, method signals, social proof, loss frame, cognitive ease, unknown method block | Passed |
| Heuristic Layer | `tests/test_behavioral_heuristics.py` | active/reference/excluded biases, support levels, method bonus, causal-claim block, heuristic-only policy block | Passed |
| OCEAN/TIPI | `tests/test_ocean.py` | TIPI scoring, consent gate, out-of-range items, OCEAN-only policy block, non-rational fixture patterns | Passed |
| Simulation | `tests/test_simulation.py` | A/B CI with known effect, exploratory bootstrap CI | Passed |
| Synthetic Fixture | `tests/test_synthetic_fixture.py` | required intake columns, non-rational personas, governance-sensitive rows, intake schema | Passed |
| 100-Person Adaptation | `tests/test_adaptation_100_person.py` | realistic 100-person sample, CI calculation, hypothesis generation, nudge candidates, orchestrator review | Passed |

## Detailed Test Protocol

### A. Orchestrator And Agent Runtime

Tests:

- Default model selection uses `GPT-5.4-Mini`.
- Deep analysis and formula review switch to a stronger model.
- Formula review sequence is short and ordered.
- Five core agent roles remain consolidated.
- All registered formulas can be reviewed.
- Run State is compactly updated after each step.

Pass Criteria:

- Orchestrator routes tasks deterministically.
- No step bypasses Evidence Gate.
- Formula review uses the required sequence.

Result:

- Passed.

### B. Evidence Pack And Token Budget

Tests:

- Agent context uses Evidence Pack by default.
- Full Context is stripped unless an explicit exception reason is present.
- Evidence Pack contains retrieval metadata and source metadata.
- Context budget contains document and section limits.

Pass Criteria:

- Agents do not receive unrestricted repository context.
- Retrieval has selection reason, relevance score and lifecycle fields.
- Full Context requires `full_context_required` plus `full_context_reason`.

Result:

- Passed.

### C. Evidence Governance

Tests:

- Blocked sources cause `hold`.
- Deprecated or blocked sources cannot support reasoning.
- Stale governance-critical sources cause `hold`.
- Unresolved conflicts block approval.
- Weak or draft evidence cannot silently override approved high evidence.

Pass Criteria:

- Unresolved evidence problems never produce `approve`.
- Conflicts remain visible and route to the right escalation target.

Result:

- Passed.

### D. Leonidas Security Layer

Tests:

- Prompt injection is detected and blocked.
- Governance bypass is detected and blocked.
- Reward or policy shortcut attempts produce `hold`.
- Out-of-range normalized behavioral signals produce `hold`.
- Benign context passes.
- Leonidas security review is included in Evidence Pack.
- Pre-dispatch blocks unsafe context before agent reasoning.

Pass Criteria:

- `safe_to_reason=false` blocks dispatch before reasoning.
- `safe_to_execute=false` blocks approval or rollout.
- Security results are auditable through `security_review`.

Result:

- Passed.

### E. Formula And Statistical Validation

Tests:

- Agent `confidence` is separate from statistical `confidence_level`.
- A/B formula holds without confidence interval.
- A/B formula can approve when CI excludes null.
- A/B formula revises when CI contains null.
- Invalid CI fields cause `hold`.
- DR-OPE holds without overlap, clipping, cross-fitting and support checks.
- All registered formulas can be reviewed.

Pass Criteria:

- No significance claim without data or simulation.
- CI fields are required for effect estimates.
- `0.95` remains the standard confidence level.
- `0.90` is treated as exploratory.

Result:

- Passed.

### F. Customer Data Intake And Hypotheses

Tests:

- Missing target behavior creates `hold` and clarification questions.
- Clear schema creates MECE hypotheses.
- Effect claims without data or CI are blocked.
- Causal claims without identification strategy are blocked.

Pass Criteria:

- The engine asks questions when customer data is incomplete.
- Hypotheses precede calculation.
- Untestable hypotheses remain `not_testable_yet`.

Result:

- Passed.

### G. Reward, Policy And No-Action Baseline

Tests:

- Required semantic guardrails must be present.
- Measured no-action baseline object is required.
- Missing vulnerability status holds active nudges.
- High cumulative exposure holds active nudges.
- Manipulation-sensitive methods require governance review.
- No-action can beat active nudges.
- Policy ranking includes no-action and all candidate actions.
- Control group remains on no-action.

Pass Criteria:

- No active nudge is approved without consent, opt-out, frequency cap, fatigue threshold and harm monitoring.
- Reward does not optimize behavior without no-action comparison.
- Blocked actions remain visible with reason codes.

Result:

- Passed.

### H. Behavioral Method Registry

Tests:

- Registry contains scientific starting set.
- Every action has mechanism and hypothesis claim type.
- Social proof requires peer norm and valid reference group.
- Loss frame blocks when fatigue is elevated.
- Cognitive ease is eligible under high friction and resistance.
- Unknown methods are blocked.

Pass Criteria:

- Behavioral methods are not free text.
- Every method is auditable with signals, mechanism and governance risk.
- Manipulative or unsupported methods do not silently enter ranking.

Result:

- Passed.

### I. Heuristic And Bias Layer

Tests:

- Active, reference-only and excluded heuristics are separate.
- Availability heuristic requires recent salient event signals.
- Present bias maps to commitment, goal-setting and reminders.
- Reference-only heuristics do not affect ranking.
- Excluded heuristics create governance risk only.
- Decision fatigue blocks pressure methods and supports no-action.
- Heuristic-only policy is blocked.
- Correlation support cannot create causal claims.
- Heuristic bonus can only influence ranking when policy is otherwise allowed.

Pass Criteria:

- Biases explain hypotheses; they do not diagnose customers.
- Bias support never creates causality.
- Heuristics cannot approve policy alone.

Result:

- Passed.

### J. OCEAN/TIPI Layer

Tests:

- TIPI reverse scoring uses the 1-to-7 scale.
- TIPI scoring returns OCEAN traits.
- Missing or out-of-range TIPI items are rejected.
- TIPI requires consent.
- Orchestrator blocks OCEAN personalization without consent.
- Orchestrator blocks OCEAN-only policy approval.
- Synthetic TIPI fixture contains non-rational trait patterns.

Pass Criteria:

- OCEAN/TIPI is consent-gated.
- OCEAN remains a low-precision hypothesis signal.
- OCEAN cannot be the only basis for reward, policy or effect claims.

Result:

- Passed.

### K. Simulation And 100-Person Adaptation

Tests:

- A/B simulation CI contains known effect.
- Bootstrap CI is marked exploratory at `0.90`.
- 100-person sample contains realistic edge cases.
- Calculations produce valid 95 percent CI.
- Hypothesis generation detects data, effect and psychological signals.
- Nudge candidates are guarded and from approved method set.
- Orchestrator blocks OCEAN-only policy.

Pass Criteria:

- Simulation validates calculation mechanics.
- Synthetic data includes imperfect, non-rational behavior.
- Nudge selection remains guarded and hypothesis-based.

Result:

- Passed.

## Current Gaps And Risks

- The current validation is mostly unit and simulation based; it is not yet validation on real customer production data.
- Statistical significance is only testable where simulation or test fixtures provide outcome data.
- Causal claims still require real experiment design, treatment/control assignment or strong identification assumptions.
- Heuristic support is explanatory and not experimentally validated.
- Security checks are rule-based v1 and should later be expanded with adversarial fixture libraries.
- The folder is not a Git repository, so change history, diff review and versioned audit trail are not available.

## Recommended Next Validation Iterations

1. Real customer schema dry-run:
Validate a real anonymized customer dataset through intake, missing-field questions, hypotheses and hold/approve routing.

2. Adversarial security fixture pack:
Add malicious documents, prompt-injection variants, poisoned source metadata and reward-bypass attempts.

3. Statistical calibration suite:
Add repeated simulations for false positives, CI coverage, power and small-sample robustness.

4. Behavioral governance scenarios:
Add edge cases for vulnerable users, fatigue, repeated exposure, manipulative framing and social proof misuse.

5. End-to-end policy replay:
Run a full synthetic customer journey from data intake to method ranking, reward comparison, no-action decision and final governance gate.

## Final Status

The Nudge Engine currently passes the full local validation protocol.

Status: `accepted for next development iteration`

Not yet status: `production validated on real customer data`
