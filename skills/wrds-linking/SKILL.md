---
name: wrds-linking
description: Use when joining WRDS datasets across CRSP, Compustat, OptionMetrics, TAQ, IBES, bonds, Capital IQ, BoardEx, SEC and other provider identifiers; covers link validity, date alignment and join cardinality.
---

# Cross-database WRDS links

Use this skill to compose datasets after selecting their source-specific
skills. `wrds-psql-agent` handles direct PostgreSQL work, including multi-schema
queries. `wrds-taq-agent` handles TAQ SAS extraction and its SSH job workflow.
Prepare the link and daily data needed by a TAQ job through PostgreSQL when
appropriate; never run PostgreSQL over SSH.

Use [wrds-catalog](../wrds-catalog/SKILL.md) to enumerate the [available linking products](references/catalog-coverage.md), exact fields, dependencies and access outcomes. The official [WRDS linking matrix](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/database-linking-tool/) documents additional database pairs. Links to authenticated procedures are references, not evidence that their contents were read.

## Choose the identifiers and link source

| Dataset | Main identifier | Linking detail |
|---|---|---|
| CRSP | PERMNO (security), PERMCO (company) | CIZ historical CUSIP and ticker have validity intervals |
| Compustat | GVKEY | [CCM reference](../wrds-compustat/references/ccm.md); the CRSP key in `ccmxpf_lnkhist` is `lpermno` |
| OptionMetrics | SECID (underlying), OPTIONID (contract) | [SECID–PERMNO reference](../wrds-optionmetrics/references/crsp-link.md) |
| Daily TAQ | Symbol root and suffix on a date | [TAQ–CRSP links](references/taq-crsp.md) |
| Monthly TAQ | SYMBOL on a date | [TAQ–CRSP links](references/taq-crsp.md), including legacy CUSIP normalization |
| IBES | Provider ticker/security mapping | [LSEG guidance](../wrds-lseg/SKILL.md); inspect current `wrdsapps_link_crsp_ibes` |
| Bonds | Bond CUSIP and issuer | [Bond guidance](../wrds-bonds/SKILL.md); keep multiple bond tranches distinct |
| Capital IQ | Company, security and trading-item IDs | [Capital IQ guidance](../wrds-capital-iq/SKILL.md); choose entity level before linking |
| BoardEx/Altrata, BvD, Audit Analytics | Provider-specific organization/person IDs and identifiers | [Governance guidance](../wrds-governance/SKILL.md); company and person links are separate |
| SEC | CIK plus filing identity | [WRDS research guidance](../wrds-research/SKILL.md); retain identifier validity and sample limits |

Prefer the documented WRDS link table for the requested pair and period. If it
does not cover the task, use [historical CUSIP intervals](references/manual-cusip.md).
Ticker matching is a last resort: combine date overlap with company-name and
share-class checks, and retain ambiguous candidates for review.

The maintained People Link endpoints `wrdsapps_plink_exec_boardex`,
`wrdsapps_plink_exec_ciq`, and `wrdsapps_plink_boardex_ciq` connect people across
ExecuComp, BoardEx and Capital IQ. Inspect the `*_link` and company-enriched
table layouts separately. A person-to-person match does not itself define
which employer or board appointment belongs to an observation date. Retain
person IDs and company/role/date information before aggregating.

## Compose and validate

1. State the final observation unit and expected relationship at each join:
   one-to-one, many options to one daily stock row, or another explicit design.
   A security-level identifier is not automatically a company-level identifier.
2. Extract a small, date-bounded sample from each source independently. Use the
   source skills for units, data-quality filters, and financial interpretation.
3. Match identifiers inside their validity intervals. Keep observation dates,
   link-validity dates, and information-availability dates distinct. Calendar
   month-end and last trading day may differ; define the period alignment
   before joining monthly data.
4. Apply the documented link-quality rule and preserve its code in the output.
   Check ties and overlapping mappings before joining. `DISTINCT` is not a
   resolution policy for conflicting matches.
5. Compare source rows, matched rows, unmatched rows, distinct source keys, and
   resulting keys. Inspect anti-joins or left joins to explain dropped coverage.
   Check boundary dates, missing identifiers, and more than one match per key.
6. Aggregate to the intended unit before a join when necessary; otherwise a
   many-to-many join can multiply economic quantities. Retain source identifiers,
   link windows, and exclusions so the merge can be reproduced.

For options matched to realized dividends and a bounded cross-database build,
read [composition examples](references/examples.md). CCM filtering and
accounting-data availability belong to `wrds-compustat`; OptionMetrics units and
link scores belong to `wrds-optionmetrics`. Keep those definitions in their
owning references rather than copying them here.
