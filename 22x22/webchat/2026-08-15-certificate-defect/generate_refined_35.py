#!/usr/bin/env python3
"""Exact weight-35 refinement of the 76 surviving n=22 defect branches.

The first certified partition fixes the exact underfull subset among the 37
certificate lines of weight at least 40.  Its first run left 76 branches
unresolved.  The only additional certificate lines with weight at least 35
are row 2, row 19, column 2 and column 19, each of weight 35.

For every surviving parent branch this script enumerates the exact underfull
subset of those four lines subject only to the remaining defect budget.  This
produces 182 complete child branches.  No symmetry assumption is used.

Each child uses the stronger exact-defect encoding:
  line defect + selected-point cover excess <= 112,
with the minimum defect of explicitly underfull lines already deducted.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import generate_branch as base
from generate_branch_exact import complement, make_zero_var

SURVIVORS = [
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,26,
    29,30,31,32,33,34,41,43,46,47,49,52,53,55,56,59,60,62,65,66,67,69,
    82,84,87,88,91,93,96,97,98,100,104,107,108,109,112,113,115,116,
    122,123,124,125,128,129,130,133,134,136,139,
]
assert len(SURVIVORS) == 76

NEW35 = [
    i for i, (family, key, weight, _group) in enumerate(base.GROUPS)
    if weight == 35
]
assert [(base.GROUPS[i][0], base.GROUPS[i][1]) for i in NEW35] == [
    ('row', 2), ('row', 19), ('col', 2), ('col', 19)
]


def refined_cases() -> list[tuple[int, tuple[int, ...]]]:
    out: list[tuple[int, tuple[int, ...]]] = []
    for parent in SURVIVORS:
        parent_under = base.BRANCHES[parent]
        parent_spent = sum(base.GROUPS[i][2] for i in parent_under)
        residual = base.SLACK - parent_spent
        for k in range(len(NEW35) + 1):
            for extra in itertools.combinations(NEW35, k):
                if 35 * k <= residual:
                    out.append((parent, extra))
    assert len(out) == 182
    return out

CASES = refined_cases()


def build(case_index: int) -> tuple[base.CNF, dict]:
    if not 0 <= case_index < len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')

    parent, extra35 = CASES[case_index]
    underfull = set(base.BRANCHES[parent]) | set(extra35)
    spent = sum(base.GROUPS[i][2] for i in underfull)
    residual = base.SLACK - spent
    assert residual >= 0

    cnf = base.CNF()

    # Original geometry.
    for line in base.maximal_lines():
        for a, b, c in itertools.combinations(line, 3):
            cnf.add(-a, -b, -c)
    cnf.exact_cardinality(list(range(1, len(base.POINTS) + 1)), base.TARGET)

    # Exact occupancy-2 and occupancy-0 flags for all certificate lines.
    sat: list[int] = []
    zero: list[int] = []
    for family, key, weight, variables in base.GROUPS:
        sat.append(base.make_saturation_var(cnf, variables, f'{family}_{key}'))
        zero.append(make_zero_var(cnf, variables))

    # Exact actual-underfull subset for every certificate line of weight >=35.
    heavy35 = [i for i, (_f, _k, w, _g) in enumerate(base.GROUPS) if w >= 35]
    assert len(heavy35) == 41
    for i in heavy35:
        cnf.add(-sat[i] if i in underfull else sat[i])

    # Cheap consequences for lighter lines from the remaining budget.
    positive_weights = sorted({w for _f, _k, w, _g in base.GROUPS if w > 0}, reverse=True)
    for threshold in positive_weights:
        eligible = [
            i for i, (_f, _k, w, _g) in enumerate(base.GROUPS)
            if i not in underfull and w >= threshold
        ]
        if not eligible:
            continue
        required_saturated = len(eligible) - residual // threshold
        if required_saturated > 0:
            cnf.require_at_least([sat[i] for i in eligible], required_saturated)

    # Occupancy consequences of exactly 34 points in each parallel family.
    cnf.require_at_least(sat[0:22], 12);  cnf.require_at_most(sat[0:22], 17)
    cnf.require_at_least(sat[22:44], 12); cnf.require_at_most(sat[22:44], 17)
    cnf.require_at_least(sat[44:65], 13); cnf.require_at_most(sat[44:65], 17)
    cnf.require_at_least(sat[65:87], 12); cnf.require_at_most(sat[65:87], 17)

    # Coupled exact-certificate budget: after the first weight unit for every
    # explicit underfull line is paid, every other underfull line, every zero
    # occupancy extra unit, and every selected-point coverage excess must fit
    # inside `residual`.
    items: list[tuple[int, int]] = []
    for p in base.POINTS:
        excess = base.point_excess(p)
        if excess > 0:
            items.append((base.PID[p], excess))

    for i, (_family, _key, weight, _variables) in enumerate(base.GROUPS):
        if weight <= 0:
            continue
        if i not in underfull:
            items.append((complement(cnf, sat[i]), weight))
        items.append((zero[i], weight))

    cnf.weighted_at_most(items, residual)

    meta = {
        'case': case_index,
        'parent_branch': parent,
        'extra_underfull_35': [
            {'family': base.GROUPS[i][0], 'key': base.GROUPS[i][1], 'weight': 35}
            for i in extra35
        ],
        'all_underfull': [
            {'family': base.GROUPS[i][0], 'key': base.GROUPS[i][1], 'weight': base.GROUPS[i][2]}
            for i in sorted(underfull)
        ],
        'minimum_defect_spent': spent,
        'residual_budget': residual,
        'vars': cnf.nvars,
        'clauses': len(cnf.clauses),
    }
    return cnf, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args()
    if args.list:
        for i, (parent, extra) in enumerate(CASES):
            spent = sum(base.GROUPS[j][2] for j in base.BRANCHES[parent]) + 35 * len(extra)
            print(i, parent, [base.GROUPS[j][:3] for j in extra], base.SLACK - spent)
        return
    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf, meta = build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
