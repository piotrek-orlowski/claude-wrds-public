# CRSP schema and identifiers

Migrated 2026-10-05 from the former CRSP agent. Column counts, types, flags, and coverage below are inherited reference material; the share-unit subsection records two bounded live checks. Verify exact tables with `wrds-schema` before relying on uncertain fields.

## Schema architecture

The `crsp` schema contains **views** pointing to underlying schemas. The
2026-10-05 catalogue confirms current stock, indexes, Treasury, and mutual-fund
schema candidates; a schema grant alone is not a data-read test:
- `crsp_a_stock` — CIZ stock tables
- `crsp_a_indexes` — Index tables
- `crsp_a_treasuries` — Treasury/risk-free data
- `crsp_q_mutualfunds` — Mutual fund data

Use the resolved current product namespace or its verified `crsp` alias.
Older alias namespaces (`crspa`, `crspm`, `crspq`) are not execution targets in
this toolkit. Their visibility does not establish which product or access
level they provide. See [current products](products.md).

CCM access may require a separate subscription. See [wrds-compustat](../../wrds-compustat/SKILL.md) for its tables and linking rules.

---

## Primary Identifiers

**PERMNO** (Permanent Security Number):
- Unique per security/share class. Never changes, never reassigned after delisting.
- Primary security identifier for stock files; store as an integer rather than a ticker.

**PERMCO** (Permanent Company Number):
- Unique per company. One PERMCO can have multiple PERMNOs (multiple share classes).
- Use PERMCO for firm-level aggregation (e.g., total market cap across share classes).

**Other Identifiers:**
- `cusip`: historical eight-character CUSIP; `hdrcusip`: header CUSIP. Keep
  identifiers as text and distinguish historical from current/header values.
- `ticker`: Trading symbol — **reused over time!** Always use with date ranges.

---

## Table and column reference (inherited snapshot)

### Daily Stock File: `crsp.dsf_v2` (50 columns)

| Column | Type | Description |
|--------|------|-------------|
| `permno` | int | Permanent security identifier |
| `permco` | int | Permanent company identifier |
| `yyyymmdd` | int | Date as YYYYMMDD integer |
| `dlycaldt` | date | Calendar date |
| `dlyprc` | numeric | Price (always positive in v2) |
| `dlyprcflg` | varchar | Price source: TR=trade, BA=bid-ask avg, MP=missing |
| `dlyret` | numeric | Total return (includes dividends AND delisting returns) |
| `dlyretx` | numeric | Return excluding dividends |
| `dlyreti` | numeric | Return on investment (index-like) |
| `dlyretmissflg` | varchar | Return missing reason (NULL = valid return) |
| `dlyretdurflg` | varchar | Return duration flag |
| `dlyvol` | numeric | Trading volume |
| `dlybid` | numeric | Closing bid |
| `dlyask` | numeric | Closing ask |
| `dlyopen` | numeric | Opening price |
| `dlyclose` | numeric | Closing price |
| `dlylow` | numeric | Daily low |
| `dlyhigh` | numeric | Daily high |
| `dlynumtrd` | int | Number of trades |
| `dlymmcnt` | smallint | Market maker count |
| `dlycap` | numeric | Market cap (pre-computed, $000s) |
| `dlycapflg` | varchar | Market cap flag |
| `dlyprevprc` | numeric | Previous price |
| `dlyprevprcflg` | varchar | Previous price flag |
| `dlyprevdt` | date | Previous price date |
| `dlyprevcap` | numeric | Previous market cap |
| `dlyprevcapflg` | varchar | Previous market cap flag |
| `dlydelflg` | varchar | Delisting day flag (Y/N) |
| `dlyorddivamt` | numeric | Ordinary dividend amount on ex-date |
| `dlynonorddivamt` | numeric | Non-ordinary dividend amount on ex-date |
| `dlyfacprc` | numeric | Factor to adjust price (point-in-time, non-cumulative) |
| `dlydistretflg` | varchar | Distribution return flag |
| `dlyprcvol` | numeric | Price-volume product |
| `dlycumfacpr` | numeric | Cumulative price adjustment factor |
| `dlycumfacshr` | numeric | Cumulative share adjustment factor |
| `shrout` | int | Shares outstanding in thousands; documented unit and bounded WRDS check below |
| `hdrcusip` | varchar | Header CUSIP |
| `cusip` | varchar | Historical CUSIP (was ncusip in v1) |
| `ticker` | varchar | Ticker symbol |
| `siccd` | int | SIC code |
| `nasdissuno` | int | NASDAQ issue number |
| `exchangetier` | varchar | Exchange tier |
| `sharetype` | varchar | Share type (NS=normal, CE=certificate, AD=ADR, etc.) |
| `securitytype` | varchar | Security type (EQTY, FUND, DERV) |
| `securitysubtype` | varchar | Security subtype (COM, ETF, CEF) |
| `usincflg` | varchar | US incorporated (Y/N) |
| `issuertype` | varchar | Issuer type (ACOR, CORP, REIT) |
| `primaryexch` | varchar | Primary exchange (N, A, Q, R, B) |
| `conditionaltype` | varchar | Conditional type (RW=real world, NW=when-issued) |
| `tradingstatusflg` | varchar | Trading status (A=active, S=suspended) |

### Monthly Stock File: `crsp.msf_v2` (45 columns)

Same pattern with `mth` prefix: `mthcaldt`, `mthprc`, `mthret`, `mthretx`, `mthvol`, `mthcap`, `mthcumfacpr`, `mthcumfacshr`, etc.

Additional monthly columns: `mthcompflg`, `mthcompsubflg`, `mthprcdt`, `mthdtflg`, `mthdelflg`, `mthretflg`, `mthdiscnt`, `mthvolflg`, `mthprcvol`, `mthfacshrflg`, `mthprcvolmisscnt`, `mthfloatshrqty`.

### Security Names: `crsp.stksecurityinfohist` (36 columns, v2)

Key columns: `permno`, `secinfostartdt`, `secinfoenddt`, `cusip`, `ticker`, `primaryexch`, `sharetype`, `securitytype`, `securitysubtype`, `usincflg`, `issuertype`, `tradingstatusflg`, `conditionaltype`, `issuernm`, `securitynm`, `shareclass`, `siccd`, `naics`.

Use `stksecurityinfohist` with `secinfostartdt`/`secinfoenddt` for date-ranged
identification. Inspect overlapping ranges and retain share-class identity.

### Delisting: `crsp.stkdelists` (19 columns, v2)

Key columns: `permno`, `delistingdt`, `delret`, `delretmisstype`, `delactiontype`, `delstatustype`, `delreasontype`, `delpaymenttype`, `delpermno`, `delpermco`, `delnextdt`, `delnextprc`, `deldivamt`.

### Distributions: `crsp.stkdistributions` (19 columns, v2)

Key columns: `permno`, `disexdt`, `disseqnbr`, `disordinaryflg`, `distype`, `disfreqtype`, `dispaymenttype`, `disdetailtype`, `distaxtype`, `disdivamt`, `disfacpr`, `disfacshr`, `disdeclaredt`, `disrecorddt`, `dispaydt`, `dispermno`, `dispermco`.

**Distribution types (`distype`):** CD=cash dividend, FRS=fractional/stock split, SP=security payment, SD=stock dividend, CP=capital payment, CG=capital gains, ROC=return of capital, TSOO=treasury stock/other.

**Frequency types (`disfreqtype`):** Q=quarterly, M=monthly, A=annual, S=semi-annual, I=irregular, E=extra, X=special.

### Shares Outstanding: `crsp.stkshares` (v2)

| Column | Type | Description |
|--------|------|-------------|
| `permno` | int | PERMNO |
| `shrstartdt` | date | Period start date |
| `shrenddt` | date | Period end date |
| `shrout` | int | Shares outstanding; CRSP CIZ flat-file guide defines thousands (see below) |
| `shrsource` | varchar | Source of shares data |

### Share units: distinguish the product and the WRDS table

The former agent asserted actual shares for every v2 table. The [CRSP CIZ flat-file guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-2-0/), checked 2026-10-05, instead defines `StkShares.ShrOut` in thousands and capitalization in thousands of dollars. Prefer precomputed `dlycap`/`mthcap` for market equity.

On 2026-10-05, direct read-only PostgreSQL checks of `crsp.dsf_v2` and `crsp.msf_v2`, each restricted to PERMNO 14593 and 2024-01-31, each returned exactly one row: price 184.4, `shrout` 15,441,881, capitalization 2,847,482,856.40. Thus `price * shrout / cap = 1`. Together with the documented capitalization unit, this supports thousands of shares in these WRDS views and contradicts the old actual-shares claim. The ratio alone would not identify an absolute unit. This checks the named views and rows, not every CRSP product or historical record.

To reproduce the monthly check:

```sql
SELECT permno, mthcaldt, mthprc, shrout, mthcap,
       mthprc * shrout / NULLIF(mthcap, 0) AS price_shares_to_cap_ratio
FROM crsp.msf_v2
WHERE permno = 14593 AND mthcaldt = DATE '2024-01-31';
```

The daily check substitutes `dsf_v2`, `dlycaldt`, `dlyprc`, and `dlycap`. Inspect exact-table metadata before applying share conversions to a different product or wrapper.

### Cumulative Adjustment Factors (v2)

`crsp.stkdlycumulativeadjfactor`: `permno`, `dlycaldt`, `dlyshrout`, `dlycumfacpr`, `dlycumfacshr`
`crsp.stkmthcumulativeadjfactor`: `permno`, `mthcaldt`, `mthshrout`, `mthcumfacpr`, `mthcumfacshr`

### Market Index Tables

**v2:** `crsp.wrds_dailyindexret_query` / `crsp.wrds_monthlyindexret_query`
Daily columns include `dlycaldt`, `vwretd`, `vwretx`, `ewretd`, `ewretx`, `sprtrn`, `spindx` (plus separate VW/EW total/USD counts and values). Verify the monthly date field separately rather than assuming the daily name.

### S&P 500 Tables

- `crsp.dsp500_v2` — S&P 500 index returns
- `crsp.dsp500list_v2` — S&P 500 constituents with date ranges
- `crsp.msp500list_v2` — monthly constituent counterpart; verify availability
- v2 membership uses `permno`, `mbrstartdt`, `mbrenddt`
- A top-100 capitalization subset of the S&P 500 is a research-defined universe, not historical S&P 100 membership. Do not label it as the S&P 100.

### Treasury / Risk-Free Rate

- `crsp_a_treasuries.tfz_dly_rf2` — Daily risk-free-rate candidate; verify exact fields and the chosen delivery vintage
- `crsp_a_treasuries.tfz_mth_rf` / `tfz_mth_rf2` — Monthly risk-free rates
- Check the selected yield field's scale, compounding, and day basis. For an annual continuously compounded rate `y` already in decimals on a 365-day basis, the simple return over `days` is `exp(y * days / 365) - 1`; convert percent to decimals first when required. Do not assume a fixed 30 days represents every month.

Exclude the legacy `riskfree` file. CRSP's
[September 2014 notice](https://www.crsp.org/crsp_pdf/september-2014-monthlyquarterly-release-notes/)
ends legacy Treasury delivery with December 2014, and its Treasury guide maps
the old risk-free file to the current series. Check current access, field
units, and delivery vintage in [current products](products.md).

### Quarterly/Annual Security Data (v2 only)

- `crsp.stkqtrsecuritydata` (37 cols) — Quarterly: `qtrprc`, `qtrcap`, `qtrret`, `qtrretx`, `qtrvol`
- `crsp.stkannsecuritydata` (37 cols) — Annual: `annprc`, `anncap`, `annret`, `annretx`, `annvol`

### Metadata Tables (v2)

- `crsp.metasiztociz` — Official SIZ-to-CIZ column mapping
- `crsp.metaiteminfo` — CIZ item/column descriptions
- `crsp.metaflaginfo` — Flag value definitions
- `crsp.metacalendarperiod` — Trading calendar

## WRDS convenience views

`crsp.wrds_dsfv2_query` and `crsp.wrds_msfv2_query` combine security data, history, shares, adjustment factors, and distribution/index information. The former source listed 98 daily and 91 monthly columns; these are undated snapshots, not a live contract. `crsp.wrds_names_query` was listed with 24 columns.

Distribution joins can produce multiple records per PERMNO-date. Prefer `dsf_v2`/`msf_v2` for returns and join a separately aggregated event table when needed. Check the intended key before aggregating. A filter such as `disexdt IS NULL` drops genuine event dates and is not a deduplication rule.

## Text and opening-price edge cases

The former source reported occasional encoding failures in issuer names. Select only needed name fields; when text fails, inspect client/server encoding and a small failing value before choosing a conversion. The former unconditional LATIN1-to-UTF8 expression can itself fail or corrupt data and is not a generic repair.

Opening prices can be missing even when returns exist. For an overnight-return design, report missing `dlyopen` observations and apply an explicit eligibility rule. Use `dlyprcflg='TR'` only when the design specifically requires a closing trade; a bid-ask midpoint is a separate price source, not automatically an invalid observation.
