# WRDS skill coverage report

Snapshot: 2026-10-05. The repository contains 21 skills and two WRDS execution agents. Skills hold database knowledge and portable metadata; agents handle direct PostgreSQL work or TAQ SAS jobs. Every dataset selected by default has a domain skill owner.

The selection rule now follows the user's clarification: **if it is the only available version, it is canonical**. This means it is the version the skills should use. It does not claim that the provider still updates it. Missing release documentation remains a note rather than a reason to hide the only available data.

## Connection and scope

Direct PostgreSQL access through `psql service=wrds` worked, including small CRSP, Compustat and OptionMetrics queries. TAQ SSH access and SAS submission also worked. The full TAQ metadata job completed with `SYSCC=0`. SSH remains limited to TAQ SAS work and its supporting transfers and monitoring.

Configured clients were used without inspecting credential files. The full inventories collected metadata, not research observations. No global installation or commit was performed.

## Coverage

| Inventory | Recorded metadata | Default selection |
|---|---|---|
| PostgreSQL | 118,646 visible relations across 1,098 schemas; 3,092,679 column instances and 48,470 dependency edges | 5,675 table/view names across 249 schemas, including alternate names for the same underlying tables; 2,920 base relations |
| TAQ SAS | 82,212 logical members across four libraries; 78 column layouts and 1,154,370 expanded column definitions | 59,479 members, including six current sample members |

These inventories overlap in products and must not be added as independent datasets. SAS counts describe logical library members; concatenated libraries can shadow physical duplicates.

Within the PostgreSQL selection, 5,560 entries have documented current-product status; 1,461 of those are labeled samples or trials. Another 115 names represent the 58 sole available datasets restored by the new rule, including restricted samples. Their inclusion does not imply full vendor coverage. The SAS default excludes 22,733 legacy members, which remain available for diagnosis with `--all`.

PostgreSQL access preflight means zero-row query planning plus evaluation of observed privilege guards. It does not establish observation availability or complete subscription coverage. A small data-returning pilot remains required for each extraction. TAQ metadata opening likewise does not prove observation access, and filename dates do not establish data coverage.

The earlier list of 153 entries was 78 underlying tables plus 75 alternate names. It mixed data with missing documentation, duplicate versions and internal tables. Each underlying table has now been reviewed:

| Decision | Underlying tables | Meaning |
|---|---:|---|
| Include as canonical | 58 | No verified available replacement for the particular data or supplied links |
| Prefer an available alternative | 15 | Nine CRSP copies and six application samples have a preferred available version |
| Keep out of research defaults | 5 | Two query helpers, two database-monitoring tables and one unexplained placeholder |

The 58 included tables comprise 35 CRSP index/portfolio tables, four CCM sample tables, 11 healthcare/MEPS tables, six application samples, Gutenberg books and the unversioned PWT national-accounts table. Their 115 names now appear in ordinary searches. The remaining 38 names remain available through `--all`.

The [full review](../catalog/lifecycle-review.json) records the choice and reason for every name. [CRSP decisions](../catalog/canonical-crsp.json) and [other decisions](../catalog/canonical-other.json) preserve the comparisons. The release uncertainty is retained separately from the choice of which table to use.

## Remaining practical limits

| Area | What remains uncertain or unavailable | Consequence |
|---|---|---|
| CRSP-Compustat company links | The account cannot access the full production linking tables; sample tables are available | The samples can support a small demonstration, but cannot be assumed to cover a full research universe |
| Some CRSP portfolio and Treasury series | These are the available versions, but exact release and update history are not established | Use the selected tables and verify the required series and dates on a small extract |
| Healthcare/MEPS and Gutenberg | The available tables are identified, but detailed coverage and their mapping to published product descriptions remain incomplete | Check the population, fields and dates needed for the question before a large extraction |
| Unversioned PWT national accounts | The exact PWT release is unknown; the catalog has no PWT 11.0 delivery | Preserve the table's identity and do not describe it as the latest PWT release |
| Application samples | Some include distinct supplied links or restricted international samples; their full coverage is unverified | Keep their sample label and do not claim that they cover the full vendor database |
| Actual observations | The inventory verified metadata and access checks, not a data extract from every table | Each new extraction still starts with a small data-returning test |

The 20 tables kept out of defaults do not represent 20 missing research products: 15 have preferred alternatives, four are internal helpers/monitoring tables, and one is a placeholder whose purpose is unknown.

## Current-product decisions

Research used 88 successfully retrieved public WRDS vendor pages, containing 575 product descriptions, plus primary provider manuals and notices. Three obsolete sitemap URLs returned errors, which remain recorded. Authentication-gated dictionary links are identified as links, not represented as documents read.

CRSP CIZ is the default stock format; discontinued SIZ and documented retired Treasury endpoints are excluded. Maintained historical index files remain included where the current guide confirms them. Compustat historical, snapshot and point-in-time products are not retired merely because of their names. OptionMetrics stale distribution aliases are excluded. Historical TAQ daily partitions remain part of the maintained product. Samples can be currently offered despite having fixed historical coverage.

See [core product decisions](current-products.md), [provider sources](provider-sources.md), and [catalog methods and limits](../skills/wrds-catalog/references/method.md) for the evidence and exact rules.

## Validation and use

The independent catalog audit reconciles every PostgreSQL table/view, column and dependency, and every SAS member and column definition, against preserved source metadata. It also checks the selection rule and runs lookup scenarios from a temporary installation outside the repository. The current result and scenario count are recorded in the linked validation report. The full SAS inventory had no reported errors, warnings or count mismatches.

Static validation checked skill and agent metadata, local references and shell examples. Evidence is in [the portable catalog validation report](../catalog/discovery/skill-catalog-validation.json) and [the packaged coverage manifest](../skills/wrds-catalog/references/coverage.json).

The [README](../README.md) describes routing, lookup commands and later installation. The [refresh procedure](../scripts/wrds_catalog/README.md) preserves dated evidence and requires a prototype before full collection. This is a dated catalog, not a promise that subscriptions or schemas will remain unchanged.
