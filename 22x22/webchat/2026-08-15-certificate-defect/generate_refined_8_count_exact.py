#!/usr/bin/env python3
"""Complete exact-count refinement at certificate weight 8.

Input frontier: 629 rigorous-open weight-15 count children.
New lines: row/col 5 and 16, all of certificate weight 8.
For each parent we split by the exact number k=0..4 of these four lines that
are underfull, omitting only counts whose minimum defect 8*k already exceeds
the parent's remaining certificate budget.

The parent CNF already contains the audited exact identity D+E=112.  This is a
complete and disjoint partition; no symmetry pruning is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_15_count_exact as level15
import weight15_frontier as frontier

base=level15.base
NEW8=[i for i,(_family,_key,weight,_group) in enumerate(base.GROUPS) if weight==8]
assert [(base.GROUPS[i][0],base.GROUPS[i][1],base.GROUPS[i][2]) for i in NEW8]==[
    ('row',5,8),('row',16,8),('col',5,8),('col',16,8)
]

PAIR_TO_LEVEL15_INDEX={pair:i for i,pair in enumerate(level15.CASES)}
OPEN15=list(frontier.OPEN_PAIRS)
assert len(OPEN15)==629


def residual_of(pair: tuple[int,int]) -> int:
    count22_index,k15=pair
    return level15.residual_of(count22_index)-15*k15


def split_cases() -> list[tuple[int,int,int]]:
    result=[]
    for count22_index,k15 in OPEN15:
        residual=residual_of((count22_index,k15))
        assert residual>=0
        for k8 in range(min(4,residual//8)+1):
            result.append((count22_index,k15,k8))
    return result

CASES=split_cases()
assert len(CASES)==1951


def build(case_index: int):
    if not 0<=case_index<len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')
    count22_index,k15,k8=CASES[case_index]
    pair=(count22_index,k15)
    parent_index=PAIR_TO_LEVEL15_INDEX[pair]
    cnf,meta=level15.build(parent_index)

    sat8=[]
    for i in NEW8:
        family,key,_weight,variables=base.GROUPS[i]
        sat8.append(base.make_saturation_var(cnf,variables,f'count8_{family}_{key}'))
    cnf.exact_cardinality(sat8,len(NEW8)-k8)

    residual=residual_of(pair)
    meta.update({
        'count8_case':case_index,
        'count22_case':count22_index,
        'weight15_underfull_count':k15,
        'weight8_underfull_count':k8,
        'weight8_lines':[
            {'family':base.GROUPS[i][0],'key':base.GROUPS[i][1],'weight':8}
            for i in NEW8
        ],
        'residual_before_weight8':residual,
        'minimum_weight8_defect':8*k8,
        'residual_after_minimum_weight8':residual-8*k8,
        'count8_frontier_size':len(CASES),
        'rigorous_open_weight15_parents':len(OPEN15),
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
        for i,(p,k15,k8) in enumerate(CASES):
            print(i,p,k15,k8,residual_of((p,k15))-8*k8)
        return
    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
