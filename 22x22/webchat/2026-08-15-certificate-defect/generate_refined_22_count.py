#!/usr/bin/env python3
"""Count-based weight-22 refinement of the current n=22 frontier.

The weight-24 count run 31897269984 split the 151 still-open strengthened
weight-35 cases into 261 children. It proved 17 of those children UNSAT and
left 244 open (all TIMEOUT; no SAT result).

The next positive certificate level contains exactly two lines of weight 22:
sum diagonals x+y=6 and x+y=36. This complete split fixes only the exact
number k of those two lines that are underfull. For a parent with residual
certificate budget R after its already-fixed weight-24 count, necessarily
0 <= k <= min(2,floor(R/22)). Across the 244 open parents this gives exactly
395 children.

No symmetry assumption is used. In particular, no transposition-based
identification is made.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_24_count as refined24

# Exact UNSAT children from run 31897269984. TIMEOUT children stay open.
CLOSED_COUNT24 = {
    35, 64, 71, 100, 118, 130, 154, 200, 214,
    216, 222, 224, 229, 231, 235, 237, 239,
}
assert len(refined24.CASES) == 261
OPEN_COUNT24 = [i for i in range(len(refined24.CASES)) if i not in CLOSED_COUNT24]
assert len(OPEN_COUNT24) == 244

base = refined24.base
NEW22 = [i for i, (_family, _key, weight, _group) in enumerate(base.GROUPS) if weight == 22]
assert [(base.GROUPS[i][0], base.GROUPS[i][1]) for i in NEW22] == [
    ('sum', 6), ('sum', 36)
]


def residual_of(count24_index: int) -> int:
    refined_index, under24_count = refined24.CASES[count24_index]
    return refined24.residual_of(refined_index) - 24 * under24_count


def split_cases() -> list[tuple[int, int]]:
    result = []
    for count24_index in OPEN_COUNT24:
        residual = residual_of(count24_index)
        for under22_count in range(min(len(NEW22), residual // 22) + 1):
            result.append((count24_index, under22_count))
    assert len(result) == 395
    return result


CASES = split_cases()


def build(case_index: int):
    if not 0 <= case_index < len(CASES):
        raise SystemExit(f'case index must be 0..{len(CASES)-1}')

    count24_index, under22_count = CASES[case_index]
    cnf, meta = refined24.build(count24_index)

    sat22 = []
    for i in NEW22:
        family, key, _weight, variables = base.GROUPS[i]
        sat22.append(base.make_saturation_var(cnf, variables, f'count22_{family}_{key}'))

    # Exactly k are underfull <=> exactly 2-k are saturated with two points.
    cnf.exact_cardinality(sat22, len(NEW22) - under22_count)

    residual = residual_of(count24_index)
    refined_index, under24_count = refined24.CASES[count24_index]
    meta.update({
        'count22_case': case_index,
        'count24_case': count24_index,
        'refined35_case': refined_index,
        'weight24_underfull_count': under24_count,
        'weight22_underfull_count': under22_count,
        'weight22_lines': [
            {'family': base.GROUPS[i][0], 'key': base.GROUPS[i][1], 'weight': 22}
            for i in NEW22
        ],
        'residual_before_weight22': residual,
        'minimum_weight22_defect': 22 * under22_count,
        'residual_after_minimum_weight22': residual - 22 * under22_count,
        'count22_frontier_size': len(CASES),
        'vars': cnf.nvars,
        'clauses': len(cnf.clauses),
    })
    return cnf, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args()

    if args.list:
        for i, (count24_index, k22) in enumerate(CASES):
            refined_index, k24 = refined24.CASES[count24_index]
            print(i, count24_index, refined_index, k24, k22, residual_of(count24_index) - 22 * k22)
        return

    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    cnf, meta = build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
