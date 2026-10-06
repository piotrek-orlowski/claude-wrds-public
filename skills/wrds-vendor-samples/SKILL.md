---
name: wrds-vendor-samples
description: Discover and query restricted WRDS vendor samples and trials, including FactSet, Markit, AHA, Calcbench, CSMAR, ETF Global, FTSE, hedge funds, NielsenIQ, Panjiva, PitchBook, Preqin, RavenPack, Revelio, ISS, Data Axle and other sample products. Never substitute them for full subscription data.
---

# WRDS vendor samples and trials

Use this skill when the account has sample/trial access to a product without a full dedicated domain skill. Load [wrds-catalog](../wrds-catalog/SKILL.md), then [wrds-psql](../wrds-psql/SKILL.md). [Coverage](references/catalog-coverage.md) lists every included schema and table count. Every exact table lookup supplies the provider page, dictionary URL, column comments and access outcome.

## Route by research object

| Object | Sample families | Verify before joining |
|---|---|---|
| Security fundamentals/ownership/supply chains | `factsamp_all`, `factsamp_revere` | Entity versus security IDs, ownership dates, relationship direction |
| CDS and securities finance | `mrktsamp_cds`, `mrktsamp_cdx`, `mrktsamp_msf`, `mrktsamp_red` | RED entity/obligation, tenor, currency, restructuring clause, contract/index series |
| Funds and private capital | `etfg_samp`, `hfrsamp_hfrdb`, `morningstarsamp_cisdm`, `pitchsmp`, `preqsamp_all` | Fund/share class/manager/deal IDs; reported versus valuation/cashflow dates |
| Corporate events/news/workforce | `ravenpack_trial`, `mpsych_sample`, `revelio_samp` | Document/event/entity/person grain, timestamps, historical versus current identifiers |
| Governance/insider records | `risksamp_all`, `twoiq_samp` | Issuer, meeting, proposal, owner, transaction and filing identities |
| Health, accounting, business locations | `aha_sample`, `calcbench_trial`, `infogroupsamp_business`, `infogroupsamp_residential`, `candid_samp` | Entity definition, reporting period, geography and version |
| Consumer sales and trade | `niq_samp`, `panjiva_samp` | Product-store-period versus shipment, quantities/units, party roles |
| Other specialized samples | `csmsamp_all`, `ftsesamp_russell_us`, `infraclear_samp`, `rstat_samp`, `zacksamp_all` | Use product-specific identifiers and dictionaries; Zacks is a separate provider from LSEG/IBES |

Other skills own CRSP, Compustat, OptionMetrics, TAQ, Capital IQ, LSEG, BoardEx/BvD/Audit Analytics, bonds and ESG samples. Follow the `skill` field returned by the catalog rather than duplicating their rules here.

## Required sample workflow

1. State that only a sample/trial is available and identify its scope from documentation and a bounded pilot. A permissive alias over sample data remains a sample.
2. Inspect one exact table's columns and the provider's current dictionary. Establish the observation unit, identifier type, date meaning, units, missing codes and sample restriction. The catalog is not a substitute for undocumented economic definitions.
3. Extract one entity or a short period and validate output shape, duplicate keys and missing values. Do not infer population coverage, country coverage, recent dates or subscription rights from successful planning.
4. Preserve provider identifier/reference tables and provenance. A returned company name or ticker is not automatically a stable join key.
5. Scale only within the requested and verified sample. If the task requires the full product, report the access gap explicitly instead of silently answering with sample results.

Product-level current means the sample is still offered by WRDS; the embedded observations or schema version may be old. Consult the delivery timestamp and sample documentation. Retired products and unlisted alternate copies are excluded from the default lookup. In particular, the obsolete SNL sample does not establish access to a current SNL product.

Primary entry point: [WRDS vendor documentation](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/). The bundled product registry contains the exact vendor page and data dictionary for each included schema, collected from both this directory and the official sitemap. A dictionary that requires login must be retrieved through an authorized session before relying on definitions unavailable in catalog comments.
