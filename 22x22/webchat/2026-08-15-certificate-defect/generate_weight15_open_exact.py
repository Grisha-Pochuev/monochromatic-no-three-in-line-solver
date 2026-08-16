#!/usr/bin/env python3
"""Generate only the 629 rigorous-open weight-15 count children."""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_refined_15_count_exact as level15
import weight15_frontier as frontier

PAIR_TO_LEVEL15_INDEX={pair:i for i,pair in enumerate(level15.CASES)}
assert len(PAIR_TO_LEVEL15_INDEX)==len(level15.CASES)==723
OPEN_LEVEL15_INDICES=[PAIR_TO_LEVEL15_INDEX[pair] for pair in frontier.OPEN_PAIRS]
assert len(OPEN_LEVEL15_INDICES)==629


def build(open_index: int):
    if not 0 <= open_index < len(OPEN_LEVEL15_INDICES):
        raise SystemExit(f'open index must be 0..{len(OPEN_LEVEL15_INDICES)-1}')
    level15_index=OPEN_LEVEL15_INDICES[open_index]
    cnf,meta=level15.build(level15_index)
    meta.update({
        'open_weight15_index':open_index,
        'level15_case_index':level15_index,
        'rigorous_open_weight15_cases':len(OPEN_LEVEL15_INDICES),
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
