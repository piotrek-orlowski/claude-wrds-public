---
name: wrds-ssh
description: Submit and monitor TAQ SAS jobs on WRDS through SSH and transfer their programs, logs, and results. Use for TAQ-related SAS schema probes and batch operations only.
---

# TAQ SAS job operations

Use the configured `wrds` SSH alias for TAQ SAS work only: submission, related
SAS schema probes, monitoring, and transfer. Use `wrds-taq` for product knowledge,
filters, and SAS analysis. Other WRDS databases use direct local PostgreSQL via
`wrds-psql-agent`; do not use SSH for PostgreSQL or remote Python.

Do not read credential files, including `~/.ssh/config`, without explicit user
permission. The SSH client may use the existing configuration normally. If
authentication or MFA needs user input, report the blocker instead of reading
secrets or repeatedly retrying. Setup instructions belong in the repository
README; do not modify authentication or scratch configuration during an extraction.

## Submit a prototype

Write the SAS program locally and prototype on one asset and at most one week.
Keep SAS notes enabled so the log retains row counts and diagnostics. Mirror
the local directory under the preconfigured remote `~/scratch` symlink.
Use a unique program basename per run so home-directory logs do not collide.

Example: local `data/taq-iv/taq_probe_20241007_aapl.sas`.

```bash
ssh wrds 'mkdir -p ~/scratch/taq-iv'
scp data/taq-iv/taq_probe_20241007_aapl.sas wrds:~/scratch/taq-iv/
ssh wrds 'qsas ~/scratch/taq-iv/taq_probe_20241007_aapl.sas'
```

`qsas` submits asynchronously; capture its job ID. Do not invoke `sas` directly
or add `-sync y`. Default logs go to **`~/taq_probe_20241007_aapl.log` in the remote
home directory**, not the scratch directory containing the program. The SAS
program determines the CSV output path. Do not assume a listing file exists.

## Monitor and retrieve

```bash
ssh wrds 'qstat -u $(whoami)'
ssh wrds 'tail -80 ~/taq_probe_20241007_aapl.log'
```

Poll the recorded job rather than sleeping for a fixed duration and assuming
success. Disappearance from the queue alone is not success: inspect the full
log for errors and warnings, confirm output completion, and validate counts,
keys, and missing values. Logs may appear only after the job starts.

```bash
scp wrds:~/taq_probe_20241007_aapl.log data/taq-iv/
scp wrds:~/scratch/taq-iv/taq_probe_20241007_aapl.csv data/taq-iv/
```

Process TAQ in place and transfer the requested processed or aggregated result.
For a large completed output, optional compression preserves the original:

```bash
ssh wrds 'gzip -c ~/scratch/taq-iv/taq_probe_20241007_aapl.csv > ~/scratch/taq-iv/taq_probe_20241007_aapl.csv.gz'
scp wrds:~/scratch/taq-iv/taq_probe_20241007_aapl.csv.gz data/taq-iv/
```

Use single quotes around remote commands so `~` and `$(whoami)` expand remotely.
Retain local programs, logs, and result provenance. Scratch is temporary; the
inherited notes record a 48-hour cleanup policy, so retrieve completed results
promptly and verify current retention if a workflow depends on it.

## Failures

- Connection or authentication failure: report the exact sanitized error and
  stop before submission. Do not treat this as a SAS or schema failure.
- A queued job: use its ID and `qstat` status; do not resubmit it solely because
  it has not started.
- Missing output: inspect the home-directory log and the output path specified
  in SAS before retrying.
- Insufficient storage: report the location and affected files. Do not run
  wildcard deletion or remove unrelated scratch outputs.
