# Governed Outreach Export

## Summary

The Nudge Engine does not contact customers directly.

It produces pseudonymous nudge candidates. Operational outreach requires a separate governed flow:

```text
Recommendation
  -> Approval
  -> Vault identity resolution
  -> Outreach export
  -> CRM / email / app import outside the engine
```

## Why This Layer Exists

Analysis alone is not operationally useful if a team cannot act on approved nudges. At the same time, direct identity must not be exposed to the engine, agents, reports or dashboard by default.

The Outreach Export Layer bridges this safely.

## V1 Behavior

V1 is local-only and does not integrate with an external CRM.

It can create:

- CSV exports for manual review/import
- JSON exports for future CRM integration

## Export Rules

The exporter only prepares outreach rows when:

- the recommendation is not `blocked`, `reject` or `hold`
- the selected action is not `no_action`
- consent is present in the segment view
- a structured outreach approval is valid for the report run
- the subject is active in the vault
- the subject is not deleted or expired

Identity resolution requires:

- `actor`
- `reason`
- `approval=True`

The preferred interface is `approval_context`, containing actor, reason, timestamp, approved scopes and the report `run_id`. The boolean argument remains only as a local backwards-compatibility adapter and is converted into the structured gate before any export decision.

## Output Fields

Minimum fields:

- `subject_id`
- resolved customer/CRM identifier when explicitly approved
- `selected_action`
- `message_variant`
- `reason_codes`
- `claim_type`
- `effect_evidence`
- `risk_tier`
- `human_review_status`
- `export_status`

## Privacy Rules

- Reports must not contain vault payloads.
- Dashboard views must not expose raw identity.
- Outreach exports default to pseudonymous IDs.
- Resolved identifiers are included only when identity resolution is explicitly approved.
- Email, phone and name are not included in the v1 export by default.

## Retention And Deletion

Vault records have retention state:

- `active`
- `deleted`
- `expired`

Deleted or expired subjects:

- cannot be re-identified
- cannot be exported
- remain audit-visible through tombstone state
