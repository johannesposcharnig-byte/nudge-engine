# Architecture Review: Pilot-Ready Behavioral Nudge Engine

## Executive Assessment

The Nudge Engine must be treated as an evidence- and governance-gated decision support system, not as a simple nudge recommendation generator.

Current status:

- local analysis entrypoint exists
- security and integrity gate exists
- PII pseudonymization exists as a development boundary
- reports and dashboard preview exist
- GitHub and CI are connected
- API and live dashboard execution are not implemented yet

Critical architectural gap:

- claims, decisions and pilot readiness must be governed before the API and dashboard are made live

## Hidden Critical Risks

1. Dashboard overtrust
- Risk: a polished dashboard can make weak evidence look authoritative.
- Control: every recommendation must expose evidence and pilot-readiness status.

2. Action fit confused with effect evidence
- Risk: a ranked action may be interpreted as proven to work.
- Control: separate `action_fit` from `effect_evidence`.

3. Weak data readiness
- Risk: bad timestamps, leakage, contaminated variants or missing IDs can invalidate results.
- Control: activation data contract and data readiness score.

4. Security gate misframed as product agent
- Risk: users may think Leonidas is a behavioral or programming agent.
- Control: product copy says `Security & Integrity Check`; Leonidas remains internal.

5. Pilot shortcuts leaking into production
- Risk: local vault, local files and no-auth flows may become accidental production patterns.
- Control: pilot-vs-production status matrix.

## Revised Architecture

1. Input & Data Contract Layer
2. Security & Integrity Gate
3. Privacy & Pseudonymization Layer
4. Data Readiness Layer
5. Hypothesis Layer
6. Evidence & Claim Permission Layer
7. Calculation Layer
8. Behavioral Fit Layer
9. Reward & Policy Layer
10. Governance & Human Review Layer
11. Result Quality Layer
12. Reporting & Dashboard Layer
13. Audit & Lineage Layer

## Internal Gate Boundary

Leonidas is an internal security and integrity gate.

It may:

- block reasoning
- hold execution
- flag unsafe context
- flag PII, secrets, prompt injection, leakage and contamination

It may not:

- approve nudges
- act as a product-facing recommendation agent
- change reward weights
- claim behavioral effects

## Immediate Architectural Verdict

Do not move directly to live dashboard/API without the control layer.

Correct order:

1. Decision model
2. Data contract
3. Claim permission
4. Result quality
5. API
6. Dashboard live connection
