# Evidence and Claims

## Summary

The Nudge Engine must not overclaim. It can rank actions for testing, but ranking is not evidence that an intervention works.

## Core Rule

Recommendation is not effect proof.

Every nudge output should keep these concepts separate:

- `action_fit`: whether an action is theoretically and contextually suitable
- `effect_evidence`: whether the effect is actually supported by data

## Evidence Ladder

| Level | Meaning | Allowed wording |
|---|---|---|
| Unknown | Insufficient data | insufficient evidence |
| Descriptive | Pattern visible | we observe |
| Correlational | Association visible | is associated with |
| Predictive | Predicts behavior | predicts |
| Quasi-causal | Identification assumptions exist | suggests an effect under assumptions |
| Experimental | A/B or holdout evidence exists | measured effect in experiment |
| Replicated | Repeated evidence | replicated measured effect |

## Significance Claims

Significance is allowed only when:

- `effect_estimate` exists
- `ci_lower` exists
- `ci_upper` exists
- `ci_method` exists
- `sample_size` exists
- `confidence_level >= 0.95`
- CI excludes the null

If these are missing or incomplete, the report must block significance wording.

## Causal Claims

Causal claims require:

- treatment/control evidence, or
- a documented identification strategy

Without this, the engine may generate hypotheses or experiment suggestions, not causal impact claims.

## Blocked Wording

Avoid:

- proves
- guarantees
- will increase
- best intervention
- the user has bias X
- significant, unless CI gate passes

