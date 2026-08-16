#!/usr/bin/env python3
"""Generate only the 1,469 rigorous-open weight-8 children, tightened by residual.

The underlying partition is the complete 1,943-child weight-8 split.  The 474
children removed here have independent exact integer Farkas proofs recorded in
weight8_frontier.py.  Every generated child keeps the exact identity D+E=112
and adds only safe consequences of its remaining residual budget.

No symmetry pruning is used.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_8_count_exact as level8
import generate_refined_8_count_tight as tight8
import weight8_frontier as frontier

TRIPLE_TO_LEVEL8_INDEX={triple:i for i,triple in enumerate(level8.CASES)}
assert len(TRIPLE_TO_LEVEL8_INDEX)==1943
OPEN_TRIPLES=list(frontier.OPEN)
OPEN_LEVEL8_INDICES=[TRIPLE_TO_LEVEL8_INDEX[t] for t in OPEN_TRIPLES]
assert len(OPEN_LEVEL8_INDICES)==1469


def build(open_index: int):
    if not 0 <= open_index < len(OPEN_LEVEL8_INDICES):
        raise SystemExit(f'open index must be 0..{len(OPEN_LEVEL8_INDICES)-1}')
    level8_index=OPEN_LEVEL8_INDICES[open_index]
    cnf,meta=tight8.build(level8_index)
    meta.update({
        'open_weight8_index':open_index,
        'level8_case_index':level8_index,
        'weight8_triple':list(OPEN_TRIPLES[open_index]),
        'rigorous_open_weight8_cases':len(OPEN_LEVEL8_INDICES),
    })
    return cnf,meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    cnf,meta=build(args.index)
    cnf.write(args.output)
    print(meta)

if __name__=='__main__':
    main()
