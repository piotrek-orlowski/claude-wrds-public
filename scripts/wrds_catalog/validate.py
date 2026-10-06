#!/usr/bin/env python3
"""Validate complete catalog coverage and summarize actual evidence scope."""
from collections import Counter, defaultdict
import argparse
import hashlib
import json
from pathlib import Path

import collect as collector
from collect import OUT, dump, load_jsonl, manifest_event, now


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT,
                        help='Existing snapshot directory to validate; raw collection files are preserved.')
    args = parser.parse_args()
    OUT = args.output.resolve()
    collector.OUT = OUT
    schemas = {r['schema_name']: r for r in load_jsonl(OUT / 'schemas.jsonl')}
    relations = {}
    keys = set()
    schema_counts = Counter()
    for row in load_jsonl(OUT / 'relations.jsonl.gz'):
        oid = row['relation_oid']
        key = (row['schema_name'], row['relation_name'])
        assert oid not in relations and key not in keys, ('duplicate_relation', oid, key)
        relations[oid] = row
        keys.add(key)
        schema_counts[row['schema_name']] += 1
    assert set(schema_counts) == set(schemas), 'schema coverage mismatch'
    for name, count in schema_counts.items():
        assert count == schemas[name]['relation_count'], ('relation_count_mismatch', name)

    relation_layout = {}
    layouts = set()
    total_columns = 0
    for row in load_jsonl(OUT / 'column-layouts.jsonl.gz'):
        assert row['layout_id'] == hashlib.sha256(dump(row['columns']).encode()).hexdigest()
        layouts.add(row['layout_id'])
        names = [c['name'] for c in row['columns']]
        ordinals = [c['ordinal'] for c in row['columns']]
        assert len(set(names)) == len(names), 'duplicate column name'
        assert ordinals == sorted(set(ordinals)) and all(o > 0 for o in ordinals)
        for oid in row['relation_oids']:
            assert oid in relations and oid not in relation_layout, ('column_relation', oid)
            assert relations[oid]['schema_name'] == row['schema_name']
            relation_layout[oid] = row['layout_id']
            total_columns += len(row['columns'])
    assert set(relation_layout) == set(relations), 'incomplete column coverage'

    edges, external_edges = set(), 0
    for row in load_jsonl(OUT / 'dependencies.jsonl.gz'):
        source, target = row['source_oid'], row['target_oid']
        assert source in relations, ('dependency_source', source)
        assert (source, target) not in edges and source != target, 'duplicate/self dependency'
        edges.add((source, target))
        if target not in relations:
            assert row['target_schema'].startswith('pg_') or row['target_schema'] == 'information_schema'
            external_edges += 1

    status_counts = Counter()
    schema_statuses = defaultdict(Counter)
    probes = set()
    for row in load_jsonl(OUT / 'access-probes.jsonl'):
        oid = row['relation_oid']
        assert oid in relations and oid not in probes, ('probe_relation', oid)
        assert row['schema_name'] == relations[oid]['schema_name']
        assert row['relation_name'] == relations[oid]['relation_name']
        probes.add(oid)
        status_counts[row['status']] += 1
        schema_statuses[row['schema_name']][row['status']] += 1
        if row['status'] == 'planning_accepted':
            assert row['zero_row_status'] == 'accepted'
            assert row['guard_status'] in ('accepted', 'not_present')
        elif row['status'] == 'not_probed_no_schema_usage':
            assert relations[oid]['schema_usage'] is False
        elif row['status'] == 'not_probed_no_select_privilege':
            assert relations[oid]['select_privilege'] is False
        elif row['status'] == 'taq_sas_required':
            assert row['schema_name'].startswith('taq')
    assert probes == set(relations), 'incomplete access coverage'

    with (OUT / 'schema-access-summary.jsonl').open('w') as output:
        for name in sorted(schemas):
            output.write(dump({**schemas[name], 'probe_statuses': dict(schema_statuses[name])}) + '\n')
    report = {
        'validated_at': now(), 'schemas': len(schemas), 'relations': len(relations),
        'columns': total_columns, 'globally_distinct_column_layouts': len(layouts),
        'dependency_edges': len(edges), 'dependencies_on_system_relations': external_edges,
        'access_statuses': dict(status_counts),
        'meaning': 'Structural coverage validated; planning acceptance and alias-guard success do not prove data-return behavior or current-product lifecycle',
        'input_sha256': {name: hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in (
            'schemas.jsonl', 'relations.jsonl.gz', 'dependencies.jsonl.gz',
            'column-layouts.jsonl.gz', 'access-probes.jsonl')}}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    manifest_event('integrity_validation', report)
    print(dump(report))


if __name__ == '__main__':
    main()
