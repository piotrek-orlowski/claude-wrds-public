---
name: wrds-schema
description: Use this skill at the start of a session when working with WRDS data (CRSP, OptionMetrics, Compustat, TAQ). It pre-loads schema knowledge — table names, column names, join keys, data types, and common gotchas — so you can write correct queries without exploratory round-trips. Invoke when the user mentions WRDS, OptionMetrics, CRSP, or structured product / options analysis.
argument-hint: "[databases: crsp optionm comp all]"
---

# WRDS Schema Pre-loader

You are starting a session that involves WRDS PostgreSQL queries. Before writing any queries, load the schema knowledge you need by dispatching specialist agents in parallel.

## Connection

Connection details are in `~/.pg_service.conf`; password in `~/.pgpass`.

```bash
psql service=wrds
```

For Python, use `psycopg2.connect("service=wrds")`. Do NOT use `pd.read_sql` (broken with psycopg2 on Python 3.13) — use cursors directly and cast `Decimal` to `float`.

**Prerequisite:** The specialist agents (`crsp-wrds-expert`, `optionmetrics-wrds-expert`, `taq-wrds-expert`) must have `Bash` in their `tools:` frontmatter in `~/.claude/agents/`. Without it, they cannot run `psql` queries.

## What to do

Based on `$ARGUMENTS` (or "all" if none given), launch the appropriate specialist agents **in parallel** using the Task tool. Each agent should query the WRDS database to retrieve current schema details and return a concise reference.

### Agent dispatches

For each requested database, launch a Task with `subagent_type` set to the matching specialist:

| Keyword | Agent | Task |
|---------|-------|------|
| `crsp` | `crsp-wrds-expert` | Retrieve schema for `crsp.dsf`, `crsp.dsi`, `crsp.msf`, `crsp.msi`, `crsp.stocknames`, delisting tables. Confirm column names (`date` not `caldt`), PERMNO lookup for SPY (84398), index columns in `dsi` (`spindx`, `sprtrn`). Note Decimal type from psycopg2. |
| `optionm` | `optionmetrics-wrds-expert` | Retrieve schema for `optionm.opprcd{YYYY}` (yearly partitioned), `optionm.securd`, `optionm.zerocd`. Confirm: `strike_price` is strike*1000, SPX SECID=108105, SPY SECID=109820, XSP SECID=189691. Column names for options tables. LEAPS expiry cycles (Jun/Dec for 2Y). |
| `comp` | `crsp-wrds-expert` | Retrieve Compustat `comp.funda` key columns, CCM linking via `crsp.ccmxpf_lnkhist` (PERMNO-GVKEY, linktype LC/LU, linkprim P/C). |
| `taq` | `taq-wrds-expert` | Retrieve TAQ table structure, trade filtering rules (TR_CORR, TR_SCOND), NBBO tables. Note: TAQ requires SAS on WRDS, not SQL. |

### Agent prompt template

Each agent should receive a prompt like:

> You are pre-loading schema knowledge for a WRDS session. Query the database to confirm current table structures and return a concise reference card. Do NOT write analysis code — just retrieve and summarize schema.
>
> Run these queries via psql:
> 1. `SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='...' AND table_name='...' ORDER BY ordinal_position;`
> 2. Any quick validation queries (e.g. `SELECT MIN(date), MAX(date) FROM crsp.dsi LIMIT 1`)
>
> Return a compact reference with: table name, key columns (name + type), date ranges, important IDs, and known gotchas.

### After agents return

Compile their results into a single **Schema Reference** block and present it to the user. Keep it compact — a lookup table, not prose. Example format:

```
=== CRSP ===
crsp.dsi: date(date), vwretd(numeric), sprtrn(numeric), spindx(numeric) | 1926-2024
crsp.dsf: permno(int), date(date), prc(numeric), ret(numeric), vol(numeric) | 1926-2024
  SPY PERMNO: 84398
  Gotcha: psycopg2 returns Decimal, cast with .apply(float)

=== OPTIONMETRICS ===
optionm.opprcd{YYYY}: secid, date, exdate, cp_flag, strike_price(/1000!), best_bid, best_offer, impl_volatility, delta, volume, open_interest
  SPX SECID: 108105 | SPY SECID: 109820 | XSP SECID: 189691
  2Y LEAPS: expire Jun/Dec only, DTE 600-830 range for quarterly initiation
optionm.zerocd: date, days, rate | zero-coupon rates by maturity
optionm.securd: secid, ticker, cusip, index_flag
  Gotcha: strike_price is strike * 1000 (divide by 1000 in queries)
```

## Known gotchas (always include these)

1. **`pd.read_sql` broken on Python 3.13** — use `cursor.execute()` + `cursor.fetchall()` + `pd.DataFrame(rows, columns=[...])`
2. **Decimal type** — psycopg2 returns `decimal.Decimal` for numeric columns. Always `.apply(float)` or `float()` before math/numpy operations.
3. **CRSP column names** — `crsp.dsi` uses `date` (not `caldt`), `spindx` (not `sprindx`)
4. **OptionMetrics strike** — `strike_price` column stores strike * 1000. Divide by 1000.
5. **OptionMetrics yearly tables** — option prices are in `optionm.opprcd{YYYY}`, NOT a single table. Loop years 1996-2025.
6. **SPX LEAPS cycle** — 2-year options only expire in June and December. Monthly initiations produce duplicate expiry targets. Use quarterly initiation for 2Y.
7. **Exec pricing** — use `(best_bid + 3*best_offer) / 4` for realistic execution (between mid and ask).
