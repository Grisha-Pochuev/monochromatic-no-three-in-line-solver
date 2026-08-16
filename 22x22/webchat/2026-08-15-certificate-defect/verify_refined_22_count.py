#!/usr/bin/env python3
"""Arithmetic/structural audit of the weight-22 count refinement."""
from collections import Counter

import generate_refined_22_count as model

assert len(model.refined24.CASES) == 261
assert len(model.CLOSED_COUNT24) == 17
assert len(model.OPEN_COUNT24) == 244
assert not (set(model.OPEN_COUNT24) & model.CLOSED_COUNT24)
assert set(model.OPEN_COUNT24) | model.CLOSED_COUNT24 == set(range(261))

assert [(model.base.GROUPS[i][0], model.base.GROUPS[i][1], model.base.GROUPS[i][2]) for i in model.NEW22] == [
    ('sum', 6, 22), ('sum', 36, 22)
]

expected = []
for parent in model.OPEN_COUNT24:
    residual = model.residual_of(parent)
    assert residual >= 0
    for k22 in range(min(2, residual // 22) + 1):
        expected.append((parent, k22))

assert model.CASES == expected
assert len(model.CASES) == 395
assert len(set(model.CASES)) == 395
assert {p for p, _k in model.CASES} == set(model.OPEN_COUNT24)

shape = Counter(k for _p, k in model.CASES)
assert shape == Counter({0: 244, 1: 118, 2: 33})

# The split is exhaustive and disjoint: every assignment to the two underfull
# indicators has a unique count k=0,1,2, and budget-infeasible counts are
# omitted because each underfull weight-22 line costs at least 22.
print(f'PASS n22 weight-22 count partition parents=244 children=395 shape={dict(shape)}')
