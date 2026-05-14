# Validation Acceptance Criteria

## Purpose

This document defines when the Nudge Engine formula and agent workflow is accepted as technically and scientifically reviewable.

## Current Acceptance Rules

- Every formula must have a registered formula class.
- Every formula must list variables, assumptions and required context.
- Every effect estimate must include uncertainty fields or produce a clear `hold`.
- `confidence` is agent certainty and must not be used as statistical significance.
- `confidence_level` is the statistical confidence level.
- Default confidence level is `0.95`.
- `0.90` is exploratory only.
- No formula may claim significance before data or simulation results exist.
- No agent may receive or rely on Full Context by default; Evidence Pack is the standard.
- Full Context requires `full_context_required` plus `full_context_reason`.
- Each Agent run must expose context budget metadata and selected sources.
- Each selected source must expose retrieval, evidence and lifecycle metadata.
- `blocked` and `deprecated` sources must not support reasoning or approval.
- Unresolved evidence conflicts must produce `hold`.
- Critical prompt-injection warnings must produce `hold`.
- Every Agent context must pass the Leonidas security review before reasoning.
- `safe_to_reason=false` from Leonidas must block agent execution before reasoning starts.
- `safe_to_execute=false` from Leonidas must block approval or rollout decisions.
- Leonidas must detect prompt injection, governance bypass, reward or policy override attempts, unsafe sources and out-of-range normalized behavioral signals.
- Leonidas must detect prompt injection in tabular customer rows and text fields.
- Leonidas must block secret exposure and hold direct PII exposure until pseudonymized.
- Direct PII must be split into vault records before customer analytics rows enter agent context.
- Agent context, Evidence Pack, Run State and reports must use `subject_id` instead of direct identifiers.
- Pseudonymization must generate audit events and keep vault records separate from analytics rows.
- Reports must not expose direct PII, vault payloads or raw identifier field names.
- Reports must separate agent confidence from statistical `confidence_level`.
- Reports must not allow significance claims unless required CI fields are complete, the CI excludes the null and `confidence_level >= 0.95`.
- Leonidas must hold data with duplicate unique event IDs, invalid timestamps, label leakage fields or treatment/control contamination.
- Stale governance-critical sources must produce `hold`.
- Weak or draft evidence must not silently override approved high evidence.
- Policy and reward formulas remain `hold` until reward calibration, no-action baseline and guardrails are present.
- Policy and reward formulas require a measured no-action baseline object, not only `no_action_baseline=true`.
- Policy and reward formulas require semantic guardrails: consent, opt-out, frequency cap, cooldown, fatigue threshold, vulnerability unknown hold, protected-state no-action, manipulation denylist, no-action monitoring and harm monitoring.
- Active nudges must `hold` when vulnerability status is unknown, fatigue is above threshold, cumulative exposure exceeds frequency cap or manipulation-sensitive methods lack governance review.
- DR-OPE remains `hold` until overlap, propensity clipping, cross-fitting and support checks are present.
- OCEAN/TIPI requires explicit `ocean_consent=true` before scoring or personalization.
- OCEAN/TIPI remains `hypothesis_only` and cannot be the only basis for policy, reward or intervention approval.
- Psychological trait claims cannot imply causality, effect, significance or user intent without behavioral evidence.

## Required Uncertainty Fields

For effect estimates, the uncertainty object must include:

- `effect_estimate`
- `ci_lower`
- `ci_upper`
- `ci_method`
- `sample_size`
- `confidence_level`
- `contains_null`

## Orchestrator Decision Rules

- `approve`: formula is defined, measurable, theoretically plausible and passes required statistical and governance gates.
- `revise`: formula is structurally useful but missing operational precision.
- `reject`: formula is not methodologically viable in the current form.
- `hold`: data, uncertainty, support, reward calibration or governance gates are missing.

## Technical Acceptance Checks

Run:

```bash
python3 -m unittest discover -s 'Nudge Engine/tests' -p 'test_*.py'
PYTHONPYCACHEPREFIX='/tmp/nudge_engine_pycache' python3 -m compileall -q 'Nudge Engine/src' 'Nudge Engine/tests'
```

Expected result:

- all tests pass
- compile check exits successfully

## Current Test Coverage

- model selection
- Evidence Pack context minimization
- Full Context exception rule
- compact Run State update
- Retrieval and source metadata
- blocked/deprecated source gate
- prompt-injection security gate
- Leonidas security review schema and Evidence Pack integration
- governance bypass, reward shortcut and data-poisoning security blockers
- secret exposure, PII exposure, row-level injection and data-integrity security blockers
- PII vault boundary, pseudonymization, redaction summary and audit events
- Decision reporting, Markdown rendering, PII-safe segment view and CI/significance gate
- unresolved conflict gate
- stale governance-critical lifecycle gate
- weak evidence override warning
- formula review sequence
- formula registry coverage
- confidence versus confidence level separation
- CI missing -> `hold`
- CI excluding null -> `approve`
- CI containing null -> `revise`
- DR-OPE missing support checks -> `hold`
- policy missing reward calibration -> `hold`
- reward policy missing semantic guardrails -> `hold`
- reward policy missing measured no-action baseline -> `hold`
- no-action can beat active nudge under fatigue or low incremental reward
- policy ranking includes no-action and all available actions
- policy ranking keeps blocked actions visible with reason codes
- selected active actions remain `hypothesis` until validated with real outcome data
- behavioral method registry contains all runtime actions and meta methods
- every behavioral method has required signals, mechanism, manipulation risk and claim type
- unknown behavioral methods are blocked
- method-specific blockers must not hide global safety blockers such as missing consent or control-group assignment
- heuristic layer outputs are always hypotheses, never customer diagnoses
- active heuristics require required signals before support is assigned
- reference-only heuristics do not influence policy ranking
- excluded heuristics can only create governance risk, never optimization reward
- heuristic-only policy approval is blocked
- correlation support cannot create causal claims
- all registered formulas can be reviewed
- simulated A/B confidence intervals
- exploratory bootstrap intervals
- TIPI/OCEAN scoring, consent gate and OCEAN-only policy blocker
- synthetic TIPI fixture with contradictory non-rational behavior patterns
