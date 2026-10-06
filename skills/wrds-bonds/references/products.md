# Choose the bond product

This guide was assembled from primary provider descriptions and the live 2026-10-05 WRDS metadata catalog. The full current inventory and data dictionaries remain in [wrds-catalog](../../wrds-catalog/SKILL.md); avoid creating competing handwritten copies of hundreds of fields.

## Product map

| Current product schema | Observed relations | Use and scope |
|---|---:|---|
| `trace_standard` | 23 | Standard TRACE transaction feeds, reference files, and daily trade summaries |
| `trace_enhanced` | 14 | Enhanced transactions and reference files; distinct corporate, agency, 144A, ABS, CMO, MBS, and TBA products |
| `fisd_fisd` | 59 | Issue/issuer terms, ratings, calls, puts, defaults, covenants, and event histories |
| `fisd_common` | 1 | `issue_issuer` identification/terms lookup |
| `fisd_naic` | 1 | Insurance-company bond transactions; not the TRACE universe |
| `msrb_all` | 3 | Municipal transactions, lookup, and a web-query support table |
| `wrdsapps_bondret` | 4 | `bondret`, `bondret_std`, `trace_enhanced_clean`, `trace_standard_clean` |
| `wrdsapps_link_crsp_bond` | 1 | `bondcrsp_link`, with explicit effective link dates |
| `contrib_bond_dickerson` | 2 | Daily bond pricing/analytics panel and monthly bond return/characteristic panel |
| `contrib_corporate_bond_returns` | 2 | `bonds` and issuer-level `firms`; separate contributed panels |
| `fisdsamp_all` | 9 | FISD sample issue/issuer/ratings/transaction products |
| `msrbsamp_all` | 1 | `msrb_trial`; a restricted sample, not the full municipal history |

All listed relations accepted zero-row planning probes in that snapshot. `trace`, `fisd`, `msrb`, and selected `contrib`/`wrdsapps` entries expose aliases; inspect the exact dependency and observed privilege-guard result before using an alias. A sample product's accessibility does not imply a full-product subscription. Old schema copies are cataloged for audit, not selected as current products.

## Raw and cleaned TRACE

FINRA distinguishes Enhanced Historical from Academic TRACE: the enhanced product includes full transaction size and additional trade-side/counterparty information, while the academic product has its own masked-dealer identifiers and delivery rules. Do not claim that a WRDS table is the academic dealer-identified product merely because it contains TRACE data. [FINRA historical data description and file layouts](https://www.finra.org/filing-reporting/trace/historic-academic-data)

Standard and enhanced transaction products have different fields and reporting-era conventions. In the current dictionary, standard `trace` uses textual `ascii_rptd_vol_tx` with quantity-format fields; enhanced `trace_enhanced` has numeric `entrd_vol_qt`. Do not cast a standard capped/display quantity to exact volume without its format definition. Corporate, agency, 144A, and securitized-product tables describe different populations; select and document them deliberately.

WRDS Bond Returns supplies cleaned standard/enhanced transactions and a monthly panel containing prices, returns, coupons, and yields. Cleaning and return construction are maintained methodology, not proof that any downstream filter is appropriate. [WRDS Bond Returns overview](https://wrds-www.wharton.upenn.edu/pages/grid-items/wrds-bond-returns/)

## FISD and municipal data

FISD's issue terms, issuer information, and insurer transactions complement trade data. The three full schemas and the sample schema are separately listed by WRDS; a metadata date-range summary can include future maturity dates and is not a trading-history completeness measure. [WRDS LSEG Mergent product description](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/lseg-mergent/)

MSRB has historical and other transaction products with different revision timing and size-display conventions. Its academic product also differs in dealer identifiers and primary-market exclusions. Inspect the actual WRDS dictionary and chosen product before claiming those features. [MSRB transaction products](https://www.msrb.org/Market-Data-and-Research/Trade-Data-Subscriptions)

`msrb_all.msrb` contains 25 columns in this snapshot, including separate `trade_date`/`time_of_trade` and `rtrs_publish_date`/`rtrs_publish_time`. `par_traded` is text. Do not assume all values are exact numeric principal amounts or that publication time equals execution time.

## Contributed bond panels

The current Dickerson provider site links both daily and monthly WRDS contributed data and its transaction-cleaning/daily-analytics pipeline. Preserve the release and current dictionary: the public project explicitly records changes. [Open Source Bond Asset Pricing](https://openbondassetpricing.com/)

The live monthly WRDS table has 140 columns and uses `cusip`/`date`; its daily counterpart has 43 columns and uses `cusip_id`/`trd_exctn_dt`. The daily table is an aggregated pricing/analytics panel with trade counts and several price measures, not a raw one-row-per-trade tape. Do not transplant field names or historical downloadable-file conventions between products.

The separate `contrib_corporate_bond_returns.bonds` and `.firms` tables have 19 and 18 fields respectively in the snapshot. Both contain `ret_eom`, `ret_exc`, and `ret_texc`, but only the bond table has the bond CUSIP. The firm panel is already aggregated; averaging it together with issue-level observations would double count issuers.
