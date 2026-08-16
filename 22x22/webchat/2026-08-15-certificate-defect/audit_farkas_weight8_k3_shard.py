#!/usr/bin/env python3
"""Sharded version of the exact no-symmetry audit for 134 k8=3 candidates.

Uses exactly the same candidate set and exact_certificate verifier as the
single-job audit.  A child closes only after every geometric identity subcase
and all four choices of the saturated weight-8 line have exact integer-checked
Farkas contradictions.  No symmetry is used.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import verify_farkas_weight15_94_dynamic as fk
import verify_farkas_weight8_k3_134_dynamic as src

base=fk.base
NEW8=tuple(src.NEW8)
ALL=list(src.CLOSED_CHILDREN)
assert len(ALL)==134


def audit_child(triple):
    parent,k15,k8=triple
    assert k8==3
    records=[]; checked=0
    for under15,sat15 in fk.identity15_subcases(parent,k15) if hasattr(fk,'identity15_subcases') else fk.identity_subcases(parent,k15):
        for under8_tuple in itertools.combinations(NEW8,3):
            under8=set(under8_tuple); sat8=set(NEW8)-under8
            under=set(under15)|under8; sat=set(sat15)|sat8
            try:
                terms,rhs=fk.exact_certificate(under,sat)
            except Exception as exc:
                return {'child':list(triple),'closed':False,'checked_subcases':checked,
                        'reason':type(exc).__name__,'detail':str(exc)[:300]}
            checked+=1
            records.append({
                'under_groups':[[base.GROUPS[i][0],int(base.GROUPS[i][1]),int(base.GROUPS[i][2])] for i in sorted(under)],
                'rhs_sum':int(rhs),'terms':[[list(ref),int(q)] for ref,q in terms],
            })
    return {'child':list(triple),'closed':True,'checked_subcases':checked,'certificates':records}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--shard',type=int,required=True)
    ap.add_argument('--shards',type=int,default=20)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); assert 0<=args.shard<args.shards
    selected=ALL[args.shard::args.shards]
    results=[]
    for i,triple in enumerate(selected,1):
        rec=audit_child(triple); results.append(rec)
        state='CLOSED' if rec['closed'] else 'OPEN'
        print(f'{state} shard={args.shard} item={i}/{len(selected)} child={triple} checked={rec["checked_subcases"]}',flush=True)
    closed=[tuple(r['child']) for r in results if r['closed']]
    payload={'n':22,'target':34,'k8':3,'symmetry':'none','shard':args.shard,
             'shards':args.shards,'selected':len(selected),'closed':len(closed),
             'closed_children':[list(t) for t in closed],'results':results}
    args.output.write_text(json.dumps(payload,separators=(',',':'))+'\n',encoding='utf-8')
    print(f'PASS shard={args.shard} selected={len(selected)} exact_closed={len(closed)} symmetry=none')

if __name__=='__main__':
    main()
