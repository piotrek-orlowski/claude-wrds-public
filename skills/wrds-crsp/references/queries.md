# CRSP query recipes

Load [wrds-psql](../../wrds-psql/SKILL.md) before execution. These are bounded prototypes migrated and corrected on 2026-10-05; they were not newly executed against WRDS during migration. Verify exact fields using `wrds-schema`, then validate a small result before extending dates or the security universe. Use `psql service=wrds`, never SSH, for these queries.

## Monthly common-stock prototype (v2)

This demonstrates the standard US common-stock population. The PERMNO restriction keeps the prototype small. Other universes require explicit classification choices.

```sql
SELECT (DATE_TRUNC('month', mthcaldt) + INTERVAL '1 month' - INTERVAL '1 day')::date AS date,
       permno, permco, mthcaldt AS crsp_date,
       mthret, mthretx, mthprc, mthcap, ticker, primaryexch, siccd
FROM crsp.msf_v2
WHERE permno IN (10107, 14593)
  AND mthcaldt >= DATE '2024-01-01'
  AND mthcaldt < DATE '2024-02-01'
  AND sharetype = 'NS'
  AND securitytype = 'EQTY'
  AND securitysubtype = 'COM'
  AND usincflg = 'Y'
  AND primaryexch IN ('N', 'A', 'Q')
ORDER BY date, permno;
```

Inspect missing returns before applying eligibility filters. Add company names through a verified date-ranged history join only if the output needs them; do not assume `issuernm` is on every stock-file view.

## Stock and market returns without dropping distribution dates (v2)

```sql
SELECT s.dlycaldt AS date, s.permno, s.dlyret, s.dlyprc, s.dlycap,
       i.vwretd, i.sprtrn,
       s.dlyret - i.vwretd AS market_adjusted_return
FROM crsp.dsf_v2 s
LEFT JOIN crsp.wrds_dailyindexret_query i ON i.dlycaldt = s.dlycaldt
WHERE s.permno = 14593
  AND s.dlycaldt >= DATE '2024-01-01'
  AND s.dlycaldt < DATE '2024-02-01'
ORDER BY date;
```

Validate one index row per trading day. The subtraction is a market-adjusted return, not an excess return over the risk-free rate. Joining stock and index files directly avoids the distribution multiplicity of a broad convenience view. Never use `disexdt IS NULL` merely to remove duplicates.

## Cumulative return with explicit missing and total-loss handling (v2)

```sql
WITH sample AS (
    SELECT permno, dlycaldt, dlyret, dlyretmissflg
    FROM crsp.dsf_v2
    WHERE permno IN (10107, 14593)
      AND dlycaldt >= DATE '2024-01-01'
      AND dlycaldt < DATE '2024-02-01'
)
SELECT permno, MIN(dlycaldt) AS first_date, MAX(dlycaldt) AS last_date,
       COUNT(*) AS n_observed_rows,
       COUNT(*) FILTER (WHERE dlyret IS NULL OR dlyretmissflg IS NOT NULL
                              OR dlyret < -1) AS n_unusable_returns,
       CASE
           WHEN COUNT(*) FILTER (WHERE dlyret IS NULL OR dlyretmissflg IS NOT NULL
                                        OR dlyret < -1) > 0 THEN NULL
           WHEN BOOL_OR(dlyret = -1) THEN -1::numeric
           ELSE EXP(SUM(LN(CASE WHEN dlyret > -1 THEN 1 + dlyret END))) - 1
       END AS cumulative_return
FROM sample
GROUP BY permno
ORDER BY permno;
```

This strict recipe returns NULL if any observed return is unusable. It does not establish that every expected trading day exists, or resolve what happens after a security delists. Check sample boundaries and the intended investment horizon separately. The guarded logarithm protects a -100% observation even when SQL evaluates aggregates before the outer `CASE`.

## Split-adjusted prices (v2)

```sql
SELECT dlycaldt AS date, permno, dlyprc AS raw_price,
       dlyprc / NULLIF(dlycumfacpr, 0) AS adjusted_price,
       dlycumfacpr, dlycumfacshr
FROM crsp.dsf_v2
WHERE permno = 10107
  AND dlycaldt >= DATE '2024-01-01'
  AND dlycaldt < DATE '2024-02-01'
ORDER BY date;
```

## Company capitalization across share classes (v2)

Prototype with a selected PERMCO. Here PERMCO 45483 is an example identifier; verify the requested issuer and historical membership before reusing it.

```sql
SELECT (DATE_TRUNC('month', mthcaldt) + INTERVAL '1 month' - INTERVAL '1 day')::date AS date,
       permco, mthcaldt AS crsp_date,
       CASE WHEN COUNT(*) FILTER (WHERE mthcap IS NULL) = 0
            THEN SUM(mthcap) END AS firm_mktcap_000s,
       COUNT(DISTINCT permno) AS n_share_classes,
       COUNT(*) FILTER (WHERE mthcap IS NULL) AS n_missing_caps
FROM crsp.msf_v2
WHERE permco = 45483
  AND mthcaldt >= DATE '2024-01-01'
  AND mthcaldt < DATE '2024-02-01'
GROUP BY permco, mthcaldt
ORDER BY date;
```

Validate uniqueness of security-month rows before summing and specify which security types belong in company capitalization.

## Links and exports

Use the [Compustat recipes](../../wrds-compustat/references/queries.md) for CCM and accounting merges. Use the [psql skill](../../wrds-psql/SKILL.md) for `COPY (...) TO STDOUT WITH CSV HEADER`, timeouts, and output handling. Export prototypes only after their keys, timing, and measurement conventions pass validation.
