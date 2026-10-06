#!/usr/bin/env python3
"""Bounded, resumable metadata/zero-row access probes. Never return data values.

ACL, zero-row planning, exact observed alias-guard checks, and deprecated
no-FROM error wrappers are separate evidence. Normal research rows are never
queried. TAQ PostgreSQL probes are excluded; use the independent SAS workflow.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

import collect as collector
from collect import OUT, artifact_path, command, dump, load_jsonl, manifest_event, now

GUARD = re.compile(r"has_table_privilege\('((?:[^']|'')*)'::text,\s*'SELECT'::text\)", re.I)
ERROR_WRAPPER = re.compile(r'\b[a-zA-Z0-9_]+_err\s*\(', re.I)


def sql_literal(value):
    return "'" + value.replace("'", "''") + "'"


def make_sql(rows):
    # Relation names and observed guard arguments are data values; identifiers
    # are quoted with PostgreSQL format(%I) and never interpolated as raw SQL.
    payload = sql_literal(dump(rows))
    body = '''
DECLARE
    item jsonb;
    guard text;
    permitted boolean;
    result jsonb;
    message text;
    code text;
    checked timestamptz;
BEGIN
    FOR item IN SELECT value FROM jsonb_array_elements(PAYLOAD::jsonb)
    LOOP
        checked := clock_timestamp();
        result := jsonb_build_object(
            'relation_oid', item->'relation_oid',
            'schema_name', item->>'schema_name',
            'relation_name', item->>'relation_name',
            'checked_at', checked,
            'method', 'select_limit0_and_observed_alias_guards',
            'guard_relations', item->'guard_relations',
            'status', 'planning_accepted',
            'zero_row_status', 'not_run',
            'guard_status', 'not_present',
            'runtime_wrapper_status', 'not_run',
            'sqlstate', NULL, 'error', NULL);
        BEGIN
            EXECUTE format('SELECT * FROM %I.%I LIMIT 0',
                           item->>'schema_name', item->>'relation_name');
            result := result || jsonb_build_object('zero_row_status', 'accepted');
            IF jsonb_array_length(item->'guard_relations') > 0 THEN
                result := result || jsonb_build_object('guard_status', 'accepted');
            END IF;
            FOR guard IN SELECT jsonb_array_elements_text(item->'guard_relations')
            LOOP
                BEGIN
                    SELECT pg_catalog.has_table_privilege(guard, 'SELECT') INTO permitted;
                    IF NOT permitted THEN
                        result := result || jsonb_build_object(
                            'status', 'guard_denied', 'guard_status', 'false',
                            'error', 'Observed alias privilege guard returned false');
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
                    result := result || jsonb_build_object(
                        'status', 'guard_denied', 'guard_status', 'error',
                        'sqlstate', code, 'error', message);
                END;
            END LOOP;
            IF (item->>'error_wrapper')::boolean THEN
                BEGIN
                    EXECUTE format('SELECT * FROM %I.%I LIMIT 1',
                                   item->>'schema_name', item->>'relation_name');
                    result := result || jsonb_build_object(
                        'method', 'select_limit0_and_error_wrapper_limit1',
                        'runtime_wrapper_status', 'accepted');
                EXCEPTION WHEN OTHERS THEN
                    GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
                    result := result || jsonb_build_object(
                        'method', 'select_limit0_and_error_wrapper_limit1',
                        'status', 'runtime_error', 'runtime_wrapper_status', 'error',
                        'sqlstate', code, 'error', message);
                END;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS message = MESSAGE_TEXT, code = RETURNED_SQLSTATE;
            result := result || jsonb_build_object(
                'status', CASE WHEN code = '42501' THEN 'permission_denied' ELSE 'planning_error' END,
                'zero_row_status', 'error', 'sqlstate', code, 'error', message);
        END;
        result := result || jsonb_build_object(
            'duration_ms', round(extract(epoch from (clock_timestamp()-checked))*1000, 3));
        RAISE NOTICE 'CATALOG_PROBE %', result::text;
    END LOOP;
END
'''.replace('PAYLOAD', payload)
    tag = '$catalog_' + hashlib.sha256(body.encode()).hexdigest()[:16] + '$'
    return 'DO ' + tag + body + tag + ';\n'


def probe_batch(rows, batch_dir, output, completed, index):
    sql = make_sql(rows)
    stem = f'{index[0]:05d}'
    index[0] += 1
    query = batch_dir / (stem + '.sql')
    query.write_text(sql)
    started = now()
    run = subprocess.run(command(timeout=60000) + ['-f', str(query)],
                         text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=75)
    # Preserve psql diagnostics without exposing the local checkout path.
    stderr = run.stderr.replace('psql:' + str(query) + ':',
                                'psql:' + artifact_path(query) + ':')
    (batch_dir / (stem + '.stderr.txt')).write_text(stderr)
    found = 0
    for line in stderr.splitlines():
        if 'CATALOG_PROBE ' not in line:
            continue
        row = json.loads(line.split('CATALOG_PROBE ', 1)[1])
        if row['relation_oid'] in completed:
            raise RuntimeError('Probe produced duplicate relation evidence')
        output.write(dump(row) + '\n')
        completed.add(row['relation_oid'])
        found += 1
    output.flush()
    manifest_event('access_batch', {
        'started_at': started, 'finished_at': now(),
        'query': artifact_path(query),
        'query_sha256': hashlib.sha256(query.read_bytes()).hexdigest(),
        'stderr': artifact_path(batch_dir / (stem + '.stderr.txt')),
        'requested': len(rows), 'recorded': found, 'exit_code': run.returncode})
    remaining = [row for row in rows if row['relation_oid'] not in completed]
    if remaining:
        if len(rows) == 1:
            row = {k: rows[0][k] for k in ('relation_oid', 'schema_name', 'relation_name')}
            row.update(method='select_limit0_batch', status='probe_incomplete', checked_at=now(),
                       sqlstate=None, error=stderr[-3000:])
            output.write(dump(row) + '\n')
            output.flush()
            completed.add(row['relation_oid'])
        else:
            midpoint = max(1, len(remaining) // 2)
            probe_batch(remaining[:midpoint], batch_dir, output, completed, index)
            if remaining[midpoint:]:
                probe_batch(remaining[midpoint:], batch_dir, output, completed, index)


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--prototype', action='store_true')
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--output', type=Path, default=OUT,
                        help='Existing metadata snapshot directory; access probes resume in this directory.')
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error('--batch-size must be positive')
    OUT = args.output.resolve()
    collector.OUT = OUT
    suffix = '-prototype' if args.prototype else ''
    path = OUT / ('access-probes' + suffix + '.jsonl')
    batch_dir = OUT / ('access-batches' + suffix)
    batch_dir.mkdir(exist_ok=True)
    completed = {row['relation_oid'] for row in load_jsonl(path)} if path.exists() else set()
    prototype_keys = {('comp','funda'), ('crsp','msf_v2'), ('crsp','ccmxpf_lnkhist'),
                      ('optionm','opprcd2024'), ('crspa','acti'),
                      ('altrata','eur_announce'), ('crsp_a_stock','msf_v2'),
                      ('crsp_a_ccm','ccmxpf_lnkhist')}
    pending, expected = [], 0
    index = [len(list(batch_dir.glob('*.sql')))]
    with path.open('a', encoding='utf-8') as output:
        for row in load_jsonl(OUT / 'relations.jsonl.gz'):
            if args.prototype and (row['schema_name'], row['relation_name']) not in prototype_keys:
                continue
            expected += 1
            if row['relation_oid'] in completed:
                continue
            base = {k: row[k] for k in ('relation_oid', 'schema_name', 'relation_name')}
            skip = ('taq_sas_required' if row['schema_name'].startswith('taq')
                    else 'not_probed_no_schema_usage' if not row['schema_usage']
                    else 'not_probed_no_select_privilege' if not row['select_privilege'] else None)
            if skip:
                base.update(method='catalog_privileges_only', status=skip, checked_at=now(),
                            sqlstate=None, error=None)
                output.write(dump(base) + '\n')
                completed.add(row['relation_oid'])
                continue
            definition = row.get('view_definition') or ''
            base['guard_relations'] = sorted({s.replace("''", "'") for s in GUARD.findall(definition)})
            base['error_wrapper'] = bool(ERROR_WRAPPER.search(definition)
                                         and not re.search(r'\bFROM\b', definition, re.I))
            pending.append(base)
        output.flush()
        for start in range(0, len(pending), args.batch_size):
            probe_batch(pending[start:start+args.batch_size], batch_dir, output, completed, index)
            if start % 1000 == 0:
                print(dump({'probe_progress': min(start+args.batch_size,len(pending)),
                            'to_probe': len(pending), 'completed_records': len(completed)}), flush=True)
    if len(completed) != expected:
        raise RuntimeError(f'Probe coverage mismatch: {len(completed)} != {expected}')
    counts = Counter(row['status'] for row in load_jsonl(path))
    details = {'finished_at': now(), 'prototype': args.prototype,
               'output': artifact_path(path), 'relations': expected, 'statuses': dict(counts)}
    manifest_event('access_summary', details)
    print(dump(details), flush=True)


if __name__ == '__main__':
    main()
