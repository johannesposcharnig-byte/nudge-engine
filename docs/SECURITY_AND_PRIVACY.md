# Security and Privacy

## Summary

The current implementation includes local development controls for security, privacy and integrity. These controls are necessary but not sufficient for production.

## Security & Integrity Gate

The engine runs an internal Security & Integrity Gate before reasoning or execution-sensitive decisions.

It checks for:

- prompt injection patterns
- governance bypass attempts
- reward or policy override attempts
- unsafe source content
- direct PII exposure
- suspicious data integrity issues

The internal code name may appear in source code. Product-facing documentation should call this the Security & Integrity Gate, not a product-facing agent.

## PII Boundary

Direct identifiers must not enter agent context, reports or dashboard result views.

Raw rows are transformed into:

- vault records for identity data
- analytics rows using `subject_id`

Reports and dashboards should expose `subject_id`, not raw user IDs, emails, phone numbers or customer IDs.

## Re-Identification And Outreach

The engine may produce nudge candidates for `subject_id`, but operational outreach must happen through a governed export flow.

Rules:

- Re-identification requires actor, reason and explicit approval.
- Every re-identification attempt is audited.
- Deleted or expired subjects cannot be resolved.
- The dashboard should not display raw identity in v1.
- Outreach exports default to pseudonymous IDs and only include resolved IDs after approval.

## Git Safety

Do not commit:

- raw customer data
- vault records
- local private reports
- secrets
- `.env` files
- production credentials

The `.gitignore` excludes common sensitive paths, but developers must still inspect staged changes.

## Production Gaps

Still required before production:

- authentication
- encrypted PII vault
- secrets management
- access control
- persistent audit store
- retention policy
- monitoring
- incident process
- legal/privacy review
