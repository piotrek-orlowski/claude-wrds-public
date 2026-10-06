---
name: wrds-lseg
description: Query current LSEG/Refinitiv/Thomson Reuters data on WRDS, especially IBES analyst forecasts, actuals and recommendations, Worldscope fundamentals, and shared security identifiers. Check subscriptions and sample-only coverage for Datastream, holdings, SDC, guidance, KPI, and other LSEG modules.
---

# LSEG data

Use `wrds-psql-agent` for SQL execution. Load
[wrds-psql](../wrds-psql/SKILL.md) before connecting and
[wrds-catalog](../wrds-catalog/SKILL.md) to select current tables, columns,
dependencies, and access evidence. All these products use direct PostgreSQL;
SSH is reserved for TAQ SAS jobs.

Read [IBES, Worldscope, identifiers, and access](references/products-and-queries.md).
Use the generated [catalog coverage](references/catalog-coverage.md) for the
complete domain inventory and its recorded access/lifecycle boundaries.
Load [wrds-linking](../wrds-linking/SKILL.md) when joining CRSP or another
provider. Do not infer a subscription from broad alias schemas such as
`ibes`, `ibescorp`, `ibeskpi`, `tfn`, or `sdc`.

## Working rules

- Separate forecasts, actuals, consensus snapshots, recommendations, and
  price targets. Choose region, measure, horizon, adjustment convention, and
  currency before extracting.
- Keep announcement, activation, review, and fiscal-period dates distinct.
  Future actuals embedded in forecast tables are labels, not information
  available on the forecast date.
- IBES tickers are vendor identities, not exchange tickers. Analyst/broker
  identities can change across vintages; retain extraction provenance.
- In Worldscope, resolve numbered items through `wsitem` and preserve code,
  frequency, year, sequence, currency, fiscal dates, and reporting basis.
- Distinguish organization, instrument, and quote IDs. Apply mapping validity
  dates and ranking/type rules before cross-database joins.
- Historical observations in a maintained product remain in scope. Retired
  archives, alternate deliveries, and samples do not replace current full
  products.
- Pilot one company and one fiscal period or a short calendar interval. Check
  keys, revisions, missing values, adjustments, units, and timing before scaling.

The 2026-10-05 catalog records metadata/preflight evidence. Verify bounded row
retrieval and requested-date coverage before promising an extract.
