#!/usr/bin/env python3
"""Sharded exact no-symmetry Farkas audit for ALL weight-8 k=2 children.

For each count child, every exact geometric identity subcase and every choice
of the two underfull weight-8 lines is tested.  `exact_certificate` first uses
an LP only to find a candidate Farkas ray, then reconstructs it over Q and
finally verifies the contradiction using Python integers.  A child is closed
only if every one of its subcases receives such an exact certificate.

If any subcase is feasible, numerically unresolved, or fails exact
reconstruction, the child remains OPEN/UNKNOWN.  Thus failures and timeouts
can never become proof.  No symmetry is used.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import generate_refined_8_count_exact as level8
import verify_farkas_weight15_94_dynamic as fk

base=fk.base
NEW8=tuple(level8.NEW8)
ALL=[t for t in level8.CASES if t[2]==2]
assert len(ALL)==376


def audit_child(triple):
    parent,k15,k8=triple
    assert k8==2
    records=[]
    checked=0
    for under15,sat15 in fk.identity_subcases(parent,k15):
        for under8_tuple in itertools.combinations(NEW8,2):
            under8=set(under8_tuple)
            sat8=set(NEW8)-under8
            under=set(under15)|under8
            sat=set(sat15)|sat8
            try:
                terms,rhs=fk.exact_certificate(under,sat)
            except Exception as exc:
                return {
                    'child':list(triple),
                    'closed':False,
                    'checked_subcases':checked,
                    'reason':type(exc).__name__,
                    'detail':str(exc)[:300],
                }
            checked+=1
            records.append({
                'under_groups':[
                    [base.GROUPS[i][0],int(base.GROUPS[i][1]),int(base.GROUPS[i][2])]
                    for i in sorted(under)
                ],
                'rhs_sum':int(rhs),
                'terms':[[list(ref),int(q)] for ref,q in terms],
            })
    return {
        'child':list(triple),
        'closed':True,
        'checked_subcases':checked,
        'certificates':records,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--shard',type=int,required=True)
    ap.add_argument('--shards',type=int,default=20)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    assert 0<=args.shard<args.shards
    selected=ALL[args.shard::args.shards]
    results=[]
    for i,triple in enumerate(selected,1):
        rec=audit_child(triple)
        results.append(rec)
        state='CLOSED' if rec['closed'] else 'OPEN'
        print(f'{state} shard={args.shard} item={i}/{len(selected)} child={triple} checked={rec["checked_subcases"]}',flush=True)
    closed=[tuple(r['child']) for r in results if r['closed']]
    payload={
        'n':22,'target':34,'k8':2,'symmetry':'none',
        'shard':args.shard,'shards':args.shards,
        'selected':len(selected),'closed':len(closed),
        'closed_children':[list(t) for t in closed],
        'results':results,
    }
    args.output.write_text(json.dumps(payload,separators=(',',':'))+'\n',encoding='utf-8')
    print(f'PASS shard={args.shard} selected={len(selected)} exact_closed={len(closed)} symmetry=none')

if __name__=='__main__':
    main()
