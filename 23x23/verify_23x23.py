#!/usr/bin/env python3
"""Independently verify the stored 35-point 23x23 construction."""
import itertools
import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("config_35.json")
data = json.loads(path.read_text(encoding="utf-8"))

assert data["board_size"] == 23
assert data["point_count"] == 35
assert data["parity"] in (0, 1)
points = [tuple(point) for point in data["points"]]
assert len(points) == len(set(points)) == 35
assert all(
    0 <= x < 23 and 0 <= y < 23 and (x + y) % 2 == data["parity"]
    for x, y in points
)

for a, b, c in itertools.combinations(points, 3):
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    assert cross != 0, (a, b, c)

print("OK: 35 distinct same-colour points on 23x23; no collinear triple.")
print("Therefore D_mono(23) >= 35.")
