# PII Vault Architecture

## Purpose

The Nudge Engine must never let direct PII enter normal agent reasoning, Evidence Packs, Run State, logs or reports.

PII belongs in a separate protected identity layer. Agents work only with pseudonymized analytics rows.

## Core Principle

Identity and behavior are separated.

- PII Vault: identity, re-identification and deletion rights
- Analytics Dataset: pseudonymous events, signals, treatments and outcomes
- Evidence Pack: minimized pseudonymous context only
- Run State: no direct PII
- Reports: no direct PII

## Production-Grade Target Architecture

```text
Raw Customer Data
  -> PII Intake Boundary
  -> PII Vault Records
  -> Pseudonymous Analytics Rows
  -> Leonidas Security Review
  -> Evidence Pack
  -> Agent Reasoning
```

## PII Vault Records

Vault records contain:

- `subject_id`
- encrypted or protected identity payload
- `pii_fields`
- `key_version`
- `created_at`
- storage class

Examples of vault-only fields:

- email
- phone
- name
- address
- CRM ID
- original customer ID if identifying

## Analytics Rows

Analytics rows contain:

- `subject_id`
- event fields
- treatment/control indicators
- outcomes
- behavioral signals
- governance-safe metadata

Analytics rows must not contain:

- email
- phone
- name
- address
- raw customer ID
- free-text PII

## Subject ID

`subject_id` is generated using keyed HMAC.

Properties:

- stable for the same identity and key version
- non-reversible without vault secret
- changes when `key_version` changes
- safe for analytics joins

## Access Rules

Agents may access:

- pseudonymous analytics rows
- redaction summaries
- risk metadata

Agents may not access:

- raw PII
- vault payload
- vault secret
- identity mapping table

Only a dedicated vault service may resolve:

- `subject_id -> identity`

Re-identification requires:

- explicit purpose
- authorized actor
- audit event
- governance approval

## Audit Events

Every vault action must create an audit event:

- `action`
- `subject_id`
- `actor`
- `reason`
- `timestamp`
- `key_version`
- fields touched

Current implemented action:

- `pseudonymize`

Future production actions:

- `reidentify`
- `delete_subject`
- `rotate_key`
- `export_subject`

## Leonidas Integration

Leonidas behavior:

- Raw PII creates `hold`.
- Pseudonymized analytics rows with `pii_pseudonymized=true` may pass.
- Secrets still block even if pseudonymization is claimed.
- Data integrity checks still run on pseudonymized rows.

## Implemented Interface

File:

- `src/pii_vault.py`

Functions:

- `stable_subject_id()`
- `pseudonymize_customer_rows()`
- `analytics_rows_are_pii_safe()`

Returned objects:

- `analytics_rows`
- `vault_records`
- `audit_events`
- `redaction_summary`

## Important Production Difference

The current implementation defines the vault boundary and deterministic test behavior.

For production:

- vault records must be stored in encrypted storage
- vault secret must come from a key manager
- vault payload must not be returned to agent runtime
- re-identification must require explicit authorization
- deletion and key rotation workflows must be implemented

## Acceptance Criteria

- Raw PII never enters Evidence Pack.
- Agents receive only `subject_id`, never direct identifiers.
- Same identity maps to same subject ID for the same key version.
- Key rotation changes subject IDs.
- Vault records are separate from analytics rows.
- Audit events are generated.
- Leonidas holds raw PII but approves pseudonymized analytics rows.
- Full tests remain green.
