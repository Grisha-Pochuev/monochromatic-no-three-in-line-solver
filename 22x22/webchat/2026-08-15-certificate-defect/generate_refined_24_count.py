#!/usr/bin/env python3
"""Count-based weight-24 refinement of the current n=22 frontier.

After the strengthened weight-35 run, 24 of its 175 cases are UNSAT and 151
remain.  The next certificate level contains exactly six lines of weight 24:
row 3, row 18, column 3, column 18, and difference diagonals -16 and 16.

Instead of branching over the identities of the underfull weight-24 lines
(which would create 1107 cases), this complete split fixes only their exact
number k.  For a parent with residual certificate budget R, necessarily
0 <= k <= floor(R/24).  Across the 151 surviving parents this gives exactly
261 cases.  The SAT solver still chooses which particular weight-24 lines are
underfull inside each count branch.

No symmetry assumption is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_35_v2 as refined35

# Exact UNSAT results of strengthened run 31896568122.
CLOSED_REFINED = {
    11,12,13,14,66,67,68,69,75,76,77,78,
    94,95,96,97,98,99,131,132,133,134,135,136,
}
OPEN_REFINED = [i for i in range(len(refined35.CASES)) if i not in CLOSED_REFINED]
assert len(refined35.CASES) == 175
assert len(OPEN_REFINED) == 151

base_model = refined35.model
base = base_model.base
NEW24 = [i for i, (_family,_key,weight,_group) in enumerate(base.GROUPS) if weight == 24]
assert [(base.GROUPS[i][0],base.GROUPS[i][1]) for i in NEW24] == [
    ('row',3),('row',18),('col',3),('col',18),('diff',-16),('diff',16)
]


def residual_of(refined_index: int) -> int:
    parent, extra35 = refined35.CASES[refined_index]
    spent = sum(base.GROUPS[j][2] for j in base.BRANCHES[parent]) + 35*len(extra35)
    return base.SLACK - spent


def split_cases() -> list[tuple[int,int]]:
    result=[]
    for refined_index in OPEN_REFINED:
        residual=residual_of(refined_index)
        for under24_count in range(min(len(NEW24), residual//24)+1):
            result.append((refined_index,under24_count))
    assert len(result) == 261
    return result

CASES=split_cases()


def build(case_index: int):
    if not 0 <= case_index < len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')
    refined_index, under24_count = CASES[case_index]
    cnf, meta = base_model.build(refined_index)

    # Duplicate exact occupancy-two flags for just the six weight-24 lines.
    # They are equivalent to the flags already present in the base formula,
    # but reintroducing them here keeps this wrapper independent of internal
    # auxiliary variable numbering.
    sat24=[]
    for i in NEW24:
        family,key,_weight,variables=base.GROUPS[i]
        sat24.append(base.make_saturation_var(cnf,variables,f'count24_{family}_{key}'))

    # Exactly k are underfull <=> exactly 6-k are saturated with two points.
    cnf.exact_cardinality(sat24,len(NEW24)-under24_count)

    residual=residual_of(refined_index)
    meta.update({
        'count24_case':case_index,
        'refined35_case':refined_index,
        'weight24_underfull_count':under24_count,
        'weight24_lines':[
            {'family':base.GROUPS[i][0],'key':base.GROUPS[i][1],'weight':24}
            for i in NEW24
        ],
        'residual_before_weight24':residual,
        'minimum_weight24_defect':24*under24_count,
        'residual_after_minimum_weight24':residual-24*under24_count,
        'count24_frontier_size':len(CASES),
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
        for i,(r,k) in enumerate(CASES):
            print(i,r,k,residual_of(r)-24*k)
        return
    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__=='__main__':
    main()
