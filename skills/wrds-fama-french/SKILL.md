---
name: wrds-fama-french
description: Use current WRDS Fama-French factors, portfolio returns, industry descriptions, and liquidity factors for risk adjustment and asset-pricing comparisons. Covers daily/monthly timing and the distinction between three-factor and five-factor series.
---

# Fama-French and related WRDS factors

Use `wrds-psql-agent` with [wrds-psql](../wrds-psql/SKILL.md) for direct PostgreSQL execution. Load [wrds-catalog](../wrds-catalog/SKILL.md) to inspect `ff_all` and its `ff` aliases, exact columns, source information, lifecycle, and access evidence. Do not select `_old` schemas or an archived factor vintage for a new current-product request.

Read [factor selection and timing](references/factors.md) before designing a merge or regression. The catalog owns the complete table/column inventory; this skill owns interpretation.

The generated [catalog coverage](references/catalog-coverage.md) lists current product schemas and aliases included in this skill.

- Choose the factor model before extracting: `factors_*` and `fivefactors_*` are distinct series. In particular, their SMB construction differs.
- Monthly `date` is the first of the month in the current catalog; `dateff` is labeled the last trading day. Create a calendar month-end key for monthly panel joins. Daily data join by trading date.
- Preserve the supplied frequency of `rf`. Subtract it from a total asset return only after matching units and dates; `mktrf` is already an excess return.
- Do not divide WRDS values by 100 merely because the public French downloads use percentage units. Verify the selected WRDS series against its dictionary or a small same-date provider comparison, and record any conversion.
- Keep a current extraction vintage. Factor histories can be revised; matching names and dates does not make different downloads identical.
- Prototype one month, validate unique dates and missing values, then extend. Record unmatched trading dates and monthly keys before estimating regressions.

The 2026-10-05 metadata inventory found 12 relations in `ff_all`; all accepted zero-row planning probes. That is access-planning evidence, not proof of complete observations or return units. No separate sample schema was established for this product.
