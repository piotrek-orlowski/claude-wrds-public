# TAQ filters and research methods

These rules and examples preserve the former TAQ expert's research coverage.
Its product snapshot was dated 2026-02-27; the filters were not independently
revalidated during migration. Check the applicable TAQ condition definitions
for the requested feed and dates before a production extraction.

Primary documentation: the [NYSE Daily TAQ Client Specification v4.1](https://www.nyse.com/publicdocs/nyse/data/Daily_TAQ_Client_Spec_v4.1.pdf),
section 3, documents trade sale conditions and message sequence fields. Select
the version applicable to the sample from NYSE's [current and historical technical
documents](https://www.nyse.com/market-data/technical-documents), checked 2026-10-05.
Confirm the CTA/UTP variant and WRDS field mapping; a modern specification is not
evidence that a historical code or sequence key has identical semantics.

## Trade and quote eligibility

| Choice | Inherited starting example | What to check |
|---|---|---|
| Trade corrections | `tr_corr in ('00','01')` | Correction/cancel semantics and duplicate correction records; legacy `CORR` is numeric. |
| Sale conditions | `tr_scond in (' ','@','E','F')` | A strict exact-string allowlist; multi-character flags require an explicit policy. It excludes many other records by design. |
| Alternative broad trade sample | Exclude conditions containing `T`, `U`, or `Z` | This is not equivalent to a regular-sale allowlist; validate other condition combinations. |
| Positive observations | `price > 0 and size > 0` | Reject nonpositive prices before logarithms; record exclusions. |
| Regular session | 09:30 through 16:00 Eastern | Use the actual trading calendar, early closes, and explicit endpoint convention. |
| Candidate BBO quote conditions | `qu_cond in ('A','B','H','O','R','W',' ')` | Inherited example only; confirm eligibility, cancellations, and status for the era. |
| Quote prices | `ask > bid and bid > 0` | This excludes locked and crossed quotes; choose and report their treatment. |
| Relative spread | `(ask-bid)/((ask+bid)/2) < 0.10` | An optional research threshold, not a provider validity rule. |

Keep `SYM_SUFFIX` when present: `SYM_ROOT` alone can combine distinct securities.
For raw NBBO use `BEST_BID`/`BEST_ASK`; for raw exchange quotes use `BID`/`ASK`.
Check status and cancellation fields before treating an update as usable.
Filtering invalid updates out and carrying the previous valid quote forward
can conceal a closed market or withdrawn quote; retain/reset state at such
events, or use a documented cleaned WRDS product with a staleness rule.

## Sampling

- **Calendar time:** On each grid point, take the latest eligible observation
  at or before that time. Define same-timestamp ordering and maximum age.
  Leave unobserved opening prices missing; do not fill them from future ticks.
  Reset state at every date and security boundary.
- **Interval endpoints:** The last observation inside each five-minute bin is
  a different rule from sampling a fixed clock grid. Use integer bins such as
  `floor((time_m - open_time)/300)` and define the treatment of the close.
  Dividing a minute index by five without rounding does not create five-minute bins.
- **Event time:** Every Nth quote or trade samples business time. Compute returns
  between the selected observations, not between a selected observation and
  the immediately previous raw tick.
- **Multivariate refresh time:** Advance when every asset has an update since
  the previous refresh. Sampling every N updates of one asset is not refresh-time
  synchronization.
- **All ticks:** Irregularly spaced positive-price log returns are available
  after filtering, but their microstructure noise differs from coarse-grid
  realized variance. Preserve the chosen frequency in the output description.

Timestamp display precision does not establish clock accuracy or economic event
ordering. Confirm numeric storage and formats, participant versus feed time,
and sequence fields. Do not infer a common nanosecond clock from a printed label.

## Matching and measures

Use WRDS `wct_YYYYMMDD` when its pre-matched NBBO at t, t-1, t-2, or t-5 seconds
matches the research design. For a custom match, sort by date, complete security
identifier, timestamp, and available sequence fields. Maintain quote state
while processing the ordered stream, then evaluate each trade using the latest
eligible quote at or before the chosen lagged trade time. A loop that reads all
quotes and then all trades does not perform this match.

Raw `cqm_` filtering alone does not compute the national BBO. Reconstruction
requires per-exchange quote state, eligibility and cancellation handling, and
aggregation across active venues after each update. Prefer the available NBBO
product unless reconstruction is itself required.

Realized variance is the sum of squared intraday log returns. Keep a partial
observed sum separate from a complete-session measure: report `observed_rv_5min`
for available returns, but leave `rv_5min` missing unless every expected grid
endpoint and return is present. Preserve `complete_grid`, expected and usable
counts, missing endpoints, and any dropped intervals. Quoted spread
is ask minus bid; effective spread is twice the absolute trade-price deviation
from the matched midpoint. Quote-rule direction uses the sign of that deviation.
For midpoint trades, a tick rule and treatment of zero price changes are needed
before calling the implementation a complete Lee-Ready classifier.

## Scaling

Filter daily files by security and time early, and select only needed columns.
Use SAS views with `open=defer` for streaming extraction; materialize the small
filtered subset when sorting or reusing it is necessary. Loop through SAS dates
and format them as `YYYYMMDD` only to construct dataset names. Check file existence
and distinguish closed trading days from unexpected missing data. The inherited
notes mention `%taq_daily_dataset_list`; verify that macro's availability and
signature before using it rather than assuming it is installed.
