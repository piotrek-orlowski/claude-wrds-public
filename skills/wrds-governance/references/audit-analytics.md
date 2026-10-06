# Audit Analytics: feeds, events, and information dates

## Select the current feed

The `audit` alias exposes multiple separately licensed products. The
2026-10-05 permission/planning inventory accepted 147 alias relations and
identified 241 denied by underlying-product guards. Inspect each requested
table; alias-level access does not cover every module. `auditsmp` is a separate
15-table sample. The website's product labels include Audit and Compliance,
Accounting and Oversight, Corporate and Legal, Europe, Canada/SEDAR, Other
Independent Audits, and ESG/Funds. These are different populations and keys.
[WRDS product directory](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/audit-analytics-and-oia-other-independent-audits/)
was retrieved 2026-10-05; its September 2026 update dates describe product loads,
not validated event coverage.

Use `wrds-catalog` `search restatement`, `tables audit`, and
`table audit.feed03_audit_fees` to inspect the current table, access evidence,
column types, and comments. Catalog metadata on 2026-10-05 verifies:

| Table | Native fields and purpose |
|---|---|
| `audit.feed03_audit_fees` | `audit_gig_key`, `auditor_fkey`, `company_fkey`, `fiscal_year`, `fiscal_year_ended`, fee components, `currency_code_fkey`, `file_date`, `file_accepted`, `restatement` |
| `audit.feed04_audit_fees_restated` | Separate restated-fee feed with corresponding fee, fiscal-period, company, and filing fields |
| `audit.feed39_financial_restatements` | `restatement_notification_key`, `company_fkey`, `restatement_type`, `res_begin_date`, `res_end_date`, `event_date`, `file_date`, `file_accepted`, category flags and magnitude fields |
| `audit.f39_restatement_filings` | `restatement_filing_key`, `restatement_notification_fkey`, `company_fkey`, `file_date`, `file_accepted`, `first_announcement`, `first_regular_filing`, `first_magnitude_announcement` |
| `audit.f39_restatement_periods` | `restatement_period_key`, `restatement_notification_fkey`, `restatement_filing_fkey`, `type`, `year`, original/restated period amounts |
| `audit.f39_restatement_to_category` | Notification-to-category bridge; `restatement_notification_fkey`, `restatement_category_fkey`, `restatement_field` |
| `audit.f39_restatement_category` | `restatement_category_key`, `category_title`, `category_description` |
| `audit.wrds_lookup_edgar_company_block` | Company lookup derived from `feed12_company_block`; `company_fkey` is documented as WRDS-created and equal to `company_key` |

These table names differ from trial aliases such as `auditsmp.auditfees`,
`auditsmp.auditfeesr`, and `auditsmp.auditnonreli`. Do not infer that sample and
full feeds have identical columns, dates, or entity coverage.

## Fees and restatement workflow

For a company-year fees panel, select the original or restated feed explicitly.
Preserve `audit_gig_key`, auditor and company IDs, fiscal-year end, currency,
filing date, and the revision indicator. Determine whether a company-year has
multiple auditors, filings, fiscal-period lengths, or revisions before
aggregation. Do not sum original and restated values together.

For a restatement event study, begin with notification-level rows. Join filings
on notification key to identify the disclosed filing/event, retaining
`first_announcement` rather than assuming the first affected fiscal period is
the event date. `first_announcement` is a numeric indicator whose code meaning
must be verified, not a date. The notification feed's `event_date` is date-typed;
verify its definition against the chosen announcement/filing evidence before
using it. Period and category tables are child tables: aggregate each to
the chosen event grain before joining them together, or keep separate output
tables. Joining both directly can multiply every period by every category.

`company_fkey` is text (`varchar(10)` in the inspected fee/restatement feeds).
Preserve leading zeros. `file_date`, `res_begin_date`, `res_end_date`, and
`fiscal_year_ended` are dates; **`file_accepted` is text (`varchar(20)`)**. Inspect
the value format and timezone before parsing it as an intraday event timestamp.
The metadata does not establish timezone or first-publication timing.

The [WRDS linking tool](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/database-linking-tool/)
routes Audit Analytics to Compustat primarily through CIK. Confirm the lookup's
identifier definition and normalize CIK consistently; do not equate every
regional `company_fkey`, `entity_map_fkey`, SEDAR issuer number, or fund key.
The inspected company-key comment establishes the within-provider merge, but
does not itself establish that this key is a CIK. Verify the external mapping.

## Validate before expanding

- One issuer and one year: compare source rows with the intended company-year
  or notification key; report duplicates and their cause.
- Check fee currency, fee components versus reported totals, missing amounts,
  original/restated status, and filing dates relative to fiscal-year ends.
- For events, retain all source filings initially; verify the rule selecting
  the event date and record later updates separately.
- For child-table joins, compare counts before/after and count distinct parent
  and child keys. Keep category codes alongside decoded descriptions.

The [official Audit and Compliance dictionary](https://wrds-www.wharton.upenn.edu/data-dictionary/audit_audit_comp/)
redirected to login during public verification. Its content was not inspected.
Use the packaged live column comments for names/types, and an authorized manual
for undocumented category semantics. No academic paper was used for this guide.
