#!/usr/bin/env python3
"""Add the audited lower half D+E>=112 to the weight-22 count frontier.

This wrapper does not change the partition.  It takes one of the 395 complete
weight-22 count children and adds the exact certificate identity to the
already present upper defect/excess budget.  Hence every genuine 34-point
configuration in that child remains feasible.

No symmetry rule is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import exact_identity
import generate_refined_22_count as model
from generate_branch_exact import complement, make_zero_var


def build(case_index: int):
    cnf, meta = model.build(case_index)
    exact_identity.add_n22_exact_identity(cnf, model.base, make_zero_var, complement)
    meta.update({
        'exact_identity_lower_half': True,
        'exact_identity_target': model.base.SLACK,
        'vars_after_exact_identity': cnf.nvars,
        'clauses_after_exact_identity': len(cnf.clauses),
    })
    return cnf, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if not 0 <= args.index < len(model.CASES):
        raise SystemExit(f'--index must be in 0..{len(model.CASES)-1}')
    cnf, meta = build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
