"""Validate TAQ SAS metadata CSVs and write compact catalog summaries.

Run with uv; standard library only. This script makes no network connections.
"""

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return [{key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(stream)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("catalog/taq"))
    parser.add_argument("--run", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    paths = {suffix: args.catalog / f"{args.run}_{suffix}.csv"
             for suffix in ("libraries", "members", "layout_map", "layout_columns", "validation")}
    for suffix in ("hash_buffer_probe", "hash_buffer_validation"):
        path = args.catalog / f"{args.run}_{suffix}.csv"
        if path.exists():
            paths[suffix] = path
    data = {suffix: read_csv(path) for suffix, path in paths.items()}
    raw_log = args.log.read_text(errors="replace")
    marker = "NOTE: AUTOEXEC processing completed."
    assert marker in raw_log
    startup_log, task_log = raw_log.split(marker, 1)
    errors = re.findall(r"(?m)^ERROR(?:\s+\d+(?:-\d+)?)?:.*$", raw_log)
    warnings = re.findall(r"(?m)^WARNING:.*$", raw_log)
    startup_warnings = re.findall(r"(?m)^WARNING:.*$", startup_log)
    task_warnings = re.findall(r"(?m)^WARNING:.*$", task_log)
    assert not errors, errors
    assert not task_warnings, task_warnings
    # Concurrent SAS sessions can fall back to the WORK registry. Preserve the
    # startup warning, but do not mistake it for a schema/extraction warning.
    assert all(w.startswith("WARNING: Unable to copy SASUSER registry to WORK registry.")
               for w in startup_warnings), startup_warnings
    assert "TAQ_METADATA_INVENTORY_COMPLETE SYSCC=0" in raw_log
    assert not data["validation"], data["validation"][:10]
    hash_probe_summary = None
    if "hash_buffer_probe" in data:
        probes = data["hash_buffer_probe"]
        assert len(probes) == 16
        assert all(row["matches"] == "1" for row in probes)
        assert {int(row["buffer_length"]) for row in probes} == {224, 256}
        assert len(data["hash_buffer_validation"]) == 2
        for row in data["hash_buffer_validation"]:
            assert (row["test_count"], row["distinct_original"],
                    row["distinct_explicit"], row["mismatch_count"]) == ("8", "8", "8", "0")
        hash_probe_summary = {
            "cases": 16,
            "explicit_buffer_mismatches": 0,
            "field_sensitivity": "all seven metadata fields, initial and subsequent chain steps",
            "nonblank_buffer_lengths": [224, 256],
        }

    key = lambda row: (row["libname"], row["memname"])
    members = {key(row): row for row in data["members"]}
    layouts = {key(row): row for row in data["layout_map"]}
    assert len(members) == len(data["members"]), "Duplicate member keys"
    assert len(layouts) == len(data["layout_map"]), "Duplicate layout-map keys"
    assert members.keys() == layouts.keys(), "Members without layouts or vice versa"
    columns = defaultdict(list)
    for row in data["layout_columns"]:
        columns[row["layout_id"]].append(row)
    for layout_id, rows in columns.items():
        positions = [int(row["varnum"]) for row in rows]
        assert positions == list(range(1, len(rows) + 1)), (layout_id, positions)
        assert len({row["name"] for row in rows}) == len(rows), layout_id
    for member_key, row in members.items():
        layout = layouts[member_key]
        assert int(row["nvar"]) == int(layout["column_count"])
        assert int(row["nvar"]) == len(columns[layout["layout_id"]])

    families = defaultdict(list)
    for member_key, row in members.items():
        match = re.fullmatch(r"(.+)_(\d{8}|\d{6}|\d{4})", row["memname"])
        family = match.group(1) if match else row["memname"]
        member_period = match.group(2) if match else None
        families[(row["libname"], family)].append((member_key, member_period))
    family_rows = []
    for (library, family), rows in sorted(families.items()):
        periods = sorted(period for _, period in rows if period)
        family_rows.append({
            "sas_library": library,
            "member_family": family,
            "member_count": len(rows),
            "unique_layout_count": len({layouts[k]["layout_id"] for k, _ in rows}),
            "filename_period_min": periods[0] if periods else None,
            "filename_period_max": periods[-1] if periods else None,
            "first_member": min(k[1] for k, _ in rows),
            "last_member": max(k[1] for k, _ in rows),
            "min_columns": min(int(members[k]["nvar"]) for k, _ in rows),
            "max_columns": max(int(members[k]["nvar"]) for k, _ in rows),
            "access_evidence": "SAS dictionary.tables and dictionary.columns metadata",
        })
    with (args.catalog / "families.jsonl").open("w", encoding="utf-8") as stream:
        for row in family_rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")

    # Keep task-specific log evidence; omit autoexec's unrelated library inventory
    # and replace the account-specific home path in the retained task log.
    task_log = re.sub(r"/home/[^/\s]+/[^/\s]+", "<WRDS_HOME>", task_log)
    task_log = re.sub(r"Owner Name=[^,\n]+,Group Name=[^,\n]+",
                      "Owner Name=<ACCOUNT>,Group Name=<GROUP>", task_log)
    (args.catalog / f"{args.run}_task.log").write_text(task_log, encoding="utf-8")
    library_counts = defaultdict(int)
    for library, _ in members:
        library_counts[library] += 1
    version_match = re.search(r"(?m)^NOTE: SAS \(r\) Proprietary Software.*$", raw_log)
    source_sas = Path(__file__).with_name(f"{args.run}.sas")
    summary = {
        "sas_job_id": args.job_id,
        "run_basename": args.run,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection_date": "2026-10-05",
        "collection_scope": ("three named TAQMSEC members and synthetic hash checks"
                             if hash_probe_summary else "four assigned TAQ libraries"),
        "status": "complete_metadata_inventory",
        "sas_version": version_match.group(0).removeprefix("NOTE: ").strip() if version_match else None,
        "program_sha256": hashlib.sha256(source_sas.read_bytes()).hexdigest() if source_sas.exists() else None,
        "member_count": len(members),
        "library_member_counts": dict(sorted(library_counts.items())),
        "family_count": len(family_rows),
        "distinct_layout_count": len(columns),
        "unique_layout_column_rows": len(data["layout_columns"]),
        "expanded_column_count": sum(int(row["nvar"]) for row in members.values()),
        "validation_mismatch_count": len(data["validation"]),
        "sas_errors": errors,
        "sas_warnings": warnings,
        "sas_startup_warnings": startup_warnings,
        "sas_task_warnings": task_warnings,
        "hash_probe_validation": hash_probe_summary,
        "raw_csv_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in paths.values()},
        "limits": [
            "Metadata only; no TAQ observation rows were read.",
            "A filename period is not validated observation coverage.",
            "NOBS is SAS header metadata, not a newly counted number of rows.",
            "Catalog metadata visibility does not prove row-level read permission.",
            "Concatenated SAS aliases can shadow duplicate physical members.",
            "An old filename range does not establish provider retirement.",
        ],
    }
    (args.catalog / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items()
                      if key not in ("raw_csv_sha256", "limits")}, indent=2))


if __name__ == "__main__":
    main()
