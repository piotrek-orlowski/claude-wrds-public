# Refresh the WRDS metadata snapshot

These standard-library scripts use direct `psql service=wrds` with `-X -w`, read-only transactions, a 10-second connection timeout, a 60-second statement timeout, and a 2-second lock timeout. They do not read credential files or use the Python `wrds` client. Run them through the WRDS PostgreSQL agent after loading `wrds-psql`. TAQ PostgreSQL catalog metadata is visible, but the probe script skips TAQ; its data and SAS metadata workflow belongs to `wrds-taq`.

Always choose a **new snapshot directory** for a refresh. The checked-in `catalog/discovery` is the preserved 2026-10-05 collection. Reusing it does not refresh grants or table definitions. The example below keeps the new snapshot separate; replace its date/suffix if that directory already contains a previous collection.

```bash
SNAPSHOT="$PWD/catalog/snapshots/2026-10-06-review"
uv run --no-project python scripts/wrds_catalog/collect.py schemas --output "$SNAPSHOT"
uv run --no-project python scripts/wrds_catalog/collect.py prototype --output "$SNAPSHOT"
```

Inspect `schemas.jsonl` for schema names, relation counts, schema USAGE, and SELECT flags. Inspect `relations-prototype.jsonl` for the four-table schema/column/dependency prototype. These read PostgreSQL metadata only, not research observations. Confirm that JSON rows parse and output/provenance are recorded before collecting the full metadata inventory.

```bash
uv run --no-project python scripts/wrds_catalog/collect.py metadata --output "$SNAPSHOT"
uv run --no-project python scripts/wrds_catalog/collect.py columns-prototype --output "$SNAPSHOT"
uv run --no-project python scripts/wrds_catalog/probe.py --prototype --output "$SNAPSHOT"
```

The column prototype covers `crsp`, `comp`, and `optionm`. The access prototype includes an ordinary current table, a denied underlying CCM schema, and a deprecated alias wrapper. Review `access-probes-prototype.jsonl`: zero-row acceptance must remain distinct from observed alias-guard errors and deprecated wrapper errors. The eight prototype names reflect the original snapshot; if a provider removes them, update the prototype list deliberately before a new full run.

After the prototypes are satisfactory:

```bash
uv run --no-project python scripts/wrds_catalog/collect.py columns --output "$SNAPSHOT"
uv run --no-project python scripts/wrds_catalog/probe.py --output "$SNAPSHOT"
uv run --no-project python scripts/wrds_catalog/validate.py --output "$SNAPSHOT"
```

`validate.py` checks relation uniqueness, complete per-relation column coverage, layout hashes, dependency integrity, complete access outcomes, and schema totals. It writes `validation.json` and `schema-access-summary.jsonl` and appends a manifest event. It does not establish current-product lifecycle, observation availability, or complete data-return access. Review those separately with current provider evidence before building a replacement skill catalog. The package builder currently reads `catalog/discovery`; promotion of a reviewed snapshot into a release is a separate explicit step, not an automatic overwrite in these collection commands.

## Files and evidence

- `schemas.jsonl`: visible non-system schemas, relation counts, and privilege flags.
- `relations.jsonl.gz`: relation identifiers/kinds/comments, privileges, and non-TAQ view definitions.
- `dependencies.jsonl.gz`: direct view dependencies and referenced column ordinals.
- `column-layouts.jsonl.gz`: ordered column names, SQL types, nullability flags, and comments; identical layouts are deduplicated by SHA256 within each schema.
- `access-probes.jsonl`: exactly one evidence outcome per relation, including explicit skipped/denied/error states.
- `column-batches/` and `access-batches/`: resumable metadata batch outputs; access batches retain exact generated SQL and stderr evidence.
- `queries/`: exact collection SQL templates named by their source hash; the manifest records bound psql variables. Access batches retain their generated SQL separately.
- `manifest.json`: collection times, query paths/hashes, archived SQL paths, statement settings, outcomes, and validation events. A `.manifest.lock` coordinates independent column and access writers.

`planning_accepted` means zero-row planning plus any observed privilege guards passed. The probe executes `LIMIT 1` only on explicitly detected, no-FROM deprecated error-wrapper views; it does not scan a research relation. A schema grant or SELECT flag alone is not subscription evidence, and a denied alias guard must not be bypassed through its target table.

## Resume and preserve

Complete collection outputs are never overwritten. A failed collection keeps a `.partial` file; a retry of the same unfinished target may replace that diagnostic partial file. Save it under a different name first if needed. Column batches resume by skipping completed batch files; access probes append only missing relation outcomes and retain prior evidence. Do not mix batches from different metadata snapshots or run two writers for the same phase/directory.

If the metadata phase stops after writing `relations.jsonl.gz` but before completing dependencies, do not delete the preserved relation file. Run the missing collection explicitly with the same script module:

```bash
uv run --no-project python - "$SNAPSHOT" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts/wrds_catalog').resolve()))
import collect
collect.OUT = Path(sys.argv[1]).resolve()
collect.collect(collect.SQL_DIR / 'dependencies.sql', collect.OUT / 'dependencies.jsonl.gz')
PY
```

That call uses the same read-only psql settings and overwrite protection. If the server catalog changed during a long collection and validation reports mismatched totals, retain the failed snapshot and start a new dated directory. Do not manufacture coverage by merging incompatible snapshots.

## Refresh public product documentation

The separate documentation collector needs BeautifulSoup. Use a new dated filename to preserve the previous evidence:

```bash
uv run --no-project --with beautifulsoup4 python scripts/collect_product_docs.py --output research/product-docs-2026-10-06-review.json
```

For a prototype, add `--url` with one public WRDS vendor-page URL. Review failures and product mappings before promoting the new file to the packaged catalog's inputs. This collector reads public pages only and does not authenticate to WRDS.
