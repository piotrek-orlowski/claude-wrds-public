# OptionMetrics filters and pricing notes

These notes preserve the prior agent's domain guidance. The numerical cutoffs
below are example research choices, not a universal definition of usable data.
Report exclusions separately and vary the cutoffs when the research question
requires it. Removing `-99.99` IV sentinels is distinct from trimming valid high
volatilities. An open-interest threshold does not prove that an option is
currently tradeable.

## Example filters

| Purpose | SQL condition | Interpretation |
|---|---|---|
| Remove missing/nonpositive IV | `impl_volatility > 0` | Excludes the source's `-99.99` sentinel |
| Optional upper IV bound | `impl_volatility < 2` | Sample choice: excludes IV at or above 200% |
| Positive, nonlocked quotes | `best_offer > best_bid AND best_bid > 0` | Strict spread filter; decide separately whether locked quotes belong |
| Liquidity screen | `volume > 0 OR open_interest > 100` | Example threshold |
| Moneyness screen | `strike / underlying BETWEEN 0.8 AND 1.2` | Requires correctly scaled strike and positive underlying price |
| Maturity screen | `(exdate - date) BETWEEN 7 AND 365` | Calendar days; sample-specific window |
| Midpoint floor | `(best_bid + best_offer) / 2 >= 0.125` | Historical example cutoff, not a universal minimum tick |

```sql
SELECT o.secid, o.optionid, o.date, o.exdate, o.cp_flag,
       o.strike_price / 1000.0 AS strike,
       (o.best_bid + o.best_offer) / 2 AS mid_price,
       o.impl_volatility AS iv, o.delta,
       o.exdate - o.date AS days_to_exp,
       u.close AS underlying,
       (o.strike_price / 1000.0) / NULLIF(u.close, 0) AS moneyness
FROM optionm.opprcd2024 o
JOIN optionm.secprd2024 u
  ON o.secid = u.secid AND o.date = u.date
WHERE o.secid = 106566
  AND o.date BETWEEN DATE '2024-06-03' AND DATE '2024-06-07'
  AND o.impl_volatility > 0 AND o.impl_volatility < 2
  AND o.best_offer > o.best_bid AND o.best_bid > 0
  AND (o.volume > 0 OR o.open_interest > 100)
  AND (o.best_bid + o.best_offer) / 2 >= 0.125
  AND (o.exdate - o.date) BETWEEN 7 AND 365
  AND u.close > 0
  AND (o.strike_price / 1000.0) / NULLIF(u.close, 0) BETWEEN 0.8 AND 1.2;
```

Validate uniqueness of the underlying security-date rows before the join and
of the intended option-date key afterward. Preserve settlement, contract size,
and adjustment fields when the sample includes adjusted or special contracts.

## Current provider pricing evidence

OptionMetrics documents model choice by exercise style, discrete dividend
projections, and a multi-thousand-step binomial tree for American options.
The earlier repository's fixed 100-step claim is superseded by this provider
description. [IvyDB US product sheet](https://optionmetrics.com/wp-content/uploads/2024/03/OM_IvyDB-US_Flyer_WEB_REV.pdf)

Determine exercise style from security/contract fields. Keep the dividend and
interest-rate inputs from the selected product, and verify the current manual
before asserting an exact solver, failure rule, or Greek unit. Do not label
every `impl_volatility` observation a Black-Scholes IV. Provider methodology,
WRDS delivery vintage, and the study's own model assumptions are separate
pieces of provenance.
