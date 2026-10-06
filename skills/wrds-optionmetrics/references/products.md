# Current OptionMetrics delivery and model families

Checked 2026-10-05 using live metadata and
[WRDS product status](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/).
Load [wrds-catalog](../../wrds-catalog/SKILL.md) for exact partitions, columns,
view dependencies, and access evidence. A `LIMIT 0` success alone does not
confirm row retrieval.

`optionm_all` is the current WRDS IvyDB US base product. The observed delivery
contains 402 tables: 13 annual families with 1996-2025 partitions plus 12
nonpartitioned tables. WRDS reports an annual June 2026 update; the
[provider's daily updating](https://optionmetrics.com/data-products/) is a
different delivery schedule. Do not promise the latest trading day from an
annual WRDS subscription. Select a year by observation date, not expiration.

`optionm` is a mixed wrapper: current US aliases, European aliases, and stale
projected-dividend aliases coexist. Resolve dependencies. `optionm_europe`
is a separate product and underlying schema usage was denied in this account;
the public WRDS page's older Europe refresh does not by itself prove provider
retirement. Samples/trials are outside the production coverage claim.

## Standard and BRFitted series

Both groups are present in the current US base; one must not be dropped merely
because it is named like an older family. The
[IvyDB US 7.0 announcement](https://optionmetrics.com/news/optionmetrics-releases-ivydb-us-7-0-and-ivydb-etf-5-0/)
describes borrow-rate-aware valuation updates. Choose and record the model
family explicitly; never concatenate them as independent option observations.

| Purpose | Standard family | BRFitted family |
|---|---|---|
| Raw option quotes/analytics | `opprcdYYYY` | `opprcbrYYYY` |
| Standardized options | `stdopdYYYY` | `stdopbrYYYY` |
| Volatility surfaces | `vsurfdYYYY` | `vsurfbrYYYY` |
| Forward prices | `fwdprdYYYY` | `fwdprbrYYYY` |
| Index dividend inputs | `idxdvd` | `idxdvbrYYYY` |

Other current annual families are `secprdYYYY,hvoldYYYY,borrateYYYY,stdbrteYYYY`.
The [schema reference](schema.md) describes standard fields; do not copy its
column spellings to BRFitted tables.

Verified BRFitted raw fields in `opprcbr2025` include:

| Standard raw field | BRFitted raw field | Interpretation |
|---|---|---|
| `secid` | `securityid` | Underlying identity |
| `exdate` | `expiration` | Expiration date |
| `cp_flag` | `callput` | Call/put flag |
| `strike_price` | `strike` | Both raw table comments specify strike times 1000 |
| `best_bid,best_offer` | `bestbid,bestoffer` | Quotes |
| `impl_volatility` | `impliedvolatility` | Model-specific IV |
| `open_interest` | `openinterest` | Contracts |
| `cfadj` | `adjustmentfactor` | Cumulative option adjustment |

The BRFitted raw metadata explicitly describes `vega` per percentage-point
volatility change and `theta` in dollars **per year**. `stdopbr` also labels
theta annualized. The standard table comments are less detailed: verify their
current provider definitions before applying a unit conversion. The inherited
claim that all option theta is per calendar day is not supported.

For a prototype, resolve one security, choose one date and one expiration,
then inspect quote/contract identity, units, settlement flags, and missing
analytics. When comparing model families, first prove a one-to-one contract
match; equal SECID/date/strike/expiry/put-call alone may omit settlement or
adjustment distinctions. Raw `opprcbr` has no implied guarantee of matching all
standard-table helper fields.

## Excluded aliases and alternate deliveries

`optionm.distrprojd1996` through `distrprojd2023` point to
`optionm_all_old.distrprojdYYYY` while their privilege predicates name absent
`optionm_all.distrprojdYYYY` relations. They are stale aliases, not a current
family that merely lags two years. No current projected-dividend replacement
was verified, so do not substitute another table or older delivery silently.
`distrd` remains the current distribution-history table; that is a different
data concept.

`optionm_all_old` is an alternate delivery outside the current toolkit. Keep
the current product's 1996 onward history: old observation years are not old
database versions. The precise retention policy of alternate delivery schemas
remains undocumented in the public sources reviewed.
