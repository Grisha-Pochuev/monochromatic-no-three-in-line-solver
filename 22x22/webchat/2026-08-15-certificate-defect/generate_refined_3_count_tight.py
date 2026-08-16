#!/usr/bin/env python3
"""Complete final positive-weight split at certificate weight 3.

Input is the current rigorous-open residual-tightened weight-8 frontier after
run 31921064464.  The only remaining positive certificate groups are row/col
6 and 15, each of weight 3.  Every surviving parent is split by the exact
number k3=0..4 of these four lines that are underfull, omitting only counts
whose minimum defect 3*k3 exceeds the current residual budget.

After fixing k3 there are no unprocessed positive-weight line groups left.
We therefore re-apply residual_tightening with processed_min_weight=3: the
remaining exact-identity budget can only pay for extra zero-occupancy charges
on already-underfull lines and selected-point cover excess.

No symmetry pruning is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_8_count_exact as level8
import generate_refined_8_count_tight as tight8
import residual_tightening
import weight8_tight_frontier as frontier

base=level8.base
NEW3=[i for i,(_family,_key,weight,_group) in enumerate(base.GROUPS) if weight==3]
assert [(base.GROUPS[i][0],base.GROUPS[i][1],base.GROUPS[i][2]) for i in NEW3]==[
    ('row',6,3),('row',15,3),('col',6,3),('col',15,3)
]

TRIPLE_TO_LEVEL8_INDEX={triple:i for i,triple in enumerate(level8.CASES)}
OPEN8=list(frontier.OPEN)
assert len(OPEN8)==1457
assert all(t in TRIPLE_TO_LEVEL8_INDEX for t in OPEN8)


def residual_before_weight3(triple: tuple[int,int,int]) -> int:
    count22_index,k15,k8=triple
    return level8.residual_of((count22_index,k15))-8*k8


def split_cases() -> list[tuple[int,int,int,int]]:
    result=[]
    for count22_index,k15,k8 in OPEN8:
        residual=residual_before_weight3((count22_index,k15,k8))
        assert residual>=0
        for k3 in range(min(4,residual//3)+1):
            result.append((count22_index,k15,k8,k3))
    return result

CASES=split_cases()


def build(case_index: int):
    if not 0<=case_index<len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')
    count22_index,k15,k8,k3=CASES[case_index]
    triple=(count22_index,k15,k8)
    level8_index=TRIPLE_TO_LEVEL8_INDEX[triple]
    cnf,meta=tight8.build(level8_index)

    sat3=[]
    for i in NEW3:
        family,key,_weight,variables=base.GROUPS[i]
        sat3.append(base.make_saturation_var(cnf,variables,f'count3_{family}_{key}'))
    cnf.exact_cardinality(sat3,len(NEW3)-k3)

    before=residual_before_weight3(triple)
    after=before-3*k3
    tightening=residual_tightening.add_residual_tightening(
        cnf,base,after,processed_min_weight=3
    )
    meta.update({
        'count3_case':case_index,
        'count22_case':count22_index,
        'weight15_underfull_count':k15,
        'weight8_underfull_count':k8,
        'weight3_underfull_count':k3,
        'weight3_lines':[
            {'family':base.GROUPS[i][0],'key':base.GROUPS[i][1],'weight':3}
            for i in NEW3
        ],
        'residual_before_weight3':before,
        'minimum_weight3_defect':3*k3,
        'residual_after_minimum_weight3':after,
        'final_positive_weight_level':True,
        'residual_tightening_after_weight3':tightening,
        'count3_frontier_size':len(CASES),
        'rigorous_open_weight8_parents':len(OPEN8),
        'vars':cnf.nvars,
        'clauses':len(cnf.clauses),
    })
    return cnf,meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--list',action='store_true')
    args=ap.parse_args()
    if args.list:
        print(f'parents={len(OPEN8)} children={len(CASES)}')
        for i,(p,k15,k8,k3) in enumerate(CASES):
            print(i,p,k15,k8,k3,residual_before_weight3((p,k15,k8))-3*k3)
        return
    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
