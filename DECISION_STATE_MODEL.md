# Decision State Model

## Purpose

The decision state model prevents the engine from collapsing security, evidence, data quality and governance into one vague status.

## States

- `not_started`
- `data_required`
- `security_blocked`
- `privacy_hold`
- `data_invalid`
- `hypothesis_only`
- `experiment_required`
- `evidence_insufficient`
- `exploratory_result`
- `pilot_candidate`
- `human_review_required`
- `pilot_approved`
- `rejected`

## Transition Rules

- Raw input enters security and privacy checks first.
- Critical security risk -> `security_blocked`.
- Direct PII not resolved -> `privacy_hold`.
- Missing required activation fields -> `data_required`.
- Prohibited or leakage fields -> `data_invalid`.
- No treatment/control or identification -> `hypothesis_only` or `experiment_required`.
- Missing or weak CI -> `evidence_insufficient`.
- High-risk intervention -> `human_review_required`.
- Passing data, evidence and governance -> `pilot_candidate`.
- Human approval after pilot candidate -> `pilot_approved`.

## Blocking Rules

- `security_blocked` blocks all reasoning and execution.
- `privacy_hold` blocks agent context and reporting of row-level data.
- `data_required` blocks calculation.
- `data_invalid` blocks pilot.
- `hypothesis_only` blocks causal and significance claims.
- `human_review_required` blocks pilot approval.

## Runtime Implementation

Implemented in `src/decision_states.py`.
