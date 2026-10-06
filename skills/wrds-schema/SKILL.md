---
name: wrds-schema
description: Select WRDS database skills and verify current products, tables, columns and access for any WRDS request. Use for schema discovery across the complete account catalog, including full products, restricted samples and TAQ SAS.
---

# WRDS schema discovery

Start with [wrds-catalog](../wrds-catalog/SKILL.md), then load only the domain skills needed for the request. Its portable lookup covers every visible table and column, with separate version, selection and access information. Defaults include reviewed sole available versions even when release documentation is missing; confirmed retired, denied and superseded entries stay excluded. This skill routes to those references; it does not keep another table catalog or spawn a specialist per database.

| Request | Knowledge | Execution agent |
|---|---|---|
| CRSP stocks, returns, adjustments, delisting | [wrds-crsp](../wrds-crsp/SKILL.md) | `wrds-psql-agent` |
| Compustat fundamentals and CCM | [wrds-compustat](../wrds-compustat/SKILL.md) | `wrds-psql-agent` |
| OptionMetrics options, IVs, surfaces | [wrds-optionmetrics](../wrds-optionmetrics/SKILL.md) | `wrds-psql-agent` |
| Cross-database identifiers and joins | [wrds-linking](../wrds-linking/SKILL.md), plus each domain | `wrds-psql-agent`; parent also coordinates TAQ if needed |
| TAQ trades, quotes, NBBO, intraday measures | [wrds-taq](../wrds-taq/SKILL.md) | `wrds-taq-agent` via SAS |
| Fama-French factors and portfolios | [wrds-fama-french](../wrds-fama-french/SKILL.md) | `wrds-psql-agent` |
| JKP global stock characteristics | [wrds-jkp](../wrds-jkp/SKILL.md) | `wrds-psql-agent` |
| TRACE, FISD, MSRB, bond returns | [wrds-bonds](../wrds-bonds/SKILL.md) | `wrds-psql-agent` |
| Capital IQ, events, capital structure, people | [wrds-capital-iq](../wrds-capital-iq/SKILL.md) | `wrds-psql-agent` |
| IBES, Worldscope and LSEG samples | [wrds-lseg](../wrds-lseg/SKILL.md) | `wrds-psql-agent` |
| Audit Analytics, BoardEx/Altrata, BvD | [wrds-governance](../wrds-governance/SKILL.md) | `wrds-psql-agent` |
| ESG, emissions and climate risk | [wrds-esg](../wrds-esg/SKILL.md) | `wrds-psql-agent` |
| Bank reports, rates, litigation, macro series | [wrds-public-data](../wrds-public-data/SKILL.md) | `wrds-psql-agent` |
| Other contributed research data | [wrds-contributed-data](../wrds-contributed-data/SKILL.md) | `wrds-psql-agent` |
| Cboe VIX/option samples, OTC prices | [wrds-market-data](../wrds-market-data/SKILL.md) | `wrds-psql-agent` |
| WRDS applications, ratios, SEC samples | [wrds-research](../wrds-research/SKILL.md) | `wrds-psql-agent` |
| Other restricted vendor products | [wrds-vendor-samples](../wrds-vendor-samples/SKILL.md) | `wrds-psql-agent` |

For an unspecified database, search the catalog by topic, table or column and load the returned skill. If asked for all available databases, use the coverage and schemas commands; do not stop at the original four domains. Do not treat access to one table as proof of another subscription, or silently substitute a sample for the full requested universe.

## PostgreSQL verification

Load [wrds-psql](../wrds-psql/SKILL.md) before querying. Inspect `information_schema.columns` for the specific schema/table and verify the column names used by the query. For example, inspect current CRSP daily data:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'crsp' AND table_name = 'dsf_v2'
ORDER BY ordinal_position;
```

For partitioned products, confirm the requested years exist rather than assuming the newest year from an old example. Check privileges and one bounded sample separately from catalog discovery. Do not run whole-table counts or unrestricted date-range scans as a connection test.

Use the CRSP skill's v2 default for new work; inspect legacy tables only for an explicit replication need. If live metadata differs from a stored reference, record the exact table, query date, and difference before adjusting the query. Historical snapshots and suggested methodology are not current catalog facts.

## TAQ verification

Use `PROC CONTENTS`, `dictionary.columns`, and `dictionary.libnames` through a small SAS job following [wrds-ssh](../wrds-ssh/SKILL.md). Probe the requested era and product before a pilot. A global PostgreSQL catalog inventory can retain TAQ relation names, but it does not establish SAS column definitions or TAQ access. Use SAS for TAQ verification and extraction.

## Return a useful reference

Report the selected tables, row grain, identifiers, date field, needed columns/types, important units, and any observed access or coverage limits. Distinguish live checks from historical reference notes. Report whole-sample coverage only when a suitable coverage check was actually performed.
