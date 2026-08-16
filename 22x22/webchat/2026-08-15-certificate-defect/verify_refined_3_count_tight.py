#!/usr/bin/env python3
"""Structural audit of the final positive-weight count partition."""
from collections import Counter

import generate_refined_3_count_tight as model
import weight8_tight_frontier as frontier

assert model.OPEN8==frontier.OPEN
assert len(model.OPEN8)==1457
expected=[]
for triple in model.OPEN8:
    residual=model.residual_before_weight3(triple)
    assert residual>=0
    for k3 in range(min(4,residual//3)+1):
        expected.append((*triple,k3))

assert model.CASES==expected
assert len(set(model.CASES))==len(model.CASES)
assert {(p,k15,k8) for p,k15,k8,_k3 in model.CASES}==set(model.OPEN8)
assert all(3*k3<=model.residual_before_weight3((p,k15,k8)) for p,k15,k8,k3 in model.CASES)
shape=Counter(k3 for _p,_k15,_k8,k3 in model.CASES)
print(f'PASS final weight3 partition parents={len(model.OPEN8)} children={len(model.CASES)} shape={dict(shape)} symmetry=none')
