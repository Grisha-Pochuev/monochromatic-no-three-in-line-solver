# Optional CP-SAT search for deciding whether 31 points exist on 20x20 parity 0.
# Requires: pip install ortools
import json
import math
import sys
from ortools.sat.python import cp_model

N = 20
PARITY = 0
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 31
SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 300
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 1


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


pts = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
line_map = {}
for i, a in enumerate(pts):
    for b in pts[i + 1:]:
        key = canonical_line(a, b)
        if key not in line_map:
            A, B, C = key
            line = [j for j, p in enumerate(pts) if A * p[0] + B * p[1] + C == 0]
            if len(line) >= 3:
                line_map[key] = tuple(line)
lines = sorted(set(line_map.values()), key=lambda L: (-len(L), L))
print("points", len(pts), "lines", len(lines), "target", TARGET, flush=True)

model = cp_model.CpModel()
x = [model.NewBoolVar(f"x{i}") for i in range(len(pts))]
for line in lines:
    model.Add(sum(x[i] for i in line) <= 2)
model.Add(sum(x) == TARGET)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = SECONDS
solver.parameters.num_search_workers = WORKERS
solver.parameters.random_seed = SEED
status = solver.Solve(model)
print("status", solver.StatusName(status), "time", solver.WallTime(), "conflicts", solver.NumConflicts(), "branches", solver.NumBranches())
if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    sol = [pts[i] for i in range(len(pts)) if solver.Value(x[i])]
    print(json.dumps(sol))
