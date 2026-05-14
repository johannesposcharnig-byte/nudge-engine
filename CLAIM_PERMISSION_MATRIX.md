# Claim Permission Matrix

## Purpose

The Nudge Engine may only make claims that the evidence level supports.

## Evidence Ladder

| Evidence Level | Meaning | Allowed Wording | Blocked Claims |
|---|---|---|---|
| `unknown` | insufficient evidence | insufficient evidence | recommendation, effect, causal, significance |
| `hypothesis` | plausible but untested | is consistent with | effect, causal, significance |
| `descriptive` | observed pattern | we observe | causal, significance |
| `correlational` | association | is associated with | causal, significance |
| `predictive` | predicts outcome | predicts | intervention effect, causal |
| `quasi_causal` | identification assumptions | suggests an effect under assumptions | strong causal proof |
| `experimental` | A/B or holdout with CI | measured effect in experiment | replicated/generalized effect |
| `replicated` | repeated measured effect | replicated measured effect | universal guarantee |

## Hard Blocking Rules

- No significance claim without complete CI and `confidence_level >= 0.95`.
- No causal claim without treatment/control or identification strategy.
- No "best nudge" claim without no-action comparison.
- No personalization claim without consent and supporting data.
- No heuristic or OCEAN-only policy approval.

## Prohibited Wording

- proves
- guarantees
- will increase
- the user has bias X
- best intervention
- significant, unless CI gate passes

## Runtime Implementation

Implemented in `src/claim_permissions.py`.
