#!/usr/bin/env python3
"""Collect WRDS catalog metadata through psql; never inspect credentials.

Run via uv run --no-project python scripts/wrds_catalog/collect.py PHASE.
No third-party packages, research-observation scans, SQL over SSH, or WRDS
Python client. SQL source, command flags, timestamps, and checksums are saved.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import fcntl
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = Path(__file__).resolve().parent
OUT = ROOT / 'catalog' / 'discovery'


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def artifact_path(path):
    """Keep repository-relative provenance, allowing independent snapshot roots."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def command(timeout=60000):
    conn = ('service=wrds connect_timeout=10 options='
            '-cdefault_transaction_read_only=on\\ -cstatement_timeout='
            + str(timeout) + '\\ -clock_timeout=2000')
    return ['psql', conn, '-X', '-w', '-q', '-t', '-A', '-v', 'ON_ERROR_STOP=1', '-P', 'pager=off']


def load_jsonl(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as source:
        for line in source:
            if line.strip():
                yield json.loads(line)


def manifest_event(phase, details):
    path = OUT / 'manifest.json'
    with (OUT / '.manifest.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        manifest = json.loads(path.read_text()) if path.exists() else {
            'format_version': 1,
            'service': 'wrds',
            'scope': 'Visible non-system PostgreSQL relation metadata; no research observation scans',
            'access_semantics': 'ACL flags and accepted zero-row planning probes do not prove data-return access or completeness',
            'taq_semantics': 'PostgreSQL metadata only; access probing and extraction use the separate SAS workflow',
            'events': []}
        manifest['events'].append({'phase': phase, **details})
        manifest['updated_at'] = now()
        path.write_text(json.dumps(manifest, indent=2) + '\n')


def collect(query, target, variables=None, timeout=60000):
    """Preserve complete valid output; failed output stays .partial for diagnosis."""
    if target.exists():
        raise RuntimeError(f'Refusing to overwrite {target}; use an explicit new snapshot')
    query_bytes = query.read_bytes()
    query_hash = hashlib.sha256(query_bytes).hexdigest()
    archive = OUT / 'queries' / (query.stem + '-' + query_hash[:16] + '.sql')
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists() and archive.read_bytes() != query_bytes:
        raise RuntimeError(f'Archived SQL differs from source: {archive}')
    if not archive.exists():
        archive.write_bytes(query_bytes)
    started = now()
    partial = target.with_name(target.name + '.partial')
    args = command(timeout)
    for name, value in (variables or {}).items():
        args += ['-v', name + '=' + value]
    args += ['-f', str(query)]
    records = 0
    with tempfile.TemporaryFile(mode='w+t') as errors:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=errors, text=True)
        assert process.stdout is not None
        opener = gzip.open if target.suffix == '.gz' else open
        try:
            with opener(partial, 'wt', encoding='utf-8') as destination:
                for line in process.stdout:
                    if not line.strip():
                        continue
                    json.loads(line)  # fail closed on diagnostics mixed with JSON
                    destination.write(line)
                    records += 1
            exit_code = process.wait(timeout=5)
        except BaseException:
            process.kill()
            process.wait()
            raise
        errors.seek(0)
        error_text = errors.read()
    details = {'started_at': started, 'finished_at': now(), 'query': artifact_path(query),
               'query_sha256': query_hash, 'archived_query': artifact_path(archive),
               'variables': variables or {}, 'records': records, 'exit_code': exit_code,
               'statement_timeout_ms': timeout, 'output': artifact_path(target),
               'error': error_text.strip() or None}
    if exit_code == 0:
        partial.rename(target)
        details['output_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest_event('collection', details)
    if exit_code:
        raise RuntimeError(error_text.strip())
    print(dump({'output': artifact_path(target), 'records': records}), flush=True)
    return records


def metadata():
    collect(SQL_DIR / 'relations.sql', OUT / 'relations.jsonl.gz')
    collect(SQL_DIR / 'dependencies.sql', OUT / 'dependencies.jsonl.gz')


def columns(prototype=False):
    schemas = list(load_jsonl(OUT / 'schemas.jsonl'))
    if prototype:
        schemas = [row for row in schemas if row['schema_name'] in ('crsp', 'comp', 'optionm')]
    batches = OUT / ('column-prototype' if prototype else 'column-batches')
    batches.mkdir(exist_ok=True)
    # Limit each batch by metadata relation count. Large individual schemas
    # stand alone; no research rows are read by the catalog query.
    groups, group, total = [], [], 0
    for row in schemas:
        if group and total + row['relation_count'] > 2500:
            groups.append(group)
            group, total = [], 0
        group.append(row['schema_name'])
        total += row['relation_count']
    if group:
        groups.append(group)
    for index, schema_group in enumerate(groups):
        target = batches / f'{index:04d}.jsonl.gz'
        if target.exists():
            continue
        collect(SQL_DIR / 'columns.sql', target,
                {'catalog_schemas': dump(schema_group)}, timeout=60000)
    target = OUT / ('column-layouts-prototype.jsonl.gz' if prototype else 'column-layouts.jsonl.gz')
    if target.exists():
        raise RuntimeError(f'Refusing to overwrite {target}')
    layout_count, relations, total_columns = 0, set(), 0
    with gzip.open(target.with_name(target.name + '.partial'), 'wt', encoding='utf-8') as destination:
        for index in range(len(groups)):
            for row in load_jsonl(batches / f'{index:04d}.jsonl.gz'):
                row['layout_id'] = hashlib.sha256(dump(row['columns']).encode()).hexdigest()
                destination.write(dump(row) + '\n')
                layout_count += 1
                for oid in row['relation_oids']:
                    if oid in relations:
                        raise RuntimeError(f'Duplicate relation layout: {oid}')
                    relations.add(oid)
                    total_columns += len(row['columns'])
    expected = sum(row['relation_count'] for row in schemas)
    if len(relations) != expected:
        raise RuntimeError(f'Column coverage mismatch: {len(relations)} != {expected}')
    target.with_name(target.name + '.partial').rename(target)
    details = {'finished_at': now(), 'output': artifact_path(target),
               'layouts': layout_count, 'relations': len(relations), 'columns': total_columns,
               'schemas': len(schemas), 'prototype': prototype}
    manifest_event('column_layouts', details)
    print(dump(details), flush=True)


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('schemas', 'prototype', 'metadata', 'columns-prototype', 'columns'))
    parser.add_argument('--output', type=Path, default=OUT,
                        help='Snapshot directory; choose a new dated directory for a refresh.')
    args = parser.parse_args()
    OUT = args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == 'schemas':
        collect(SQL_DIR / 'schema-summary.sql', OUT / 'schemas.jsonl')
    elif args.phase == 'prototype':
        collect(SQL_DIR / 'prototype.sql', OUT / 'relations-prototype.jsonl')
    elif args.phase == 'metadata':
        metadata()
    else:
        columns(args.phase == 'columns-prototype')


if __name__ == '__main__':
    main()
