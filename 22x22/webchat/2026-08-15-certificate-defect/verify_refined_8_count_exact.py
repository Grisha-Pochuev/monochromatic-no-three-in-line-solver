#!/usr/bin/env python3
"""Structural audit of the complete weight-8 defect count partition."""
from collections import Counter

import generate_refined_8_count_exact as model
import weight15_frontier as frontier

assert model.OPEN15==frontier.OPEN_PAIRS
assert len(model.OPEN15)==629

expected=[]
for pair in model.OPEN15:
    residual=model.residual_of(pair)
    assert residual>=0
    for k8 in range(min(4,residual//8)+1):
        expected.append((pair[0],pair[1],k8))

assert model.CASES==expected
assert len(model.CASES)==1951
assert len(set(model.CASES))==1951
assert {(p,k15) for p,k15,_k8 in model.CASES}==set(model.OPEN15)
assert all(8*k8<=model.residual_of((p,k15)) for p,k15,k8 in model.CASES)
shape=Counter(k8 for _p,_k15,k8 in model.CASES)
assert shape==Counter({0:629,1:546,2:376,3:246,4:154})
print(f'PASS n22 weight-8 exact partition parents=629 children=1951 shape={dict(shape)}')
