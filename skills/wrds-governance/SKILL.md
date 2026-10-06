---
name: wrds-governance
description: Research WRDS Audit Analytics filings and audit events, BoardEx and Altrata directors and executive networks, and Bureau van Dijk Orbis or Bank Focus company ownership and financials. Distinguish full products, samples, role periods, ownership snapshots, and restated data.
---

# Audit, people, and corporate ownership data

Use `wrds-psql-agent` and `wrds-psql` for direct local PostgreSQL execution.
When that agent loads this skill, continue the same task. Do not route these
products through SSH. Start with one company and a short date range; use a
bounded issuer lookup when no stable identifier is supplied.

1. Load `wrds-catalog` and inspect the exact table's columns, access evidence,
   underlying product, sample status, and collection date. Catalog visibility,
   planning acceptance, and successful row retrieval are different evidence.
   [Catalog coverage](references/catalog-coverage.md) binds this skill to the
   generated account-specific product/table inventory; use it for routing and
   completeness, then the lookup helper for exact columns.
2. Choose the relevant reference only:
   - [Audit Analytics](references/audit-analytics.md): fees, auditor changes,
     restatements, filing dates, and feed/support-table joins.
   - [BoardEx and Altrata](references/boardex.md): person/company/role keys,
     regional products, dated appointments, and networks.
   - [Bureau van Dijk](references/bvd.md): Orbis ownership, company identifiers,
     financial-statement variants, Bank Focus, and legacy Amadeus.
3. State the output grain and time meaning before joining. Keep filing/public
   information time separate from fiscal periods, role periods, and current
   ownership snapshots. A recent extract of historical records is not evidence
   of what was known historically.
4. Build the small prototype with native identifiers and raw code fields.
   Check key uniqueness, join multiplication, missing or coded dates, currencies,
   units, and unmatched identifiers. Do not use DISTINCT to hide unresolved
   many-to-many joins.
5. Report the exact tables, product vintage, full/sample status, period logic,
   exclusions, successful access test, and any definitions still unverified.
   Use `wrds-linking` for joins to CRSP, Compustat, or other providers.

The references bind provider documentation to the **2026-10-05** metadata
snapshot. Refresh the catalog when the requested product or schema differs;
do not silently substitute a trial, archived product, or differently scoped
region when access is denied.
