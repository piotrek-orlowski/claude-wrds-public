---
name: wrds-taq
description: Select, filter, and analyze NYSE TAQ trades, quotes, NBBO, and intraday indicators using SAS on WRDS. Use for TAQ schema discovery, realized variance, spreads, and trade classification.
---

# TAQ data and methods

The `wrds-taq-agent` executes this workflow using `wrds-ssh` for SAS submission,
monitoring, and result transfer. When that agent loads this skill, it continues
in the same task. TAQ work in this toolkit uses SAS on WRDS, including schema
probes. Do not route TAQ extraction through PostgreSQL.

1. Choose the data product, era, security identifiers, session, and required
   output frequency. Prefer the WRDS NBBO, consolidated trades, or intraday
   indicators when they already provide the requested measure.
2. Read [catalog binding](references/catalog.md) for current SAS metadata,
   access evidence, annual partitions, and product versions. Use
   [products and schema](references/products-and-schema.md) for libraries,
   dated coverage, variables, and naming traps. Confirm the requested daily
   file with `PROC CONTENTS` before building its extraction.
3. Read [filters and methods](references/filters-and-methods.md) to specify sale
   conditions, quote eligibility, sampling, and matching. These are research
   choices that depend on the era and output, not universal exclusion rules.
4. Read [SAS examples](references/sas-examples.md) when implementing the probe,
   views, sampling, daily loops, or measures. Start with one asset and at most
   one week. Validate counts, missing values, time ordering, ties, and output
   keys before scaling.
5. Report the product, dates, filters, sampling and tie rules, retained counts,
   missing-grid counts, output path, and any unverified assumptions. Preserve
   the SAS program and log with the result.

The inherited product notes were recorded on **2026-02-27**; the catalog
binding records newer **2026-10-05** metadata evidence and its limits. A listed
endpoint or library does not establish observation coverage, entitlement, or
timestamp accuracy. For a cross-database task,
have the main session arrange a separate PostgreSQL leg and use `wrds-linking`
for identifier and date alignment; this skill owns the TAQ leg.
