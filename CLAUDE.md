# WRDS toolkit instructions

## Two execution agents

- Delegate all direct PostgreSQL work to `wrds-psql-agent`. It handles every non-TAQ product, schema discovery, and cross-database SQL by loading the appropriate skills.
- Delegate TAQ work to `wrds-taq-agent`. Its primary execution path is SAS on WRDS Cloud through SSH, including small SAS schema probes, submission, monitoring, and result transfer.
- For requests combining TAQ with other data, the parent coordinates these two agents using explicit identifiers, dates, and output keys. There is no separate WRDS orchestrator or database-specific execution agent.

Skills are the source of database knowledge. Do not duplicate table catalogs, identifier rules, or query recipes in agent prompts. `wrds-schema` selects the relevant skills; `wrds-catalog` supplies the dated portable table/column inventory and current-product/access decisions; `wrds-linking` supplies cross-database guidance.

Use documented current products or the reviewed sole available version of a dataset. If it is the only available version with no verified replacement, it is canonical; missing version documentation does not exclude it. Keep its release and maintenance uncertainty visible separately. Keep historical years within maintained products, but exclude confirmed retired formats and superseded copies from new query recipes. Database visibility, accepted access checks, returned data and complete sample coverage are different evidence levels. Samples/trials must remain labeled.

## Access and credentials

Use direct local `psql service=wrds` for PostgreSQL. Do not use SSH for PostgreSQL queries, and do not use the interactive `wrds` Python library. `wrds-psql` provides the connection, timeout, export, and validation workflow.

Never read credential files without explicit user permission. This includes `.pgpass`, `.pg_service.conf`, `.ssh/config`, `.env`, `.netrc`, and other password/token/connection-secret files. Normal use of an already configured psql or SSH client is allowed; opening its credential files for inspection is a separate action requiring permission.

Do not put credentials in commands, logs, or output. Report configuration errors without inspecting secrets. Use `uv` exclusively for Python dependency management and script execution; never manually edit `pyproject.toml` or `uv.lock`.

## Validation and TAQ jobs

Always prototype the complete pipeline on small data before a full extraction: one asset/month for PostgreSQL, or one asset/week for TAQ. Check units, missing values, output keys, date boundaries, and join coverage.

TAQ job mechanics live in `wrds-ssh`. Mirror the local task subdirectory under `~/scratch/`, retain the submitted job ID, and inspect the SAS log before using the output. Default `qsas` logs are in the remote home directory (`~/prog.log`); do not infer the log path from the SAS program's scratch directory. CSV paths are set by the SAS program. Follow explicit paths reported by the actual submission.

Preserve source inputs, SQL/SAS programs, extraction parameters, and validation evidence. Do not commit code or data solely because an extraction completed; follow the user's task and the project's Git policy.

## First-time setup

Users configure the PostgreSQL service/password files themselves. SSH keys, the `wrds` host alias, and the scratch symlink are needed only for TAQ. See README.md for setup and migration from the former specialist agents.
