---
name: wrds-esg
description: Query WRDS environmental, social and governance data, S&P ESG, Trucost emissions and climate risk, and restricted MSCI, Sustainalytics, RepRisk and environmental samples. Use for selecting the correct score, emissions scope, release, identifier, and observation date.
---

# WRDS ESG and climate data

Load [wrds-catalog](../wrds-catalog/SKILL.md) and [wrds-psql](../wrds-psql/SKILL.md). Read [catalog coverage](references/catalog-coverage.md) for all tables. Catalog access preflight does not establish complete company or time coverage.

## Product selection

| Product | Tables/schema families | Interpretation checks |
|---|---|---|
| S&P ESG | `sp_esg.wrds_esg`, `wrds_esg_facts`, `spgquestion`, `spgtransparencyscore` | Identify assessment year, question/metric, reported versus calculated score and revision timing |
| Trucost | `trucost_common`, `trucost_environ`, `trucost_carbon`, `trucost_fossilfuel`, `trucost_paris`, `trucost_risk`, `trucost_sector_ff`, `trucost_sector_revenue` | Use company and data-item dictionaries; preserve units, scope, scenario and forecast horizon |
| MSCI | `msci_common_samp`, `msci_esg_samp`, `msci_climate_samp` | Sample-only; keep issuer/instrument distinction and metadata definitions |
| Sustainalytics | `sustainalyticssamp_all` | Sample-only; distinguish raw scores, weighted scores, weights and risk-rating components |
| RepRisk | `reprisk_sample` | Sample-only; keep event, entity identifier, issue and metric tables distinct; stored sample versions can differ from full current product |
| WRDS environmental | `wrds_environmental_samp` | Sample-only; facility and geography identifiers need explicit company links |

Use the catalog's table lookup to retrieve exact columns. Do not hard-code a guessed company-ID field or assume every `wrds_*` table uses the same ID. Join through documented company/reference tables before [cross-database linking](../wrds-linking/SKILL.md).

## Workflow

Select one company, one reporting period, and a small set of metrics first. Record the data-item code and units alongside the value. Test the intended key including assessment/release dates, scenario and scope where present. Multiple rows often describe distinct metrics or revisions and should not be removed merely to force company-year uniqueness.

For emissions, establish whether a measure covers Scope 1, 2 or 3 and whether it is reported, estimated, intensity-based or absolute. Do not sum overlapping scopes or aggregate intensities as emissions totals. For climate scenarios, keep observed values separate from forecasts. For backtests, use a documented availability date rather than assuming the fiscal period was the publication date.

A score from one provider is not the same measure as a similarly named score from another. Retain source, product version and missing-reason codes in comparisons. Check current delivered coverage with a bounded sample; provider page date ranges can contain sentinel dates.

## Primary documentation

- [WRDS S&P Global and Trucost products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sp-global-market-intelligence/).
- [WRDS MSCI products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-msci/).
- [WRDS Sustainalytics products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/sustainalytics/).
- [WRDS RepRisk products and archived versions](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/reprisk/).

Each catalog product includes its dictionary URL. A login-gated dictionary has not been read merely because its URL is recorded.
