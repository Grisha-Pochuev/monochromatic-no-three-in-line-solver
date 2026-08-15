#!/usr/bin/env python3
"""Dependency-free arithmetic audit of the weight-24 count refinement."""

# Residual budgets of the 151 surviving strengthened weight-35 cases are
# derived from their already fixed minimum certificate defect.  Only their
# distribution is needed to check completeness of the count split.
from collections import Counter

RESIDUAL_DISTRIBUTION = {
    112:1, 77:4, 72:2, 68:2, 64:4, 58:2, 52:2, 49:4, 45:2, 42:6,
    40:2, 37:8, 33:8, 32:3, 29:16, 28:4, 27:2, 24:9, 23:8, 20:10,
    18:4, 17:8, 16:5, 14:20, 13:2, 12:5, 10:8,
}
assert sum(RESIDUAL_DISTRIBUTION.values()) == 151

# Six certificate lines have weight exactly 24.  In a case with residual R,
# if k of them are underfull they spend at least 24k, hence exactly the values
# k=0..min(6,floor(R/24)) cover every possibility without overlap.
branch_count = sum(
    multiplicity * (min(6, residual // 24) + 1)
    for residual, multiplicity in RESIDUAL_DISTRIBUTION.items()
)
assert branch_count == 261

shape = Counter()
for residual, multiplicity in RESIDUAL_DISTRIBUTION.items():
    shape[min(6, residual // 24) + 1] += multiplicity
assert shape == Counter({1:70, 2:60, 3:14, 4:6, 5:1})

print(f'PASS n22 weight-24 count partition parents=151 children=261 shape={dict(shape)}')
