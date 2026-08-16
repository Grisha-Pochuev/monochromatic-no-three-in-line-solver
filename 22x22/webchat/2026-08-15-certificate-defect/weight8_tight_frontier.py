#!/usr/bin/env python3
"""Rigorous n=22 frontier after residual-tightened SAT run 31921064464.

The preceding exact-Farkas weight-8 frontier contains 1,469 rigorous-open
children.  Run 31921064464 regenerated exactly those children with only safe
residual-budget consequences.  It returned 12 UNSAT, 1,457 TIMEOUT, no SAT
and no errors.  TIMEOUT cases remain open.

The UNSAT indices below are indices in generate_weight8_open_tight.OPEN_TRIPLES,
so the mapping to the underlying (count22,k15,k8) child is deterministic and
reproducible.  No symmetry pruning is used.
"""
from __future__ import annotations

from collections import Counter
import generate_weight8_open_tight as source

RUN=31921064464
CLOSED_OPEN_INDICES={
    807,860,863,986,1125,1167,1169,1172,1180,1188,1190,1243,
}
assert len(CLOSED_OPEN_INDICES)==12
assert all(0<=i<len(source.OPEN_TRIPLES) for i in CLOSED_OPEN_INDICES)

CLOSED={source.OPEN_TRIPLES[i] for i in CLOSED_OPEN_INDICES}
assert len(CLOSED)==12

OPEN=[
    triple for i,triple in enumerate(source.OPEN_TRIPLES)
    if i not in CLOSED_OPEN_INDICES
]
assert len(source.OPEN_TRIPLES)==1469
assert len(OPEN)==1457
assert not (set(OPEN) & CLOSED)
assert set(OPEN) | CLOSED == set(source.OPEN_TRIPLES)

if __name__=='__main__':
    print(
        f'PASS weight8 tightened frontier run={RUN} '
        f'parents=1469 unsat={len(CLOSED)} open={len(OPEN)} '
        f'k8_shape={dict(Counter(k8 for _p,_k15,k8 in OPEN))} symmetry=none'
    )
