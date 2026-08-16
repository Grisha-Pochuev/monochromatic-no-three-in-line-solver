#!/usr/bin/env python3
"""Exact no-symmetry Farkas audit for 95 weight-8 k=4 count children.

These candidates lie below the current rigorous-open weight-15 frontier.  In
all of them all four weight-8 certificate lines (row/col 5 and 16) are
underfull.  Numerical LP was used only to screen the candidates.  This audit
reconstructs every exact Farkas ray over Q, clears denominators, and checks by
Python integer arithmetic that all 242 point coefficients cancel and the RHS
is strictly negative.

636 exact geometric identity subcases are verified independently.  No
symmetry is used for pruning, identification, or certificate transport.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import verify_farkas_weight15_94_dynamic as fk
import weight15_frontier as frontier

base=fk.base
NEW8=tuple(i for i,(_f,_k,w,_g) in enumerate(base.GROUPS) if w==8)
assert [(base.GROUPS[i][0],base.GROUPS[i][1],base.GROUPS[i][2]) for i in NEW8]==[
    ('row',5,8),('row',16,8),('col',5,8),('col',16,8)
]

CLOSED_CHILDREN=[
    (0,3,4),(0,4,4),(1,3,4),(2,2,4),(3,3,4),(4,2,4),(6,2,4),(9,0,4),
    (12,2,4),(12,3,4),(13,1,4),(14,0,4),(15,1,4),(21,2,4),(21,3,4),
    (22,1,4),(23,0,4),(24,1,4),(30,2,4),(30,3,4),(31,1,4),(32,0,4),
    (33,1,4),(39,2,4),(39,3,4),(40,1,4),(41,0,4),(42,1,4),(48,0,4),
    (51,0,4),(54,0,4),(57,0,4),(60,0,4),(63,0,4),(66,0,4),(66,1,4),
    (75,1,4),(75,2,4),(76,0,4),(78,0,4),(93,1,4),(93,2,4),(94,0,4),
    (96,0,4),(111,0,4),(111,1,4),(120,0,4),(120,1,4),(129,1,4),
    (129,2,4),(130,0,4),(132,0,4),(147,1,4),(147,2,4),(148,0,4),
    (150,0,4),(165,0,4),(165,1,4),(174,2,4),(181,0,4),(184,0,4),
    (187,0,4),(190,0,4),(193,1,4),(202,0,4),(212,0,4),(215,1,4),
    (225,2,4),(232,0,4),(235,0,4),(238,0,4),(241,0,4),(244,2,4),
    (245,1,4),(247,1,4),(252,0,4),(255,0,4),(258,0,4),(261,0,4),
    (264,1,4),(265,0,4),(267,0,4),(286,0,4),(293,0,4),(304,1,4),
    (305,0,4),(307,0,4),(318,2,4),(319,1,4),(321,1,4),(326,0,4),
    (329,0,4),(332,0,4),(335,0,4),(390,0,4),
]
assert len(CLOSED_CHILDREN)==95
assert all(k8==4 for _p,_k15,k8 in CLOSED_CHILDREN)
assert {(p,k15) for p,k15,_k8 in CLOSED_CHILDREN} <= set(frontier.OPEN_PAIRS)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    records=[]
    total=0
    for child_no,(parent,k15,k8) in enumerate(CLOSED_CHILDREN,1):
        sub=0
        for under15,sat15 in fk.identity_subcases(parent,k15):
            under=set(under15)|set(NEW8)
            sat=set(sat15)
            terms,rhs=fk.exact_certificate(under,sat)
            records.append({
                'count22_case':parent,
                'weight15_underfull_count':k15,
                'weight8_underfull_count':k8,
                'under_groups':[
                    [base.GROUPS[i][0],int(base.GROUPS[i][1]),int(base.GROUPS[i][2])]
                    for i in sorted(under)
                ],
                'rhs_sum':int(rhs),
                'terms':[[list(ref),int(q)] for ref,q in terms],
            })
            sub+=1; total+=1
        assert sub>0
        print(f'PASS child {child_no}/95 parent={parent} k15={k15} k8=4 subcases={sub}',flush=True)
    assert total==636,total
    if args.output:
        args.output.write_text(json.dumps({
            'n':22,'target':34,'children':CLOSED_CHILDREN,
            'identity_subcases':total,'symmetry':'none','certificates':records,
        },separators=(',',':'))+'\n',encoding='utf-8')
    print('PASS exact n22 weight8 k4 Farkas children=95 identity_subcases=636 symmetry=none points=242')

if __name__=='__main__':
    main()
