#!/usr/bin/env python3
"""Read the bundled WRDS metadata catalog; never connect to a server."""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'references'


def rows(filename):
    with gzip.open(DATA / filename, 'rt') as stream:
        for line in stream:
            yield json.loads(line)


def display(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def compact(row):
    return {key:row.get(key) for key in ['name','comment','lifecycle','canonical','canonical_reason','default_eligible','access','transport','sample','skill','product_schemas']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['coverage','schemas','search','tables','table','columns','taq'])
    parser.add_argument('term',nargs='?',default='')
    parser.add_argument('--schema')
    parser.add_argument('--all',action='store_true',help='Also include noncanonical and denied records.')
    parser.add_argument('--limit',type=int,default=50)
    args=parser.parse_args()
    if args.limit<1: parser.error('--limit must be positive')
    if args.command in ['tables','table','columns'] and not args.term:
        parser.error('This command requires a schema, qualified table, or column term.')
    if args.command=='coverage':
        display(json.loads((DATA/'coverage.json').read_text()));return
    if args.command=='schemas':
        matches=[r for r in json.loads((DATA/'schemas.json').read_text())
                 if (args.all or r['default_preflight_relations']) and args.term.lower() in r['schema'].lower()]
    elif args.command=='taq':
        path=DATA/'taq-members.jsonl.gz'
        if not path.exists():
            display({'error':'SAS metadata inventory is not included in this snapshot.'});raise SystemExit(1)
        matches=[r for r in rows('taq-members.jsonl.gz')
                 if (args.all or r['default_eligible']) and args.term.lower() in json.dumps(r).lower()]
        exact=[r for r in matches if r['name'].lower()==args.term.lower()]
        if exact:
            matches=exact
            for match in matches:
                match['columns']=next(r['columns'] for r in rows('taq-layouts.jsonl.gz') if r['layout_id']==match['layout_id'])
    else:
        candidates=[r for r in rows('relations.jsonl.gz')
                    if (args.all or args.command=='table' or r['default_eligible'])
                    and (not args.schema or r['schema']==args.schema)]
        term=args.term.lower()
        if args.command=='table':
            matches=[r for r in candidates if r['name'].lower()==term]
            if matches:
                layout=matches[0]['layout_id']
                matches[0]['columns']=next(r['columns'] for r in rows('layouts.jsonl.gz') if r['layout_id']==layout)
                products=json.loads((DATA/'products.json').read_text())
                matches[0]['products']=[products[s] for s in matches[0]['product_schemas'] if s in products]
        elif args.command=='columns':
            needed={r['layout_id'] for r in candidates}
            layouts={r['layout_id']:[c for c in r['columns'] if term in c['name'].lower() or term in (c.get('comment') or '').lower()]
                     for r in rows('layouts.jsonl.gz') if r['layout_id'] in needed}
            matches=[{**compact(r),'matching_columns':layouts[r['layout_id']]} for r in candidates if layouts[r['layout_id']]]
        else:
            matches=[compact(r) for r in candidates
                     if (r['schema']==args.term if args.command=='tables' else
                         term in ' '.join([r['name'],r.get('comment') or '',*r['product_schemas']]).lower())]
    snapshot=json.loads((DATA/'coverage.json').read_text())['snapshot_date']
    display({'snapshot':snapshot,'matches':len(matches),'returned':min(len(matches),args.limit),
             'truncated':len(matches)>args.limit,'results':matches[:args.limit]})
    if args.command=='table' and not matches: raise SystemExit(1)


if __name__=='__main__':main()
