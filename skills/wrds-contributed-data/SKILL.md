---
name: wrds-contributed-data
description: Use WRDS contributed research datasets for CEO turnover, characteristic returns, corporate culture and litigation, intangible capital, liquidity measures, patents, and shareholder value. Find contributor-specific tables, definitions, provenance, and release limitations.
---

# WRDS contributed research data

Load [wrds-catalog](../wrds-catalog/SKILL.md), then [wrds-psql](../wrds-psql/SKILL.md). The [complete table coverage](references/catalog-coverage.md) includes aliases and base schemas. JKP Global Factor Data uses [wrds-jkp](../wrds-jkp/SKILL.md); Dickerson and other bond returns use [wrds-bonds](../wrds-bonds/SKILL.md).

## Select a dataset

| Topic | Current product/table entry points |
|---|---|
| CEO changes | `contrib_ceo_turnover.ceo_turnover` |
| Characteristic portfolios | `contrib_char_returns.char_returns` |
| Corporate culture | `contrib_corporate_culture.corp_culture` |
| Corporate federal litigation | `contrib_corp_fed_litigation.lawsuit_level`, `firmyear_level` |
| Intangible value | `contrib_intangible_value.int_factors`, `int_xsec` |
| Innovation and patent links | `contrib_kpss.kpss_patents`, `kpss_permco_link`; `contrib_patent_firm_link.patent_level`, `firm_year_panel` |
| Precomputed liquidity | `contrib_liquidity_taq.bbd`, `ilc` |
| Long-term shareholder value | `contrib_liva.liva` |
| Other contributed datasets | Enumerate `contrib_general`; do not infer a common row grain or update policy |

These names are catalog observations, not interchangeable measures. Select the contributor's product even when another contributed table has a similar name. Retain its release identity, methodology reference and transformations with the extract. A WRDS delivery timestamp can describe an upload without changing the underlying research sample.

## Extraction workflow

1. Retrieve the exact table's columns and comments with the catalog helper. Determine whether the row is a firm-year, patent, lawsuit, date-country portfolio or another unit. Check the contributor's dictionary before assigning units or interpreting a numeric flag.
2. Keep original identifiers and observation dates. For patent or lawsuit links, test multiplicity before aggregating to firms; one source event can legitimately map to several entities.
3. Prototype one entity or one year. Inspect missing keys, repeated keys and whether a measure is a level, return, score, percentile or count. Do not infer decimal-versus-percent returns from a name.
4. Preserve raw fields before applying research-specific sample filters. Report unmatched joins and the contributor's actual release coverage.

`contrib_liquidity_taq` contains delivered research measures accessible through PostgreSQL. Recomputing them from raw TAQ requires [wrds-taq](../wrds-taq/SKILL.md) and SAS. The delivered measures do not establish raw TAQ access or reproduce every possible filter choice.

## Documentation

[WRDS contributed products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-vendor-partner-contributor/) lists each contributor product and dictionary. The local catalog records the specific source URL and retrieval date. Follow the dataset's own documentation and attribution requirements. If understanding its paper is required, first produce the structured paper summary required by the project instructions; a schema inspection alone is not a methodology review.
