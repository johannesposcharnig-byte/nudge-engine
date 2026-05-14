# Heuristic Layer for Cognitive Biases

## Purpose

The heuristic layer explains observed behavior as cognitive-bias hypotheses.
It must not diagnose customers and must not approve actions on its own.

Primary practical source:
- https://thedecisionlab.com/biases

Taxonomy references:
- https://commons.wikimedia.org/wiki/File:Cognitive_bias_codex_en.svg
- https://2019.busterbenson.com/piles/cognitive-biases/

## Runtime Rule

Correct:

```text
Behavior is consistent with an availability-heuristic hypothesis.
```

Incorrect:

```text
The customer has availability bias.
```

## Active Heuristics

- `availability_heuristic`
- `present_bias`
- `hyperbolic_discounting`
- `status_quo_bias`
- `loss_aversion`
- `framing_effect`
- `choice_overload`
- `anchoring_bias`
- `social_norms`
- `bandwagon_effect`
- `ambiguity_effect`
- `planning_fallacy`
- `confirmation_bias`
- `salience_bias`
- `decision_fatigue`
- `base_rate_fallacy`
- `attentional_bias`
- `mere_exposure_effect`
- `endowment_effect`
- `regret_aversion`
- `optimism_bias`
- `normalcy_bias`
- `omission_bias`
- `wysiati`

## Reference-Only Heuristics

These are retained as references but do not influence ranking until operationalized.

- `barnum_effect`
- `dunning_kruger_effect`
- `halo_effect`
- `fundamental_attribution_error`
- `just_world_hypothesis`
- `naive_realism`
- `self_serving_bias`
- `spotlight_effect`
- `illusion_of_transparency`
- `illusion_of_control`
- `illusion_of_validity`
- `hindsight_bias`
- `peak_end_rule`
- `source_confusion`
- `rosy_retrospection`
- `nostalgia_effect`
- `telescoping_effect`
- `serial_position_effect`
- `primacy_effect`
- `recency_effect`
- `google_effect`
- `ikea_effect`
- `benjamin_franklin_effect`
- `observer_expectancy_effect`
- `pygmalion_effect`
- `outcome_bias`
- `look_elsewhere_effect`

## Excluded Biases

These are not optimization levers. They may only appear as governance risk.

- `sexual_overperception_bias`
- `parasocial_trust_in_ai`
- `bye_now_effect`
- `cashless_effect`
- `bottom_dollar_effect`
- `scarcity_pressure`
- `deceptive_urgency`

## Validation

- Missing required signals -> `not_testable_yet`.
- Correlation can produce at most `moderate_support`.
- Correlation never creates causality.
- Experimental validation is required for `validated_experimentally`.
- Alternative explanations remain visible.
- Heuristic-only policy is blocked.

## Implementation

Code:
- `src/behavioral_heuristics.py`

Tests:
- `tests/test_behavioral_heuristics.py`
