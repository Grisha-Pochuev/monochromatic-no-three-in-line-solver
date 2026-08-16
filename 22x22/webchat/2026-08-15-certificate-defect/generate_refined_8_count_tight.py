#!/usr/bin/env python3
"""Weight-8 count generator plus safe residual consequences of D+E=112."""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_8_count_exact as level8
import residual_tightening


def build(case_index: int):
    cnf,meta=level8.build(case_index)
    count22_index,k15,k8=level8.CASES[case_index]
    residual=level8.residual_of((count22_index,k15))-8*k8
    tightening=residual_tightening.add_residual_tightening(
        cnf,level8.base,residual,processed_min_weight=8
    )
    meta.update({
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
    if not 0<=args.index<len(level8.CASES):
        raise SystemExit(f'--index must be 0..{len(level8.CASES)-1}')
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
