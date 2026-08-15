#!/usr/bin/env python3
"""Dependency-free audit of the weight-35 refinement of n=22 survivors."""
from __future__ import annotations

import itertools

SLACK = 112
SURVIVORS = [
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,26,
    29,30,31,32,33,34,41,43,46,47,49,52,53,55,56,59,60,62,65,66,67,69,
    82,84,87,88,91,93,96,97,98,100,104,107,108,109,112,113,115,116,
    122,123,124,125,128,129,130,133,134,136,139,
]
assert len(SURVIVORS) == 76

# Parent minimum defects copied from the independently collected first run.
# They are determined purely by the exact underfull heavy-line subset.
RESIDUAL = {
0:112,1:49,2:64,3:64,4:49,5:49,6:64,7:64,8:49,9:68,10:52,11:40,12:27,
13:13,16:13,17:27,18:40,19:52,20:68,21:72,22:58,23:45,24:32,25:20,26:12,
29:12,30:20,31:32,32:45,33:58,34:72,41:9,43:16,46:16,47:16,49:20,52:20,
53:24,55:10,56:24,59:16,60:16,62:20,65:20,66:24,67:10,69:24,82:16,
84:20,87:20,88:24,91:24,93:20,96:20,97:24,98:10,100:24,104:9,107:24,
108:28,109:14,112:14,113:28,115:12,116:12,122:12,123:12,124:28,125:14,
128:14,129:28,130:18,133:18,134:32,136:18,139:18,
}
assert set(RESIDUAL) == set(SURVIVORS)

# Exactly four additional certificate lines have weight 35:
# row 2, row 19, column 2, column 19.
new_lines = ('row2','row19','col2','col19')

children=[]
per_parent={}
for parent in SURVIVORS:
    r=RESIDUAL[parent]
    local=[]
    for k in range(5):
        for subset in itertools.combinations(new_lines,k):
            if 35*k <= r:
                local.append(subset)
                children.append((parent,subset))
    per_parent[parent]=len(local)

assert len(children)==182
assert len(set(children))==182
assert sum(per_parent.values())==182

# Expected shape: low residual -> 1 child, enough for one extra 35-line -> 5,
# enough for two -> 11, and the completely unsplit parent 0 allows up to three
# extra lines -> 15. Four would already cost 140>112.
from collections import Counter
shape=Counter(per_parent.values())
assert shape == Counter({1:55,5:18,11:2,15:1})

print(
    'PASS n22 weight-35 refinement audit '
    f'parents={len(SURVIVORS)} children={len(children)} shape={dict(shape)}'
)
