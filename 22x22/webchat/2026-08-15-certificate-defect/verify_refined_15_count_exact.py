#!/usr/bin/env python3
"""Structural audit of the current rigorous weight-15 count partition."""
from collections import Counter

import generate_refined_15_count_exact as model
import weight22_frontier as frontier

assert model.OPEN_COUNT22==frontier.OPEN
assert set(model.OPEN_COUNT22).isdisjoint(frontier.CLOSED)
assert set(model.OPEN_COUNT22)|set(frontier.CLOSED)==set(range(395))

expected=[]
for parent in model.OPEN_COUNT22:
    residual=model.residual_of(parent)
    assert residual>=0
    for k15 in range(min(4,residual//15)+1):
        expected.append((parent,k15))

assert model.CASES==expected
assert len(set(model.CASES))==len(model.CASES)
assert {p for p,_k in model.CASES}==set(model.OPEN_COUNT22)
assert all(15*k<=model.residual_of(p) for p,k in model.CASES)

shape=Counter(k for _p,k in model.CASES)
print(
    'PASS n22 weight-15 exact partition '
    f'parents={len(model.OPEN_COUNT22)} children={len(model.CASES)} shape={dict(shape)}'
)
