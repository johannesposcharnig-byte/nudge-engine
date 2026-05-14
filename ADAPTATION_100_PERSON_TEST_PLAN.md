# 100-Person Adaptation Test Plan

## Purpose

This test checks whether the Nudge Engine can move from static formula review toward guarded adaptation:

- calculate treatment effects on a 100-person sample
- score optional OCEAN/TIPI signals only with consent
- generate MECE hypotheses from the available schema
- determine candidate nudges without turning psychological traits into unsupported claims
- block unsafe personalization when consent, fatigue, vulnerability or governance gates fail

## Why This Test Exists

Synthetic test data often becomes too rational:

- high openness always clicks
- low openness never clicks
- every nudge has clean effects
- users behave like personas instead of humans

This test intentionally includes contradictory behavior. The engine must learn that adaptation is probabilistic, evidence-based and governance-bounded.

## Test Steps

### Step 1: Generate 100-Person Sample

What is tested:
- deterministic sample of exactly 100 persons
- treatment/control split
- consent and vulnerability edge cases
- noisy TIPI responses
- contradictory trait-behavior patterns

Definition of Done:
- exactly 100 rows exist
- treatment and control groups are non-empty
- at least one no-consent person exists
- at least one vulnerable person exists
- at least one high-openness but resistant person exists
- at least one low-openness but clicking/exploratory person exists

Failure Signals:
- all behavior follows traits too cleanly
- no governance-sensitive rows exist
- no treatment/control contrast exists

Success Signals:
- data contains realistic inconsistency
- governance edge cases are present
- sample is reproducible by seed

### Step 2: Test Calculations

What is tested:
- TIPI reverse scoring
- OCEAN score creation with consent
- no scoring without consent
- A/B mean difference
- 95% confidence interval fields

Definition of Done:
- every consented person has an OCEAN signal
- no-consent persons have `blocked_reason=ocean_consent_required`
- A/B interval includes `effect_estimate`, `ci_lower`, `ci_upper`, `ci_method`, `sample_size`, `confidence_level`, `contains_null`
- `sample_size=100`
- `confidence_level=0.95`

Failure Signals:
- missing uncertainty fields
- confidence level below 0.90 for validation
- no-consent scores are computed
- confidence interval bounds are invalid

Success Signals:
- calculations run deterministically
- uncertainty is explicit
- no significance is claimed without CI

### Step 3: Test Hypothesis Generation

What is tested:
- schema inference detects IDs, time, outcome, treatment and psychological fields
- MECE hypotheses are generated
- psychological signals inform behavioral mechanism and segment hypotheses only as hypotheses

Definition of Done:
- all MECE groups are present
- data-quality hypothesis is testable
- target-behavior hypothesis is testable
- effect hypothesis is testable
- behavioral-mechanism hypothesis sees psychological signal
- segment-heterogeneity hypothesis sees psychological fields

Failure Signals:
- missing MECE group
- OCEAN becomes a final recommendation instead of a hypothesis
- treatment or outcome fields are not detected

Success Signals:
- hypotheses are structured and testable where data exists
- uncertainty remains visible where data is insufficient

### Step 4: Determine Candidate Nudges

What is tested:
- candidate nudge mapping from measured barriers
- no-action baseline
- governance guards before personalization
- scientifically defensible method set
- policy ranking across all available actions

Definition of Done:
- every row has a candidate nudge or `no_action`
- all methods are from the approved behavioral method set
- no-consent users get `no_action`
- vulnerable users get `no_action`
- high-fatigue users are held or assigned no-action, not pressure nudges
- candidate nudges are marked as `hypothesis`, not final effect claims
- every row has a policy ranking containing `no_action`
- ranking is ordered by risk-adjusted reward
- blocked active actions remain visible with reason codes
- final selected active action is only a hypothesis, not a proven recommendation

Failure Signals:
- loss frame or pressure nudges for vulnerable/fatigued users
- OCEAN-only nudge selection
- unsupported method appears
- ranking hides blocked actions
- active action wins without beating no-action
- no-consent, protected-state or high-fatigue rows receive active nudges

Success Signals:
- nudges are generated conservatively
- no-action is used as a real baseline
- governance-sensitive users are protected
- policy can compare several actions per person
- final action is selected from a transparent ranking

### Step 5: Orchestrator Formula Review

What is tested:
- A/B formula review accepts only with treatment/control and CI
- reward/policy remains gated by reward calibration, no-action and guardrails
- no-action baseline is measured as an object, not represented by a boolean
- guardrails are semantically complete, not just present

Definition of Done:
- A/B formula review can approve the calculated interval
- policy review does not rely on OCEAN alone
- policy review includes guardrails and no-action baseline
- reward policy holds if semantic guardrails are missing
- reward policy holds if no-action baseline is not measured
- no-action can win when active reward is weak or risk-adjusted reward is negative

Failure Signals:
- formula review approves without CI
- policy approves OCEAN-only logic
- missing guardrails are ignored
- `no_action_baseline=true` is treated as sufficient evidence
- fatigue, exposure or unknown vulnerability do not affect policy approval

Success Signals:
- formula gate, evidence gate and governance gate agree
- approval is based on data and CI, not personality assumptions
- reward ranking compares every active action against no-action
- governance-first reward blocks unsafe action ranking before optimization

## Overall Definition of Done

- all automated tests pass
- syntax check passes
- 100-person adaptation sample is reproducible
- calculations, hypotheses and nudge candidates are all tested
- no OCEAN-only policy approval is possible
- no no-consent psychological personalization is possible
- final outputs remain hypotheses until real customer data validates effects
