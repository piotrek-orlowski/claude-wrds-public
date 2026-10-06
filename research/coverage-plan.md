# WRDS coverage expansion

Requested 2026-10-05: cover every accessible table in current WRDS products, using live schema discovery and primary documentation. Save the skills here; installation on this machine is a later step.

Completed 2026-10-05, then updated to apply the user's rule that a sole available version is canonical. See the [coverage report](coverage-report.md) for results, validation evidence and remaining limits. The allocation below records how the work was performed.

## Evidence required

1. A dated catalog of non-system schemas, tables/views, columns, permissions, and alias/dependency relationships from the configured WRDS account.
2. An access outcome that distinguishes catalog visibility, privilege eligibility, successful query validation, denied access, and unverified cases. Existing CCM views illustrate why visible metadata alone is insufficient.
3. Product/version classification backed by WRDS or provider documentation. Keep historical observations in a current product; exclude superseded database versions from active recipes. Do not infer deprecation merely from a year, `hist`, `snapshot`, or `pit` suffix.
4. A skill owner and discoverable table/column reference for every accessible current table. Use product families and shared catalog references rather than one skill per physical partition.
5. Explicit excluded/replaced product records, documentation sources with retrieval dates, and reproducible catalog collection scripts.
6. Validation of coverage completeness, reference links, metadata, representative workflows, and bounded access probes. Keep unknown release or maintenance status visible even when the sole available version is selected as canonical.

## Execution boundaries

Use direct read-only PostgreSQL for catalog discovery and non-TAQ work. TAQ computation and SAS schema probes use its SSH/SAS agent. Do not inspect credential files. Use uv for Python. Prototype catalog collection on a small subset before scaling; no whole-table data scans. Preserve existing uncommitted work. Do not install globally or commit during this task.

## Work allocation

- Metadata collection: `migrate_crsp`, owning `catalog/` and discovery scripts/queries.
- Current CRSP/Compustat/OptionMetrics documentation: `migrate_optionmetrics`.
- Provider documentation and subsequent additional product skills: `skill_structure`.
- Catalog packaging, complete coverage reconciliation, additional skills, routing, and final audit: root.
