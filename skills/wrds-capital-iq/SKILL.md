---
name: wrds-capital-iq
description: Query S&P Capital IQ on WRDS for capital structure, key developments, people and compensation, transactions, and company/security identifiers. Use for CIQ entity links, debt components, event timing, and deal panels; distinguish accessible modules from sample-only ratings/transcripts.
---

# Capital IQ

Use `wrds-psql-agent` for execution. Load
[wrds-psql](../wrds-psql/SKILL.md) before SQL and
[wrds-catalog](../wrds-catalog/SKILL.md) for the exact current table, columns,
dependencies, lifecycle, and access evidence. Use direct PostgreSQL; SSH is
reserved for the TAQ SAS workflow.

Read [products, keys, and research workflow](references/products-and-queries.md)
for the requested module. Load [wrds-linking](../wrds-linking/SKILL.md) for
cross-product work and [wrds-compustat](../wrds-compustat/SKILL.md) for accounts.
The generated [catalog coverage](references/catalog-coverage.md) records the
full domain inventory and its access/lifecycle boundaries.

## Working rules

- Choose the module before the table. The broad `ciq` alias does not establish
  access to every Capital IQ product. A zero-row probe proves planning only.
- Keep company, security, trading-item, person, financial-instance, component,
  event, and transaction IDs separate. A company can have many of each.
- Date identifier links and retain primary flags; test multiplicity rather
  than assuming a primary designation makes a link unique.
- For accounts, preserve period end, filing date, financial instance, unit,
  currency, data item, and restatement flags. Latest-record flags describe the
  delivered database, not historical availability.
- For events, preserve announcement, entry, modification, and timezone fields.
  Choose the event-time convention before calculating market responses.
- For deals, distinguish announcement, completion, cancellation, and current
  status. A related-company row is not a unique transaction.
- Start with one company and a short period, prove the output grain and units,
  then scale. Do not treat sample ratings/transcripts as a full subscription.

The 2026-10-05 inventory established schema/column and preflight evidence,
not complete row coverage. The catalog is the full table dictionary; this
skill supplies the module choices and joins that need research judgment.
