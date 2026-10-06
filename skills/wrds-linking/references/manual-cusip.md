# Historical CUSIP fallback

Use a manual link only when the relevant WRDS link table is unavailable or
inadequate for the task. Preserve all candidate links and explain how conflicts
are resolved. Matching names is a useful check, not proof that two share
classes or securities are interchangeable.

## Normalize the identifier, then match its validity interval

- Current CRSP CIZ `stksecurityinfohist.cusip` records historical CUSIP in
  intervals defined by `secinfostartdt` and `secinfoenddt`. A header CUSIP does
  not establish historical identity.
- OptionMetrics `securd.cusip` is an eight-character value in a current master
  snapshot. Use `secnmd.cusip` and `effect_date` for historical work.
- Standard CUSIP has six issuer characters, two issue characters, and a ninth
  check character. An eight-character match keeps issuer and issue identity;
  a six-character issuer match can conflate securities.
- Monthly TAQ's legacy 12-character CUSIP adds a three-character exchange
  extension to the nine-character CUSIP. See [TAQ links](taq-crsp.md) before
  comparing those values to CRSP's eight-character historical CUSIP.

Retain original identifiers alongside normalized values. Inspect blank values,
padding, missing identifiers, and conflicting histories. Never convert CUSIPs
to numbers: leading zeros and letters matter.

## OptionMetrics–CRSP interval example

This prototype uses current CRSP CIZ security history as a fallback and links
one SECID around one month. It closes each OptionMetrics interval on the day
before the next effective record. Confirm the source histories have one
unambiguous record per SECID/effective date and valid start dates before
running it. The historical sample month is part of the current product, not a
request for a retired product version.

Compute `LEAD` before filtering missing CUSIPs: a later record with missing
identity still ends the prior record's known validity. Filter the SECID before
the window operation but retain its full effective-date history, including the
record preceding the sample window.

```sql
WITH om_history AS (
    SELECT secid, cusip, effect_date,
           LEAD(effect_date) OVER (
               PARTITION BY secid ORDER BY effect_date
           ) AS next_date
    FROM optionm.secnmd
    WHERE secid = 106566
), om_intervals AS (
    SELECT secid, LEFT(TRIM(cusip), 8) AS cusip8,
           effect_date AS first_date,
           COALESCE(next_date - 1, 'infinity'::date) AS last_date
    FROM om_history
    WHERE cusip IS NOT NULL AND TRIM(cusip) <> ''
), crsp_intervals AS (
    SELECT permno, LEFT(TRIM(cusip), 8) AS cusip8,
           secinfostartdt AS first_date, secinfoenddt AS last_date
    FROM crsp.stksecurityinfohist
    WHERE cusip IS NOT NULL AND TRIM(cusip) <> ''
      AND secinfostartdt <= DATE '2024-06-30'
      AND secinfoenddt >= DATE '2024-06-01'
), candidates AS (
    SELECT o.secid, c.permno, o.cusip8,
           GREATEST(o.first_date, c.first_date) AS link_start,
           LEAST(o.last_date, c.last_date) AS link_end
    FROM om_intervals o
    JOIN crsp_intervals c
      ON o.cusip8 = c.cusip8
     AND o.first_date <= c.last_date
     AND o.last_date >= c.first_date
)
SELECT secid, permno, cusip8, link_start, link_end
FROM candidates
WHERE link_start <= DATE '2024-06-30'
  AND link_end >= DATE '2024-06-01'
ORDER BY secid, link_start, permno;
```

The open-ended final OptionMetrics interval is an explicit assumption for this
example, not evidence that the security remained active indefinitely. Check
source endpoint semantics for the requested sample. NULL CRSP endpoints are
excluded here; inspect them before introducing an open-ended replacement.

Join observations only where their dates fall between `link_start` and
`link_end`. Validate how many PERMNOs each SECID-date receives, including the
effective-date transition itself. Do not hide conflicts with `SELECT DISTINCT`
or select a link arbitrarily by row order. Keep uncertain ticker/CUSIP matches
separate from accepted mappings and report their coverage.
