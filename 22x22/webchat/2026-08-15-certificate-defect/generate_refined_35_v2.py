#!/usr/bin/env python3
"""Latest weight-35 refinement after the exact-defect follow-up.

The first 140-branch run proved 64 parents UNSAT.  The exact-defect follow-up
then proved seven more of its 76 survivors UNSAT:

    41, 47, 55, 67, 98, 104, 123.

This wrapper reuses the audited strengthened weight-35 encoding but removes
all children of those seven already-closed parents.  Each of the seven had
residual budget below 35 and hence exactly one weight-35 child, so the refined
frontier decreases from 182 to 175 cases.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_35 as model

NEWLY_CLOSED_PARENTS = {41, 47, 55, 67, 98, 104, 123}
CASES = [case for case in model.CASES if case[0] not in NEWLY_CLOSED_PARENTS]
assert len(model.CASES) == 182
assert len(CASES) == 175
assert not ({parent for parent, _extra in CASES} & NEWLY_CLOSED_PARENTS)

# Make the imported build() resolve the reduced complete case list.
model.CASES = CASES


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args()

    if args.list:
        for index, (parent, extra) in enumerate(CASES):
            spent = sum(model.base.GROUPS[j][2] for j in model.base.BRANCHES[parent]) + 35 * len(extra)
            print(index, parent, [model.base.GROUPS[j][:3] for j in extra], model.base.SLACK - spent)
        return

    if args.index is None or args.output is None:
        raise SystemExit('--index and --output are required unless --list is used')
    if not 0 <= args.index < len(CASES):
        raise SystemExit(f'--index must be in 0..{len(CASES)-1}')

    cnf, meta = model.build(args.index)
    meta['removed_exact_unsat_parents'] = sorted(NEWLY_CLOSED_PARENTS)
    meta['refined_frontier_size'] = len(CASES)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
