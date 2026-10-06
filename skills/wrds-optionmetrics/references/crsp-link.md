# OptionMetrics to CRSP

Use `wrdsapps.opcrsphist` for SECID-to-PERMNO links. OptionMetrics tables do not
contain PERMNO. Field types and counts here come from the source agent's
**2026-02-27 snapshot**; confirm the relation for the current task through
`wrds-schema` and `wrds-psql-agent`.

| Column | Recorded type | Meaning |
|---|---|---|
| `secid` | double precision | OptionMetrics underlying identifier |
| `sdate` | date | First valid link date |
| `edate` | date | Last valid link date |
| `permno` | integer | CRSP security identifier |
| `score` | double precision | Link quality code |

The source describes these observed scores (approximate link counts):

- 1: exact CUSIP match (~28K).
- 2: CUSIP match with minor difference (~190).
- 4: ticker-based match (~660).
- 5: weak match (~5.7K).
- 6: no match, with NULL PERMNO; index securities had score 6 in that snapshot.

These descriptions are the inherited code summary, not a substitute for the
current WRDS linking documentation. The examples retain the source's strict
`score <= 2` policy. Preserve scores in output, inspect the codes actually
present, and report coverage lost to the policy. Do not force index options
onto an unrelated CRSP security because they lack an equity PERMNO.

## Options with stock returns

This example follows [wrds-crsp](../../wrds-crsp/SKILL.md)'s current CIZ/v2
stock product. Retired SIZ query variants are outside this toolkit.

```sql
SELECT o.secid, o.optionid, o.date, o.exdate, o.cp_flag,
       o.strike_price / 1000.0 AS strike, o.impl_volatility,
       l.permno, l.score AS link_score,
       c.dlyret AS stock_return, c.dlyretmissflg,
       c.dlyprc AS stock_price, c.dlyprcflg
FROM optionm.opprcd2024 o
JOIN wrdsapps.opcrsphist l
  ON o.secid = l.secid
 AND o.date BETWEEN l.sdate AND l.edate
 AND l.score <= 2
JOIN crsp.dsf_v2 c ON l.permno = c.permno AND o.date = c.dlycaldt
WHERE o.secid = 106566
  AND o.date = DATE '2024-06-28'
  AND o.impl_volatility > 0;
```

This is an option-date panel, so a daily stock return repeats across options
deliberately. Verify that each SECID-date has at most one eligible PERMNO for
the intended design and that each CRSP PERMNO-date is unique. Run a left-join
diagnostic first to distinguish missing links from missing CRSP observations;
an inner join alone cannot measure dropped coverage. If an end date is NULL,
inspect documented endpoint semantics before treating it as open-ended.

For temporal CUSIP fallback and general join validation, load
[wrds-linking](../../wrds-linking/SKILL.md). CCM details belong to
[wrds-compustat](../../wrds-compustat/SKILL.md), not this link table.
