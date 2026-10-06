# Composing cross-database queries

Start with one security and a short date window. Use `wrds-psql-agent` for
PostgreSQL source queries and the combined query. For TAQ measurements, request
a small SAS extraction from `wrds-taq-agent` and link the exported result at
the intended frequency.

## Example: JNJ options with dividends to expiration

1. Resolve the SECID through OptionMetrics name history and the date-valid
   PERMNO through the [OptionMetrics–CRSP link](../../wrds-optionmetrics/references/crsp-link.md).
   Confirm names and class. Do not assume current ticker/master matches are
   valid at an earlier observation date.
2. Extract a single-day option panel using the raw-option example in
   [wrds-optionmetrics](../../wrds-optionmetrics/references/queries.md), with
   the chosen maturity range. Retain each option's SECID, OPTIONID, observation
   date, expiration, and matched PERMNO.
3. Use [wrds-crsp](../../wrds-crsp/SKILL.md) for distribution definitions,
   cash-dividend filters, and units. Validate the candidate dividend events
   independently before attaching them to options.
4. Aggregate eligible dividends for each option's window, then join that single
   result to the option row. Matching every dividend event directly to the
   option table changes the panel grain and can multiply option observations.
5. Check an independently known event and verify pre/post-join option counts,
   unmatched links, cash-dividend exclusions, and date-boundary behavior.

The following is a composition pattern, not a standalone extraction. Here
`options` is a validated option-date relation including `permno`, and
`dividends` is a validated cash-dividend event relation with `permno`, `exdt`,
and `divamt`:

```sql
SELECT o.*, d.dividend_count, d.dividend_total
FROM options o
CROSS JOIN LATERAL (
    SELECT COUNT(*) AS dividend_count,
           SUM(divamt) AS dividend_total
    FROM dividends v
    WHERE v.permno = o.permno
      AND v.exdt > o.date
      AND v.exdt <= o.exdate
) d;
```

This window excludes the observation date and includes the expiration date.
State and adapt those boundaries for the economic question, including contract
settlement conventions. The aggregate returns one row even when there are no
events: count is zero and sum is NULL. Only turn NULL into zero once source
coverage is established; missing dividend data is not evidence of no dividend.

This is a sum of subsequently realized dividends. It is not a dividend forecast
known when the option was priced. Predictive or pricing work needs information
availability and dividend expectations; retain declaration/publication dates
and the forecast vintage as required. Historical realized distributions are
useful for a different question and should be labeled accordingly.

## Other common compositions

- CRSP–Compustat: follow the single maintained [CCM reference](../../wrds-compustat/references/ccm.md)
  for `lpermno`, link filters, accounting reporting filters, and selection of an
  available accounting observation. An 18-month date window alone can attach
  multiple annual rows to one stock month.
- OptionMetrics–CRSP daily returns: use the concrete SQL in the
  [SECID link reference](../../wrds-optionmetrics/references/crsp-link.md).
  Preserve the option-date grain or explicitly aggregate to security-date.
- TAQ–CRSP: use [TAQ link examples](taq-crsp.md); define intraday/session and
  daily date alignment before joining returns or aggregating measurements.

For any composition, validate individual subqueries before combining them,
record row counts at every join, and filter each large source by date and
identifier. A final `LIMIT` does not guarantee a small upstream join.
