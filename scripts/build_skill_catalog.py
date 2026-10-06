"""Build the installable WRDS catalog from dated discovery and product evidence.

This is local metadata processing, not a database query. Run with uv run
--no-project python scripts/build_skill_catalog.py after collectors finish.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'catalog' / 'discovery'
DEST = ROOT / 'skills' / 'wrds-catalog' / 'references'


def read_lines(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def save_lines(path, rows):
    with path.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as stream:
        for row in rows:
            stream.write((json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n').encode())


def owner(schema):
    if schema.startswith(('taq', 'wrds_taq')): return 'wrds-taq'
    if schema.startswith(('crsp',)): return 'wrds-crsp'
    if schema.startswith(('comp',)): return 'wrds-compustat'
    if schema.startswith(('optionm',)): return 'wrds-optionmetrics'
    if schema.startswith(('ff_',)) or schema == 'ff': return 'wrds-fama-french'
    if schema.startswith('contrib_global_factor'): return 'wrds-jkp'
    if schema.startswith(('fisd', 'trace', 'msrb', 'contrib_bond', 'contrib_corporate_bond', 'wrdsapps_bondret')): return 'wrds-bonds'
    if schema.startswith(('ciq',)): return 'wrds-capital-iq'
    if schema.startswith(('audit', 'boardex', 'altrata', 'bvd')): return 'wrds-governance'
    if schema.startswith(('tr_', 'trsamp', 'ibessamp')): return 'wrds-lseg'
    if schema.startswith(('sp_esg', 'trucost', 'msci', 'sustain', 'reprisk', 'wrds_environmental')): return 'wrds-esg'
    if schema.startswith(('bank', 'frb', 'macrofin', 'fjc', 'pwt', 'doe', 'block', 'public', 'dmef', 'rq_', 'totalq')): return 'wrds-public-data'
    if schema.startswith('contrib'): return 'wrds-contributed-data'
    if schema.startswith(('cboe', 'otc')): return 'wrds-market-data'
    if schema.startswith(('wrdsapps_link', 'wrdsapps_plink')): return 'wrds-linking'
    if schema.startswith(('wrds', 'sec', 'gutenberg')): return 'wrds-research'
    return 'wrds-vendor-samples'


def package_taq():
    """Package validated SAS header metadata without treating it as row access."""
    source=ROOT/'catalog'/'taq'; path=source/'summary.json'
    if not path.exists(): return None,[],{}
    summary=json.loads(path.read_text())
    if summary.get('status')!='complete_metadata_inventory' or summary.get('validation_mismatch_count')!=0:
        raise RuntimeError('TAQ inventory has not passed metadata validation.')
    def load(suffix):
        filename=source/(summary['run_basename']+'_'+suffix+'.csv')
        expected=summary['raw_csv_sha256'][filename.name]
        if hashlib.sha256(filename.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('TAQ source checksum mismatch: '+str(filename))
        with filename.open(newline='') as stream:
            return [{k.lower():v for k,v in r.items()} for r in csv.DictReader(stream)]
    mapping={(r['libname'],r['memname']):r for r in load('layout_map')}
    layouts=defaultdict(list)
    for row in load('layout_columns'):
        layouts[row['layout_id']].append({k:row[k] for k in ['name','type','length','varnum','label','format','informat']})
    records=[]; names=defaultdict(list)
    for row in load('members'):
        key=(row['libname'],row['memname']);layout=mapping[key]['layout_id']
        if len(layouts[layout])!=int(row['nvar']):raise RuntimeError('TAQ member column mismatch')
        current=row['libname'] in ('TAQMSEC','TAQMSAMP')
        record={'name':'.'.join(key),'sas_library':key[0],'member':key[1],
                'layout_id':layout,'column_count':int(row['nvar']),'label':row['memlabel'],
                'header_nobs':row['nobs'],'header_modified_at':row['modate'],
                'access':'sas_metadata_opened','lifecycle':'current' if current else 'legacy_product',
                'default_eligible':current,'sample':row['libname'].endswith('SAMP'),
                'transport':'sas','skill':'wrds-taq',
                'sources':['https://www.nyse.com/data-products/catalog/daily-taq',
                           'https://www.nyse.com/market-data/technical-documents'],
                'evidence':'SAS dictionary metadata, not observation coverage or row-return verification.'}
        records.append(record);names[key[1].lower()].append(record['name'])
    save_lines(DEST/'taq-members.jsonl.gz',records)
    save_lines(DEST/'taq-layouts.jsonl.gz',({'layout_id':key,'columns':cols} for key,cols in sorted(layouts.items())))
    (DEST/'taq-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    stats={**summary,'current_sas_members':sum(r['default_eligible'] for r in records),
           'legacy_sas_members':sum(not r['default_eligible'] for r in records)}
    return stats,[path,*[source/n for n in summary['raw_csv_sha256']]],names


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    schema_evidence=list(read_lines(RAW/'schemas.jsonl'))
    snapshot_date=min(r['collected_at'][:10] for r in schema_evidence)
    relations = {r['relation_oid']: r for r in read_lines(RAW / 'relations.jsonl.gz')}
    probes = {r['relation_oid']: r for r in read_lines(RAW / 'access-probes.jsonl')}
    if set(probes) != set(relations):
        raise RuntimeError('Access collection is incomplete; wait for every relation outcome.')
    deps = defaultdict(set)
    for row in read_lines(RAW / 'dependencies.jsonl.gz'):
        if row['source_oid'] != row['target_oid']:
            deps[row['source_oid']].add(row['target_oid'])
    products = {}
    docs = json.loads((ROOT / 'research' / 'product-docs.json').read_text())
    for page in docs['pages']:
        for item in page['products']:
            schema = item['schema'].split()[0]
            products[schema] = {**item, 'schema': schema, 'vendor': page['vendor'],
                                'source_url': page['url'], 'retrieved_at': page['retrieved_at']}
    policy = json.loads((ROOT / 'catalog' / 'product-policy.json').read_text())
    overrides = {}
    for rule in json.loads((ROOT / 'research' / 'current-product-overrides.json').read_text()):
        for table in rule['tables']:
            overrides[rule['schema']+'.'+table] = {k: v for k,v in rule.items() if k != 'tables'}
    selection_files=[ROOT/'catalog'/'canonical-crsp.json', ROOT/'catalog'/'canonical-other.json']
    selection_rules={}
    names={r['schema_name']+'.'+r['relation_name']:oid for oid,r in relations.items()}
    for path in selection_files:
        for decision in json.loads(path.read_text())['decisions']:
            name=decision['name']
            if name in selection_rules or name not in names:
                raise RuntimeError('Duplicate or absent canonical selection endpoint: '+name)
            if not isinstance(decision['canonical'],bool) or not decision['reason']:
                raise RuntimeError('Invalid canonical selection decision: '+name)
            if any(n not in names for n in decision['counterparts']):
                raise RuntimeError('Unknown canonical selection counterpart: '+name)
            selection_rules[name]=decision
    classified = {}

    def classify(oid, trail=()):
        if oid in classified: return classified[oid]
        if oid in trail or oid not in relations:
            return {'status': 'unresolved', 'reason': 'Unresolved or cyclic catalog dependency.'}
        row = relations[oid]
        schema = row['schema_name']; name = schema+'.'+row['relation_name']
        explicit = overrides.get(name)
        product_rule = policy['schemas'].get(schema)
        if explicit:
            result = dict(explicit)
        elif product_rule:
            result = dict(product_rule)
        elif deps[oid]:
            parents = [classify(target, trail+(oid,)) for target in sorted(deps[oid])]
            status = 'current' if all(p['status']=='current' for p in parents) else 'unresolved'
            if any(p['status'] in ('retired','superseded_copy','stale_alias') for p in parents):
                status = 'stale_alias'
            result = {'status':status, 'reason':'Lifecycle inherited from observed view dependencies.',
                      'source_urls': sorted({url for p in parents for url in p.get('source_urls', [])}),
                      'product_schemas': sorted({s for p in parents for s in p.get('product_schemas', [])})}
        elif re.fullmatch(r'taqm_\d{4}', schema) or schema=='taqmsec':
            result = {'status':'current',
                      'reason':'Historical partition of maintained Daily TAQ; a closed annual partition is not a superseded database version. This taxonomy is inferred from NYSE Daily TAQ and the WRDS Daily TAQ linking manual.',
                      'source_urls':['https://www.nyse.com/data-products/catalog/daily-taq',
                                     'https://www.nyse.com/market-data/technical-documents',
                                     'https://wrds-www.wharton.upenn.edu/documents/1336/NYSE_Daily_TAQ_to_CRSP_Linking_BPNFjWm.pdf'],
                      'product_schemas':[schema]}
        elif schema in products:
            product = products[schema]
            legacy = 'legacy' in (product.get('update_frequency') or '').lower()
            result = {'status': 'retired' if legacy else 'current',
                      'reason': 'WRDS explicitly labels this product legacy/no longer updated.' if legacy else
                                'Currently listed WRDS product; no retirement label. Delivery freshness is recorded separately.',
                      'source_urls':[product['source_url']], 'product_schemas':[schema]}
        elif schema.endswith('_old') and schema[:-4] in products:
            result = {'status':'superseded_copy', 'reason':'Unlisted alternate copy; the paired unsuffixed schema is the documented product endpoint. This is endpoint selection, not a provider retirement announcement.',
                      'replacement':schema[:-4], 'source_urls':[products[schema[:-4]]['source_url']]}
        else:
            result = {'status':'unresolved', 'reason':'No current product mapping established from public documentation and catalog dependencies.'}
        result.setdefault('product_schemas', [schema] if schema in products or result['status']=='current' else [])
        # An explicit product label cannot rehabilitate a view over an excluded copy.
        if result['status']=='current' and deps[oid]:
            bad = [classify(t,trail+(oid,)) for t in deps[oid]]
            if any(p['status'] in ('retired','superseded_copy','stale_alias') for p in bad):
                result = {**result, 'status':'stale_alias', 'reason':'A documented product view resolves to a retired or alternate delivery.'}
        classified[oid] = result
        return result

    selected={}
    def select(oid, trail=()):
        if oid in selected:return selected[oid]
        if oid in trail:return (False,'Cyclic selection dependency.',[])
        life=classify(oid);row=relations[oid]
        name=row['schema_name']+'.'+row['relation_name']
        decision=selection_rules.get(name)
        if decision:
            if life['status']!='unresolved' or deps[oid]:
                raise RuntimeError('Canonical review must target an unresolved root: '+name)
            if decision['canonical'] and probes[oid]['status']!='planning_accepted':
                raise RuntimeError('Sole available endpoint no longer passes access preflight: '+name)
            result=(decision['canonical'],decision['reason'],decision['counterparts'])
        elif life['status']=='current':
            result=(True,'Documented current product endpoint.',[])
        elif life['status']=='unresolved' and deps[oid]:
            parents=[select(d,trail+(oid,)) for d in sorted(deps[oid])]
            canonical=all(p[0] for p in parents)
            result=(canonical,'Canonical selection inherited from observed view dependencies.' if canonical else
                    'One or more view dependencies are not canonical.',sorted({n for p in parents for n in p[2]}))
        else:
            result=(False,life['reason'],[])
        selected[oid]=result
        return result

    def selected_owner(oid):
        row=relations[oid];life=classify(oid);schemas=life.get('product_schemas',[])
        if life['status']=='unresolved' and select(oid)[0] and deps[oid]:
            owners={selected_owner(d) for d in deps[oid]}
            if len(owners)==1:return owners.pop()
        return owner(schemas[0] if len(schemas)==1 else row['schema_name'])

    all_rows=[]; eligible=[]
    for oid,row in sorted(relations.items(), key=lambda kv:(kv[1]['schema_name'],kv[1]['relation_name'])):
        life=classify(oid); probe=probes[oid]; schema=row['schema_name']
        p_schemas=life.get('product_schemas',[])
        skill=selected_owner(oid)
        canonical,canonical_reason,counterparts=select(oid)
        record={'name':schema+'.'+row['relation_name'], 'schema':schema,'table':row['relation_name'],
                'oid':oid,'kind':row['relation_kind'],'comment':row.get('comment'),
                'lifecycle':life['status'],'lifecycle_reason':life['reason'],
                'canonical':canonical,'canonical_reason':canonical_reason,'canonical_counterparts':counterparts,
                'replacement':life.get('replacement'), 'sources':life.get('source_urls',[]),
                'product_schemas':p_schemas, 'skill':skill,
                'access':probe['status'],'access_checked_at':probe['checked_at'],
                'access_error':probe.get('error'),'transport':'sas' if probe['status']=='taq_sas_required' else 'psql',
                'dependencies':sorted(relations[d]['schema_name']+'.'+relations[d]['relation_name'] for d in deps[oid] if d in relations)}
        record['sample']=any(any(token in s for token in ('samp','smp','trial')) or
                             any(token in (products.get(s,{}).get('title') or '').lower() for token in ('sample','trial'))
                             for s in [schema,*p_schemas])
        record['default_eligible']=canonical and probe['status']=='planning_accepted' and record['transport']=='psql'
        all_rows.append(record)
        if record['default_eligible']: eligible.append(record)
    # Preserve metadata for every visible relation, but default queries select only
    # canonical products with accepted access preflight. Lifecycle evidence stays separate.
    column_map={}; layouts={}
    for row in read_lines(RAW / 'column-layouts.jsonl.gz'):
        layouts[row['layout_id']]=row['columns']
        for oid in row['relation_oids']: column_map[oid]=row['layout_id']
    taq,taq_inputs,taq_names=package_taq()
    for row in all_rows:
        row['layout_id']=column_map[row['oid']]
        if row['transport']=='sas':
            row['sas_name_matches']=taq_names.get(row['table'].lower(),[])
    save_lines(DEST/'relations.jsonl.gz',all_rows)
    save_lines(DEST/'layouts.jsonl.gz',({'layout_id':key,'columns':value} for key,value in sorted(layouts.items())))
    (DEST/'products.json').write_text(json.dumps(products,indent=2,ensure_ascii=False)+'\n')
    schema_summaries=[]
    for schema in sorted({r['schema'] for r in all_rows}):
        rows=[r for r in all_rows if r['schema']==schema]
        defaults=[r for r in rows if r['default_eligible']]
        schema_summaries.append({'schema':schema,'visible_relations':len(rows),
            'current_preflight_relations':sum(r['lifecycle']=='current' for r in defaults),
            'default_preflight_relations':len(defaults),
            'lifecycle':dict(Counter(r['lifecycle'] for r in rows)), 'access':dict(Counter(r['access'] for r in rows)),
            'skills':sorted({r['skill'] for r in rows}), 'sample':all(r['sample'] for r in rows)})
    (DEST/'schemas.json').write_text(json.dumps(schema_summaries,indent=2)+'\n')
    missing=sorted({r['skill'] for r in eligible if not (ROOT/'skills'/r['skill']/'SKILL.md').exists()})
    documented=[r for r in eligible if r['lifecycle']=='current']
    summary={'built_at':datetime.now(timezone.utc).isoformat(),'snapshot_date':snapshot_date,
      'visible_relations':len(all_rows),'schemas':len(schema_summaries),
      'current_preflight_relations':len(documented),'current_preflight_base_relations':sum(r['kind']!='v' for r in documented),
      'current_preflight_schemas':len({r['schema'] for r in documented}),
      'default_preflight_relations':len(eligible),'default_preflight_base_relations':sum(r['kind']!='v' for r in eligible),
      'default_preflight_schemas':len({r['schema'] for r in eligible}),
      'lifecycle':dict(Counter(r['lifecycle'] for r in all_rows)),
      'access':dict(Counter(r['access'] for r in all_rows)),
      'current_by_skill':dict(sorted(Counter(r['skill'] for r in documented).items())),
      'default_by_skill':dict(sorted(Counter(r['skill'] for r in eligible).items())),
      'unresolved_preflight':sum(r['lifecycle']=='unresolved' and r['access']=='planning_accepted' for r in all_rows),
      'canonical_unresolved_preflight':sum(r['lifecycle']=='unresolved' for r in eligible),
      'unresolved_excluded_preflight':sum(r['lifecycle']=='unresolved' and r['access']=='planning_accepted' and not r['default_eligible'] for r in all_rows),
      'missing_skill_owners':missing,
      'taq_sas':taq,
      'semantics':'Canonical selects documented current products and reviewed sole available research versions, including restricted samples. Canonical selection does not establish maintenance or resolve uncertain lifecycle. Preflight is zero-row query planning plus observed privilege guards, not a data-return or sample-completeness guarantee. TAQ uses the separate SAS inventory.',
      'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [Path(__file__).resolve(),RAW/'schemas.jsonl',RAW/'relations.jsonl.gz',RAW/'dependencies.jsonl.gz',RAW/'column-layouts.jsonl.gz',RAW/'access-probes.jsonl',ROOT/'research'/'product-docs.json',ROOT/'catalog'/'product-policy.json',ROOT/'research'/'current-product-overrides.json',*selection_files,*taq_inputs]}}
    (DEST/'coverage.json').write_text(json.dumps(summary,indent=2)+'\n')
    unresolved=[{k:r[k] for k in ['name','lifecycle','lifecycle_reason','canonical','canonical_reason','canonical_counterparts','default_eligible','sample','access','skill','sources','dependencies']}
                for r in all_rows if r['lifecycle']=='unresolved' and r['access']=='planning_accepted']
    (ROOT/'catalog'/'lifecycle-review.json').write_text(json.dumps(unresolved,indent=2)+'\n')
    # Product-specific compact references are portable alongside the shared skill.
    for skill in sorted({r['skill'] for r in eligible}):
        path=ROOT/'skills'/skill/'references'/'catalog-coverage.md';path.parent.mkdir(parents=True,exist_ok=True)
        own=[r for r in eligible if r['skill']==skill]
        lines=['# Catalog coverage','', f'Generated from the {snapshot_date} account snapshot. Counts include aliases; they are not counts of independent datasets. Selection includes documented current products and reviewed sole available versions; uncertain lifecycle remains labeled. Access is accepted planning and privilege-guard checks, not proof that every query returns rows.', '',
               'Use [wrds-catalog](../../wrds-catalog/SKILL.md) to find every table, column, dependency, source, and excluded version.', '', '| Schema | Relations | Sample/trial |','|---|---:|---|']
        for schema in sorted({r['schema'] for r in own}):
            group=[r for r in own if r['schema']==schema]
            lines.append(f"| `{schema}` | {len(group)} | {'yes' if all(r['sample'] for r in group) else 'no'} |")
        path.write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
