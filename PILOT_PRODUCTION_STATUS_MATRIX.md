# Pilot vs Production Status Matrix

## Prototype

Acceptable:

- local files
- static dashboard
- synthetic data
- development-only vault secret
- no auth

Not acceptable:

- effect claims without evidence status
- PII in report outputs
- hidden blockers

## Internal Demo

Acceptable:

- sample reports
- mocked dashboard run
- synthetic fixtures

Not acceptable:

- implying real effect
- hiding uncertainty
- using real customer data without privacy boundary

## Local Pilot

Required:

- API around `run_analysis()`
- dashboard live run
- activation data contract
- data readiness score
- claim permission layer
- result quality gate
- security/privacy gate
- human review triggers
- lightweight audit lineage

Acceptable shortcut:

- local execution
- file-based logs
- development-only non-cloud setup

Unacceptable shortcut:

- direct PII in agent context
- autonomous nudge execution
- unsupported causal claims
- high-risk interventions without review

## Enterprise Pilot

Required:

- access control
- encrypted vault
- run lineage
- retention policy
- approval workflow
- audit logs

## Production

Required:

- authentication
- encrypted storage
- secrets management
- deployment monitoring
- versioned policies
- incident process
- privacy/legal review
- model governance
- data processing agreement
