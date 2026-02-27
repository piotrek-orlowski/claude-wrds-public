---
name: wrds-psql
description: Use this skill when the user needs to query WRDS data via PostgreSQL from the local machine. Covers psql connection using .pgpass credentials, query execution patterns, CSV/parquet export, and best practices for large extractions. Invoke when the user wants to pull data from WRDS (CRSP, OptionMetrics, Compustat) via SQL.
argument-hint: "[query or description of data needed]"
---

# WRDS PostgreSQL Query Skill (Local psql via .pgpass)

Execute WRDS queries directly from the local machine using `psql` with service file authentication. No SSH required.

## Critical Rule: Single-Line Commands Only

**Always write psql commands as a single line.** Never use `\` line continuation or heredocs. This avoids shell expansion approval prompts.

```bash
# GOOD — single line
psql service=wrds -c "SELECT permno, date, ret FROM crsp.dsf WHERE permno = 84398 LIMIT 10;"

# BAD — multi-line
psql service=wrds \
    -c "SELECT permno, date, ret
        FROM crsp.dsf
        WHERE permno = 84398 LIMIT 10;"
```

For complex queries, write SQL to a file and use `-f`:
```bash
psql service=wrds -f query.sql
```

## Connection

Connection details are in `~/.pg_service.conf` (host, port, database, user); password in `~/.pgpass`.

## Query Patterns

### Inline query
```bash
psql service=wrds -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='crsp' AND table_name='dsf' ORDER BY ordinal_position;"
```

### Query from file (preferred for complex SQL)
```bash
psql service=wrds -f query.sql
```

### Tuples-only output (no headers/footers)
```bash
psql service=wrds -t -A -F',' -c "SELECT permno, date, ret FROM crsp.dsf WHERE permno=84398 LIMIT 10"
```
Flags: `-t` (tuples only), `-A` (unaligned), `-F','` (comma field separator).

## Data Export

### CSV to stdout (pipe to file)
```bash
psql service=wrds -c "COPY (SELECT permno, date, ret, prc FROM crsp.dsf WHERE permno = 84398 AND date >= '2020-01-01' ORDER BY date) TO STDOUT WITH CSV HEADER" > output.csv
```

### CSV with custom delimiter
```bash
psql service=wrds -c "COPY (SELECT ...) TO STDOUT WITH (FORMAT CSV, HEADER, DELIMITER '|')" > output.csv
```

### Tab-separated
```bash
psql service=wrds -c "COPY (SELECT ...) TO STDOUT WITH (FORMAT TEXT)" > output.tsv
```

### Convert CSV to parquet (after download)

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('output.csv', parse_dates=['date'])
df.to_parquet('output.parquet', index=False)
"
```

## Schema Discovery

```bash
psql service=wrds -c "\dn" | head -40
psql service=wrds -c "\dt crsp.*"
psql service=wrds -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema='crsp' AND table_name='dsf' ORDER BY ordinal_position;"
psql service=wrds -c "SELECT COUNT(*), MIN(date), MAX(date) FROM crsp.dsf;"
```

## Common Databases and Key Tables

| Schema | Table | Description | Key Columns |
|--------|-------|-------------|-------------|
| `crsp` | `dsf` | Daily stock file | permno, date, ret, prc, vol, shrout |
| `crsp` | `dsi` | Daily S&P index | date, sprtrn, spindx, vwretd |
| `crsp` | `msf` | Monthly stock file | permno, date, ret, prc |
| `crsp` | `stocknames` | Security names/identifiers | permno, namedt, nameendt, ticker, cusip |
| `crsp` | `delist` | Delisting events | permno, dlstdt, dlret, dlstcd |
| `optionm` | `opprcd{YYYY}` | Option prices (yearly) | secid, date, exdate, cp_flag, strike_price(/1000!), best_bid, best_offer, impl_volatility, delta |
| `optionm` | `securd` | Security reference | secid, ticker, cusip, index_flag |
| `optionm` | `stdopd` | Standardized options | secid, date, days, impl_volatility, delta |
| `optionm` | `zerocd` | Zero-coupon rates | date, days, rate |
| `comp` | `funda` | Annual fundamentals | gvkey, datadate, at, ni, ceq |
| `comp` | `fundq` | Quarterly fundamentals | gvkey, datadate, atq, niq |
| `crsp` | `ccmxpf_lnkhist` | CRSP-Compustat link | gvkey, lpermno, linkdt, linkenddt, linktype, linkprim |
| `wrdsapps` | `opcrsphist` | OptionMetrics-CRSP link | secid, permno, sdate, edate |

## Known Gotchas

1. **OptionMetrics strike_price** — stored as strike * 1000. Always `strike_price / 1000.0` in queries.
2. **OptionMetrics yearly tables** — option prices are partitioned by year: `optionm.opprcd1996`, `optionm.opprcd1997`, ..., `optionm.opprcd2025`. Use `UNION ALL` across years or query one at a time.
3. **CRSP column names** — `crsp.dsi` uses `date` (not `caldt`), `spindx` (not `sprindx`).
4. **Numeric precision** — PostgreSQL returns `numeric` type for many WRDS columns. When loading into Python, cast to `float64`.
5. **Large queries** — WRDS may timeout on queries returning millions of rows. Break into date ranges:
   ```sql
   -- Instead of: SELECT * FROM crsp.dsf WHERE permno IN (...)
   -- Do: SELECT * FROM crsp.dsf WHERE date >= '2020-01-01' AND date < '2021-01-01' AND permno IN (...)
   ```
6. **COPY vs SELECT** — `COPY ... TO STDOUT` is much faster than piping `SELECT` output for large extractions.
7. **NULL handling** — many columns have NULLs (missing returns, missing prices). Always consider `WHERE ret IS NOT NULL` or handle in downstream code.
8. **SPY identifiers** — CRSP PERMNO: 84398. OptionMetrics SECID: 109820. SPX SECID: 108105.
9. **CCM linking filters** — always filter: `linktype IN ('LC','LU') AND linkprim IN ('P','C')` and check date overlap.

## Best Practices

1. **Always filter by date first** — date columns are indexed; this dramatically reduces scan time.
2. **Use COPY for bulk export** — `COPY (...) TO STDOUT WITH CSV HEADER` is the fastest way to extract data.
3. **Test with LIMIT** — always test queries with `LIMIT 100` before running full extraction.
4. **Save as parquet** — after CSV download, convert to parquet for faster subsequent loads.
5. **Avoid SELECT *** — specify only the columns you need to reduce data transfer.
6. **Use CTEs for complex joins** — break multi-table queries into `WITH` clauses for readability and to help the query planner.

## Putting It Together: Full Extraction Workflow

```bash
# 1. Test the query
psql service=wrds -c "SELECT permno, date, ret, prc FROM crsp.dsf WHERE permno = 84398 AND date >= '2020-01-01' ORDER BY date LIMIT 10;"

# 2. Export to CSV
psql service=wrds -c "COPY (SELECT permno, date, ret, prc FROM crsp.dsf WHERE permno = 84398 AND date >= '2020-01-01' ORDER BY date) TO STDOUT WITH CSV HEADER" > data/crsp_spy.csv
```

## Instructions

When given a query request (`$ARGUMENTS`):

1. Identify which WRDS schemas/tables are needed
2. Write the SQL query with appropriate filters and joins
3. Wrap it in the appropriate `psql` command for execution
4. If the user wants data saved locally, use `COPY ... TO STDOUT WITH CSV HEADER` piped to a file
5. Suggest any data quality filters or gotchas specific to the tables involved
6. For large extractions, suggest breaking into date ranges
