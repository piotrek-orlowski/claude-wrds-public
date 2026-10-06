# WRDS database skills

Reusable WRDS database knowledge with two [Claude Code execution agents](https://code.claude.com/docs/en/sub-agents): one for direct PostgreSQL queries and one for TAQ SAS jobs. Skills hold the schemas, identifiers, filters, and examples. Agents load the skills required for the task and execute a small validated pilot before scaling.

## Structure

```text
agents/
  wrds-psql-agent.md       # All PostgreSQL requests, including cross-database SQL
  wrds-taq-agent.md        # TAQ SAS jobs through SSH
  paper-reader.md         # Existing optional research helper, separate from WRDS
skills/
  wrds-psql/              # Connection, export, local processing, query workflow
  wrds-ssh/               # TAQ SAS submission, monitoring, logs, and transfer
  wrds-schema/            # Select skills and verify needed metadata
  wrds-catalog/           # Portable catalog, column lookup, versions and access
  wrds-crsp/              # Stock returns, adjustments, identifiers, version rules
  wrds-compustat/         # Fundamentals and CRSP-Compustat linking (CCM)
  wrds-optionmetrics/     # Options, IVs, surfaces, units, quality filters
  wrds-taq/               # Intraday products, SAS schemas, filters, sampling
  wrds-linking/           # Cross-database identifiers, date alignment, join checks
  wrds-fama-french/       # Factor and portfolio returns
  wrds-jkp/               # Global Factor Data / stock characteristics
  wrds-bonds/             # TRACE, FISD, MSRB and delivered bond returns
  wrds-capital-iq/        # Capital structure, transactions, events and people
  wrds-lseg/              # IBES, Worldscope and LSEG sample products
  wrds-governance/        # Audit Analytics, BoardEx/Altrata and BvD
  wrds-esg/               # S&P ESG, Trucost and other climate/ESG samples
  wrds-public-data/       # Bank reports, rates, courts and macro series
  wrds-contributed-data/  # Other contributor datasets and their provenance
  wrds-market-data/       # Cboe and OTC products
  wrds-research/          # WRDS applications, ratios and SEC samples
  wrds-vendor-samples/    # Remaining restricted vendor samples/trials
catalog/                  # Dated raw metadata and validation evidence
research/                 # Primary documentation and lifecycle decisions
scripts/                  # Reproducible collection, build and audit tools
CLAUDE.md                 # Agent routing and repository instructions
settings.json             # Existing optional command permissions
```

Each skill has a short `SKILL.md`. Detailed schemas and examples live in linked `references/` files so a query need not load the whole database catalog. Database knowledge is maintained in one place and shared by both agents where relevant. Historical catalog observations are labeled as snapshots; verify tables and columns needed for a new extraction.

The PostgreSQL agent preloads `wrds-psql` and `wrds-schema`, then loads domain skills as needed. The TAQ agent preloads `wrds-ssh` and `wrds-taq`. For a request combining TAQ and daily stock data, the parent coordinates the two agents with agreed identifiers, dates, and output keys. A separate orchestrator agent is unnecessary.

## Catalog and current products

The 2026-10-05 snapshot records 118,646 visible PostgreSQL relations across 1,098 schemas, including exact column types/comments, alias dependencies and an access outcome for each. These are catalog counts, not subscription counts. Query planning and observed privilege-guard checks distinguish usable candidates from denied views; bounded data checks remain part of each requested extraction. TAQ metadata and access follow the separate SAS route.

```bash
uv run --no-project python skills/wrds-catalog/scripts/catalog.py coverage
uv run --no-project python skills/wrds-catalog/scripts/catalog.py schemas
uv run --no-project python skills/wrds-catalog/scripts/catalog.py search "bond"
uv run --no-project python skills/wrds-catalog/scripts/catalog.py table crsp.msf_v2
```

The default search selects documented current products and reviewed sole available versions that pass access checks. If a dataset has no verified accessible replacement, it is canonical for this account even when its release or maintenance status is unclear. The catalog records that uncertainty separately. Add `--all` to inspect excluded copies, denied products and internal tables. Historical partitions remain included, and samples/trials remain labeled. Primary WRDS/provider documentation supports product decisions; dictionary URLs that require login are identified as links rather than claimed as read.

See the [coverage report](research/coverage-report.md), [catalog evidence and limitations](skills/wrds-catalog/references/method.md), [core version decisions](research/current-products.md), and [provider sources](research/provider-sources.md). The lookup and compressed references travel with the skill folders; they do not depend on repository-level files after installation.

The [refresh procedure](scripts/wrds_catalog/README.md) preserves each dated snapshot and runs metadata/access prototypes before full collection. To audit a packaged release locally:

```bash
uv run --no-project --with pyyaml python scripts/validate_toolkit.py
uv run --no-project python scripts/validate_skill_catalog.py
```

These checks validate all reference links and the catalog's correspondence to the source evidence, then exercise the lookup from a temporary installation. They make no WRDS queries.

The same checks run in GitHub Actions on pushes and pull requests. They need no WRDS credentials. They verify the toolkit and saved metadata; a research extraction still needs its own small data test before scaling.

## Install in Claude Code

From this repository, copy the two WRDS agents and all skill folders:

```bash
mkdir -p ~/.claude/agents ~/.claude/skills
cp agents/wrds-psql-agent.md agents/wrds-taq-agent.md ~/.claude/agents/
cp -R skills/. ~/.claude/skills/
```

Review existing toolkit files before overwriting local customizations. The paper-reader agent is optional and is not needed for WRDS. Merge the relevant instructions from [CLAUDE.md](CLAUDE.md) into your project or user instructions, replacing any old WRDS routing block.

Agents use Claude Code's [`skills` frontmatter](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents). Other agent runtimes can reuse the skill content, but need their own agent/tool configuration. The skill entrypoints use shared Agent Skills metadata rather than Claude-only argument hints.

### Upgrading an existing installation

After copying the new agents and skills, retire these old definitions from the installed agents directory, preserving any personal modifications outside that directory:

- `crsp-wrds-expert.md`
- `optionmetrics-wrds-expert.md`
- `taq-wrds-expert.md`
- `wrds-query-orchestrator.md`

Remove instructions that still route to those agents. Do not keep compatibility copies in the discovery directory: they can continue receiving requests and carry stale schemas. No global files are modified by editing this repository.

| Previous knowledge location | New home |
|---|---|
| CRSP specialist | `wrds-crsp`; fundamentals and CCM in `wrds-compustat` |
| OptionMetrics specialist | `wrds-optionmetrics` |
| TAQ specialist | `wrds-taq`; job mechanics in `wrds-ssh` |
| Orchestrator joins and identifiers | `wrds-linking` and linked domain references |
| Orchestrator project workflow | `wrds-psql/references/query-workflow.md` |
| Repeated catalogs in access/preloader skills | Domain skills; live discovery through `wrds-schema` |

### Optional command permissions

Review and merge only the intended `permissions.allow` entries from `settings.json` into your existing configuration. Do not replace your settings file or import unrelated plugin settings. These rules grant command permission; they do not provide credentials or restrict SQL to read-only statements. The access skill sets read-only mode explicitly. Commands with additional connection options may need separate runtime approval.

## First-time WRDS setup

You need a [WRDS account](https://wrds-www.wharton.upenn.edu/register/), the relevant data subscriptions, and a local `psql` client. SSH access is needed only for TAQ.

Credential files must be created or edited by the user, or with explicit user permission. Agents may use already configured clients but must not inspect credential contents without permission.

### PostgreSQL

Configure `~/.pg_service.conf`:

```ini
[wrds]
host=wrds-pgdata.wharton.upenn.edu
port=9737
dbname=wrds
user=YOUR_WRDS_USERNAME
```

Configure `~/.pgpass` with your own password:

```text
wrds-pgdata.wharton.upenn.edu:9737:wrds:YOUR_WRDS_USERNAME:YOUR_PASSWORD
```

Restrict password-file permissions:

```bash
chmod 600 ~/.pgpass
```

Use the bounded, noninteractive connection check in [wrds-psql](skills/wrds-psql/SKILL.md), followed by a small query of the requested dataset. Authentication and subscription access are separate checks. Do not count an entire table to test connectivity.

### TAQ SSH setup

Register your SSH key with WRDS and configure the host alias in `~/.ssh/config`:

```sshconfig
Host wrds
    HostName wrds-cloud-sshkey.wharton.upenn.edu
    User YOUR_WRDS_USERNAME
    IdentityFile ~/.ssh/wrds
    Port 22
```

After SSH is configured, create the scratch symlink once:

```bash
ssh wrds 'ln -sf /scratch/$(basename $(dirname $HOME))/$(whoami) ~/scratch'
```

Use SSH for TAQ SAS jobs and their schema probes, monitoring, and transfers. Do not use it as a PostgreSQL fallback. Follow the [TAQ job workflow](skills/wrds-ssh/SKILL.md), including the small pilot, retained job ID, and log checks. Default `qsas` logs are in the remote home directory, such as `~/prog.log`; CSV output goes to the path specified by SAS. Follow explicit locations reported by the actual submission.

## Usage

Describe the data request; the parent chooses one of the two agents:

```text
Get daily CRSP returns for AAPL and MSFT for January 2024.
Get SPY option IVs for a day and match them to CRSP returns.
Merge monthly stock returns with available Compustat fundamentals.
Compute five-minute realized variance for AAPL for one week from TAQ.
```

You can also request schema discovery with `/wrds-schema crsp optionm`, or invoke a domain skill for a methods question. PostgreSQL requests involving several databases stay with the same PostgreSQL agent; it loads each relevant skill.

Results should include the query or SAS program, output paths, filters, units, and pilot validation. Distinguish historical availability from current access. Save extraction provenance; commit only when requested or authorized by the project.

## Troubleshooting

- **Network/DNS failure:** distinguish the execution sandbox's network restrictions from WRDS availability. Use the runtime's approval path when required; do not fall back to SSH for SQL.
- **Authentication failure:** report the client error and have the user check their service/password setup. Do not inspect credential files without permission.
- **Missing table or permission:** verify the exact requested table/year and subscription. A successful login does not establish access to every product.
- **TAQ job incomplete:** inspect the recorded job ID and SAS log using the SSH skill. Do not resubmit solely because a local wait timed out.
- **Schema mismatch:** inspect the exact product/version and update the query from observed metadata. Keep historical references distinct from live evidence.

Use `uv` for local Python dependency management and scripts. PostgreSQL extraction itself requires only `psql`; TAQ execution uses SAS on WRDS Cloud.
