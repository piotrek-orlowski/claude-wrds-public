---
name: wrds-optionmetrics
description: Use for WRDS OptionMetrics IvyDB option prices, implied volatility, Greeks, standardized options, volatility surfaces, security histories, and SECID links to CRSP.
---

# OptionMetrics on WRDS

Use this skill for dataset knowledge. The `wrds-psql-agent` executes queries
using [wrds-psql](../wrds-psql/SKILL.md); when that agent loads this skill, it
continues in the same task. Use direct PostgreSQL; SSH is reserved for the
TAQ SAS workflow.

Choose only the references needed for the request:

- [Catalog coverage](references/catalog-coverage.md): generated table inventory,
  access outcomes, and lifecycle exclusions for this domain.
- [Current product and access](references/products.md): US versus European
  delivery, aliases, annual partitions, and excluded alternate/sample products.
- [Schema and units](references/schema.md): tables, year partitions, columns,
  grids, security histories, index/ETF distinctions, and historical coverage.
- [Query examples](references/queries.md): identifier lookup, raw and standardized
  options, surfaces, IV spreads, skew, term structure, and multi-year extraction.
- [Filters and pricing](references/filters-pricing.md): sample restrictions,
  missing values, and the provider-model notes retained from the source agent.
- [CRSP links](references/crsp-link.md): `wrdsapps.opcrsphist`, score handling,
  date validity, and options matched to stock returns. For a manual fallback or
  more databases, load [wrds-linking](../wrds-linking/SKILL.md).

Confirm the requested table/year with [wrds-schema](../wrds-schema/SKILL.md),
then prototype one security and a short date range before scaling. The schema
reference distinguishes inherited February 2026 field notes from the October
2026 metadata refresh; neither is a complete row-coverage guarantee.
All historical-year partitions of the current IvyDB product remain in scope.
Do not substitute alternate vintage or trial schemas for a current-data request.

Keep these distinctions visible in every extraction:

- Raw `opprcdYYYY.strike_price` is scaled by 1,000. Do not apply that scaling
  automatically to standardized-option or surface strikes.
- `stdopdYYYY` contains both calls and puts. Preserve or explicitly select
  `cp_flag` before forming an ATM series or term structure.
- `vsurfdYYYY.delta` uses percentage-point grid values (for example, 25);
  raw-option `delta` examples use fractions (for example, 0.25).
- `secid` identifies the underlying and `optionid` the contract. Retain the
  contract key when validating duplicates or linking raw options to daily stock
  observations.
- Missing-value removal and researcher-selected liquidity, maturity, or IV caps
  serve different purposes. Record each exclusion and its effect on sample size.

Use the existing connection service without reading credential files. Do not
inspect credentials without explicit user permission, and do not use the
interactive `wrds` Python library. Connection/export mechanics live in
`wrds-psql`; do not copy them into dataset references.
