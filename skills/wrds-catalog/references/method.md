# Coverage and evidence

The catalog separates existence, account access, release/maintenance evidence, preferred version and sample coverage. A table can be the preferred available version while its release identity remains unknown.

## Evidence

- PostgreSQL system catalogs supply schemas, names, relation kinds, exact column types/comments, ACL flags, view definitions and dependencies. These do not require research-table scans.
- Non-TAQ relations with schema USAGE and relation SELECT eligibility receive a zero-row planning probe. For views with an observed `has_table_privilege` guard, the collector evaluates that exact guard separately: planning alone can miss a denied underlying schema. Explicit no-FROM deprecation wrappers receive a bounded runtime check so an error function cannot pass as usable data.
- Other outcomes retain denied access, runtime errors, and unverified cases separately. `planning_accepted` is deliberately weaker than a data-return test. No whole-table counts or maximum-date scans were used to claim coverage.
- TAQ uses separate `PROC CONTENTS` and SAS dictionary jobs through SSH/qsas. PostgreSQL TAQ rows are discovery metadata only.
- Public WRDS vendor pages and its sitemap provide product codes, titles, update frequency, last update, and dictionary URLs. Internet searches locate additional WRDS/provider manuals and migration notices. A public listing is not subscription evidence. A login-gated dictionary link is a reference, not a claim to have read its contents.

## Current product policy

The user's selection rule is: if it is the only available version, it is canonical. Defaults therefore include documented current products and explicitly reviewed sole available research versions. `canonical` and its reason record this choice independently of `lifecycle`. Aliases inherit the choice of their underlying tables. Denied copies do not disqualify the only available version. Samples stay labeled, and an internal helper does not become a research dataset merely because it is unique.

The review compares actual alternatives, not names alone. Prefer a verified available replacement where one exists; retain distinct datasets when equivalence is unproven. This rule does not reopen confirmed retired or superseded products. Canonical status does not establish active maintenance, recent observations, or complete coverage. The source policies are preserved in `catalog/canonical-crsp.json` and `catalog/canonical-other.json`; their decisions and reasons are carried in the portable catalog.

An explicit provider/WRDS retirement or migration statement takes precedence over table presence. CRSP CIZ stock/index and TFZ Treasury families are selected by documented mappings. Standalone index files explicitly retained by the July 2026 provider guide also remain current; the word "legacy" alone does not prove discontinuation. Alternate old deliveries and stale aliases are excluded from defaults. Product-level current status means the product remains listed without a retirement label, not that every historical observation has been revised or every field has a documented interpretation.

Historical observation years inside a maintained product remain included. `hist`, point-in-time and snapshot products are not automatically obsolete. `_old` is not sufficient evidence by itself: an unlisted copy is excluded only when a corresponding documented endpoint or explicit lifecycle rule exists. Unresolved cases remain labeled whether or not selected as canonical. Samples and trials remain labeled even when their schema is publicly offered. A sample's latest delivery is not full-universe coverage.

Catalog comments and provider coverage ranges can include sentinel dates or malformed outliers. Do not turn them into verified sample start/end dates. A requested extraction still needs a small date/identifier pilot and a check of row grain, duplicate keys, units, missing-value codes and actual coverage.

## Refresh and provenance

The source repository keeps SQL and collection scripts under `scripts/wrds_catalog/`, TAQ SAS jobs under `scripts/wrds_taq_inventory/`, raw evidence under `catalog/`, and source/lifecycle decisions under `research/`. `scripts/build_skill_catalog.py` creates this portable bundle. `coverage.json` records source SHA256 checksums and exact status counts. The installed lookup requires only this skill directory; it never reads credentials or contacts WRDS.

This is an account-specific snapshot, not a universal WRDS subscription inventory. Recheck access and current documentation before a new large extraction. Refresh evidence rather than editing generated relation or layout files by hand.
