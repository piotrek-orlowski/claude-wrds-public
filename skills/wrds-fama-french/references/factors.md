# Factor selection and timing

Table names, columns, and date labels below come from live WRDS catalog metadata collected 2026-10-05. Use the installed [catalog](../../wrds-catalog/SKILL.md) for the complete dictionary and subsequent access/lifecycle checks. `ff_all` is the provider product schema; `ff` exposes aliases to it.

## Current table families

| Tables in `ff_all` | Intended use | Distinctions to preserve |
|---|---|---|
| `factors_daily`, `factors_monthly` | Three-factor research series with `mktrf`, `smb`, `hml`, `rf`, `umd` | `umd` is an additional momentum series, not one of the three FF factors |
| `fivefactors_daily`, `fivefactors_monthly` | Adds `rmw` and `cma`, with its five-factor SMB series | Do not silently mix SMB from the three-factor table into FF5 |
| `portfolios`, `portfolios_d` | Six size/book-to-market portfolio return series | Portfolio returns are not automatically long-short factor returns |
| `portfolios25` | Twenty-five size/book-to-market portfolio returns | Inspect the requested weighting/portfolio fields in the catalog |
| `industry12`, `industry48` | Industry descriptions/classification files | Their names do not imply time-series industry returns |
| `liq_ps` | `ps_level`, `ps_innov`, `ps_vwf` | Aggregate liquidity level, innovation, and traded-factor concepts differ |
| `liq_sadka` | `sadka_tf`, `sadka_pv` | Transitory-fixed and permanent-variable liquidity measures |
| `factors_china` | `mnthdt`, `rf_mon`, `mktrf`, `smb`, `vmg` | Separate China series; verify its methodology and scale rather than relabeling `vmg` as US HML |

WRDS identifies `ff_all` as its current Fama-French product and describes the distinct liquidity datasets. These definitions are not a reason to treat every liquidity measure as a traded return. [WRDS product documentation](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/fama-french-portfolios-factors/)

French's five-factor specification defines size, value, profitability, and investment spreads using its underlying portfolio sorts. The five-factor SMB combines size spreads from three sorts. Its market series is already net of the risk-free series; the provider changed the risk-free source beginning June 2024. Preserve those definitions when comparing vintages. [French's five-factor description](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html)

## Dates and units

In the live dictionary, both monthly factor tables label `date` as the first day of the month and `dateff` as the last trading day. `liq_ps.date` and `liq_sadka.date` are also labeled last trading day. A month key prevents accidental loss of observations when merging these with CRSP's last trading date or JKP's calendar month-end.

The numeric data types and labels do not establish whether a return is stored in decimals or percentage points. Keep values unchanged until the WRDS dictionary or a same-date provider check establishes their scale. Apply one documented conversion consistently to asset returns, factor returns, and `rf`. Do not subtract the risk-free rate twice from an already excess-return outcome.

Use the supplied daily `rf` with daily returns; do not create a daily rate by dividing a monthly value by an assumed number of days. State how missing factor dates, market holidays, and sample endpoints are treated. A spread between an asset return and `mktrf` is not a conventional excess asset return.

## Bounded monthly recipe

```sql
SELECT (DATE_TRUNC('month', date) + INTERVAL '1 month' - INTERVAL '1 day')::date AS date,
       date AS provider_date, dateff,
       mktrf, smb, hml, rmw, cma, rf, umd
FROM ff_all.fivefactors_monthly
WHERE date >= DATE '2024-01-01' AND date < DATE '2024-02-01'
ORDER BY date;
```

This preserves raw values and both supplied date fields. It was checked against current column metadata and accepted table-level planning evidence; no factor observations were downloaded for this skill. Before a larger run, verify exactly one observation per intended date key and the value scale. For a daily prototype, use `fivefactors_daily` over the same bounded month and select its `date` directly; it has no monthly `dateff`, `year`, or `month` fields.
