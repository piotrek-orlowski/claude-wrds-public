---
name: wrds-catalog
description: Find WRDS tables, exact columns, product versions, access outcomes, aliases, and documentation in the account-specific catalog. Use before querying an unfamiliar WRDS product or checking whether a current database is available, including samples and TAQ SAS members.
---

# WRDS catalog

Use the dated local catalog to select a product and its domain skill. The snapshot was collected on 2026-10-05. It contains metadata, not research observations or credentials. Read [coverage and evidence](references/method.md) before interpreting access or version status.

Resolve `CATALOG` to this skill's directory, wherever installed. The lookup script uses Python's standard library and does not connect to WRDS:

```bash
uv run --no-project python "$CATALOG/scripts/catalog.py" coverage
uv run --no-project python "$CATALOG/scripts/catalog.py" schemas
uv run --no-project python "$CATALOG/scripts/catalog.py" search "bank"
uv run --no-project python "$CATALOG/scripts/catalog.py" tables comp_na_daily_all
uv run --no-project python "$CATALOG/scripts/catalog.py" table comp_na_daily_all.funda
uv run --no-project python "$CATALOG/scripts/catalog.py" columns gvkey --schema comp_na_daily_all
uv run --no-project python "$CATALOG/scripts/catalog.py" taq TAQMSEC.CTM_20241007
```

Searches default to canonical products whose access checks passed: documented current products and reviewed sole available versions with no verified accessible replacement. `canonical` records selection; `lifecycle` separately records whether release/maintenance status is established. A canonical table can have unresolved lifecycle. Add `--all` to inspect excluded copies, denied products and internal tables. An explicit `table SCHEMA.TABLE` lookup always displays its status. Use `--limit` to control results; output reports matches and truncation. Exact table output includes columns, types, comments, dependencies, selection reasons and the skill to load.

Never equate catalog visibility with a subscription. `planning_accepted` means a zero-row query was accepted and any observed privilege guards passed. It does not establish returned observations, requested coverage, or the cost of a full query. Verify a bounded requested-date sample through [wrds-psql](../wrds-psql/SKILL.md). If a view has a guard failure, report it; do not bypass it through an underlying table.

For TAQ, use the `taq` command and [wrds-taq](../wrds-taq/SKILL.md). An exact SAS member name returns its SAS types, lengths, labels and formats. Partial searches return matching members. PostgreSQL TAQ metadata is retained for discovery, but it is not a SQL access route. A successful SAS metadata open does not establish all observations are readable. Name matches between PostgreSQL and SAS metadata are lookup candidates, not a verified equality of data. Keep old dated partitions within current TAQ products; excluded product versions remain visible only with `--all` for diagnosis.

Load only the relevant domain skill returned by the lookup. For joins, also load [wrds-linking](../wrds-linking/SKILL.md). Use a canonical table even when lifecycle is unresolved, while retaining the uncertainty and checking the fields and dates required by the task. Missing version documentation alone is not a reason to block its use. Confirmed retired or superseded copies remain excluded; a restricted sample does not provide full-universe coverage.
