---
name: wrds-ssh
description: This skill should be used when the user needs to connect to WRDS servers, run SAS code on WRDS, execute SQL queries on WRDS PostgreSQL, submit batch jobs to WRDS, or transfer files to/from WRDS. Use this skill whenever WRDS server access is required for data extraction, processing, or analysis.
version: 1.0.0
---

# WRDS SSH Connection Skill

This skill provides guidance on connecting to and working with WRDS (Wharton Research Data Services) servers via SSH.

## Connection

The SSH connection to WRDS is pre-configured. Connect using:

```bash
ssh wrds
```

This connects to the WRDS cloud server (`wrds-cloud-sshkey.wharton.upenn.edu`) via the `~/.ssh/config` host alias.

## WRDS Paths

- **Home directory:** `~` (on WRDS)
- **Scratch directory:** `~/scratch` (symlink — see CLAUDE.md setup instructions)

All SSH commands use single quotes to avoid local shell expansion. Paths like `~/scratch/` expand on the remote side.

## Running Commands on WRDS

### Interactive Session

For quick commands or testing:

```bash
ssh wrds "command_here"
```

### Running SAS Code

**IMPORTANT:** On WRDS Cloud, you cannot run `sas` directly. You must use `qsas` which submits jobs to the Grid Engine queue. Jobs run asynchronously.

**Step 1: Create the SAS program file on WRDS:**
```bash
ssh wrds 'cat > ~/scratch/myprogram.sas << EOF
options nonotes nosource;
proc contents data=crsp.dsf; run;
EOF'
```

**Step 2: Submit the job:**
```bash
ssh wrds 'qsas ~/scratch/myprogram.sas'
```
This returns immediately with a job ID (e.g., `Your job 12345678 ("myprogram.sas") has been submitted`).

**Step 3: Wait for completion and check output:**
```bash
# Check if job is still running
ssh wrds 'qstat -u $(whoami)'

# Once complete, check the log for errors
ssh wrds 'tail -50 ~/scratch/myprogram.log'

# View the listing output
ssh wrds 'cat ~/scratch/myprogram.lst'
```

**Output files:** SAS creates `.log` and `.lst` files in the same directory as the `.sas` file.

**NOTE:** The `-sync y` option does NOT work on WRDS Cloud. Jobs are always asynchronous. Use `sleep` or poll `qstat` to wait for completion.

### Running SQL Queries (PostgreSQL)

Use `psql` directly with `~/.pgpass` for automatic authentication:
```bash
# Single query
psql service=wrds \
    -c "SELECT * FROM crsp.dsf WHERE date > '2025-01-01' LIMIT 10;"

# Output to CSV
psql service=wrds \
    -c "COPY (SELECT * FROM optionm.securd LIMIT 100) TO STDOUT WITH CSV HEADER" > output.csv
```

**Via SSH (fallback):**
```bash
ssh wrds "psql -h wrds-pgdata.wharton.upenn.edu -d wrds -c 'SELECT * FROM crsp.dsf LIMIT 10;'"
```

### Running Python Code

```bash
ssh wrds 'qpython ~/myscript.py'
```

## File Transfer

### Upload files to WRDS

```bash
scp local_file.sas wrds:~/scratch/
```

### Download files from WRDS

```bash
scp wrds:~/scratch/results.csv ./
```

### Bulk transfer with rsync

```bash
rsync -avz wrds:~/scratch/output/ ./local_output/
```

## WRDS Directory Structure

| Path | Purpose | Notes |
|------|---------|-------|
| `~` | Home directory | Permanent storage, limited quota |
| `~/scratch` | Scratch space (symlink) | Large temporary storage, auto-deleted after 48 hours |
| `/wrds/` | Data libraries | SAS libraries for all WRDS databases |

## Common SAS Libraries on WRDS

| Library | Database |
|---------|----------|
| `crsp` | CRSP Stock/Index |
| `comp` | Compustat |
| `optionm` | OptionMetrics |
| `taq` | TAQ Monthly |
| `taqmsec` | TAQ Millisecond |
| `ibes` | I/B/E/S |
| `tfn` | Thomson Reuters |
| `wrdsapps` | WRDS-created linking tables |

## Best Practices

### 1. Use Scratch Space for Large Files
Always write large intermediate files to `~/scratch/` rather than home directory.

### 2. Check Job Status
After submitting a batch job:
```bash
ssh wrds "qstat"
```

### 3. Use Screen for Long Sessions
For long-running interactive sessions:
```bash
ssh wrds "screen -S mysession"
```

Detach with `Ctrl+A, D`. Reattach with:
```bash
ssh wrds "screen -r mysession"
```

### 4. Download Only Processed Results
Never download raw WRDS data. Process on the server and download only aggregated results.

### 5. Compress Before Transfer
```bash
ssh wrds 'gzip ~/scratch/large_file.csv'
scp wrds:~/scratch/large_file.csv.gz ./
```

## Example Workflow

**Option A: Upload existing SAS file**
```bash
# 1. Upload SAS program
scp analysis.sas wrds:~/scratch/

# 2. Submit job (returns immediately)
ssh wrds 'qsas ~/scratch/analysis.sas'

# 3. Wait and check job status
ssh wrds 'sleep 60 && qstat -u $(whoami)'

# 4. Check log for errors
ssh wrds 'tail -50 ~/scratch/analysis.log'

# 5. View results or download
ssh wrds 'cat ~/scratch/analysis.lst'
scp wrds:~/scratch/results.csv ./
```

**Option B: Create and run SAS code remotely**
```bash
# 1. Create SAS file via heredoc
ssh wrds 'cat > ~/scratch/analysis.sas << EOF
options nonotes nosource;
proc sql;
    create table out as
    select * from crsp.dsf where date > "01JAN2025"d;
quit;
proc export data=out outfile="~/scratch/results.csv" dbms=csv replace; run;
EOF'

# 2. Submit and wait
ssh wrds 'qsas ~/scratch/analysis.sas'
ssh wrds 'sleep 90 && grep -E "ERROR|WARNING|NOTE:.*created" ~/scratch/analysis.log'

# 3. Download results
scp wrds:~/scratch/results.csv ./
```

## Troubleshooting

**Connection timeout:**
- WRDS may be under maintenance; check https://wrds-www.wharton.upenn.edu/

**Permission denied:**
- Verify SSH key is properly configured
- Check that WRDS account is active

**Job stuck in queue:**
- Check queue status: `ssh wrds "qstat -u username"`
- Consider using off-peak hours for large jobs

**Out of disk space:**
- Clean up scratch: `ssh wrds 'rm -rf ~/scratch/temp*'`
- Check quota: `ssh wrds "quota -s"`
