#!/usr/bin/env python3
"""HiGHS MILP feasibility search for 28 points on the parity-0 half of 18x18."""
import math
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    a = y2 - y1
    b = x1 - x2
    c = -(a * x1 + b * y1)
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    a //= g
    b //= g
    c //= g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    n = 18
    parity = 0
    target = 28

    pts = [(x, y) for x in range(n) for y in range(n) if (x + y) % 2 == parity]
    line_map = {}
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            key = canonical_line(a, b)
            if key not in line_map:
                A, B, C = key
                line = [r for r in pts if A * r[0] + B * r[1] + C == 0]
                if len(line) >= 3:
                    line_map[key] = line
    lines = list({tuple(sorted(v)): v for v in line_map.values()}.values())
    print("points", len(pts), "lines", len(lines), "target", target, flush=True)

    rows = len(lines) + 1
    cols = len(pts)
    idx = {pt: i for i, pt in enumerate(pts)}
    matrix = lil_matrix((rows, cols), dtype=float)
    lb = np.full(rows, -np.inf)
    ub = np.empty(rows)

    for r, line in enumerate(lines):
        for pt in line:
            matrix[r, idx[pt]] = 1
        ub[r] = 2

    for pt, i in idx.items():
        matrix[len(lines), i] = 1
    lb[-1] = target
    ub[-1] = np.inf

    c = -np.ones(cols)
    constraints = LinearConstraint(csr_matrix(matrix), lb, ub)
    result = milp(
        c=c,
        integrality=np.ones(cols),
        bounds=Bounds(0, 1),
        constraints=constraints,
        options={"time_limit": seconds, "disp": True, "mip_rel_gap": 0},
    )
    print(result)
    if result.x is not None:
        sol = [pts[i] for i, v in enumerate(result.x) if v > 0.5]
        print(len(sol), sol)


if __name__ == "__main__":
    main()
