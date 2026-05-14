# Backward Validation Test Plan

## Purpose

This plan validates the Nudge Engine from the final decision boundary backwards to the first customer-data intake step. The goal is to find defects, unsafe assumptions and missing gates before the engine is tested with real customer data.

## Principle

Validate from the point of highest risk backwards:

1. Final decision and execution readiness
2. Governance, security and conflict gates
3. Policy and reward readiness
4. Formula and uncertainty readiness
5. Behavioral mechanism readiness
6. Data and measurement readiness
7. Customer data intake and clarification

No downstream layer may compensate for a failed upstream gate.

## Agent Assignments

### Data & Measurement Agent

Scope:
- Customer data intake
- MECE hypotheses
- formula classes
- A/B, CUPED, CATE and DR-OPE readiness
- confidence intervals and support checks

Decision rule:
- `approve` only when the data and uncertainty fields support the claim.
- `hold` when outcome, treatment, time, support or CI are missing.

### Policy & Reward Agent

Scope:
- reward calibration
- no-action baseline
- guardrails
- policy formula review
- action ranking safety

Decision rule:
- `approve` only when reward calibration, no-action baseline and guardrails exist.
- `hold` when reward or guardrail context is incomplete.

### Critic & Governance Agent

Scope:
- prompt injection
- blocked or deprecated sources
- stale governance-critical context
- unresolved conflicts
- dark-pattern and manipulation risk

Decision rule:
- `hold` for critical security warnings, unresolved conflicts or blocked sources.
- `revise` for weak evidence attempting to override stronger evidence.

## Backward Test Matrix

| Layer | Test | Expected |
|---|---|---|
| Final decision | Valid A/B with non-null 95% CI | `approve` |
| Final decision | CI contains null | `revise` |
| Governance | Prompt injection in external content | `hold` |
| Governance | Stale governance-critical source | `hold` |
| Governance | unresolved evidence conflict | `hold` |
| Policy | reward policy without calibration | `hold` |
| Policy | reward policy with calibration, no-action and guardrails | `approve` or no hard hold |
| Formula | DR-OPE without support checks | `hold` |
| Formula | A/B without CI | `hold` |
| Intake | missing outcome variable | `hold` plus clarification |
| Intake | valid schema with outcome/time/entity | `approve` |
| Intake | prompt injection in customer data | `hold` |

## Acceptance Criteria

- All automated tests pass.
- Every high-risk failure mode returns `hold` or `revise`, never silent `approve`.
- Customer data intake is governed before any formula or policy review.
- Security and retrieval governance are active at the first entry point.
- The final validation report lists remaining risks explicitly.
