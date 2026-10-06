---
name: wrds-psql
description: Connect to WRDS directly with psql, validate small queries and export PostgreSQL data for any non-TAQ product, including cross-database SQL. Use wrds-ssh for TAQ SAS jobs.
---

# WRDS PostgreSQL access

Use direct local `psql service=wrds`. The `wrds-psql-agent` handles both single-database and multi-database requests by loading the relevant skills. Database tables, units, filters, and joins belong in those skills, not here.

## Connection

Let libpq use the existing service and password configuration. Never open credential files such as `~/.pg_service.conf`, `~/.pgpass`, `.env`, or `~/.ssh/config` without explicit permission. Do not print passwords or put them in commands. If configuration is missing, report the error and ask for setup; do not inspect the files to diagnose it.

Keep shell invocations on one line. Save substantial SQL in a file and pass `-f`; the SQL file itself can contain multiple lines.

Use a noninteractive, read-only connection with a short timeout for the initial check:

```bash
psql 'service=wrds connect_timeout=10 options=-cdefault_transaction_read_only=on\ -cstatement_timeout=15000' -X -w -v ON_ERROR_STOP=1 -P pager=off -c 'SELECT 1 AS connection_ok;'
```

`-X` skips psql startup files, `-w` disables password prompts, and `ON_ERROR_STOP` propagates SQL errors. The client still uses existing authentication normally. A successful connection proves authentication, not access to every subscription.

Distinguish a network/DNS failure from authentication failure or missing table privileges. Use the runtime's normal network approval mechanism when needed. Do not use SSH as a PostgreSQL fallback, or the interactive `wrds` Python package.

## Load knowledge and verify a pilot

1. Use [wrds-schema](../wrds-schema/SKILL.md) to select the domain skills and inspect only the tables needed for the request.
2. For multiple datasets, also load [wrds-linking](../wrds-linking/SKILL.md). Agree on output grain, dates, identifiers, and information availability before joining.
3. Prototype the complete extraction on one asset and a small date window. Validate units, NULLs, missing-value codes, uniqueness, and join coverage. `LIMIT` alone does not bound aggregate or sort work.
4. Scale only after the pilot is valid. Keep date and identifier bounds; batch large exports by date or asset. A timeout calls for a smaller query or a plan check before raising the limit.

For saved queries, start with a bounded runtime appropriate to the sample:

```bash
psql 'service=wrds connect_timeout=10 options=-cdefault_transaction_read_only=on\ -cstatement_timeout=60000' -X -w -v ON_ERROR_STOP=1 -P pager=off -f queries/pilot.sql
```

TAQ extraction belongs to `wrds-taq-agent` using [wrds-taq](../wrds-taq/SKILL.md) and [wrds-ssh](../wrds-ssh/SKILL.md). A mixed TAQ/stock task can exchange small keyed outputs between the two agents through their parent; it does not require a third orchestrator agent.

## Export and preserve provenance

Use a SQL file containing `COPY (bounded_query) TO STDOUT WITH CSV HEADER` for larger exports. Keep psql output quiet and write to a temporary filename so a failed query is not mistaken for a complete result:

```bash
psql 'service=wrds connect_timeout=10 options=-cdefault_transaction_read_only=on\ -cstatement_timeout=60000' -X -w -q -v ON_ERROR_STOP=1 -f queries/export.sql > output/results.csv.partial
```

Check exit status, expected columns, sample values, and row counts before renaming the partial file. Do not overwrite the only copy of an earlier extraction. For alternate delimiters, use `WITH (FORMAT CSV, HEADER, DELIMITER '|')` or PostgreSQL text output. For small human-readable results, `-t -A -F ','` gives unaligned tuples; use COPY for actual CSV escaping.

Preserve SQL, parameters, extraction date, source tables, units, filter definitions, and validation results with the output. See [query workflow](references/query-workflow.md) for project organization and review. For optional local Python/Parquet processing, see [Python processing](references/python.md).
