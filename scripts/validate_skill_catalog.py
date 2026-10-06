#!/usr/bin/env python3
"""Validate the portable catalog against raw metadata, without a database connection.

Run with ``uv run --no-project python scripts/validate_skill_catalog.py``.
Copies skills to a temporary installation and runs the installed CLI from an
unrelated working directory. Only standard-library modules are required.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def read_rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        yield from (json.loads(line) for line in stream)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def source_urls(value):
    if isinstance(value, dict):
        return set().union(*(source_urls(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(source_urls(item) for item in value))
    return {value} if isinstance(value, str) and value.startswith(('https://', 'http://')) else set()


def expected_lifecycles(raw_relations, raw_dependencies, products, policies, overrides):
    """Reconstruct lifecycle/product identity from source evidence, not build output."""
    names = {f"{row['schema_name']}.{row['relation_name']}": oid for oid, row in raw_relations.items()}
    exact = {}
    for rule in overrides:
        for table in rule['tables']:
            exact[f"{rule['schema']}.{table}"] = rule
    excluded = {'retired', 'superseded_copy', 'stale_alias'}
    resolved = {}

    def resolve(name, active=frozenset()):
        if name in resolved:
            return resolved[name]
        if name in active or name not in names:
            return 'unresolved', frozenset()
        oid = names[name]
        schema = raw_relations[oid]['schema_name']
        dependencies = raw_dependencies[oid] - {name}
        rule = exact.get(name, policies['schemas'].get(schema))
        inherited = None
        if rule is not None:
            status = rule['status']
            if 'product_schemas' in rule:
                inherited = frozenset(rule['product_schemas'])
        elif dependencies:
            parent_states = [resolve(dep, active | {name}) for dep in sorted(dependencies)]
            states = {state for state, _ in parent_states}
            status = 'stale_alias' if states & excluded else ('current' if states == {'current'} else 'unresolved')
            inherited = frozenset().union(*(schemas for _, schemas in parent_states))
        elif re.fullmatch(r'taqm_\d{4}', schema) or schema == 'taqmsec':
            status = 'current'
            inherited = frozenset({schema})
        elif schema in products:
            status = 'retired' if 'legacy' in (products[schema].get('update_frequency') or '').lower() else 'current'
            inherited = frozenset({schema})
        elif schema.endswith('_old') and schema[:-4] in products:
            status = 'superseded_copy'
        else:
            status = 'unresolved'
        if inherited is None:
            inherited = frozenset({schema}) if schema in products or status == 'current' else frozenset()
        if status == 'current' and dependencies:
            if any(resolve(dep, active | {name})[0] in excluded for dep in dependencies):
                status = 'stale_alias'
        resolved[name] = status, inherited
        return resolved[name]

    for name in names:
        resolve(name)
    return resolved


def expected_canonical(repo, by_name, lifecycle_states, coverage):
    """Resolve explicit root selection and aliases without importing the builder."""
    decisions = {}
    for filename in ('catalog/canonical-crsp.json', 'catalog/canonical-other.json'):
        require(filename in coverage['inputs'], f'Canonical policy is missing from build provenance: {filename}')
        policy = json.loads((repo / filename).read_text())
        for decision in policy['decisions']:
            name = decision['name']
            require(name in by_name and name not in decisions, f'Unknown or duplicate canonical decision: {name}')
            require(isinstance(decision['canonical'], bool), f'Non-boolean canonical decision: {name}')
            require(isinstance(decision['reason'], str) and decision['reason'].strip(), f'Missing canonical reason: {name}')
            require(isinstance(decision['counterparts'], list) and len(set(decision['counterparts'])) == len(decision['counterparts']),
                    f'Invalid canonical counterparts: {name}')
            require(all(other in by_name and other != name for other in decision['counterparts']),
                    f'Unknown or self-referential canonical counterpart: {name}')
            require(not by_name[name]['dependencies'], f'Canonical policy must select roots, not aliases: {name}')
            require(lifecycle_states[name][0] == 'unresolved', f'Canonical policy changes a resolved lifecycle: {name}')
            if decision['canonical']:
                require(by_name[name]['access'] == 'planning_accepted' and by_name[name]['transport'] == 'psql',
                        f'Explicit canonical selection lacks PostgreSQL preflight: {name}')
            decisions[name] = decision
    resolved = {}

    def resolve(name, active=frozenset()):
        if name in resolved:
            return resolved[name]
        if name in active:
            return False, frozenset()
        row = by_name[name]
        status = lifecycle_states[name][0]
        if status == 'current':
            result = True, frozenset()
        elif status != 'unresolved':
            result = False, frozenset()
        elif name in decisions:
            decision = decisions[name]
            result = decision['canonical'], frozenset(decision['counterparts'])
        elif row['dependencies']:
            parents = [resolve(dep, active | {name}) for dep in row['dependencies']]
            result = all(selected for selected, _ in parents), frozenset().union(*(peers for _, peers in parents))
        else:
            result = False, frozenset()
        resolved[name] = result
        return result

    for name in by_name:
        resolve(name)
    return resolved, decisions


def validate_taq(repo, data, coverage, installed, known_urls, report):
    """Compare SAS members/layouts with the validated, hashed CSV inventory."""
    files = [data / name for name in ('taq-members.jsonl.gz', 'taq-layouts.jsonl.gz', 'taq-summary.json')]
    if not any(path.exists() for path in files):
        require(not coverage.get('taq_sas'), 'Coverage advertises a missing SAS bundle')
        report['sas_validation'] = {'status': 'not_included', 'reason': 'No SAS bundle in this build.'}
        return None
    require(all(path.exists() for path in files), 'Incomplete SAS bundle')
    raw_dir = repo / 'catalog/taq'
    raw_summary = json.loads((raw_dir / 'summary.json').read_text())
    summary = json.loads((data / 'taq-summary.json').read_text())
    require(summary == raw_summary, 'Packaged SAS summary differs from raw inventory')
    require(summary['status'] == 'complete_metadata_inventory' and summary['validation_mismatch_count'] == 0,
            'SAS source inventory has not passed validation')
    for filename, checksum in summary['raw_csv_sha256'].items():
        require(digest(raw_dir / filename) == checksum, f'SAS raw CSV changed: {filename}')

    def raw_csv(suffix):
        path = raw_dir / (summary['run_basename'] + '_' + suffix + '.csv')
        require(path.name in summary['raw_csv_sha256'], f'SAS CSV is not hashed in summary: {suffix}')
        with path.open(newline='', encoding='utf-8') as stream:
            return [{k.lower(): value for k, value in row.items()} for row in csv.DictReader(stream)]

    raw_members = raw_csv('members')
    member_sources = {(row['libname'], row['memname']): row for row in raw_members}
    require(len(member_sources) == len(raw_members), 'Duplicate SAS source member')
    raw_map = raw_csv('layout_map')
    mappings = {(row['libname'], row['memname']): row for row in raw_map}
    require(len(mappings) == len(raw_map) and mappings.keys() == member_sources.keys(), 'SAS layout map coverage mismatch')
    expected_layouts = defaultdict(list)
    for row in raw_csv('layout_columns'):
        expected_layouts[row['layout_id']].append({k: row[k] for k in ('name', 'type', 'length', 'varnum', 'label', 'format', 'informat')})
    layout_rows = list(read_rows(data / 'taq-layouts.jsonl.gz'))
    layouts = {row['layout_id']: row['columns'] for row in layout_rows}
    require(len(layouts) == len(layout_rows) and layouts == expected_layouts, 'SAS column layouts differ from raw CSV metadata')
    for layout, columns in layouts.items():
        require([int(c['varnum']) for c in columns] == list(range(1, len(columns) + 1)), f'SAS column ordering invalid: {layout}')
        require(len({c['name'] for c in columns}) == len(columns), f'Duplicate SAS column name: {layout}')
    libraries = raw_csv('libraries')
    library_names = {row['libname'] for row in libraries}
    require({key[0] for key in member_sources} <= library_names, 'SAS member references an uncollected library')
    require(not raw_csv('validation'), 'SAS validation CSV contains mismatched members')

    members = list(read_rows(data / 'taq-members.jsonl.gz'))
    by_name = {row['name']: row for row in members}
    require(len(by_name) == len(members) == len(member_sources) == summary['member_count'], 'SAS member count mismatch')
    require(set(by_name) == {'.'.join(key) for key in member_sources}, 'SAS member coverage mismatch')
    require((installed / 'wrds-taq/SKILL.md').is_file(), 'SAS catalog owner missing from installation')
    current = {'TAQMSEC', 'TAQMSAMP'}
    names_by_member = defaultdict(list)
    for row in members:
        key = (row['sas_library'], row['member'])
        raw = member_sources[key]
        mapping = mappings[key]
        require(row['layout_id'] == mapping['layout_id'], f'SAS member layout mismatch: {row["name"]}')
        require(row['column_count'] == int(raw['nvar']) == int(mapping['column_count']) == len(layouts[row['layout_id']]),
                f'SAS member column count mismatch: {row["name"]}')
        require(row['label'] == raw['memlabel'] and row['header_nobs'] == raw['nobs'] and row['header_modified_at'] == raw['modate'],
                f'SAS member header metadata mismatch: {row["name"]}')
        require(row['access'] == 'sas_metadata_opened' and row['transport'] == 'sas' and row['skill'] == 'wrds-taq',
                f'SAS access scope changed: {row["name"]}')
        require('not observation' in row['evidence'].lower() and 'row-return' in row['evidence'].lower(),
                f'SAS row-verification limitation omitted: {row["name"]}')
        is_current = row['sas_library'] in current
        require(row['default_eligible'] == is_current and row['lifecycle'] == ('current' if is_current else 'legacy_product'),
                f'SAS default lifecycle mismatch: {row["name"]}')
        require(row['sample'] == (row['sas_library'] in {'TAQMSAMP', 'TAQSAMP'}), f'SAS sample classification mismatch: {row["name"]}')
        require(set(row['sources']) <= known_urls and row['sources'], f'SAS source attribution missing: {row["name"]}')
        names_by_member[row['member'].lower()].append(row['name'])

    counts = dict(Counter(row['sas_library'] for row in members))
    require(counts == summary['library_member_counts'], 'SAS per-library counts differ')
    require(len(layouts) == summary['distinct_layout_count'], 'SAS layout count differs')
    require(sum(map(len, layouts.values())) == summary['unique_layout_column_rows'], 'SAS unique column count differs')
    expanded = sum(row['column_count'] for row in members)
    require(expanded == summary['expanded_column_count'], 'SAS expanded column count differs')
    sas_coverage = coverage['taq_sas']
    require(all(sas_coverage.get(k) == value for k, value in summary.items()), 'SAS coverage summary differs from source')
    require(sas_coverage['current_sas_members'] == sum(row['default_eligible'] for row in members), 'SAS current count differs')
    require(sas_coverage['legacy_sas_members'] == sum(not row['default_eligible'] for row in members), 'SAS legacy count differs')
    report['sas_validation'] = {'status': 'passed', 'members': len(members), 'library_member_counts': counts,
                                'layouts': len(layouts), 'expanded_column_count': expanded,
                                'current_members': sas_coverage['current_sas_members'],
                                'legacy_members': sas_coverage['legacy_sas_members'],
                                'access_scope': 'SAS metadata opened; observations were not verified.'}
    return {'members': by_name, 'layouts': layouts, 'counts': counts, 'names_by_member': names_by_member}


def validate(repo, report):
    package = repo / 'skills/wrds-catalog'
    references = package / 'references'
    tracked = sorted(path for path in package.rglob('*') if path.is_file())
    initial_hashes = {str(path.relative_to(repo)): digest(path) for path in tracked}
    coverage = json.loads((references / 'coverage.json').read_text())
    report['catalog_built_at'] = coverage['built_at']
    report['catalog_input_hashes'] = coverage['inputs']
    for filename, expected in coverage['inputs'].items():
        require(digest(repo / filename) == expected, f'Stale build input: {filename}')

    raw_relations = {str(row['relation_oid']): row for row in read_rows(repo / 'catalog/discovery/relations.jsonl.gz')}
    raw_access = {str(row['relation_oid']): row for row in read_rows(repo / 'catalog/discovery/access-probes.jsonl')}
    raw_dependencies = defaultdict(set)
    for row in read_rows(repo / 'catalog/discovery/dependencies.jsonl.gz'):
        raw_dependencies[str(row['source_oid'])].add(f"{row['target_schema']}.{row['target_relation']}")
    raw_layout_ids = {}
    raw_columns = {}
    for row in read_rows(repo / 'catalog/discovery/column-layouts.jsonl.gz'):
        layout = row['layout_id']
        if layout in raw_columns:
            require(raw_columns[layout] == row['columns'], f'Raw layout hash collision: {layout}')
        raw_columns[layout] = row['columns']
        for oid in row['relation_oids']:
            require(str(oid) not in raw_layout_ids, f'Duplicate raw column assignment: {oid}')
            raw_layout_ids[str(oid)] = layout

    documents = json.loads((repo / 'research/product-docs.json').read_text())
    policies = json.loads((repo / 'catalog/product-policy.json').read_text())
    overrides = json.loads((repo / 'research/current-product-overrides.json').read_text())
    known_urls = source_urls(documents) | source_urls(policies) | source_urls(overrides)
    source_register = repo / 'research/provider-sources.md'
    known_urls.update(re.findall(r'https?://[^\s)\]>]+', source_register.read_text()))
    report['additional_source_evidence_sha256'] = {'research/provider-sources.md': digest(source_register)}
    product_sources = defaultdict(list)
    for page in documents['pages']:
        for product in page['products']:
            product_sources[product['schema']].append((page, product))

    with tempfile.TemporaryDirectory(prefix='wrds-skill-catalog-validation-') as temp:
        temp = Path(temp)
        installed = temp / 'installed/skills'
        shutil.copytree(repo / 'skills', installed)
        unrelated = temp / 'unrelated-working-directory'
        unrelated.mkdir()
        data = installed / 'wrds-catalog/references'
        helper = installed / 'wrds-catalog/scripts/catalog.py'
        for path in tracked:
            relative = path.relative_to(package)
            require(digest(installed / 'wrds-catalog' / relative) == initial_hashes[str(path.relative_to(repo))],
                    f'Copy differs from hashed package: {relative}')

        relations = list(read_rows(data / 'relations.jsonl.gz'))
        by_name = {row['name']: row for row in relations}
        by_oid = {str(row['oid']): row for row in relations}
        require(len(relations) == len(by_name) == len(by_oid), 'Duplicate packaged relation key')
        require(by_oid.keys() == raw_relations.keys(), 'Packaged relation coverage differs from raw catalog')
        layouts = {row['layout_id']: row['columns'] for row in read_rows(data / 'layouts.jsonl.gz')}
        require(layouts.keys() == raw_columns.keys(), 'Packaged layout coverage differs from raw catalog')
        for layout, columns in layouts.items():
            normalized = json.dumps(columns, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            require(hashlib.sha256(normalized.encode()).hexdigest() == layout, f'Invalid layout digest: {layout}')
            require(columns == raw_columns[layout], f'Packaged columns differ from raw metadata: {layout}')

        products = json.loads((data / 'products.json').read_text())
        for schema, product in products.items():
            candidates = product_sources[schema]
            require(candidates, f'Product has no raw provider evidence: {schema}')
            require(any(all(product.get(k) == v for k, v in original.items())
                        and product.get('source_url') in {page.get('url'), page.get('resolved_url')}
                        and product.get('retrieved_at') == page.get('retrieved_at')
                        and product.get('vendor') == page.get('vendor')
                        for page, original in candidates), f'Product facts differ from collected provider evidence: {schema}')

        taq = validate_taq(repo, data, coverage, installed, known_urls, report)

        lifecycle_states = expected_lifecycles(raw_relations, raw_dependencies, products, policies, overrides)
        canonical_states, canonical_decisions = expected_canonical(repo, by_name, lifecycle_states, coverage)
        default_rows = []
        current_rows = []
        unresolved_rows = []
        for row in relations:
            oid = str(row['oid'])
            raw = raw_relations[oid]
            prefix = row['name']
            require(row['name'] == f"{raw['schema_name']}.{raw['relation_name']}", f'Name mismatch: {prefix}')
            require(row['schema'] == raw['schema_name'] and row['table'] == raw['relation_name'], f'Identifier mismatch: {prefix}')
            require(row['comment'] == raw['comment'] and row['kind'] == raw['relation_kind'], f'Relation metadata mismatch: {prefix}')
            require(row['layout_id'] == raw_layout_ids[oid], f'Column layout mismatch: {prefix}')
            require(set(row['dependencies']) == raw_dependencies[oid], f'Dependency mismatch: {prefix}')
            require(all(name in by_name for name in row['dependencies']), f'Dependency absent from package: {prefix}')
            require(row['access'] == raw_access[oid]['status'], f'Access status mismatch: {prefix}')
            require(row['access_checked_at'] == raw_access[oid]['checked_at'], f'Access timestamp mismatch: {prefix}')
            require(row['access_error'] == raw_access[oid]['error'], f'Access error mismatch: {prefix}')
            require(set(row['sources']) <= known_urls, f'Unattributed source URL: {prefix}')
            require(isinstance(row['sample'], bool), f'Invalid sample flag: {prefix}')
            expected_lifecycle, expected_product_schemas = lifecycle_states[prefix]
            require(row['lifecycle'] == expected_lifecycle, f'Lifecycle changed from source evidence: {prefix}')
            require(set(row['product_schemas']) == expected_product_schemas, f'Product ancestry changed: {prefix}')
            expected_sample = any(any(token in schema for token in ('samp', 'smp', 'trial')) or
                                  any(token in (products.get(schema, {}).get('title') or '').lower() for token in ('sample', 'trial'))
                                  for schema in {row['schema'], *expected_product_schemas})
            require(row['sample'] == expected_sample, f'Sample restriction changed: {prefix}')
            expected_selected, expected_counterparts = canonical_states[prefix]
            require(isinstance(row['canonical'], bool) and row['canonical'] == expected_selected,
                    f'Canonical selection differs from policy/dependencies: {prefix}')
            require(isinstance(row['canonical_reason'], str) and row['canonical_reason'].strip(), f'Missing canonical reason: {prefix}')
            require(isinstance(row['canonical_counterparts'], list) and
                    len(row['canonical_counterparts']) == len(set(row['canonical_counterparts'])) and
                    set(row['canonical_counterparts']) == expected_counterparts, f'Canonical counterpart inheritance differs: {prefix}')
            if prefix in canonical_decisions:
                require(row['canonical_reason'] == canonical_decisions[prefix]['reason'], f'Canonical policy reason changed: {prefix}')
            if row['lifecycle'] not in {'current', 'unresolved'}:
                require(not row['canonical'] and not row['default_eligible'], f'Canonical selection revived an excluded lifecycle: {prefix}')
            if taq and row['transport'] == 'sas':
                require(set(row.get('sas_name_matches', [])) == set(taq['names_by_member'].get(row['table'].lower(), [])),
                        f'PostgreSQL/SAS name cross-reference differs: {prefix}')
            require(row['transport'] == ('sas' if raw_access[oid]['status'] == 'taq_sas_required' else 'psql'),
                    f'Transport route changed: {prefix}')
            preflight = row['access'] == 'planning_accepted' and row['transport'] == 'psql'
            expected_default = expected_selected and preflight
            require(row['default_eligible'] == expected_default, f'Default eligibility mismatch: {prefix}')
            if row['lifecycle'] == 'current' and preflight:
                current_rows.append(row)
            if row['lifecycle'] == 'unresolved' and preflight:
                unresolved_rows.append(row)
            if row['default_eligible']:
                if row['lifecycle'] == 'current':
                    require(row['sources'], f'Current default lacks source evidence: {prefix}')
                require((installed / row['skill'] / 'SKILL.md').is_file(), f'Missing installed skill owner: {prefix}')
                require(row['layout_id'] in layouts, f'Missing installed layout: {prefix}')
                default_rows.append(row)

        require(len(relations) == coverage['visible_relations'], 'Coverage relation count mismatch')
        for scope, rows in (('current', current_rows), ('default', default_rows)):
            require(len(rows) == coverage[f'{scope}_preflight_relations'], f'Coverage {scope} count mismatch')
            require(sum(row['kind'] != 'v' for row in rows) == coverage[f'{scope}_preflight_base_relations'],
                    f'Coverage {scope} base count mismatch')
            require(len({row['schema'] for row in rows}) == coverage[f'{scope}_preflight_schemas'],
                    f'Coverage {scope} schema count mismatch')
            require(dict(Counter(row['skill'] for row in rows)) == coverage[f'{scope}_by_skill'], f'{scope} skill ownership count mismatch')
        require(len(unresolved_rows) == coverage['unresolved_preflight'], 'Unresolved preflight count mismatch')
        require(sum(row['default_eligible'] for row in unresolved_rows) == coverage['canonical_unresolved_preflight'],
                'Selected unresolved count mismatch')
        require(sum(not row['default_eligible'] for row in unresolved_rows) == coverage['unresolved_excluded_preflight'],
                'Excluded unresolved count mismatch')
        require(dict(Counter(row['lifecycle'] for row in relations)) == coverage['lifecycle'], 'Lifecycle summary mismatch')
        require(dict(Counter(row['access'] for row in relations)) == coverage['access'], 'Access summary mismatch')
        require(coverage['missing_skill_owners'] == [], 'Build recorded missing domain skills')
        review = json.loads((repo / 'catalog/lifecycle-review.json').read_text())
        require(len(review) == len(unresolved_rows) == len({row['name'] for row in review}), 'Lifecycle review count differs')
        require({row['name'] for row in review} == {row['name'] for row in unresolved_rows}, 'Lifecycle review dropped unresolved endpoints')
        review_fields = {'name', 'lifecycle', 'lifecycle_reason', 'canonical', 'canonical_reason', 'canonical_counterparts',
                         'default_eligible', 'sample', 'access', 'skill', 'sources', 'dependencies'}
        for row in review:
            require(review_fields <= row.keys(), f'Lifecycle review omits selection evidence: {row["name"]}')
            require(all(by_name[row['name']][key] == value for key, value in row.items()),
                    f'Lifecycle review differs from package: {row["name"]}')
        schemas = json.loads((data / 'schemas.json').read_text())
        by_schema = defaultdict(list)
        for row in relations:
            by_schema[row['schema']].append(row)
        require(len(schemas) == coverage['schemas'] == len(by_schema), 'Schema count mismatch')
        for schema in schemas:
            members = by_schema[schema['schema']]
            require(schema['visible_relations'] == len(members), f'Schema visible count mismatch: {schema["schema"]}')
            require(schema['current_preflight_relations'] == sum(r['lifecycle'] == 'current' and r['access'] == 'planning_accepted'
                                                                and r['transport'] == 'psql' for r in members),
                    f'Schema current count mismatch: {schema["schema"]}')
            require(schema['default_preflight_relations'] == sum(r['default_eligible'] for r in members),
                    f'Schema default count mismatch: {schema["schema"]}')

        audit = next(r['name'] for r in default_rows if r['schema'] == 'auditsmp_all')
        option_sample = next(r['name'] for r in default_rows if r['schema'] == 'optionmsamp_us')
        unknown = 'comp_global_daily.g_tmptable_pkg6775_tbl5551'
        cases = [
            ('coverage', ['coverage']),
            ('current_schemas', ['schemas', '--limit', '2000']),
            ('crsp_search', ['search', 'crsp', '--limit', '2000']),
            ('crsp_tables', ['tables', 'crsp', '--limit', '2000']),
            ('current_crsp', ['table', 'crsp.msf_v2']),
            ('deprecated_crsp', ['table', 'crsp.dsf']),
            ('denied_ccm', ['table', 'crsp.ccmxpf_lnkhist']),
            ('audit_sample', ['table', audit]),
            ('optionmetrics_sample', ['table', option_sample]),
            ('jkp', ['table', 'contrib_global_factor.global_factor']),
            ('unfamiliar_bank_product', ['table', 'bank.wrds_bank_reg_vars']),
            ('unresolved_product', ['table', unknown]),
            ('unresolved_default_search', ['search', unknown]),
            ('unresolved_explicit_search', ['search', unknown, '--all']),
            ('crsp_columns', ['columns', 'mthret', '--schema', 'crsp', '--limit', '2000']),
            ('compustat_columns', ['columns', 'gvkey', '--schema', 'comp_na_daily_all', '--limit', '2000']),
        ]
        selected_cases = {
            'selected_gutenberg': 'gutenberg.gutenberg_book',
            'selected_pwt': 'pwt_all.na',
            'selected_pwt_alias': 'pwt.na',
            'selected_select_treasury': 'crsp_a_indexes.cs20yr',
            'selected_select_treasury_alias': 'crsp.cs20yr',
            'selected_meps': 'public_all.mepssumm',
            'selected_meps_alias': 'public.mepssumm',
            'selected_ccm_sample': 'crspsamp_all.ccmxpf_lnkhist',
            'selected_ccm_sample_alias': 'crspsamp.ccmxpf_lnkhist',
        }
        cases.extend((label, ['search', name]) for label, name in selected_cases.items())
        if taq:
            cases.extend([
                ('taq_default', ['taq', '--limit', '3']),
                ('taq_all', ['taq', '--all', '--limit', '3']),
                ('taq_exact', ['taq', 'TAQMSEC.CTM_20241007']),
                ('taq_current_sample', ['taq', 'TAQMSAMP.', '--limit', '3']),
                ('taq_legacy_default', ['taq', 'TAQ.', '--limit', '3']),
                ('taq_legacy_all', ['taq', 'TAQ.', '--all', '--limit', '3']),
                ('taq_legacy_sample', ['taq', 'TAQSAMP.', '--all', '--limit', '3']),
            ])

        def invoke(case):
            label, args = case
            # This interpreter is managed by the parent uv run; no global install.
            result = subprocess.run([sys.executable, str(helper), *args], cwd=unrelated,
                                    text=True, capture_output=True, timeout=60)
            require(result.returncode == 0, f'Installed CLI failed for {label}: {result.stderr}')
            return label, args, json.loads(result.stdout)

        with ThreadPoolExecutor(max_workers=4) as pool:
            cli_results = list(pool.map(invoke, cases))
        cli = {}
        for label, args, result in cli_results:
            cli[label] = result
            if label == 'coverage':
                require(result == coverage, 'Installed coverage differs from bundled file')
            elif args[0] == 'table':
                require(result['matches'] == result['returned'] == 1, f'Exact lookup failed: {label}')
                actual = result['results'][0]
                expected = by_name[args[1]]
                require(all(actual[k] == v for k, v in expected.items()), f'Exact lookup metadata changed: {label}')
                require(actual['columns'] == layouts[expected['layout_id']], f'CLI column details changed: {label}')
                require(actual['products'] == [products[s] for s in expected['product_schemas'] if s in products],
                        f'CLI product source details changed: {label}')
            elif args[0] == 'schemas':
                require({r['schema'] for r in result['results']} == {r['schema'] for r in default_rows}, 'Default schemas differ')
            elif args[0] == 'taq':
                for actual in result['results']:
                    expected = taq['members'][actual['name']]
                    require(all(actual[k] == value for k, value in expected.items()), f'SAS CLI member metadata changed: {label}')
                    if '--all' not in args:
                        require(expected['default_eligible'], f'SAS default CLI leaked legacy product: {label}')
                    if 'columns' in actual:
                        require(actual['columns'] == taq['layouts'][expected['layout_id']], f'SAS CLI columns changed: {label}')
            else:
                for actual in result['results']:
                    expected = by_name[actual['name']]
                    for field in ('lifecycle', 'canonical', 'canonical_reason', 'default_eligible', 'sample', 'access', 'transport'):
                        require(field in actual and actual[field] == expected[field],
                                f'Compact lookup omitted or changed {field}: {label}')
                if '--all' not in args:
                    require(all(by_name[r['name']]['default_eligible'] for r in result['results']), f'Default CLI leaked an exclusion: {label}')
                if args[0] == 'columns':
                    term = args[1]
                    for row in result['results']:
                        expected_columns = [c for c in layouts[by_name[row['name']]['layout_id']]
                                            if term in c['name'].lower() or term in (c.get('comment') or '').lower()]
                        require(row['matching_columns'] == expected_columns, f'Column search changed source details: {row["name"]}')

        require(cli['current_crsp']['results'][0]['default_eligible'], 'Current CRSP unexpectedly excluded')
        require(not cli['deprecated_crsp']['results'][0]['default_eligible'], 'Legacy DSF exposed by default')
        ccm = cli['denied_ccm']['results'][0]
        require(ccm['access'] == 'guard_denied' and ccm['canonical'] and not ccm['default_eligible'], 'CCM denial/current selection separation lost')
        require(cli['audit_sample']['results'][0]['sample'] and cli['optionmetrics_sample']['results'][0]['sample'], 'Sample product mislabeled')
        require(cli['unresolved_default_search']['matches'] == 0, 'Unresolved product exposed by default search')
        require(any(r['name'] == unknown for r in cli['unresolved_explicit_search']['results']), 'Unresolved product absent with --all')
        require(not by_name[unknown]['canonical'], 'Placeholder was selected as canonical')
        for label, name in selected_cases.items():
            exact = [row for row in cli[label]['results'] if row['name'] == name]
            require(len(exact) == 1, f'Selected unresolved endpoint absent from default search: {name}')
            actual = exact[0]
            require(actual['lifecycle'] == 'unresolved' and actual['canonical'] and actual['default_eligible'],
                    f'Selected endpoint lost its unresolved lifecycle: {name}')
            if 'ccm_sample' in label:
                require(actual['sample'], f'Canonical selection lost CCM sample restriction: {name}')
        for alias, target in [('public.mepssumm', 'public_all.mepssumm'),
                              ('crspsamp.ccmxpf_lnkhist', 'crspsamp_all.ccmxpf_lnkhist')]:
            require(by_name[alias]['dependencies'] == [target] and alias not in canonical_decisions,
                    f'CLI alias case no longer exercises policy inheritance: {alias}')
            require(set(by_name[alias]['canonical_counterparts']) == set(by_name[target]['canonical_counterparts']),
                    f'Alias counterparts not inherited: {alias}')
        require(all(r['name'] != 'crsp.dsf' for r in cli['crsp_tables']['results']), 'Legacy DSF included in default schema table list')
        require(all(r['name'] != 'crsp.ccmxpf_lnkhist' for r in cli['crsp_tables']['results']), 'Denied CCM included in default table list')
        if taq:
            require(cli['taq_default']['matches'] == coverage['taq_sas']['current_sas_members'], 'SAS default CLI count differs')
            require(cli['taq_all']['matches'] == len(taq['members']), 'SAS --all CLI count differs')
            require(cli['taq_current_sample']['matches'] == taq['counts'].get('TAQMSAMP', 0), 'SAS current sample count differs')
            require(cli['taq_legacy_default']['matches'] == 0, 'Legacy TAQ exposed by default')
            require(cli['taq_legacy_all']['matches'] == taq['counts'].get('TAQ', 0), 'Legacy TAQ missing from --all')
            require(cli['taq_legacy_sample']['matches'] == taq['counts'].get('TAQSAMP', 0), 'Legacy sample missing from --all')
            exact = cli['taq_exact']
            require(exact['matches'] == exact['returned'] == 1, 'Exact SAS member lookup failed')
            require(len(exact['results'][0]['columns']) == 17 and exact['results'][0]['access'] == 'sas_metadata_opened',
                    'Expected 17-column SAS trade descriptor with metadata-only access evidence')

        report['checked'] = {
            'relations': len(relations), 'global_column_layouts': len(layouts),
            'column_instances': sum(len(layouts[r['layout_id']]) for r in relations),
            'dependency_edges': sum(len(r['dependencies']) for r in relations),
            'default_relations': len(default_rows), 'product_descriptions': len(products),
            'current_preflight_relations': len(current_rows),
            'canonical_policy_roots': len(canonical_decisions),
            'canonical_unresolved_preflight': sum(row['default_eligible'] for row in unresolved_rows),
            'unresolved_excluded_preflight': sum(not row['default_eligible'] for row in unresolved_rows),
            'installed_skill_owners': len({r['skill'] for r in default_rows}),
            'cli_cases': len(cases),
        }
        report['cli_cases'] = [{'label': label, 'arguments': args,
                                'matches': result.get('matches'), 'passed': True}
                               for label, args, result in cli_results]
        report['isolated_installation'] = {'skills_copied': True, 'unrelated_working_directory': True,
                                          'temporary_installation_removed_after_test': True,
                                          'python_interpreter': 'Inherited from uv run; standard library only'}
        report['artifact_sha256'] = initial_hashes
    require({str(path.relative_to(repo)): digest(path) for path in tracked} == initial_hashes,
            'Catalog changed during validation; rerun against the completed build')
    for filename, expected in coverage['inputs'].items():
        require(digest(repo / filename) == expected, f'Build input changed during validation: {filename}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output or repo / 'catalog/discovery/skill-catalog-validation.json'
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Portable catalog metadata, provenance preservation, and local CLI behavior; no database connection or research-data access.'}
    try:
        validate(repo, report)
        report['status'] = 'passed'
    except (AssertionError, KeyError, StopIteration, subprocess.SubprocessError, ValueError) as exc:
        report['status'] = 'failed'
        report['error'] = str(exc) or type(exc).__name__
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'catalog_built_at', 'checked', 'error') if k in report}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
