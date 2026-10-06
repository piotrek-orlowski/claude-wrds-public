---
name: wrds-public-data
description: Find and query WRDS bank regulatory reports, Federal Reserve rates and FX, Federal Judicial Center litigation, Macro Finance Society series, Research Quotient and Total q. Distinguish entity identifiers, observation dates, vintages, and retired public datasets.
---

# WRDS public and research series

Use [wrds-catalog](../wrds-catalog/SKILL.md) for exact tables/columns and [wrds-psql](../wrds-psql/SKILL.md) for queries. [Coverage](references/catalog-coverage.md) is the complete table map for this account snapshot.

| Topic | Product | First checks |
|---|---|---|
| Bank Call Reports | `bank_all` | Bank versus holding company, regulatory item dictionary, reporting period, institution history |
| Bank identifiers/research variables | `bank_premium_samp` | Restricted sample; do not infer full premium access |
| Rates and FX | `frb_all.rates_daily`, `rates_monthly`, `fx_daily`, `fx_monthly` | Rate maturity, quotation direction, units and frequency |
| Federal court data | `fjc_litigation`, `fjc_linking` | Case versus party versus linked firm; filing, termination and event dates differ |
| Macro-finance research series | `macrofin_comm_trade` | Select the exact contributed series and release; frequencies and units differ |
| Research Quotient | `rq_all.rq_data` | Firm identifier, fiscal year, estimate definition and availability |
| Total q and intangible capital | `totalq_all.total_q` | Preserve supplied components and definitions; do not substitute accounting book assets |
| Blockholder ownership | `block_all` | Provider definitions, fixed historical sample, firm/shareholder multiplicity |
| Order-execution disclosures | `doe_all` | Reporting market, security, reporting period and execution-quality measure definitions |
| Healthcare spending | `public_all` MEPS tables | Canonical available delivery; verify each table's population, units and observation dates |
| Unversioned national accounts | `pwt_all.na` | Canonical for this distinct available table; exact PWT release and observation dates remain unverified |

For banks, use `wrds_bank_reg_vars` to interpret regulatory variables and inspect `wrds_bank_crsp_link` before equity joins. Regulatory prefixes encode reporting scope: do not combine similarly numbered items from different forms or scopes without the item dictionary. Pilot one reporting entity and period, then validate mergers, identifier changes and duplicate report versions before expanding.

For macro series, distinguish observation period from publication/revision timing. The WRDS snapshot does not itself prove a real-time vintage. Keep each input frequency and unit explicit when joining. For litigation, keep all candidate firm links until multiplicity and date validity have been assessed.

## Version restrictions

The named version tables in `pwt_all` are PWT 6.x/7.x-era releases. The provider publishes PWT 11.0; those old WRDS editions are excluded from current defaults. The unversioned `na` table is canonical because no exact replacement was established, but its release remains unknown; do not describe it as PWT 11.0. MEPS tables are also canonical for this account; the visible alternate copy is inaccessible. Legacy DMEF/IRI/Dow Jones/PHLX products and removed SNL data remain excluded where retirement is established. Canonical selection does not prove continued maintenance or recent observations.

## Sources

- [WRDS Bank Regulatory](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-bank-regulatory/).
- [Federal Reserve products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-federal-reserve-board/).
- [Federal Judicial Center products](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/federal-judicial-center/).
- [Macro Finance Society](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-macro-finance-society/).
- [Contributed products, including RQ and Total q](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-vendor-partner-contributor/).
- [Provider's current Penn World Table](https://www.rug.nl/ggdc/productivity/pwt/).

Use the catalog's separate canonical and lifecycle fields: a sole available version is usable by default without claiming its release is verified. Other excluded public schemas remain searchable with `--all`.
