# Bond identifiers, timing, and recipes

Field names and types below were observed in the live catalog on 2026-10-05. Resolve complete layouts through [wrds-catalog](../../wrds-catalog/SKILL.md), then use [wrds-psql](../../wrds-psql/SKILL.md) for bounded direct SQL. These recipes were matched to metadata; research observations were not downloaded for them.

## Keys and date alignment

- Raw TRACE: `cusip_id` identifies a bond; `msg_seq_nb` alone is not a globally unique permanent trade key. Preserve execution/report dates, original-message identifiers, status, and era-specific control fields when resolving revisions.
- FISD: `issue_id` and `issuer_id` are separate identifiers. `complete_cusip` is the nine-character bond key. `fisd_rating_hist` includes `issue_id`, `rating_type`, `rating_date`, `rating`, `rating_status`, and `reason`; do not join all historical ratings to every trade or take a future rating.
- MSRB: retain `rtrs_control_number` and `version_number` alongside dates and report metadata. Investigate versions before counting trades. The provider can revise published trade records. [MSRB explanation of revisions](https://emma.msrb.org/EmmaHelp/UnderstandingMarketStatistics)
- WRDS bond-equity links: `bondcrsp_link` contains `cusip`, `permno`, `permco`, TRACE/CRSP date ranges, and `link_startdt`/`link_enddt`. Match on the effective link interval and validate multiplicity. The linking suite is expressly designed to connect bond issues with CRSP equity. [WRDS linking documentation](https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/linking-bondtracemergent-fisd-with-crsp/)
- Dickerson: monthly fields are `cusip`, `date`, `permno`, `gvkey`; daily fields are `cusip_id`, `trd_exctn_dt`, `permno`, `permco`, `gvkey`. The catalog stores these GVKEYs numerically, unlike Compustat's textual identifier; validate integer values and restore the required string representation before a Compustat merge.

## Interpret measures before filtering

WRDS monthly `bondret` and `bondret_std` both have 59 columns in this snapshot. Preserve `price_eom_flg`, `gap`, `t_date`, coupon fields, and the distinction among `ret_eom`, `ret_ldm`, and `ret_l5m`. A carried price is not a new transaction, and a multi-month gap can change the intended holding period.

Dickerson daily `pr` is labeled clean price, `prfull` dirty price, `acclast` accrued interest, and `accpmt` accumulated coupon payments. `ytm`, `mod_dur`, and `credit_spread` are distinct from monthly `cs`, `md_dur`, and `spc_rat`. The labels alone do not prove percentage versus decimal yield/spread units or a numeric rating cutoff. Require a current codebook or a validated small comparison before any conversion or investment-grade screen.

Do not reconstruct total return from clean prices alone: coupon income and accrued interest matter. Distinguish a supplied total return from a risk-free-adjusted or Treasury-adjusted return. For the separate contributed `bonds`/`firms` panels, labels identify `ret_exc` as risk-free-adjusted and `ret_texc` as Treasury-adjusted; these have different economic meanings.

TRACE execution and reporting times are `time without time zone` on the raw enhanced table, but the similarly named fields on `wrdsapps_bondret.trace_enhanced_clean` are numeric in the current dictionary. Confirm their encoding before converting to timestamps. Do not infer timestamp precision, timezone, or clock accuracy from a type alone.

## Monthly Dickerson prototype

```sql
SELECT date, cusip, permno, gvkey, ret_vw, cs, md_dur, spc_rat
FROM contrib_bond_dickerson.dickerson_bonds_monthly
WHERE permno = 14593
  AND date >= DATE '2024-01-01' AND date < DATE '2024-02-01'
ORDER BY date, cusip;
```

This is one issuer/month, potentially several bond issues. Check one row per CUSIP-month and the availability of the requested return/characteristic fields. Do not call the issuer-month complete merely because one bond is present. A firm-level portfolio needs an explicit lagged weighting convention and handling of missing tranches.

## WRDS return-panel prototype

Supply `bond_cusip` as a psql variable containing an actual bond identifier from the research request or a verified lookup. The quoted psql substitution makes it a SQL string literal.

```sql
SELECT date, cusip, issue_id, price_eom, price_eom_flg, gap,
       ret_eom, ret_ldm, ret_l5m, yield, duration,
       rating_num, rating_cat, rating_class
FROM wrdsapps_bondret.bondret
WHERE cusip = :'bond_cusip'
  AND date >= DATE '2024-01-01' AND date < DATE '2024-02-01'
ORDER BY date;
```

The same column names occur on `bondret_std`; choosing that table changes the underlying product, not just a label. Preserve this choice in exported provenance.

## Raw enhanced TRACE inspection

```sql
SELECT cusip_id, trd_exctn_dt, trd_exctn_tm, trd_rpt_dt, trd_rpt_tm,
       msg_seq_nb, orig_msg_seq_nb, trc_st, rptd_pr, entrd_vol_qt,
       rpt_side_cd, cntra_mp_id, asof_cd, sale_cndtn_cd,
       first_trade_ctrl_date, first_trade_ctrl_num
FROM trace_enhanced.trace_enhanced
WHERE cusip_id = :'bond_cusip'
  AND trd_exctn_dt >= DATE '2024-01-08'
  AND trd_exctn_dt < DATE '2024-01-13'
ORDER BY trd_exctn_dt, trd_exctn_tm, trd_rpt_dt, trd_rpt_tm, msg_seq_nb;
```

This is an inspection sample, not a complete correction/reversal cleaning algorithm. Subsequent messages can refer to earlier trades and may require a report-date buffer outside the execution window. Read the [FINRA layouts for the relevant era](https://www.finra.org/filing-reporting/trace/historic-academic-data) before defining the message linkage and final transaction population. Keep raw records and exclusion reasons rather than overwriting the source sample.
