---
name: wrds-crsp
description: Query current CRSP products on WRDS, including CIZ stock returns, prices, identifiers, events, indexes, mutual funds, Treasuries, and REITs. Load wrds-compustat for fundamentals and CCM links.
---

# Current CRSP products

Load [wrds-psql](../wrds-psql/SKILL.md) before executing SQL and use direct `psql service=wrds`. Use [wrds-schema](../wrds-schema/SKILL.md) to check exact tables, fields, and access when the query needs verification. The PostgreSQL execution agent is `wrds-psql-agent`.

Use CIZ/v2 tables (`crsp.dsf_v2`, `crsp.msf_v2`) for stock work. The retired SIZ product is outside this toolkit; its last release covers December 2024. Historical observations inside CIZ remain in scope. Test one security and a short date interval before expanding. See the [WRDS transition notice](https://wrds-www.wharton.upenn.edu/pages/data-announcements/changes-to-crsp-data/).

## Read the relevant reference

- [Catalog coverage](references/catalog-coverage.md): generated schema/table coverage, access outcomes, and lifecycle exclusions for this domain.
- [Current products and access](references/products.md): stock/index, mutual-fund, Treasury, REIT, and CCM product boundaries; aliases and delivery vintages.
- [Schema and identifiers](references/schema.md): tables, column names, shares, indexes, and point-in-time identifiers.
- [CIZ codes and excluded versions](references/versions-and-codes.md): classification filters, missing-value flags, and the retired SIZ replacement.
- [Returns and adjustments](references/returns-and-adjustments.md): compounding, delisting, splits, distribution events, and portfolio measurement choices.
- [Query recipes](references/queries.md): bounded v2 extraction, cumulative returns, index joins, and firm capitalization.
- [Compustat and CCM](../wrds-compustat/SKILL.md): fundamentals and PERMNO-GVKEY links; this skill is the single owner of CCM conventions.

## Apply these invariants

- `dlyret` and `mthret` already incorporate delisting returns. Do not add a second delisting adjustment to v2.
- Use precomputed `dlycap`/`mthcap` for capitalization. The CIZ guide and a bounded 2026-10-05 check of `dsf_v2`/`msf_v2` support `shrout` in thousands for those tables; verify other products separately. See the reference for evidence and scope.
- Keep a valid -100% return. Exclude missing sentinels without dropping `ret = -1`, and handle that value explicitly before log compounding.
- Cumulative price and share factors are different. Do not adjust reported returns again.
- Preserve event dates. Convenience views may repeat security-date observations after joining distributions; select the correct grain or aggregate events rather than dropping all rows with a distribution.
- Use PERMNO for securities and PERMCO for companies. Tickers can be reused; names and classifications require date-range matching.
- For monthly merged panels, emit calendar month-end as the first `date` column and retain the original trading date as `crsp_date`. Use the original date for security/link validity.
- Check key uniqueness, missingness, date coverage, units, and return tails on the prototype. Do not assume a historical schema snapshot or a prior uniqueness result is current.

## Provenance

Migrated on 2026-10-05 from the former `agents/crsp-wrds-expert.md`. The same day's [catalog snapshot](../wrds-catalog/SKILL.md) inventories all visible PostgreSQL tables and columns; lifecycle and access evidence are recorded separately. Row validation was limited to two one-row v2 unit checks, not a full observation-coverage refresh. Older sample statistics remain labeled as historical snapshots. Source-backed corrections are recorded beside the affected guidance.
