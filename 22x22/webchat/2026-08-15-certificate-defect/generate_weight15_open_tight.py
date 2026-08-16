#!/usr/bin/env python3
"""Generate a rigorous-open weight-15 child with safe residual tightening."""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_weight15_open_exact as open15
import generate_refined_15_count_exact as level15
import residual_tightening


def build(open_index: int):
    cnf,meta=open15.build(open_index)
    level15_index=open15.OPEN_LEVEL15_INDICES[open_index]
    count22_index,k15=level15.CASES[level15_index]
    residual=level15.residual_of(count22_index)-15*k15
    tightening=residual_tightening.add_residual_tightening(
        cnf,level15.base,residual,processed_min_weight=15
    )
    meta.update({
        'residual_after_minimum_weight15':residual,
        'residual_tightening':tightening,
        'vars_after_tightening':cnf.nvars,
        'clauses_after_tightening':len(cnf.clauses),
    })
    return cnf,meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if not 0<=args.index<len(open15.OPEN_LEVEL15_INDICES):
        raise SystemExit(f'--index must be 0..{len(open15.OPEN_LEVEL15_INDICES)-1}')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
