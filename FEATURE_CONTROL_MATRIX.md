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
| Customer Data Intake | connected | `run_analysis()`, orchestrator tests | strengthen data profiling |
| PII Pseudonymization | connected | PII vault tests | production vault blocked |
| Security & Integrity Gate | connected | security tests | advanced adversarial fixtures later |
| MECE Hypotheses | connected | orchestrator and analysis tests | improve question-to-hypothesis mapping |
| Data Contract | implemented | `src/data_contracts.py` | expand beyond activation |
| Claim Permission | implemented | `src/claim_permissions.py` | enforce in report wording and dashboard |
| Decision State Model | implemented | `src/decision_states.py` | expand state transition tests |
| Result Quality Gate | connected | `src/result_quality.py`, analysis tests | dashboard visualization missing |
| A/B CI Calculation | connected | simulation and analysis tests | add CUPED/CATE later |
| Formula Review | connected | orchestrator tests | universal formula runtime missing |
| Behavioral Method Registry | connected | behavioral method tests | evidence-based fit calibration missing |
| Intervention Risk Tiering | implemented | all methods covered in tests | wire into dashboard/readiness display |
| Heuristic/Bias Layer | tested | heuristic tests | not yet central in report UX |
| Reward/Policy Ranking | connected | reward and analysis tests | no live policy learning |
| Decision Report | connected | reporting tests | result quality UI missing |
| Dashboard Static Preview | tested | dashboard tests | live API not connected |
| Dashboard Live Run | blocked | none | requires local API |
| Report Chat Preview | implemented | static JS | real report-grounded endpoint not built |
| GitHub CI/Safe Push | connected | workflow and scripts | production release flow later |

## Pilot Readiness Rule

A feature may only become `pilot_ready` when it is implemented, tested, connected, documented and has no unresolved blocker that can create unsafe claims, PII exposure or governance bypass.
