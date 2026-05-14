# OCEAN Signal Model

## Purpose

The OCEAN layer gives the Nudge Engine an optional psychological signal, not a standalone decision engine.

It may help generate or test behavioral hypotheses, but it must not approve interventions, policy actions, or reward logic without behavioral evidence, consent, and governance review.

## Instrument

Default instrument: Ten-Item Personality Inventory, `TIPI`.

Scientific basis:
- Gosling, Rentfrow, and Swann developed the TIPI as a very brief Big Five self-report measure.
- The instrument uses 10 items on a 1-7 agreement scale.
- Reverse-scored items are 2, 4, 6, 8, and 10.
- It is intentionally low precision compared with longer personality inventories.

Source:
- https://gosling.psy.utexas.edu/scales-weve-developed/ten-item-personality-measure-tipi/

## Scoring

Reverse score:

```text
reverse(x) = 8 - x
```

Trait scores:

```text
extraversion = mean(tipi_1, reverse(tipi_6))
agreeableness = mean(reverse(tipi_2), tipi_7)
conscientiousness = mean(tipi_3, reverse(tipi_8))
emotional_stability = mean(reverse(tipi_4), tipi_9)
openness = mean(tipi_5, reverse(tipi_10))
neuroticism = 8 - emotional_stability
```

## Governance Rules

- OCEAN/TIPI requires explicit consent before scoring or personalization.
- OCEAN outputs are `hypothesis_only`.
- OCEAN cannot be the only basis for policy approval.
- OCEAN cannot prove effect, causality, significance, or intervention fit.
- If OCEAN contradicts observed behavior, observed behavior wins for product decisions.
- No vulnerable-user targeting may be based on personality traits.

## Evidence Interpretation

Allowed claim type:
- `hypothesis`

Allowed use:
- segment hypothesis generation
- behavioral mechanism review
- candidate moderator for treatment heterogeneity
- feature for later analysis only after consent and governance review

Blocked use:
- standalone policy routing
- standalone reward optimization
- manipulating high-risk or vulnerable users
- claiming that a user will behave in a certain way from traits alone

## Implementation

Code:
- `src/ocean.py`

Tests:
- `tests/test_ocean.py`
- `tests/fixtures/synthetic_tipi_responses.csv`

The synthetic fixture intentionally contains contradictory patterns, for example high self-reported openness with high observed resistance. This prevents the test data from becoming an unrealistically rational persona dataset.
