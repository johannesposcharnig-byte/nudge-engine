# Synthetic Customer Events Fixture

## Purpose

This fixture is a small synthetic customer-event dataset for end-to-end validation of the Nudge Engine.

It is intentionally **not** a clean persona dataset. It contains noisy, contradictory and non-rational-looking behavior because real customers often do not behave as stable rational personas, especially for openness, resistance and fatigue.

## Design Principles

- `openness_signal` is not ground truth.
- High openness does not always mean opening, clicking, renewing or accepting nudges.
- Low openness does not always mean no action.
- Consent and vulnerability must override optimization.
- Loss framing can backfire under high resistance.
- Social proof and reciprocity can create governance-sensitive cases.
- Control users may renew and treated users may churn.
- Company-level effects can contradict user-level signals.

## Columns

- `user_id`: synthetic user identifier.
- `company_id`: synthetic account/company identifier.
- `event_time`: event timestamp.
- `signup_date`: customer signup date.
- `plan_tier`: synthetic plan tier.
- `consent`: whether intervention use is permitted.
- `region`: broad synthetic region.
- `account_role`: admin or user.
- `login_count_30d`: recent login count.
- `feature_usage_30d`: recent product usage count.
- `support_tickets_30d`: recent support tickets.
- `manual_task_count_30d`: friction/proxy burden signal.
- `last_nps`: last observed NPS-like score, may be missing.
- `nudge_variant`: `control` or `treatment`.
- `nudge_method`: behavioral method used or `none`.
- `opened_nudge`: observed open event.
- `clicked_nudge`: observed click event.
- `renewal`: synthetic outcome.
- `upsell`: synthetic secondary outcome.
- `openness_signal`: noisy proxy, not a persona truth.
- `resistance_signal`: noisy proxy for reactance/resistance.
- `fatigue_signal`: noisy proxy for overcontact or burden.
- `vulnerability_flag`: synthetic governance-sensitive flag.
- `notes_flag`: human-readable synthetic anomaly marker.

## Known Traps for the Engine

- `u003`: high `openness_signal`, but no consent and high risk. Must not be optimized.
- `u005`: high usage but low openness and high fatigue.
- `u008`: high openness, no treatment, no renewal.
- `u013`: low openness but clicked and renewed.
- `u014`: positive response but no consent, so must be excluded from actionable learning.
- `u015`: inactive user but company-level renewal; user-level inference would be misleading.
- `u017`: high resistance and loss-frame backfire pattern.

## Intended Use

Use this fixture for:

- Customer Data Intake tests.
- MECE hypothesis generation.
- Governance and consent checks.
- Behavioral-method safety checks.
- A/B and CI smoke tests after filtering consent-valid rows.
- Policy/reward tests that must respect no-action, guardrails and governance.

Do not use this fixture to claim real-world effect sizes.
