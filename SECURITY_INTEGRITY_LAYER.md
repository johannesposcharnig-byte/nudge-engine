# Security & Integrity Layer: Leonidas

## Purpose

Leonidas is the always-on security check for the Nudge Engine.

Its job is not to create recommendations. Its job is to prevent unsafe, manipulated or invalid context from reaching agent reasoning or execution.

## Authority

Leonidas can:

- block agent reasoning before dispatch
- hold execution when integrity risks remain unresolved
- flag unsafe evidence sources
- flag reward, policy or governance bypass attempts
- flag schema-level data poisoning risks
- flag exposed secrets and direct PII
- flag row-level prompt injection in customer data
- flag duplicate event IDs, invalid timestamps, label leakage and treatment/control contamination

Leonidas cannot:

- approve a behavioral intervention alone
- override governance
- change reward weights
- claim behavioral effects
- diagnose customers

## Runtime Decision Fields

Leonidas returns:

- `security_status`: `approve`, `revise`, `hold` or `reject`
- `risk_level`: `low`, `medium`, `high` or `critical`
- `detected_risks`
- `blocked_content`
- `required_mitigations`
- `safe_to_reason`
- `safe_to_execute`
- `decision_rationale`

## Blocking Rules

- `safe_to_reason=false` blocks the agent before reasoning.
- `safe_to_execute=false` blocks final approval or rollout.
- Critical risks use `action=block`.
- High integrity risks use `action=hold`.

## Current Checks

- Prompt injection:
  - examples: `ignore previous instructions`, `disable governance`, `override policy`, `reveal system prompt`
- Reward and policy integrity:
  - examples: `heuristic_only_policy`, `ocean_only_decision`, `disable_no_action_baseline`
- Governance bypass:
  - examples: `force_approve`, `bypass_governance`, `ignore_guardrails`
- Source integrity:
  - blocked, deprecated or untrusted sources
- Data poisoning / schema violation:
  - normalized behavioral signals outside `[0, 1]`
- Secrets and PII:
  - API keys, tokens, passwords, credentials, emails and phone numbers
- Row-level prompt injection:
  - hostile instructions inside customer notes, feedback, support tickets or CSV cells
- Data integrity:
  - duplicate unique event IDs
  - invalid timestamp-like fields
  - future, post-treatment, label or target leakage fields
  - same entity appearing in both treatment and control groups

## Evidence Pack Integration

Every minimized agent context includes:

- `security_agent="Leonidas"`
- `security_review`
- `security_warnings`

The Evidence Pack also stores the same fields so later review can reconstruct why an agent run was allowed or blocked.

## Design Boundary

Leonidas is intentionally implemented as a security gate, not as a sixth core agent. This keeps the 5-agent architecture simple while still making security mandatory.

## Acceptance

Leonidas is accepted when:

- prompt injection blocks before reasoning
- governance bypass blocks before reasoning
- reward or policy shortcut attempts prevent approval
- out-of-range behavioral signals create a hold
- secrets block before reasoning
- PII creates a hold until pseudonymized
- label leakage and treatment/control contamination create a hold
- benign context passes
- all tests remain green
