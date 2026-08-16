#!/usr/bin/env python3
"""Next complete defect split, only over the rigorous open weight-22 frontier.

Each parent is first strengthened by the audited exact identity D+E=112.
Then the four certificate groups of weight 15 (row/col 4 and 17) are split
by their exact number k of underfull lines.  Counts that already exceed the
remaining defect budget are impossible and omitted.

This is a complete/disjoint count partition.  No symmetry pruning is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_22_count as level22
import generate_refined_22_count_exact as level22_exact
import weight22_frontier as frontier

base=level22.base
NEW15=[i for i,(_family,_key,weight,_group) in enumerate(base.GROUPS) if weight==15]
assert [(base.GROUPS[i][0],base.GROUPS[i][1],base.GROUPS[i][2]) for i in NEW15]==[
    ('row',4,15),('row',17,15),('col',4,15),('col',17,15)
]

OPEN_COUNT22=list(frontier.OPEN)


def residual_of(count22_index: int) -> int:
    count24_index,k22=level22.CASES[count22_index]
    return level22.residual_of(count24_index)-22*k22


def split_cases() -> list[tuple[int,int]]:
    result=[]
    for count22_index in OPEN_COUNT22:
        residual=residual_of(count22_index)
        assert residual>=0
        for under15_count in range(min(len(NEW15),residual//15)+1):
            result.append((count22_index,under15_count))
    return result

CASES=split_cases()


def build(case_index: int):
    if not 0<=case_index<len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')
    count22_index,under15_count=CASES[case_index]
    cnf,meta=level22_exact.build(count22_index)

    sat15=[]
    for i in NEW15:
        family,key,_weight,variables=base.GROUPS[i]
        sat15.append(base.make_saturation_var(cnf,variables,f'count15_{family}_{key}'))
    # exactly k underfull <=> exactly 4-k saturated with two points
    cnf.exact_cardinality(sat15,len(NEW15)-under15_count)

    residual=residual_of(count22_index)
    meta.update({
        'count15_case':case_index,
        'count22_case':count22_index,
        'weight15_underfull_count':under15_count,
        'weight15_lines':[
            {'family':base.GROUPS[i][0],'key':base.GROUPS[i][1],'weight':15}
            for i in NEW15
        ],
        'residual_before_weight15':residual,
        'minimum_weight15_defect':15*under15_count,
        'residual_after_minimum_weight15':residual-15*under15_count,
        'count15_frontier_size':len(CASES),
        'rigorous_open_weight22_parents':len(OPEN_COUNT22),
        'vars':cnf.nvars,
        'clauses':len(cnf.clauses),
    })
    return cnf,meta


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--list',action='store_true')
    args=ap.parse_args()
    if args.list:
        for i,(p,k) in enumerate(CASES):
            print(i,p,k,residual_of(p)-15*k)
        return
    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
