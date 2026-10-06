---
name: wrds-jkp
description: Query the current JKP Global Factor Data stock-characteristic panel on WRDS, including identifiers, sample screens, return timing, and Common Task Framework companion tables. Use for precomputed equity characteristics, not as a substitute for published factor-return definitions.
---

# JKP Global Factor Data

Use `wrds-psql-agent` and [wrds-psql](../wrds-psql/SKILL.md) for direct PostgreSQL. Read [wrds-catalog](../wrds-catalog/SKILL.md) for the full `contrib_global_factor` dictionary and its `contrib` aliases; use current product entries, not `_old` copies.

Read [panel selection and timing](references/panel.md) for verified fields, sample screens, and a bounded recipe.

The generated [catalog coverage](references/catalog-coverage.md) lists current product schemas and aliases included in this skill.

- `global_factor` is a stock-level panel. Its 444 columns in the 2026-10-05 catalog include identifiers, returns, flags, and characteristics; they are not 444 published factors.
- Use `id` and `eom` to define the requested stock-month grain and verify it. `permno` is useful for US CRSP links but is not a global identifier available for every stock. Preserve textual `gvkey` values.
- The published JKP sample uses `common=1`, `exch_main=1`, `primary_sec=1`, and `obs_main=1`. Apply a deliberate country/date selection as well; do not impose the US screen on a requested global universe.
- `ret` and `ret_exc` refer to the observation month, whereas `ret_exc_lead1m` is the next-month outcome. Never use the lead outcome as a contemporaneously available predictor.
- Distinguish USD and local-currency returns, raw characteristics, transformed predictors, and signed long-short factor returns. Verify each measure's scale and direction from its current definition.
- Prototype one security and one month. Check keys, missing links, sample flags, and target timing before a country/year extraction.

All four relations in `contrib_global_factor` accepted zero-row planning probes on 2026-10-05. This does not establish data completeness or all research conventions. Provider download examples may use the interactive `wrds` package; this toolkit uses the existing `psql service=wrds` configuration instead.
