---
name: wrds-bonds
description: Select and interpret current WRDS fixed-income data from TRACE, FISD, MSRB, WRDS Bond Returns, and contributed corporate-bond panels including Dickerson. Use for bond trades, issue terms, ratings, returns, and bond-equity links.
---

# Bond data on WRDS

Use `wrds-psql-agent` with [wrds-psql](../wrds-psql/SKILL.md) for direct PostgreSQL, including raw TRACE queries. Read [wrds-catalog](../wrds-catalog/SKILL.md) for complete current tables, aliases, columns, source documentation, sample restrictions, and access evidence. SSH/SAS is the TAQ route, not the TRACE route.

Choose the product in [product selection](references/products.md), then read [identifiers, returns, and bounded recipes](references/methods.md). Retain the selected product and release with every result.

The generated [catalog coverage](references/catalog-coverage.md) lists current full products, samples, and aliases included in this skill.

- Raw TRACE transactions, cleaned WRDS transactions, WRDS monthly returns, and contributed return panels are separate products. Do not join their records merely because their columns sound similar.
- FISD describes issues, issuers, terms, ratings, and events; MSRB describes municipal trades. A corporate-bond filtering convention does not automatically apply to municipalities or securitized products.
- Preserve full nine-character bond CUSIPs as text. Issue CUSIPs are not issuer CUSIPs or equity CUSIPs. Use dated bond-equity links when needed.
- Keep execution, reporting, publication, settlement, and month-end dates separate. Clean cancellations/corrections with the provider's era-specific identifiers before computing trade counts or volume.
- Distinguish clean prices, dirty prices, coupons, total returns, and excess returns. Confirm units and rating scales for the chosen table before thresholds, weighting, or return arithmetic.
- Prototype one bond or one issuer over a short interval. Check intended row grain, event multiplicity, stale prices, missing observations, and joins before a full extraction.

The 2026-10-05 catalog includes all current TRACE/FISD/MSRB tables and the contributed/WRDS panel families listed in the references, with separate sample products. Their reported checks establish zero-row planning and relevant alias-guard acceptance, not complete trade coverage or research-data quality. Use the catalog's current lifecycle and access classification before selecting a table.
