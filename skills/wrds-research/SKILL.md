---
name: wrds-research
description: Use WRDS research applications and delivered datasets for financial ratios, event studies, patent links, subsidiaries, country indices, EU shorts, MIDAS and SEC analytics samples. Verify source dependencies, grain and delivery limits before querying.
---

# WRDS research applications and SEC data

Start with [wrds-catalog](../wrds-catalog/SKILL.md) and [wrds-psql](../wrds-psql/SKILL.md). [Catalog coverage](references/catalog-coverage.md) lists all selected tables. Use [wrds-linking](../wrds-linking/SKILL.md) for cross-database identifiers and [wrds-bonds](../wrds-bonds/SKILL.md) for WRDS bond returns.

## Select the delivered table

| Task | Product family |
|---|---|
| Financial ratios | `wrdsapps_finratio`, `wrdsapps_finratio_ibes` |
| Event-study inputs | `wrdsapps_evtstudy_us`, `wrdsapps_evtstudy_int` |
| Patents and citations | `wrdsapps_patents` |
| Company relationships | `wrdsapps_subsidiary` |
| World indices | `wrdsapps_windices` |
| European short positions | `wrdsapps_eushort` |
| Delivered MIDAS security table | `wrdssec_midas` |
| SEC filings, text and links | `secsamp_all` is the restricted SEC sample in this snapshot |
| ABS, insider filings, mutual funds, environmental or short volume | `wrds_*_samp` are separate restricted sample products |
| Gutenberg books | `gutenberg.gutenberg_book` is the canonical available table; exact release and relation to the documented WTA product remain unverified |

Some `wrdsappssamp_all` tables provide the only verified available delivery of
their particular sample or supplied identifier links. The catalog marks these
canonical without claiming full product access or current maintenance. Use
the recorded selection reason to distinguish them from samples with an
available full counterpart.

Use exact table columns and comments. A research application is not an interchangeable copy of its source database: record its construction method, identifier map, update date, supported market and return convention. Do not infer point-in-time availability from an accounting period or event date.

For event studies, specify event date, trading-calendar alignment, estimation/event windows, benchmark model, and overlap treatment before extraction. For financial ratios, keep numerator/denominator definitions and missing-denominator handling; ratios with similar names can use different samples or lags. Prototype with one firm and a short date range and compare a small number of manually reconstructed values if the question depends on exact definitions.

For SEC data, preserve filing/accession identity, form, amendment status, filing date/time and report period separately where supplied. Holdings report dates differ from public filing dates. Text counts, sentiment measures, exhibits and forms have different row grains; joining on CIK alone can multiply observations. Sample access does not establish full SEC subscription or all filing types.

MIDAS is a delivered SEC/WRDS product. Do not confuse it with raw TAQ; TAQ jobs follow [wrds-taq](../wrds-taq/SKILL.md). If a derived application depends on an inaccessible source, report that limitation rather than bypassing its privilege guard.

## Primary documentation

[WRDS product list](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-wrds/), [Analytics by WRDS](https://wrds-www.wharton.upenn.edu/pages/analytics/), and [SEC Analytics Suite](https://wrds-www.wharton.upenn.edu/pages/analytics/sec-analytics-suite-wrds/) describe the products and link their documentation. The catalog stores per-product dictionary URLs and delivery metadata. Do not represent an authenticated guide as read if only its public link was available.
