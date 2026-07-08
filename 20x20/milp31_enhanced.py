import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix

N = 20
PARITY = 0
TL = float(sys.argv[1]) if len(sys.argv) > 1 else 300
HERE = Path(__file__).resolve().parent
cert = json.loads((HERE / "upper_certificate_31.json").read_text(encoding="utf-8"))["certificates"]["even"]


def F(s):
    return Fraction(s)


def w(tbl, k):
    return F(cert[tbl].get(str(k), "0"))


def cover(p):
    x, y = p
    return w("row_y", y) + w("column_x", x) + w("diag_x_minus_y", x - y) + w("diag_x_plus_y", x + y)


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    A = y2 - y1
    B = x1 - x2
    C = -(A * x1 + B * y1)
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
    A //= g
    B //= g
    C //= g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return A, B, C


P = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
slack = np.array([int((cover(p) - 1) * 78) for p in P], dtype=float)
print("point slack hist", {int(s): int((slack == s).sum()) for s in sorted(set(slack))}, flush=True)

line_map = {}
for i, a in enumerate(P):
    for b in P[i + 1:]:
        key = canonical_line(a, b)
        if key not in line_map:
            A, B, C = key
            line = tuple(idx for idx, r in enumerate(P) if A * r[0] + B * r[1] + C == 0)
            if len(line) >= 3:
                line_map[key] = line
lines = sorted(set(line_map.values()), key=lambda z: (-len(z), z))
print("vars", len(P), "lines", len(lines), flush=True)

rows = []
lb = []
ub = []
for line in lines:
    rows.append(line)
    lb.append(-np.inf)
    ub.append(2.0)
rows.append(tuple(range(len(P))))
lb.append(31.0)
ub.append(31.0)

m = len(rows) + 1
n = len(P)
A = lil_matrix((m, n), dtype=float)
for r, line in enumerate(rows):
    for i in line:
        A[r, i] = 1.0
lb2 = np.array(lb + [-np.inf], dtype=float)
ub2 = np.array(ub + [34.0], dtype=float)
for i, s in enumerate(slack):
    A[len(rows), i] = s

extra = []


def add_weighted(table, keyfun, name):
    for k, v in cert[table].items():
        u = int(F(v) * 78)
        pts = [i for i, p in enumerate(P) if keyfun(p) == int(k)]
        if not pts:
            continue
        if u > 34:
            extra.append((pts, 2, 2, f"{name}{k}", u))
        elif 2 * u > 34:
            extra.append((pts, 1, 2, f"{name}{k}", u))


add_weighted("row_y", lambda p: p[1], "row")
add_weighted("column_x", lambda p: p[0], "col")
add_weighted("diag_x_minus_y", lambda p: p[0] - p[1], "dm")
add_weighted("diag_x_plus_y", lambda p: p[0] + p[1], "dp")
print("extra lower constraints", len(extra), [(e[3], e[1], e[4]) for e in extra], flush=True)

A2 = lil_matrix((m + len(extra), n), dtype=float)
A2[:m, :] = A
lb3 = np.concatenate([lb2, np.array([e[1] for e in extra], dtype=float)])
ub3 = np.concatenate([ub2, np.array([e[2] for e in extra], dtype=float)])
for rr, e in enumerate(extra, start=m):
    for i in e[0]:
        A2[rr, i] = 1.0

constraints = LinearConstraint(csr_matrix(A2), lb3, ub3)
rng = np.random.default_rng(123)
c = rng.normal(0, 1e-5, n)
t = time.time()
res = milp(
    c=c,
    integrality=np.ones(n),
    bounds=Bounds(np.zeros(n), np.ones(n)),
    constraints=constraints,
    options={"time_limit": TL, "mip_rel_gap": 0, "disp": True},
)
print("status", res.status, res.message, "fun", res.fun, "time", time.time() - t, flush=True)
if res.x is not None:
    sol = [P[i] for i, v in enumerate(res.x) if v > 0.5]
    print("selected", len(sol), json.dumps(sol), flush=True)
    print("slack", sum(int(slack[i]) for i, v in enumerate(res.x) if v > 0.5), flush=True)
