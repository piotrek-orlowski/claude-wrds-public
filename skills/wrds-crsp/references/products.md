# Current CRSP products and access

Checked 2026-10-05 against WRDS public product documentation and live PostgreSQL
metadata. Lifecycle and entitlement are separate: a current product can be
unsubscribed, and a retired table can still accept queries. Load
[wrds-catalog](../../wrds-catalog/SKILL.md) to inspect the shipped table/column
inventory and access evidence before choosing a table. A successful `LIMIT 0`
only establishes planning, not that rows can be read.

## Product map

| Product | Observed current schema | Selection rule |
|---|---|---|
| Stocks | `crsp_a_stock` | Annual CIZ delivery; use `crsp.dsf_v2`/`msf_v2` or underlying `stk*` tables |
| Indexes | `crsp_a_indexes` | Prefer CIZ `ind*` and `*_v2`; separately maintained IFZ/SFZ files remain in scope where exact lifecycle is documented |
| Mutual funds | `crsp_q_mutualfunds` | Quarterly maintained product, 29 tables |
| Treasuries | `crsp_a_treasuries`, `crsp_q_treasuries` | Current `tfz_*` files; choose one delivery, never concatenate overlapping annual/quarterly products |
| CCM | `crsp_a_ccm` and other delivery schemas | Maintained separate product; underlying schema usage was denied in this account |
| Ziman REITs | CRSP Ziman delivery schemas | Maintained separate product; no accessible underlying product established here |

The `crsp` schema mixes aliases to several products. Resolve each view's
dependency before treating it as entitled. Annual/quarterly/monthly in a schema
name denotes delivery cadence, not necessarily the frequency of observations.
Stock-only and stock-plus-index bundles also differ. The
[WRDS CRSP product page](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/center-for-research-in-security-prices-crsp/)
lists these product boundaries. Do not filter products by words such as
`historical`: a historical-index product can be maintained.

## Stock and index table selection

Use [schema](schema.md), [codes](versions-and-codes.md), and [queries](queries.md)
for stock work. For indexes, use `indseriesinfohdr` and `indfamilyinfohdr` to
select the desired `indno`/family before extracting `inddlyseriesdata` or
`indmthseriesdata`. The `_ind` counterparts belong to the full index product.
Preserve index identity in the output: frequency, universe, weighting,
dividend treatment, and rebalancing are economically different choices.

`wrds_dailyindexret_query` and `wrds_monthlyindexret_query` provide useful
current market-index returns. Current S&P tables are `dsp500_v2`, `msp500_v2`,
`dsp500list_v2`, and `msp500list_v2`; membership intervals are not a current
constituent list. Inspect their recorded columns before joining.

Excluded: SIZ `dsf`, `msf`, `stocknames`, `dse*`, `mse*`, `dsi`, and `msi`.
The [WRDS CIZ webinar, slide 27](https://wrds-www.wharton.upenn.edu/documents/2084/Webinar.pdf)
explicitly maps these to current CIZ families; the
[transition notice](https://wrds-www.wharton.upenn.edu/pages/data-announcements/changes-to-crsp-data/)
confirms the December 2024 final SIZ period. The
[Format 1.0 guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-1-0/)
also identifies the retired `saz_*` stock delivery.

The [July 2026 Historical Indexes guide](https://indexes.morningstar.com/docs/guide/crsp-historical-indexes-guide?isRdp=true)
continues IFZ and documents SFZ alternatives, so cataloged maintained files
remain in scope. For new applicable workflows prefer CIZ; match portfolio
identity rather than replacing it with a composite level. The three Select
Treasury series and portfolio datasets without a verified available replacement
are canonical, even where release documentation is incomplete. Prefer the
available `_v2` S&P membership tables and unsuffixed SFZ copies over their
reviewed alternatives. Internal `qvards` tables remain excluded from research
defaults. See the catalog selection reason; latest observation dates still
need checking. Available CCM samples are canonical within their restricted
scope while production CCM remains inaccessible to this account.

## Mutual funds

Read this product at its own grain. `crsp_fundno` identifies a fund/share-class
record; `crsp_portno` identifies a portfolio. They are not stock PERMNOs.

| Task | Current tables and verified fields |
|---|---|
| Returns | `daily_returns(crsp_fundno,caldt,dret)`, `monthly_returns(crsp_fundno,caldt,mret)` |
| NAV/assets | `daily_nav`, `monthly_nav`, `monthly_tna(crsp_fundno,caldt,mtna)`; combined tables also exist |
| Identity/history | `fund_names` with `chgdt,chgenddt`; `fund_hdr`, `fund_hdr_hist` |
| Fund to portfolio | `crsp_portno_map(crsp_fundno,crsp_portno,begdt,enddt)`; inspect `portnomap` separately |
| Fees/styles/flows | `fund_fees`, `fund_style`, `fund_flows` |
| Holdings | `holdings(crsp_portno,report_dt,security_rank,eff_dt,percent_tna,nbr_shares,market_val,permno,cusip,...)` |
| Distributions/loads | `dividends`, front/rear load detail and group tables |

Bound the pilot to one fund and a month, or one portfolio/report date. Join
fund names and portfolio mappings within validity intervals. Several share
classes can map to one portfolio: do not repeat and sum its holdings for each
class. `report_dt` is the holdings period end; `eff_dt` is when CRSP obtained
the information, not necessarily the public release date. Preserve both.
Missing stock identifiers are legitimate for non-equity holdings.

Before aggregating, verify return, TNA, market-value, and fee units in the
current provider dictionary; stock-file units do not transfer automatically.
Keep inactive/dead funds when the research universe requires them. The latest
header is not a historical fund universe. Check share-class counts, interval
overlap, duplicate portfolio holdings, weight totals, and missing reporting
periods before scaling.

## Treasuries

The current delivery uses `tfz_*`. Individual issues use `kytreasno` in the
WRDS PostgreSQL layout, while supplementary series use `kytreasnox`; do not
copy provider display `(KY)TREASNO` literally into SQL. Calendar dates are
`caldt` in `tfz_dly`, and `mcaldt` in `tfz_mth` (check the catalog for each
supplementary file).

| Need | Current files |
|---|---|
| Issue descriptions/master/payments | `tfz_iss`, `tfz_mast`, `tfz_pay` |
| Issue price/return/yield panels | `tfz_dly`, `tfz_mth` |
| Supplemental series metadata | `tfz_idx` |
| Fixed-term indexes | `tfz_dly_ft`, `tfz_mth_ft` |
| Bond portfolios/Fama-Bliss | `tfz_mth_bp`, `tfz_mth_fb` |
| Risk-free series | `tfz_mth_rf`, `tfz_dly_rf2`, `tfz_mth_rf2` |
| Term structures | `tfz_mth_ts`, `tfz_dly_ts2`, `tfz_mth_ts2` |
| CPI/rates | `tfz_dly_cpi`, `tfz_mth_cpi`, `tfz_dly_cd`, `tfz_mth_cd` |

For example, `tfz_mth_rf` has `kytreasnox,mcaldt,rmtreasno,rmcrspid,tmbidytm,
tmaskytm,tmytm,tmduratn`. Its `tmytm` is an annualized percentage yield, not a
monthly holding-period return. A pricing discount factor and an excess-return
benchmark require different transformations. The
[Treasury guide](https://www.crsp.org/wp-content/uploads/guides/CRSP_US_Treasury_Database_Guide_for_SAS_ASCII_EXCEL_R.pdf)
distinguishes original monthly RF series from daily/monthly RF2 series.

Prototype one `kytreasno` or `kytreasnox` and a short interval. Preserve the
selected series definition, quote side, accrued-interest treatment, return
unit, duration unit, and day-count convention. Do not assume Treasury returns
or yields use the same scale as equity returns.

Excluded legacy `bm*`, `bx*`, and `riskfree` mappings should use current TFZ
counterparts. The [September 2014 release notice](https://www.crsp.org/crsp_pdf/september-2014-monthlyquarterly-release-notes/)
states that December 2014 was the final legacy delivery. The
[2010 monthly Treasury manual, pp. 24–25](https://wrds-www.wharton.upenn.edu/documents/409/CRSP_Monthly_US_Treasury_Guide.pdf)
explicitly identifies the other retired MB, bond-portfolio, Fama-Bliss and
bid/ask/average supplemental filenames. Their TFZ counterparts preserve the
economic series; check the series definition and units when changing formats.
