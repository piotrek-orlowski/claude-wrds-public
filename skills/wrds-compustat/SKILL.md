---
name: wrds-compustat
description: Query current Compustat North America, Global, and ExecuComp products on WRDS; interpret accounting filters, securities, executive compensation, reporting lags, and CCM links subject to product access.
---

# Current Compustat products

Load [wrds-psql](../wrds-psql/SKILL.md) before executing SQL; use direct `psql service=wrds`. Use [wrds-schema](../wrds-schema/SKILL.md) for exact-field and access checks. The PostgreSQL execution agent is `wrds-psql-agent`; no separate Compustat or CRSP specialist agent is required.

Read [products and access](references/products.md) before choosing North America,
Global, ExecuComp, or a separate point-in-time/snapshot product. Read
[fundamentals and linking](references/ccm.md) for accounting and link rules,
and [query recipes](references/queries.md) for bounded extracts and CIZ joins.
Load [wrds-crsp](../wrds-crsp/SKILL.md) for returns or capitalization. Current
product history remains in scope; retired duplicate versions and sample/trial
products are not substitutes for current production access.

Read the generated [catalog coverage](references/catalog-coverage.md) for the
complete domain inventory and its recorded access/lifecycle boundaries.

## Apply these invariants

- Preserve `gvkey` as text, including leading zeros. `datadate` identifies a fiscal period end, not the date that investors learned the information.
- For the standard consolidated domestic industrial sample, use `indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, and `consol='C'`. Other populations need their own explicit filters. Verify uniqueness after filtering.
- Use `crsp.ccmxpf_lnkhist` and its `lpermno` field. The standard primary-link sample uses `linktype IN ('LC','LU')` and `linkprim IN ('P','C')`, plus date validity and a nonmissing linked security.
- Treat a NULL `linkenddt` as open-ended. Validate link multiplicity in the requested sample; filters do not replace that check.
- State the date at which a link is evaluated. Current issuer mapping, historical fiscal-period mapping, and portfolio-formation mapping are different research choices.
- Define an information-availability rule before joining accounts to returns. A latest-`datadate` lookup or an 18-month lookback alone permits look-ahead. A chosen reporting lag is a convention, not observed publication timing; ordinary Compustat also contains later revisions.
- An 18-month window can include two fiscal years. Choose the most recent eligible report only after validating source keys and links; do not use row numbering to hide conflicting links.
- Prototype one firm/security and a short interval, then validate output keys, row counts, NULLs, currencies, units, and timing before scaling.

## Provenance

Migrated on 2026-10-05 from the former `agents/crsp-wrds-expert.md`. The original source supplied CCM detail and standard Compustat filters, rather than a full Compustat dictionary. Historical counts remain labeled snapshots. A preceding session confirmed the `lpermno` column; the migration's standalone `comp.funda` pilot succeeded, but its live CCM merge was denied access to `crsp_a_ccm`. Tiny synthetic PostgreSQL cases verified merge syntax and duplicate diagnostics, not live CCM rows. See the query reference for exact validation scope.
