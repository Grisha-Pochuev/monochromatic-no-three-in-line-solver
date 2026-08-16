#!/usr/bin/env python3
"""Structural audit for the compact 1,469-case tightened weight-8 frontier."""
from collections import Counter

import generate_weight8_open_tight as model
import weight8_frontier as frontier

assert model.OPEN_TRIPLES==frontier.OPEN
assert len(model.OPEN_TRIPLES)==1469
assert len(model.OPEN_LEVEL8_INDICES)==1469
assert len(set(model.OPEN_LEVEL8_INDICES))==1469
assert all(model.level8.CASES[i]==t for i,t in zip(model.OPEN_LEVEL8_INDICES,model.OPEN_TRIPLES))
assert set(model.OPEN_TRIPLES).isdisjoint(frontier.CLOSED)
assert set(model.OPEN_TRIPLES)|set(frontier.CLOSED)==set(model.level8.CASES)
assert Counter(k8 for _p,_k15,k8 in model.OPEN_TRIPLES)==Counter({0:621,1:443,2:234,3:112,4:59})
print('PASS compact tightened weight8 frontier open=1469 closed=474 total=1943 symmetry=none')
