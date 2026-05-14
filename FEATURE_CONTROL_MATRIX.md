# Feature Control Matrix

## Status Definitions

- `implemented`: code or document exists
- `tested`: automated or documented validation exists
- `connected`: included in the main runtime path
- `pilot_ready`: acceptable for a controlled local pilot
- `blocked`: not usable until a named gap is closed

## Current Feature Status

| Feature | Status | Evidence | Blocker / Next Step |
|---|---|---|---|
| Customer Data Intake | connected | `run_analysis()`, orchestrator tests | expand data profiling beyond activation |
| PII Pseudonymization | connected | PII vault tests | production vault blocked |
| Security & Integrity Gate | connected | security tests | advanced adversarial fixtures later |
| MECE Hypotheses | connected | orchestrator and analysis tests | improve question-to-hypothesis mapping |
| Data Contract | tested | `src/data_contracts.py`, data contract tests | expand beyond activation |
| Claim Permission | connected | `src/claim_permissions.py`, report/result quality tests | dashboard wording still needs visual QA in browser |
| Decision State Model | implemented | `src/decision_states.py` | expand state transition tests |
| Result Quality Gate | connected | `src/result_quality.py`, analysis/dashboard tests | live API payload validation later |
| A/B CI Calculation | connected | simulation and analysis tests | add CUPED/CATE later |
| Formula Review | connected | orchestrator tests | universal formula runtime missing |
| Behavioral Method Registry | connected | behavioral method tests | evidence-based fit calibration missing |
| Intervention Risk Tiering | connected | all methods covered in tests, dashboard displays risk/review | calibrate risk weights with pilot feedback |
| Heuristic/Bias Layer | tested | heuristic tests | not yet central in report UX |
| Reward/Policy Ranking | connected | reward and analysis tests | no live policy learning |
| Decision Report | connected | reporting tests | add enterprise export formats later |
| Audit Lineage Light | connected | `src/audit_lineage.py`, audit tests | persistent audit store not built |
| Local API `/analyze` | tested | `src/api.py`, API tests | no auth, local-only |
| Dashboard Static Preview | tested | dashboard tests | visual browser QA blocked for local `file://` in current app policy |
| Dashboard Live Run | connected | dashboard can call local API for `customer_rows` JSON | requires API process to be running manually |
| Report Chat Preview | implemented | static JS | real report-grounded endpoint not built |
| GitHub CI/Safe Push | connected | workflow and scripts | production release flow later |

## Pilot Readiness Rule

A feature may only become `pilot_ready` when it is implemented, tested, connected, documented and has no unresolved blocker that can create unsafe claims, PII exposure or governance bypass.
