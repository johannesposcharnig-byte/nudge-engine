# Architecture

## Purpose

The Nudge Engine is an evidence- and governance-gated decision support system. It should help developers and operators understand which behavioral interventions are plausible to test, while making uncertainty, blockers and governance constraints visible.

## Runtime Flow

```text
Input payload
  -> Security & Integrity Gate
  -> PII pseudonymization
  -> Data Contract / Data Readiness
  -> MECE Hypotheses
  -> Evidence / Claim Permission
  -> Calculation Layer
  -> Experiment Design (when evidence is insufficient)
  -> Behavioral Fit
  -> Reward / Policy
  -> Structured Human Approval
  -> Result Quality
  -> Reporting / Dashboard
  -> Audit Lineage
```

## Core Layers

### Input and Data Contract

Validates whether activation analysis has enough structure to run:

- identity field
- timestamp
- outcome
- consent
- optional treatment/control field
- missingness and field profile checks
- treatment balance
- outcome profile

### Security & Integrity Gate

Screens external content, customer rows and analysis context for risks such as prompt injection, governance bypass, unsafe data, PII exposure and policy override attempts.

The internal code name may appear in implementation details, but product-facing documentation should refer to this as the Security & Integrity Gate.

### PII Pseudonymization

Splits raw identity fields from analytics rows. Agents, reports and dashboard views should use `subject_id`, not direct identifiers.

### Hypothesis Layer

Creates MECE hypotheses before recommendations. Untestable hypotheses remain visible and must not be silently converted into recommendations.

### Evidence and Claim Permission

Determines which claims are allowed based on data, uncertainty, treatment/control logic, no-action baseline and identification assumptions.

### Calculation Layer

Currently supports local A/B-style uncertainty estimation when treatment/control and numeric outcome are available.

### Experiment Design Assistant

When the evidence gate cannot support an effect claim, the engine emits a structured A/B, holdout or CUPED measurement plan. Missing outcomes produce clarification questions instead of an invented plan. The plan is explicitly not evidence of effectiveness.

### Reward and Policy Layer

Ranks actions against no-action while preserving blockers such as missing consent, fatigue, protected states, missing guardrails or invalid no-action baseline.

### Result Quality

Combines data readiness, claim permission, security/privacy state and policy output into a decision state and pilot readiness status.

### Structured Human Approval

Pilot and outreach approval is bound to an actor, reason, timestamp, scope and run ID. Security, privacy and rejected data-contract blockers cannot be overridden by ordinary approval.

### Reporting and Dashboard

Produces JSON-compatible reports and dashboard-visible sections for status, evidence, nudges, blockers, result quality and audit lineage.

### Audit Lineage

Records run metadata without storing raw customer rows:

- run ID
- schema hash
- row count
- versions
- decision state
- blockers
- security status
- human override status
