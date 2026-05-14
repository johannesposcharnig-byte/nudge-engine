# Layer Control Matrix

## Purpose

This matrix prevents the engine from presenting smart outputs before the underlying decision layers are trustworthy.

| Layer | Current Status | Required Control | Pilot Gap |
|---|---|---|---|
| Input | partial | parse question, JSON/CSV rows, config | API upload missing |
| Security & Integrity | connected | block prompt injection, secrets, PII, leakage, contamination | advanced adversarial pack later |
| Privacy | connected | pseudonymize before analysis, no PII in reports | encrypted production vault missing |
| Data Contract | implemented | activation minimum fields and prohibited fields | needs API and dashboard feedback |
| Data Readiness | implemented | score, missing groups, causal readiness | richer profiling missing |
| Hypotheses | connected | MECE hypothesis set | weak natural-language interpretation |
| Claim Permission | implemented | evidence ladder and blocked claims | dashboard wording not yet fully wired |
| Calculation | partial | A/B CI when supported | CUPED/CATE/DR-OPE runtime missing |
| Behavioral Fit | connected | method registry and heuristic support | real calibration missing |
| Reward & Policy | connected | no-action, guardrails, ranking | no live learning |
| Governance & Human Review | partial | risk tiers and review triggers | approval workflow missing |
| Result Quality | connected | decision state, data, claims, pilot readiness | dashboard UI missing |
| Reporting | connected | JSON/Markdown report, PII-safe | claim wording needs stricter UI |
| Dashboard | partial | static preview | live API missing |
| Audit & Lineage | partial | schema hash, result status | run log store missing |
| Operations | partial | GitHub CI and safe push | deployment/auth/monitoring missing |

## Acceptance Rule

If any upstream layer is `blocked`, downstream layers may display only blocked, hold, hypothesis or experiment-required states. They may not display causal or significance claims.
