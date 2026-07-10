"""Enhanced SciPy/HiGHS MILP feasibility search for a 31-point set.

This is exploratory. It uses only consequences that are independently checked
from upper_certificate_31.json, so a feasible solution is valid; a time limit is
not a proof of infeasibility.
"""

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

N = 20
PARITY = 0
TARGET = 31
TIME_LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20260710
HERE = Path(__file__).resolve().parent


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    A = y2 - y1
    B = x1 - x2
    C = -(A * x1 + B * y1)
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C)) or 1
    A //= g
    B //= g
    C //= g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return A, B, C


points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
line_map = {}
for i, p in enumerate(points):
    for q in points[i + 1 :]:
        key = canonical_line(p, q)
        if key in line_map:
            continue
        A, B, C = key
        members = tuple(
            j for j, (x, y) in enumerate(points) if A * x + B * y + C == 0
        )
        if len(members) >= 3:
            line_map[key] = members
lines = sorted(set(line_map.values()), key=lambda z: (-len(z), z))

certificate = json.loads((HERE / "upper_certificate_31.json").read_text(encoding="utf-8"))
if certificate.get("kind") != "all_line_dual_lp_certificate_v2":
    raise ValueError("expected all_line_dual_lp_certificate_v2")
denominator = int(certificate["denominator"])
weights = [tuple(map(int, row)) for row in certificate["weights"]]
upper_numerator = 2 * sum(weight for _, _, _, weight in weights)
gap = upper_numerator - TARGET * denominator

cover = np.array(
    [
        sum(weight for A, B, C, weight in weights if A * x + B * y == C)
        for x, y in points
    ],
    dtype=np.int64,
)
if int(cover.min()) < denominator or not (0 <= gap < denominator):
    raise ValueError("invalid certificate")

rows = []
lower = []
upper = []
coefficients = []

for members in lines:
    rows.append(members)
    coefficients.append(None)
    lower.append(-np.inf)
    upper.append(2.0)

rows.append(tuple(range(len(points))))
coefficients.append(None)
lower.append(float(TARGET))
upper.append(float(TARGET))

forced = []
for A, B, C, weight in weights:
    members = tuple(i for i, (x, y) in enumerate(points) if A * x + B * y == C)
    if weight > gap:
        rows.append(members)
        coefficients.append(None)
        lower.append(2.0)
        upper.append(2.0)
        forced.append((A, B, C, weight))

rows.append(tuple(i for i, value in enumerate(cover) if value > denominator))
coefficients.append(
    {i: int(cover[i] - denominator) for i in range(len(points)) if cover[i] > denominator}
)
lower.append(-np.inf)
upper.append(float(gap))

matrix = lil_matrix((len(rows), len(points)), dtype=float)
for r, members in enumerate(rows):
    custom = coefficients[r]
    if custom is None:
        for i in members:
            matrix[r, i] = 1.0
    else:
        for i, value in custom.items():
            matrix[r, i] = float(value)

constraints = LinearConstraint(matrix.tocsr(), np.array(lower), np.array(upper))
rng = np.random.default_rng(SEED)
objective = rng.normal(0.0, 1e-7, len(points))
print(
    "points", len(points),
    "lines", len(lines),
    "forced_certificate_lines", len(forced),
    "gap", gap,
    flush=True,
)

started = time.time()
result = milp(
    c=objective,
    integrality=np.ones(len(points)),
    bounds=Bounds(np.zeros(len(points)), np.ones(len(points))),
    constraints=constraints,
    options={"time_limit": TIME_LIMIT, "mip_rel_gap": 0.0, "presolve": True, "disp": True},
)
print("status", result.status, result.message, "elapsed", time.time() - started, flush=True)
if result.x is not None:
    selected = [points[i] for i, value in enumerate(result.x) if value > 0.5]
    print("selected", len(selected), json.dumps(selected), flush=True)
