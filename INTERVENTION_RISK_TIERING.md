# Intervention Risk Tiering

## Purpose

Every runtime intervention must have an explicit risk tier before it can appear in pilot recommendations.

## Runtime Coverage

The current Nudge Engine contains these runtime methods in `src/behavioral_methods.py`:

| Method | Kind | Risk Tier | Human Review |
|---|---|---|---|
| `no_action` | baseline | baseline | no |
| `cognitive_ease` | action | low | no |
| `simplification` | action | low | no |
| `gain_frame` | action | low | no |
| `goal_setting` | action | low | no |
| `progress_feedback` | action | low | no |
| `transparency_explanation` | action | low | no |
| `default` | action | medium | yes |
| `social_proof` | action | medium | yes |
| `commitment` | action | medium | no by tier, governance still required |
| `reciprocity` | action | medium | yes |
| `timely_reminder` | action | medium | no by tier, governance still required |
| `just_in_time_intervention` | action | medium | no by tier, governance still required |
| `progress_oriented_default` | action | medium | yes |
| `loss_frame` | action | high | yes |
| `personalization` | meta | meta | governed selection layer |

## Prohibited Techniques

These are not runtime actions and must not be added as optimization levers:

- deceptive urgency
- shame-based nudges
- fear exploitation
- social exposure pressure
- vulnerability targeting
- hidden defaults
- fake scarcity
- manipulative reciprocity
- dark-pattern opt-out friction

## Rule

All registered methods must be covered by `INTERVENTION_RISK_TIERS`. New methods without an explicit risk tier are treated as prohibited until reviewed.

## Runtime Implementation

Implemented in `src/behavioral_methods.py` with test coverage in `tests/test_behavioral_methods.py`.
