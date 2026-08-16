#!/usr/bin/env python3
"""Exact no-symmetry Farkas audit for 134 weight-8 k=3 count children.

These candidates lie below the current rigorous-open weight-15 frontier.
Numerical LP was used only to screen candidates.  This audit expands every
choice of the three underfull weight-8 lines, reconstructs the corresponding
Farkas ray exactly over Q, clears denominators, and verifies with Python
integer arithmetic that all 242 point coefficients cancel and the right-hand
side is strictly negative.

Exactly 4,888 geometric identity subcases are checked independently.  No
symmetry is used for pruning, identification, or certificate transport.
"""
from __future__ import annotations

import argparse
import itertools
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
    (0,4,3),(1,3,3),(1,4,3),(2,2,3),(3,3,3),(3,4,3),(4,2,3),
    (5,1,3),(6,2,3),(7,1,3),(9,1,3),(12,2,3),(12,3,3),(13,2,3),
    (14,0,3),(15,1,3),(16,0,3),(18,0,3),(21,2,3),(21,3,3),(22,2,3),
    (23,0,3),(24,1,3),(25,0,3),(27,0,3),(30,2,3),(30,3,3),(31,2,3),
    (32,0,3),(33,1,3),(34,0,3),(36,0,3),(39,2,3),(39,3,3),(40,2,3),
    (41,0,3),(42,1,3),(43,0,3),(45,0,3),(48,1,3),(51,1,3),(54,0,3),
    (54,1,3),(57,0,3),(57,1,3),(60,1,3),(63,1,3),(66,1,3),(67,0,3),
    (69,0,3),(75,2,3),(76,1,3),(78,1,3),(81,0,3),(84,0,3),(87,0,3),
    (90,0,3),(93,2,3),(94,1,3),(96,1,3),(99,0,3),(102,0,3),(105,0,3),
    (108,0,3),(111,1,3),(112,0,3),(114,0,3),(120,1,3),(121,0,3),
    (123,0,3),(129,2,3),(130,1,3),(132,1,3),(135,0,3),(138,0,3),
    (141,0,3),(144,0,3),(147,2,3),(148,1,3),(150,1,3),(153,0,3),
    (156,0,3),(159,0,3),(162,0,3),(165,1,3),(166,0,3),(168,0,3),
    (174,2,3),(175,1,3),(176,0,3),(177,1,3),(181,0,3),(184,0,3),
    (187,0,3),(190,0,3),(196,0,3),(202,1,3),(205,0,3),(210,0,3),
    (212,1,3),(218,0,3),(225,2,3),(226,1,3),(227,0,3),(228,1,3),
    (232,0,3),(235,0,3),(238,0,3),(241,0,3),(244,3,3),(247,1,3),
    (248,0,3),(250,0,3),(264,2,3),(278,1,3),(296,1,3),(304,2,3),
    (318,3,3),(321,1,3),(322,0,3),(324,0,3),(342,0,3),(344,0,3),
    (350,0,3),(352,0,3),(357,0,3),(359,0,3),(363,0,3),(365,0,3),
    (367,0,3),(369,0,3),(374,0,3),(380,0,3),(385,0,3),
]
assert len(CLOSED_CHILDREN)==134
assert all(k8==3 for _p,_k15,k8 in CLOSED_CHILDREN)
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
            for under8_tuple in itertools.combinations(NEW8,3):
                under8=set(under8_tuple)
                sat8=set(NEW8)-under8
                under=set(under15)|under8
                sat=set(sat15)|sat8
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
        print(f'PASS child {child_no}/134 parent={parent} k15={k15} k8=3 subcases={sub}',flush=True)
    assert total==4888,total
    if args.output:
        args.output.write_text(json.dumps({
            'n':22,'target':34,'children':CLOSED_CHILDREN,
            'identity_subcases':total,'symmetry':'none','certificates':records,
        },separators=(',',':'))+'\n',encoding='utf-8')
    print('PASS exact n22 weight8 k3 Farkas children=134 identity_subcases=4888 symmetry=none points=242')

if __name__=='__main__':
    main()
