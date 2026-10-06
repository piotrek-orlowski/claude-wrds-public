# Compustat and CCM query recipes

Load [wrds-psql](../../wrds-psql/SKILL.md) before executing these through direct `psql service=wrds`. Migrated and corrected on 2026-10-05; validation scope and access limits are recorded at the end. The examples use a small known-company identifier for prototyping, not as a universal mapping. Verify fields and the requested identity before extending.

## Annual fundamentals prototype

```sql
SELECT datadate AS date, gvkey, fyear, curcd, at, ceq, ni,
       indfmt, datafmt, popsrc, consol
FROM comp.funda
WHERE gvkey = '001690'
  AND datadate >= DATE '2023-01-01'
  AND datadate < DATE '2024-01-01'
  AND indfmt = 'INDL' AND datafmt = 'STD'
  AND popsrc = 'D' AND consol = 'C'
ORDER BY date;
```

## Quarterly fundamentals prototype

```sql
SELECT datadate AS date, gvkey, fyearq, fqtr, rdq, curcdq,
       atq, ceqq, niq, indfmt, datafmt, popsrc, consol
FROM comp.fundq
WHERE gvkey = '001690'
  AND datadate >= DATE '2023-01-01'
  AND datadate < DATE '2024-01-01'
  AND indfmt = 'INDL' AND datafmt = 'STD'
  AND popsrc = 'D' AND consol = 'C'
ORDER BY date;
```

Check firm-period uniqueness and the interpretation of `rdq` before joining quarterly figures to returns. Do not copy annual flow-item conventions into quarterly or year-to-date fields without checking definitions.

## CRSP v2 security-month link

```sql
SELECT (DATE_TRUNC('month', m.mthcaldt) + INTERVAL '1 month' - INTERVAL '1 day')::date AS date,
       m.permno, l.gvkey, m.mthcaldt AS crsp_date, m.mthret,
       l.linkdt, l.linkenddt, l.linktype, l.linkprim
FROM crsp.msf_v2 m
JOIN crsp.ccmxpf_lnkhist l
  ON l.lpermno = m.permno
 AND m.mthcaldt BETWEEN l.linkdt AND COALESCE(l.linkenddt, DATE '9999-12-31')
WHERE m.permno = 14593
  AND m.mthcaldt >= DATE '2024-01-01'
  AND m.mthcaldt < DATE '2024-02-01'
  AND l.linktype IN ('LC', 'LU')
  AND l.linkprim IN ('P', 'C')
ORDER BY date, gvkey;
```

This inner join excludes unlinked stock rows. Use a left join with all link filters in `ON` when an unmatched-coverage audit is needed; report match rates before restricting the sample. Check PERMNO-date multiplicity and conflicting GVKEYs before merging fundamentals.

Use current CIZ stock files throughout; the retired SIZ replacement is
documented in [wrds-crsp](../../wrds-crsp/references/versions-and-codes.md).
Do not infer CCM access from stock or Compustat access: the current account's
underlying CCM schema was denied in the recorded validation below.

## Lagged annual fundamentals merged to v2 returns

This example treats the previous calendar month-end as formation and requires accounts to be at least six months old at that date. It takes the latest eligible fiscal year within 18 months. Those are illustrative research conventions, not observed publication dates or a historical Compustat vintage.

First verify uniqueness of filtered `comp.funda` at `(gvkey, datadate)` and links at the selected security-month grain. The diagnostic counts below remain in the result; reject ambiguous rows before analysis.

```sql
WITH stock AS (
    SELECT m.permno, m.mthcaldt, m.mthret, m.mthcap,
           (DATE_TRUNC('month', m.mthcaldt) - INTERVAL '1 day')::date AS formation_date
    FROM crsp.msf_v2 m
    WHERE m.permno = 14593
      AND m.mthcaldt >= DATE '2024-01-01'
      AND m.mthcaldt < DATE '2024-02-01'
), linked AS (
    SELECT s.*, l.gvkey,
           COUNT(*) OVER (PARTITION BY s.permno, s.mthcaldt) AS n_link_matches
    FROM stock s
    JOIN crsp.ccmxpf_lnkhist l
      ON l.lpermno = s.permno
     AND s.mthcaldt BETWEEN l.linkdt AND COALESCE(l.linkenddt, DATE '9999-12-31')
     AND l.linktype IN ('LC', 'LU')
     AND l.linkprim IN ('P', 'C')
), eligible AS (
    SELECT l.*, f.datadate, f.curcd, f.at, f.ceq, f.ni,
           ROW_NUMBER() OVER (
               PARTITION BY l.permno, l.mthcaldt
               ORDER BY f.datadate DESC, l.gvkey
           ) AS rn,
           COUNT(*) OVER (
               PARTITION BY l.permno, l.mthcaldt, f.datadate
           ) AS n_same_period_candidates
    FROM linked l
    JOIN comp.funda f ON f.gvkey = l.gvkey
     AND f.datadate >= l.formation_date - INTERVAL '18 months'
     AND f.datadate <= l.formation_date - INTERVAL '6 months'
     AND f.indfmt = 'INDL' AND f.datafmt = 'STD'
     AND f.popsrc = 'D' AND f.consol = 'C'
)
SELECT (DATE_TRUNC('month', mthcaldt) + INTERVAL '1 month' - INTERVAL '1 day')::date AS date,
       permno, gvkey, mthcaldt AS crsp_date, formation_date,
       mthret, mthcap, datadate, curcd, at, ceq, ni,
       n_link_matches, n_same_period_candidates
FROM eligible
WHERE rn = 1
ORDER BY date, permno;
```

Require both diagnostic counts to equal one. This recipe anchors the issuer link at the return month's CRSP date; change that anchor deliberately when the design maps at formation or fiscal period end. Even with a six-month lag, late filings and subsequently revised values can prevent a strict point-in-time interpretation. Keep eligible and rejected record counts for reproducibility.

## Source-key check

This prototype check should return no rows. A wider extraction needs the same check over its selected company/date scope.

```sql
SELECT gvkey, datadate, COUNT(*) AS n_rows
FROM comp.funda
WHERE gvkey = '001690'
  AND datadate >= DATE '2022-01-01'
  AND datadate < DATE '2024-01-01'
  AND indfmt = 'INDL' AND datafmt = 'STD'
  AND popsrc = 'D' AND consol = 'C'
GROUP BY gvkey, datadate
HAVING COUNT(*) > 1;
```

Adapt to quarterly fields and research-specific keys as appropriate. A zero-row result proves only the tested key and sample; it does not establish complete reporting coverage or availability timing.

## Validation on 2026-10-05

The annual recipe was executed through read-only direct PostgreSQL, restricted to GVKEY 001690 and 2023. It returned one row and one unique firm-period key, with no missing `at`, `ceq`, or `ni`: fiscal date 2023-09-30, USD, `at=352583`, `ceq=62146`, `ni=96995`. This checks the fields and sample shown, not the quarterly recipe or entire Compustat population.

The live merged recipe, restricted to PERMNO 14593 and January 2024, failed with `permission denied for schema crsp_a_ccm`. No live CCM merge result or link cardinality was validated. Catalog knowledge and access to stock/fundamental tables do not prove CCM subscription access.

The exact merged recipe was then run in PostgreSQL after substituting tiny `VALUES` CTEs for its three tables. A baseline with one link and three fiscal years selected the eligible 2022-09-30 report and returned one unique security-month with both diagnostic counts equal to one. A duplicated link raised `n_link_matches` to two; a duplicated accounting record raised `n_same_period_candidates` to two. Each ambiguity was observable after latest-period selection. These checks validate syntax, timing-window behavior, and diagnostics only; real-table permissions, types, data quality, and coverage still require an authorized live pilot.
