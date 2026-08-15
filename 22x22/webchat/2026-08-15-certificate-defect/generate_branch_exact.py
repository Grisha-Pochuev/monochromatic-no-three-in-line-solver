#!/usr/bin/env python3
"""Stronger exact SAT encoding for the remaining n=22 defect branches.

This imports the already-audited 140-branch partition from generate_branch.py
and adds one further exact consequence of the same rational certificate.
For every certificate line we distinguish occupancy 2, occupancy 1 and
occupancy 0.  If `sat` means occupancy 2 and `zero` means occupancy 0, the
line defect is exactly

    weight * ((1 - sat) + zero).

For target 34 the certificate identity is

    total_line_defect + selected_point_excess = 112.

After a branch has already spent one weight unit for each explicitly
underfull heavy line, all remaining minimum defect plus point excess must fit
inside the residual budget.  This file encodes that coupled budget directly.
No additional symmetry assumption is introduced.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import generate_branch as base


def complement(cnf: base.CNF, x: int) -> int:
    """Return z exactly equivalent to not x."""
    z = cnf.new()
    cnf.add(z, x)
    cnf.add(-z, -x)
    return z


def make_zero_var(cnf: base.CNF, variables: list[int]) -> int:
    """Return z exactly equivalent to all variables being false."""
    z = cnf.new()
    for x in variables:
        cnf.add(-z, -x)          # z -> not x
    cnf.add_clause([z] + variables)  # all x false -> z
    return z


def build(branch_index: int) -> tuple[base.CNF, dict]:
    if not 0 <= branch_index < len(base.BRANCHES):
        raise SystemExit(f'branch index must be 0..{len(base.BRANCHES)-1}')

    underfull = set(base.BRANCHES[branch_index])
    spent = sum(base.GROUPS[i][2] for i in underfull)
    residual = base.SLACK - spent
    assert residual >= 0

    cnf = base.CNF()

    # Original geometry, exactly as in the audited generator.
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

    heavy = [i for i, (_fam, _key, w, _g) in enumerate(base.GROUPS) if w >= 40]
    for i in heavy:
        cnf.add(-sat[i] if i in underfull else sat[i])

    # Keep the cheap threshold consequences from the first encoding.
    positive_weights = sorted({w for _f, _k, w, _g in base.GROUPS if w > 0}, reverse=True)
    for threshold in positive_weights:
        eligible = [i for i, (_f, _k, w, _g) in enumerate(base.GROUPS)
                    if i not in underfull and w >= threshold]
        if not eligible:
            continue
        max_under = residual // threshold
        required_saturated = len(eligible) - max_under
        if required_saturated > 0:
            cnf.require_at_least([sat[i] for i in eligible], required_saturated)

    # Parallel-family occupancy consequences of exactly 34 selected points.
    cnf.require_at_least(sat[0:22], 12);  cnf.require_at_most(sat[0:22], 17)
    cnf.require_at_least(sat[22:44], 12); cnf.require_at_most(sat[22:44], 17)
    cnf.require_at_least(sat[44:65], 13); cnf.require_at_most(sat[44:65], 17)
    cnf.require_at_least(sat[65:87], 12); cnf.require_at_most(sat[65:87], 17)

    # Coupled exact-certificate consequence.  Each explicitly underfull heavy
    # line has already spent one copy of its weight.  For any other line,
    # not being saturated spends at least one copy.  Occupancy zero spends a
    # second copy for every line, including the explicitly underfull ones.
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
        'branch': branch_index,
        'underfull': [
            {'family': base.GROUPS[i][0], 'key': base.GROUPS[i][1], 'weight': base.GROUPS[i][2]}
            for i in sorted(underfull)
        ],
        'minimum_defect_spent': spent,
        'residual_budget': residual,
        'encoding': 'exact_line_defect_plus_point_excess',
        'vars': cnf.nvars,
        'clauses': len(cnf.clauses),
    }
    return cnf, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    cnf, meta = build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
