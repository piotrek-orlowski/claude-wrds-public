## WRDS Setup (one-time per user)

New users must configure these files before WRDS access works:

1. **`~/.pg_service.conf`** — PostgreSQL connection (host, port, database, user)
2. **`~/.pgpass`** — PostgreSQL password (chmod 600)
3. **`~/.ssh/config`** — SSH host alias for WRDS cloud:
   ```
   Host wrds
       HostName wrds-cloud-sshkey.wharton.upenn.edu
       User <your-wrds-username>
       IdentityFile ~/.ssh/wrds
       Port 22
   ```
4. **WRDS scratch symlink** — run once after SSH is configured:
   ```bash
   ssh wrds 'ln -sf /scratch/$(basename $(dirname $HOME))/$(whoami) ~/scratch'
   ```

## WRDS Database Access

**NEVER use SSH to access WRDS databases.** Use direct PostgreSQL connections via `psql`.

**PostgreSQL connection:**
```bash
psql service=wrds
```

**Standard access pattern** (CRSP, OptionMetrics, Compustat, etc.):
```bash
psql service=wrds -q -c "
COPY (SELECT ... FROM schema.table WHERE ...) TO STDOUT WITH CSV HEADER
" > output.csv
```

**Exception — TAQ only:** NYSE TAQ data is too large for direct SQL. Use SSH + SAS on WRDS cloud for TAQ. Access: `ssh wrds`.

**TAQ workflow:**
1. **Always prototype first** — test SAS program on a small subset (one week) before submitting the full job.
2. **Mirror local directory structure on WRDS.** If SAS files live in `data/taq-iv/` locally, create `~/scratch/taq-iv/` on WRDS and upload there.
3. **Submit:** `scp data/taq-iv/prog.sas wrds:~/scratch/taq-iv/` then `ssh wrds 'qsas ~/scratch/taq-iv/prog.sas'`
4. **Logs go to `~/prog.log`** (home dir), not `/scratch/`. CSV output goes wherever the SAS program specifies.
5. **Monitor:** `ssh wrds 'qstat -u $(whoami)'`

**Never use the `wrds` Python library** — it has interactive prompts that don't work in non-interactive contexts. Use `psql` directly or `sqlalchemy`/`psycopg2` with the `.pgpass` credentials.

**Always delegate WRDS queries to specialist agents.** Never write WRDS SQL directly — the expert agents know the correct table names, schemas, and conventions.
- **Multi-schema or ambiguous requests** → use `wrds-query-orchestrator` first. It will coordinate the right specialists and compose merged queries. Use this when the prompt mentions multiple databases (e.g., CRSP + OptionMetrics), or when it's unclear which schema to query.
- **Single-schema requests** → delegate directly to the appropriate expert:
  - `crsp-wrds-expert` — CRSP returns, prices, adjustments, delisting, identifiers
  - `optionmetrics-wrds-expert` — option prices, IVs, Greeks, volatility surfaces
  - `taq-wrds-expert` — TAQ high-frequency trades, quotes, NBBO (SSH + SAS)
