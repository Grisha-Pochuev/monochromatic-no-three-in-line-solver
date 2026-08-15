#!/usr/bin/env python3
"""Dependency-free exact audit of the 140-branch n=22 defect partition."""
from __future__ import annotations

import itertools

N = 22
TARGET = 34
Q = 187
OBJECTIVE = 6470
SLACK = OBJECTIVE - TARGET * Q

ROW = [63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63]
COL = ROW[:]
DIFF = {-20:0,-18:0,-16:24,-14:44,-12:60,-10:72,-8:85,-6:99,-4:109,
        -2:115,0:117,2:115,4:109,6:99,8:85,10:72,12:60,14:44,16:24,
        18:0,20:0}
SUM = {0:0,2:0,4:0,6:22,8:40,10:54,12:67,14:80,16:92,18:100,
       20:104,22:104,24:100,26:92,28:80,30:67,32:54,34:40,36:22,
       38:0,40:0,42:0}

points = [(x,y) for y in range(N) for x in range(N) if (x+y)%2 == 0]
assert len(points) == 242
assert SLACK == 112

# Exact dual objective: each line has capacity two.
weight_sum = sum(ROW) + sum(COL) + sum(DIFF.values()) + sum(SUM.values())
assert 2 * weight_sum == OBJECTIVE

# Exact point coverage.
covers = {
    (x,y): ROW[y] + COL[x] + DIFF[x-y] + SUM[x+y]
    for x,y in points
}
assert min(covers.values()) >= Q
assert min(covers.values()) == Q

# Build the certificate-line list exactly as the branch generator does.
groups = []
for y,w in enumerate(ROW): groups.append(('row',y,w))
for x,w in enumerate(COL): groups.append(('col',x,w))
for d,w in DIFF.items(): groups.append(('diff',d,w))
for s,w in SUM.items(): groups.append(('sum',s,w))
assert len(groups) == 87

heavy = [i for i,g in enumerate(groups) if g[2] >= 40]
forced = [i for i in heavy if groups[i][2] > SLACK]
candidates = [i for i in heavy if i not in set(forced)]
assert len(heavy) == 37
assert len(forced) == 3
assert [groups[i] for i in forced] == [
    ('diff',-2,115), ('diff',0,117), ('diff',2,115)
]
assert len(candidates) == 34

# A heavy underfull line contributes at least its weight to the line-defect D.
# Since D <= 112, three candidate heavy lines can never all be underfull.
assert 3 * min(groups[i][2] for i in candidates) > SLACK

# Enumerate every possible underfull subset of heavy candidate lines whose
# mandatory minimum defect can fit in the budget.  This is the complete split.
complete = [()]
complete += [(i,) for i in candidates if groups[i][2] <= SLACK]
complete += [
    (a,b) for a,b in itertools.combinations(candidates,2)
    if groups[a][2] + groups[b][2] <= SLACK
]
assert len(complete) == 140
assert len(set(complete)) == 140

print(
    'PASS n22 defect partition audit '
    f'points={len(points)} objective={OBJECTIVE}/{Q} slack={SLACK} '
    f'heavy={len(heavy)} forced={len(forced)} branches={len(complete)} '
    f'min_cover={min(covers.values())}'
)
