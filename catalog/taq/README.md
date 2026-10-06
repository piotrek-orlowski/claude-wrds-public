# TAQ SAS metadata evidence

Collection date: 2026-10-05. This directory contains metadata only, with no
trade or quote observations. The programs are in
`scripts/wrds_taq_inventory/` at the repository root.

## Scope and evidence

- `taq_metadata_probe_20261005T222724_*`: successful one-member
  `PROC CONTENTS` probe of `TAQMSEC.CTM_20241007` (job 40376301, 17 columns)
  and assigned TAQ library paths. The raw library result has six repeated rows
  per distinct path; use the deduplicated full inventory's library file.
- `prototype-pipeline/`: completed three-member dictionary/hash/export pipeline
  (job 40376634): `CTM_20241007`, `CTM_20241008`, `CQM_20241007`. Its summary
  validates member/layout coverage, ordered columns, counts and log diagnostics.
  Sixteen synthetic hash tests verify sensitivity to all seven metadata fields
  and equivalence to an explicit 256-character buffer. No temporary-buffer
  truncation was observed. A SASUSER-to-WORK registry startup warning from the
  concurrent SAS session is retained in the summary; the metadata steps had
  no warnings/errors and completed with `SYSCC=0`.
- `taq_metadata_inventory_20261005T223200_*`: full four-library metadata run,
  job 40376344. Its completed output is validated into `summary.json` and
  `families.jsonl`; those files establish completed coverage, not the mere
  existence of a submitted job or the one-member prototype.

The full run completed in 38:45.77 with `SYSCC=0`, zero errors/warnings and
zero member/column mismatches. It contains 82,212 logical members, 78 layouts,
2,521 representative column rows and 1,154,370 expanded column definitions.
Member counts: `TAQMSEC` 59,473; `TAQ` 22,719; `TAQSAMP` 14; `TAQMSAMP` 6.
There are 38 library/family groups after recognizing daily, monthly and annual
filename suffixes. Exact source CSVs are preserved without normalization.

Notable filename cases remain explicit: `TAQMSEC.MASTM_2011060` has a
seven-digit suffix and is not interpreted as a valid daily partition;
`TAQ.WRDS_IID` coexists with 22 annual members. Auxiliary four-column `IX_*`
members are inventoried rather than silently discarded. Inspect layouts and
overlap before using these as research inputs.

The selected aliases are `TAQ`, `TAQMSEC`, `TAQSAMP`, and `TAQMSAMP`. Current
Daily TAQ and its historical year partitions are distinct from historical
monthly TAQ. Samples are separate products. ISSM/NASTRAQ remain separate legacy
products in the PostgreSQL discovery catalog; this SAS run does not enumerate
them. SSH authentication used the configured alias normally; no credential or
authentication configuration file was opened. BatchMode reported a
keyboard-interactive requirement, while one normal TTY connection succeeded
without prompting. No authentication configuration was modified.

## Files and interpretation

| Suffix | Meaning |
|---|---|
| `libraries.csv` | Distinct SAS libname/engine/path bindings |
| `members.csv` | Member names, labels, SAS header `NVAR`/`NOBS`, create/modify metadata |
| `layout_map.csv` | Every observed logical member mapped to an ordered metadata layout |
| `layout_columns.csv` | One representative's ordered variables per distinct layout: names, numeric/character type, lengths, labels, formats and informats |
| `validation.csv` | Members missing column metadata or with `NVAR`/column-count mismatches; expected zero rows |
| `*_task.log` | Task-specific SAS log after initialization; account-specific home paths removed |
| `summary.json` | Counts, scope, diagnostics, CSV SHA-256 checksums and limits |
| `families.jsonl` | Filename-family counts, layouts, and filename-period bounds |

An MD5 chain fingerprints metadata fields; it is not a hash of research
observations or a security claim. Every field is separately hashed into a
fixed-length component; field order is retained. Full source logs are retained
outside the repository during the run; the repository artifacts contain only
task-specific log evidence and sanitized diagnostics.

Header `NOBS` is not a fresh row count. Filename date bounds do not prove
observation coverage or a complete trading calendar. Metadata opens do not
establish row-level access to every observation. Concatenated library aliases
can shadow duplicate physical member names. Counts refer to logical members
exposed by the selected aliases, not every physical file on WRDS storage.

## Reproduction

Use `wrds-ssh` for submission/monitoring/transfer. Copy the programs to new
unique basenames and update their `run`/output prefixes before a new collection.
Run the bounded pipeline first. Submit the full inventory only after the
prototype validates; preserve the job ID and inspect its home-directory log.
Never rerun solely because a job is slow: dictionary metadata discovery opens
many member headers and can take substantial time.
The literal uppercase `LIBNAME IN (...)` restrictions follow
[SAS Usage Note 9581](https://support.sas.com/kb/9/581.html); do not wrap the
dictionary `LIBNAME` column in a function that defeats library restriction.

After transfer, validate locally from the repository root:

```bash
uv run --no-project python scripts/wrds_taq_inventory/summarize_inventory.py \
  --catalog catalog/taq \
  --run taq_metadata_inventory_20261005T223200 \
  --job-id 40376344 \
  --log /path/to/taq_metadata_inventory_20261005T223200.log
```

Use the actual new run name, job ID, and retrieved log path when recollecting.
The validator is standard-library-only and makes no network connections.
