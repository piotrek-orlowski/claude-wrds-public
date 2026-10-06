# OptionMetrics schema and units

Provenance: core field explanations were migrated from the repository's
OptionMetrics agent (verified there on **2026-02-27**). Product families,
partitions, and aliases were refreshed from live metadata on **2026-10-05**.
Row counts and numerical grids below remain the earlier snapshots, not current
guarantees. Confirm requested fields and a bounded sample before extraction.

Contents: schema families; year partitions; option prices; underlying prices;
volatility surfaces; standardized options; security/name history;
distributions; other tables; index and ETF interpretation.

## Current product layout

The WRDS [OptionMetrics product page](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/)
identifies `optionm_all` as IvyDB US and `optionm_europe` as IvyDB Europe.
The 2026-10-05 metadata discovery finds schema usage for US, but not Europe;
the visible `optionm` wrapper is not evidence of entitlement to both.
See [products and access](products.md) for status and delivery distinctions.

| Schema | Type | Description |
|--------|------|-------------|
| `optionm` | VIEWs | **Primary access point.** Views pointing to `optionm_all` (US) or `optionm_europe` (European). Use this schema. |
| `optionm_all` | BASE TABLEs | Underlying US data tables. `optionm.opprcd2024` is a VIEW on `optionm_all.opprcd2024`. |
| `optionm_europe` | BASE TABLEs | Separate European product; schema access denied in the current discovery. |

**CRITICAL:** The `optionm` schema contains **two families of views** mixed together:
- **US data views** (`opprcdYYYY`, `securd`, `secnmd`, `secprdYYYY`, `stdopdYYYY`, `vsurfdYYYY`, etc.) — point to `optionm_all` and were accessible in the source environment.
- **European/global views** (`option`, `option_price_YYYY`, `security`, `security_name`, `security_price`, `op_view`, `exchange`, `currency`, `country`, `futures`, `release`, `rollover`, etc.) — the inherited mapping points to `optionm_europe`; current alias dependencies and access must be checked before use.

## Table Families and Year Partitioning

**Pattern:** US year-partitioned tables use suffix `YYYY` (e.g., `opprcd2024`),
not a separate schema per year. Years identify observation partitions within
the current product; they are not obsolete database versions. Select the table
from observation year, which can differ from expiration year.

### Year-Partitioned Tables (US Data, 1996-2025)

| Table Family | Years | Description |
|-------------|-------|-------------|
| `opprcdYYYY` | 1996-2025 | Daily option prices, IVs, Greeks |
| `secprdYYYY` | 1996-2025 | Daily underlying security prices |
| `stdopdYYYY` | 1996-2025 | Standardized ATM-forward options |
| `vsurfdYYYY` | 1996-2025 | Interpolated volatility surface |
| `fwdprdYYYY` | 1996-2025 | Computed forward prices |
| `hvoldYYYY` | 1996-2025 | Historical (realized) volatility |
| `borrateYYYY` | 1996-2025 | Implied borrow rates (by expiration) |
| `stdbrteYYYY` | 1996-2025 | Standardized borrow rates (by days) |
| `opprcbrYYYY` | 1996-2025 | BRFitted daily option quotes and analytics |
| `stdopbrYYYY` | 1996-2025 | BRFitted standardized options |
| `vsurfbrYYYY` | 1996-2025 | BRFitted volatility surfaces |
| `fwdprbrYYYY` | 1996-2025 | BRFitted forward prices |
| `idxdvbrYYYY` | 1996-2025 | BRFitted index dividend inputs |

These 13 families were observed in the current US base. BRFitted columns use
different names; see [model families](products.md). Projected-dividend
`distrprojdYYYY` aliases are stale and excluded, with no verified replacement.

### Non-Partitioned Tables (US Data)

| Table | Rows | Description |
|-------|------|-------------|
| `secprd` | ~66M | All-years security prices (same data as UNION of secprdYYYY). **No equivalent for opprcd.** |
| `securd` | ~120K | Security master (current snapshot) |
| `securd1` | ~120K | Security master + `issuer` column |
| `secnmd` | ~272K | Historical ticker/name/CUSIP changes |
| `opinfd` | ~14K | Option contract specifications |
| `indexd` | ~83K | Index security master |
| `exchgd` | ~209K | Exchange listing history |
| `distrd` | ~742K | Distribution (dividend/split) history |
| `opvold` | ~81M | Daily aggregated option volume |
| `idxdvd` | ~2.7M | Index continuous dividend yields |
| `zerocd` | ~304K | Zero-coupon interest rate curve |
| `optionmnames` | ~70M | OptionMetrics name/identifier history (**very large — filter aggressively**) |

## Column Definitions

### opprcdYYYY — Daily Option Prices (1996-2025)

One row per option contract per trading day.

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Underlying security ID |
| `date` | date | Observation date |
| `symbol` | varchar(21) | Option symbol (OSI format) |
| `symbol_flag` | varchar(1) | Symbol type flag ("1" = standard) |
| `exdate` | date | Expiration date |
| `last_date` | date | Last trade date |
| `cp_flag` | varchar(1) | Call ("C") or Put ("P") |
| `strike_price` | double precision | **Strike x 1000 — DIVIDE BY 1000 for actual strike** |
| `best_bid` | double precision | Best closing bid price |
| `best_offer` | double precision | Best closing ask price |
| `volume` | double precision | Daily contract volume |
| `open_interest` | double precision | Open interest (contracts) |
| `impl_volatility` | double precision | Model-implied IV (**-99.99 = missing**); see [pricing notes](filters-pricing.md) |
| `delta` | double precision | Option delta |
| `gamma` | double precision | Option gamma |
| `vega` | double precision | Option vega; verify the current provider unit before scaling or combining with model Greeks |
| `theta` | double precision | Option theta; verify the current provider time unit before scaling |
| `optionid` | double precision | Unique option contract identifier |
| `cfadj` | double precision | Cumulative adjustment factor |
| `am_settlement` | double precision | AM settlement flag (1 = AM, 0 = PM) |
| `contract_size` | double precision | Contract multiplier (typically 100) |
| `ss_flag` | varchar(1) | Special settlement flag ("0" = standard) |
| `forward_price` | double precision | Computed forward price of underlying |
| `expiry_indicator` | varchar(1) | Expiry indicator |
| `root` | varchar(5) | Option root symbol |
| `suffix` | varchar(2) | Option suffix |

### secprdYYYY / secprd — Daily Security Prices

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `date` | date | Observation date |
| `open` | double precision | Opening price |
| `high` | double precision | Daily high |
| `low` | double precision | Daily low |
| `close` | double precision | Closing price |
| `volume` | double precision | Share volume |
| `return` | double precision | Daily total return |
| `cfadj` | double precision | Cumulative price adjustment factor |
| `cfret` | double precision | Cumulative return adjustment factor |
| `shrout` | double precision | Shares outstanding (thousands; 0 for indices) |

**Notes:**
- `secprd` (no year suffix) is a non-partitioned BASE TABLE containing all years (~66M rows).
- `secprdYYYY` tables contain the same data partitioned by year.
- Contains both equity AND index securities (index `shrout` = 0).

### vsurfdYYYY — Interpolated Volatility Surface

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `date` | date | Observation date |
| `days` | double precision | Days to expiration |
| `delta` | double precision | Delta level (integer) |
| `impl_volatility` | double precision | Interpolated IV |
| `impl_strike` | double precision | Implied strike price |
| `impl_premium` | double precision | Implied option premium |
| `dispersion` | double precision | Dispersion measure |
| `cp_flag` | varchar(1) | Call ("C") or Put ("P") |

**Days grid (11 values):** 10, 30, 60, 91, 122, 152, 182, 273, 365, 547, 730

**Delta grid (by 5s):**
- Puts: -90, -85, -80, -75, -70, -65, -60, -55, -50, -45, -40, -35, -30, -25, -20, -15, -10
- Calls: 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90

### stdopdYYYY — Standardized ATM-Forward Options

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `date` | date | Observation date |
| `days` | double precision | Days to expiration |
| `forward_price` | double precision | Computed forward price |
| `strike_price` | double precision | Strike price (= forward_price for ATM) |
| `premium` | double precision | Option premium |
| `impl_volatility` | double precision | ATM-forward IV |
| `delta` | double precision | Option delta |
| `gamma` | double precision | Option gamma |
| `theta` | double precision | Option theta |
| `vega` | double precision | Option vega |
| `cp_flag` | varchar(1) | Call ("C") or Put ("P") |

**Days grid (11 values):** 10, 30, 60, 91, 122, 152, 182, 273, 365, 547, 730

Both calls and puts are reported for each days/date combination.

### securd — Security Master

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `cusip` | varchar(8) | CUSIP (8-digit) |
| `ticker` | varchar(6) | Current ticker |
| `sic` | varchar(4) | SIC code |
| `index_flag` | varchar(1) | "0" = equity, "1" = index |
| `exchange_d` | double precision | Exchange code (bitmask) |
| `class` | varchar(1) | Security class |
| `issue_type` | varchar(1) | Issue type ("0" = common stock, "A" = index/ADR, "F" = foreign, "U" = unit) |
| `industry_group` | double precision | Industry group code |

~120K total: ~38K equities, ~83K indices. `securd1` adds an `issuer` column.

### secnmd — Security Name History

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `effect_date` | date | Effective date of this record |
| `cusip` | varchar(8) | CUSIP at this date |
| `ticker` | varchar(6) | Ticker at this date |
| `class` | varchar(1) | Security class |
| `issuer` | varchar(28) | Issuer name |
| `issue` | varchar(20) | Issue description |
| `sic` | varchar(4) | SIC code |

Multiple rows per secid when ticker/name/CUSIP changes.

### opinfd — Option Contract Info

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `div_convention` | varchar(1) | Dividend convention ("I" = index) |
| `exercise_style` | varchar(1) | "A" = American, "E" = European |
| `am_set_flag` | varchar(1) | AM settlement flag |

One row per optionable security.

### indexd — Index Security Master

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `ticker` | varchar(6) | Ticker |
| `cusip` | varchar(8) | CUSIP |
| `exchange_d` | double precision | Exchange code |
| `issue_type` | varchar(1) | Issue type |
| `class` | varchar(1) | Security class |
| `indexnam` | varchar(28) | Index name |
| `issue` | varchar(20) | Issue description |
| `div_convention` | varchar(1) | Dividend convention ("I" = index) |
| `exercise_style` | varchar(1) | Exercise style ("E" = European) |
| `am_set_flag` | varchar(1) | AM settlement flag |

### distrd — Distribution History

| Column | Type | Description |
|--------|------|-------------|
| `secid` | double precision | Security ID |
| `record_date` | date | Record date |
| `seq_num` | double precision | Sequence number |
| `ex_date` | date | Ex-dividend date |
| `amount` | double precision | Distribution amount (per share) |
| `adj_factor` | double precision | Adjustment factor (for splits) |
| `declare_date` | date | Declaration date |
| `payment_date` | date | Payment date |
| `link_secid` | double precision | Linked security ID (for spinoffs) |
| `distr_type` | varchar(1) | "1" = cash div, "%" = projected, "2" = stock div, "5" = split, "4" = spinoff, "3" = return of capital |
| `frequency` | varchar(1) | Distribution frequency |
| `currency` | varchar(3) | Currency |
| `approx_flag` | varchar(1) | "0" = exact |
| `cancel_flag` | varchar(1) | Cancellation flag |
| `liquid_flag` | varchar(1) | Liquidation flag |

### Other Tables

| Table | Description |
|-------|-------------|
| `hvoldYYYY` | Historical (realized) volatility. Days: 10, 14, 30, 60, 91, 122, 152, 182, 273, 365, 547, 730, 1825 |
| `borrateYYYY` | Implied borrow rates by expiration date (-99.99 = missing) |
| `stdbrteYYYY` | Standardized borrow rates at fixed days (10, 30, 60, ..., 730) |
| `fwdprdYYYY` | Forward prices: secid, date, expiration, amsettlement, forwardprice |
| `opvold` | Aggregated option volume: 3 rows per secid-date (total, calls, puts) |
| `zerocd` | Zero-coupon curve: date, days (10-730), rate (annualized %) |
| `idxdvd` | Index dividend yields: secid, date, expiration, rate (continuous yield %) |
| `exchgd` | Exchange listing history with status ("$" = active, "X"/"D" = delisted) |
| `optionmnames` | Name/identifier history (~70M rows — **filter aggressively**) |

## Index and ETF interpretation

Index and equity options share the option tables. Select a security through
`securd.index_flag` or `indexd`, and inspect `opinfd.exercise_style` and the
contract's `am_settlement` field. Do not infer settlement from ticker alone.

| SECID in source examples | Ticker | Security |
|---|---|---|
| 108105 | SPX | CBOE S&P 500 index |
| 117801 | VIX | CBOE Market Volatility index |
| 109820 | SPY | SPDR S&P 500 ETF (an ETF, not the index itself) |

The source describes equity options as generally American with discrete
dividends (`distrd`), and index options as generally European with continuous
dividend yields (`idxdvd`). Check actual exercise and settlement flags instead
of applying those descriptions to every contract. The source's SPX
AM-settlement example is not a rule for all SPX observations. Underlying
`shrout` is zero for index securities in the recorded schema. Pricing-model
notes are in [filters-pricing.md](filters-pricing.md).
