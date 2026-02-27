# Claude Code WRDS Toolkit

A set of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) agents, skills, and configuration files that let Claude autonomously query [WRDS](https://wrds-www.wharton.upenn.edu/) databases — CRSP, OptionMetrics, Compustat, and TAQ — directly from your terminal.

## What's included

```
agents/
  crsp-wrds-expert.md          # CRSP returns, prices, identifiers, delisting
  optionmetrics-wrds-expert.md  # IvyDB option prices, IVs, Greeks, surfaces
  taq-wrds-expert.md            # TAQ high-frequency trades/quotes (SSH + SAS)
  wrds-query-orchestrator.md    # Coordinates multi-database queries
skills/
  wrds-psql/SKILL.md            # psql connection patterns and formatting rules
  wrds-ssh/SKILL.md             # SSH connection, SAS job submission, file transfer
  wrds-schema/SKILL.md          # Schema pre-loader for starting new sessions
settings.json                   # Pre-approved permissions for WRDS commands
```

**Agents** are autonomous specialists Claude delegates to. Each one knows the schema, gotchas, and best practices for its database.

**Skills** are reference documents agents load before running commands. The `wrds-psql` skill, for example, enforces single-line `psql` commands to avoid shell-expansion approval prompts.

## Prerequisites

You need a [WRDS account](https://wrds-www.wharton.upenn.edu/register/) with SSH key access configured through the WRDS website.

## First-time setup

### 1. PostgreSQL service file

Create `~/.pg_service.conf`:

```ini
[wrds]
host=wrds-pgdata.wharton.upenn.edu
port=9737
dbname=wrds
user=YOUR_WRDS_USERNAME
```

### 2. PostgreSQL password file

Create `~/.pgpass`:

```
wrds-pgdata.wharton.upenn.edu:9737:wrds:YOUR_WRDS_USERNAME:YOUR_PASSWORD
```

Then restrict permissions:

```bash
chmod 600 ~/.pgpass
```

### 3. SSH config

Add to `~/.ssh/config`:

```
Host wrds
    HostName wrds-cloud-sshkey.wharton.upenn.edu
    User YOUR_WRDS_USERNAME
    IdentityFile ~/.ssh/wrds
    Port 22
```

Replace `YOUR_WRDS_USERNAME` with your WRDS username and ensure `~/.ssh/wrds` is your WRDS SSH private key.

### 4. WRDS scratch symlink

Run once after SSH is working:

```bash
ssh wrds 'ln -sf /scratch/$(basename $(dirname $HOME))/$(whoami) ~/scratch'
```

This creates `~/scratch` on the WRDS server pointing to your institution's scratch space. All agents use `~/scratch/` paths so no institution-specific values are needed.

### 5. Verify connectivity

```bash
# PostgreSQL (should return rows)
psql service=wrds -c "SELECT COUNT(*) FROM crsp.dsf LIMIT 1;"

# SSH (should print your username)
ssh wrds 'whoami'
```

## Installation

Copy the agents, skills, and settings into your Claude Code config directory:

```bash
# From the repo root
cp -r agents/ ~/.claude/agents/
cp -r skills/ ~/.claude/skills/
cp settings.json ~/.claude/settings.json
```

If you already have a `~/.claude/settings.json`, merge the `permissions.allow` entries manually:

```json
{
  "permissions": {
    "allow": [
      "Bash(psql service=wrds*)",
      "Bash(ssh wrds*)",
      "Bash(scp * wrds:*)",
      "Bash(scp wrds:*)"
    ]
  }
}
```

These permission rules let the WRDS agents run `psql`, `ssh`, and `scp` commands without prompting you for approval each time.

## Usage

### General pattern

Ask Claude for WRDS data and it will delegate to the right specialist agent automatically. You don't need to name agents — just describe what you need.

```
> Get me daily returns for AAPL and MSFT for 2024

> What's the ATM implied volatility for SPY options with 30-day maturity?

> Merge CRSP monthly returns with Compustat annual fundamentals for 2020-2024
```

### How it works

1. Claude reads your request and identifies which databases are involved
2. For multi-database or ambiguous requests, it consults the **orchestrator** agent first
3. The orchestrator delegates to the appropriate **expert** agents
4. Each expert invokes the **wrds-psql** skill (which loads connection rules), then runs the query
5. Results are returned as CSV, displayed inline, or saved to a file

### CRSP (stocks)

The `crsp-wrds-expert` handles everything in the `crsp` schema: daily/monthly stock files, index returns, stocknames, delisting, distributions, and CRSP-Compustat linking.

**Example queries you can ask:**

- Daily returns for a list of PERMNOs
- Split-adjusted price histories
- Market capitalization time series
- Cumulative returns over event windows
- Common stock universe with standard filters (SHRCD, EXCHCD)
- Fama-French style portfolio sorts
- Delisting-adjusted returns

### OptionMetrics (options)

The `optionmetrics-wrds-expert` covers the `optionm` schema: option prices, implied volatilities, Greeks, volatility surfaces, standardized options, and zero-coupon rates.

**Example queries:**

- Option chain for a given stock and date
- ATM implied volatility term structure
- Volatility surface extraction
- Put-call IV spread
- IV skew measures
- Multi-year IV time series

### Cross-database queries

When your request spans multiple databases, the **orchestrator** agent coordinates:

- **OptionMetrics + CRSP**: Links via `wrdsapps.opcrsphist` (SECID ↔ PERMNO) or 8-char CUSIP matching
- **CRSP + Compustat**: Links via `crsp.ccmxpf_lnkhist` (PERMNO ↔ GVKEY)
- **TAQ + CRSP**: Links via `wrdsapps.taqmclink` (symbol ↔ PERMNO, Sept 2003+)

Example:

```
> Get option implied volatilities for SPY and match them with CRSP daily returns
```

The orchestrator will dispatch the OptionMetrics expert for option data, the CRSP expert for stock returns, and compose the merged query using the appropriate link table.

---

## TAQ (high-frequency data)

TAQ is fundamentally different from the other databases. The data is too large for direct PostgreSQL queries, so all processing happens on the WRDS cloud server via **SSH + SAS**.

### How TAQ works in this toolkit

The `taq-wrds-expert` agent writes SAS programs, uploads them to WRDS, submits them as batch jobs, monitors completion, and downloads results. The `wrds-ssh` skill provides the connection patterns.

### TAQ workflow

```
> Compute 5-minute realized variance for AAPL for January 2024 from trade
> records
```

What happens behind the scenes:

1. Agent writes a SAS program locally
2. Uploads it to WRDS: `scp prog.sas wrds:~/scratch/`
3. Submits the job: `ssh wrds 'qsas ~/scratch/prog.sas'`
4. Polls for completion: `ssh wrds 'qstat -u $(whoami)'`
5. Checks logs: `ssh wrds 'tail -50 ~/scratch/prog.log'`
6. Downloads results: `scp wrds:~/scratch/output.csv ./`

### TAQ gotchas

- SAS jobs on WRDS are **asynchronous only**. The `-sync y` option does not work on WRDS Cloud.
- Log files go to the same directory as the `.sas` file, not a separate log directory.
- TAQ millisecond data uses `SYM_ROOT` (not `SYMBOL_ROOT`), `TIME_M` (not `TIME`), and `ASK` (not `OFR`). Always verify variable names with `PROC CONTENTS` before writing extraction code.
- Use SAS views (`data ... / view=...;`) with `open=defer` to avoid materializing huge intermediate datasets.
- TAQ scratch files on WRDS are auto-deleted after 48 hours.

### TAQ example queries

```
> Get NBBO bid-ask spreads for AAPL for the first week of 2024

> Compute Lee-Ready signed trades matched with prevailing quotes

> Extract all trades for SPY on 2024-01-15 with standard quality filters
```

---

## Schema pre-loading

At the start of a session, you can ask Claude to pre-load schema knowledge:

```
> /wrds-schema crsp optionm
```

or just:

```
> /wrds-schema
```

This dispatches the specialist agents to query `information_schema.columns` and return a compact reference card with table names, column types, date ranges, and known gotchas. This avoids exploratory round-trips during the actual work.

## Troubleshooting

**"Connection refused" from psql:**
- Verify `~/.pg_service.conf` has the correct host/port/dbname/user
- Verify `~/.pgpass` has the matching password line and `chmod 600` permissions
- Test: `psql service=wrds -c "SELECT 1;"`

**"Permission denied" from SSH:**
- Verify your SSH key is registered on the [WRDS website](https://wrds-www.wharton.upenn.edu/)
- Verify `~/.ssh/config` has the correct `Host wrds` entry
- Test: `ssh wrds 'echo ok'`

**Agent keeps asking for permission:**
- Ensure `settings.json` is in `~/.claude/settings.json` (global) or `.claude/settings.json` (project-level)
- The permission patterns must match exactly: `Bash(psql service=wrds*)`, etc.

**SAS job stuck in queue:**
- Check status: `ssh wrds 'qstat -u $(whoami)'`
- WRDS has limited grid slots — large jobs may wait during peak hours

**"Table does not exist" for OptionMetrics:**
- OptionMetrics tables are yearly: `optionm.opprcd2024`, not `optionm.opprcd`
- Check available years: `psql service=wrds -c "\dt optionm.opprcd*"`

**SSH asks for a Duo push / MFA code:**
- WRDS requires Duo two-factor authentication for SSH connections
- On first connect, you'll get a Duo prompt — approve the push on your phone or enter a passcode
- SSH sessions are typically cached for a period after a successful Duo authentication, so subsequent commands within the same window won't re-prompt
- If you're getting Duo prompts on every `ssh wrds` call (e.g., during a TAQ workflow with multiple steps), consider using SSH connection multiplexing. Add to `~/.ssh/config`:
  ```
  Host wrds
      ControlMaster auto
      ControlPath ~/.ssh/sockets/%r@%h-%p
      ControlPersist 4h
  ```
  Then `mkdir -p ~/.ssh/sockets`. The first connection authenticates with Duo; subsequent connections reuse the tunnel for up to 4 hours.

## Design decisions

**Why `psql service=wrds` instead of connection flags?**
Shell variables like `$WRDS_USERNAME` and command substitutions like `$(...)` trigger Claude Code's manual approval prompt on every invocation. Using `pg_service.conf` avoids this entirely — the connection string is a static literal.

**Why single-line psql commands?**
Multi-line commands with `\` continuation also trigger approval prompts. The `wrds-psql` skill enforces writing psql as a single line, or writing SQL to a file and using `psql service=wrds -f query.sql` for complex queries.

**Why SSH + SAS for TAQ but PostgreSQL for everything else?**
TAQ data is orders of magnitude larger than other WRDS databases. A single day of millisecond trade data can be tens of gigabytes. Direct SQL queries would timeout or exhaust memory. SAS on the WRDS grid processes data in-place without network transfer.

**Why `~/scratch` symlink?**
WRDS scratch space paths include institution and username components (e.g., `/scratch/wharton/jsmith`). The symlink `~/scratch → /scratch/{institution}/{username}` makes all paths portable across users without any hardcoded credentials.

**Why not the `wrds` Python library?**
The `wrds` pip package uses interactive prompts for authentication that don't work in non-interactive contexts like Claude Code agents. Use `psql` for command-line queries or `psycopg2.connect("service=wrds")` for Python scripts.
