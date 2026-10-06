# OptionMetrics query examples

Examples use historical tables and the source agent's JNJ SECID, `106566`.
Verify identifiers, table availability, and sample restrictions before reuse.
Run through `wrds-psql-agent` with `wrds-psql`. These are small prototypes;
validate output grain, nulls, date boundaries, and row counts before widening
dates or securities. See [schema.md](schema.md) for units and
[filters-pricing.md](filters-pricing.md) for the meaning of optional cutoffs.

Contents: identifiers; raw options; ATM IV; surfaces; put-call spreads;
delta-based skew; term structure; multi-year queries; export and Python use.

## Find security identifiers

```sql
SELECT secid, ticker, cusip, effect_date
FROM optionm.secnmd
WHERE ticker = 'AAPL'
ORDER BY effect_date DESC
LIMIT 5;

SELECT secid, cusip, class, issue_type, index_flag
FROM optionm.securd
WHERE secid = 106566;
```

`securd` is a current master snapshot. For historical identity, use the
effective-date intervals in `secnmd`; the most recent matching ticker does not
by itself establish identity on an earlier observation date.

## Basic option extraction

```sql
SELECT secid, optionid, date, exdate, cp_flag,
       strike_price / 1000.0 AS strike,
       best_bid, best_offer, (best_bid + best_offer) / 2 AS mid_price,
       impl_volatility AS iv, delta, gamma, vega, theta,
       volume, open_interest, am_settlement, contract_size, cfadj, ss_flag,
       exdate - date AS days_to_exp
FROM optionm.opprcd2024
WHERE secid = 106566
  AND date = DATE '2024-01-31'
  AND exdate BETWEEN DATE '2025-01-01' AND DATE '2025-02-28'
  AND best_bid > 0 AND impl_volatility > 0
ORDER BY cp_flag, strike_price, optionid;
```

Expiration can fall after the observation-table year. Choose the year suffix
from the observation date, not `exdate`.

## ATM implied volatility

Standardized ATM-forward options avoid choosing the closest listed strike.
Calls and puts are separate observations, so retain `cp_flag`:

```sql
SELECT secid, date, days, cp_flag,
       impl_volatility AS atm_iv, forward_price
FROM optionm.stdopd2024
WHERE secid = 106566
  AND date BETWEEN DATE '2024-06-03' AND DATE '2024-06-07'
  AND days IN (30, 60, 91, 182, 365)
  AND impl_volatility > 0
ORDER BY date, days, cp_flag;
```

For the listed option closest to spot ATM, rank within each expiration and
option type. This differs from standardized ATM-forward IV. The example uses
`optionid` to break equal-distance ties reproducibly; document a different
contract-selection rule if appropriate.

```sql
WITH underlying AS (
    SELECT secid, date, close
    FROM optionm.secprd2024
    WHERE secid = 106566
      AND date BETWEEN DATE '2024-06-03' AND DATE '2024-06-07'
      AND close > 0
), ranked AS (
    SELECT o.secid, o.optionid, o.date, o.exdate, o.cp_flag,
           o.strike_price / 1000.0 AS strike,
           o.impl_volatility, u.close AS underlying_price,
           ROW_NUMBER() OVER (
               PARTITION BY o.secid, o.date, o.exdate, o.cp_flag
               ORDER BY ABS(o.strike_price / 1000.0 - u.close), o.optionid
           ) AS rn
    FROM optionm.opprcd2024 o
    JOIN underlying u ON o.secid = u.secid AND o.date = u.date
    WHERE o.secid = 106566
      AND o.date BETWEEN DATE '2024-06-03' AND DATE '2024-06-07'
      AND o.impl_volatility > 0 AND o.impl_volatility < 2
)
SELECT secid, optionid, date, exdate, cp_flag, strike,
       impl_volatility, underlying_price
FROM ranked
WHERE rn = 1
ORDER BY date, exdate, cp_flag;
```

## Volatility surface

```sql
SELECT secid, date, days, delta, cp_flag,
       impl_volatility, impl_strike
FROM optionm.vsurfd2024
WHERE secid = 106566
  AND date = DATE '2024-06-28'
  AND impl_volatility > 0
ORDER BY days, cp_flag, delta;
```

## Put-call IV spread

Pair on security, date, expiration, strike, and compatible contract terms.
Check that each side is unique on those matching columns before joining;
multiple contract variants otherwise produce multiple candidate pairs.

```sql
SELECT c.secid, c.date, c.exdate,
       c.optionid AS call_optionid, p.optionid AS put_optionid,
       c.strike_price / 1000.0 AS strike,
       c.impl_volatility AS call_iv, p.impl_volatility AS put_iv,
       p.impl_volatility - c.impl_volatility AS iv_spread
FROM optionm.opprcd2024 c
JOIN optionm.opprcd2024 p
  ON c.secid = p.secid AND c.date = p.date
 AND c.exdate = p.exdate AND c.strike_price = p.strike_price
 AND c.am_settlement = p.am_settlement
 AND c.contract_size = p.contract_size
 AND c.cfadj = p.cfadj AND c.ss_flag = p.ss_flag
WHERE c.cp_flag = 'C' AND p.cp_flag = 'P'
  AND c.impl_volatility > 0 AND c.impl_volatility < 2
  AND p.impl_volatility > 0 AND p.impl_volatility < 2
  AND c.secid = 106566 AND c.date = DATE '2024-06-28';
```

Rows with missing matching terms are excluded by equality joins. Inspect those
exclusions instead of treating two missing terms as evidence of compatibility.

## IV skew: selected OTM put minus selected OTM call

This example selects the closest observed raw-option delta to -0.25 or +0.25,
within the source's delta bands and 20–60 calendar-day maturity window. It is
a delta-based spread example, not an exact replication of a named paper.
Rank before joining so several options in a delta band do not multiply rows.

```sql
WITH candidates AS (
    SELECT secid, optionid, date, exdate, cp_flag, delta, impl_volatility,
           am_settlement, contract_size, cfadj, ss_flag,
           ROW_NUMBER() OVER (
               PARTITION BY secid, date, exdate, cp_flag,
                            am_settlement, contract_size, cfadj, ss_flag
               ORDER BY ABS(ABS(delta) - 0.25), optionid
           ) AS rn
    FROM optionm.opprcd2024
    WHERE secid = 106566 AND date = DATE '2024-06-28'
      AND impl_volatility > 0 AND impl_volatility < 2
      AND (exdate - date) BETWEEN 20 AND 60
      AND ((cp_flag = 'P' AND delta BETWEEN -0.30 AND -0.20)
        OR (cp_flag = 'C' AND delta BETWEEN 0.20 AND 0.30))
)
SELECT p.secid, p.date, p.exdate, p.am_settlement,
       p.contract_size, p.cfadj, p.ss_flag,
       p.optionid AS put_optionid, c.optionid AS call_optionid,
       p.impl_volatility AS otm_put_iv,
       c.impl_volatility AS otm_call_iv,
       p.impl_volatility - c.impl_volatility AS iv_skew
FROM candidates p
JOIN candidates c
  ON p.secid = c.secid AND p.date = c.date AND p.exdate = c.exdate
 AND p.am_settlement = c.am_settlement
 AND p.contract_size = c.contract_size
 AND p.cfadj = c.cfadj AND p.ss_flag = c.ss_flag
WHERE p.cp_flag = 'P' AND c.cp_flag = 'C'
  AND p.rn = 1 AND c.rn = 1;
```

## Term structure

First verify uniqueness on `(secid, date, days, cp_flag)`. The aggregate below
pivots maturities; it must not silently select the larger of a call and put IV.

```sql
SELECT secid, date, cp_flag,
       MAX(CASE WHEN days = 30 THEN impl_volatility END) AS iv_30,
       MAX(CASE WHEN days = 60 THEN impl_volatility END) AS iv_60,
       MAX(CASE WHEN days = 91 THEN impl_volatility END) AS iv_91,
       MAX(CASE WHEN days = 182 THEN impl_volatility END) AS iv_182,
       MAX(CASE WHEN days = 365 THEN impl_volatility END) AS iv_365
FROM optionm.stdopd2024
WHERE secid = 106566
  AND date BETWEEN DATE '2024-06-03' AND DATE '2024-06-07'
  AND impl_volatility > 0
GROUP BY secid, date, cp_flag
ORDER BY date, cp_flag;
```

## Multi-year queries

Filter every branch. This boundary prototype uses one week on each side of
New Year; expand only after validating the single-year components.

```sql
SELECT secid, date, impl_volatility, days, cp_flag
FROM optionm.stdopd2023
WHERE secid = 106566
  AND date BETWEEN DATE '2023-12-25' AND DATE '2023-12-31'
  AND impl_volatility > 0
UNION ALL
SELECT secid, date, impl_volatility, days, cp_flag
FROM optionm.stdopd2024
WHERE secid = 106566
  AND date BETWEEN DATE '2024-01-01' AND DATE '2024-01-05'
  AND impl_volatility > 0
ORDER BY date, days, cp_flag;
```

The recorded `secprd` table contains all years of underlying prices:

```sql
SELECT secid, date, close, return
FROM optionm.secprd
WHERE secid = 106566
  AND date BETWEEN DATE '2023-12-25' AND DATE '2024-01-05';
```

There is no corresponding all-years `opprcd` in the source snapshot. Confirm
available yearly relations before composing a union.

## Export and Python use

Wrap the validated SELECT in the direct PostgreSQL COPY pattern from
[wrds-psql](../../wrds-psql/SKILL.md). Preserve `secid`, `optionid`, observation
date, and contract descriptors in raw-option exports. For bounded Python
queries, bind SECID and date parameters through psycopg2 rather than formatting
SQL strings; the connection/parameterized-query examples also live in
`wrds-psql`. Run Python through `uv`; never use the interactive `wrds` library.
