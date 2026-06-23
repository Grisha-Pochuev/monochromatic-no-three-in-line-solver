# Optional CP-SAT search script for the 19x19 checkerboard case.
# Requires: pip install ortools

import json
import math
import sys
from ortools.sat.python import cp_model

N = 19


def points(parity):
    return [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == parity]


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


def all_lines(P):
    line_map = {}
    for i, a in enumerate(P):
        for b in P[i + 1:]:
            key = canonical_line(a, b)
            if key not in line_map:
                A, B, C = key
                line = [idx for idx, r in enumerate(P) if A * r[0] + B * r[1] + C == 0]
                if len(line) >= 3:
                    line_map[key] = tuple(line)
    return sorted(set(line_map.values()), key=lambda line: (-len(line), line))


def solve(parity=0, seconds=600, workers=8):
    P = points(parity)
    lines = all_lines(P)
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(P))]
    for line in lines:
        model.Add(sum(x[i] for i in line) <= 2)
    model.Maximize(sum(x))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_workers = workers
    status = solver.Solve(model)

    print("status", solver.StatusName(status))
    print("objective", solver.ObjectiveValue() if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) else None)
    print("best_bound", solver.BestObjectiveBound())
    print("wall_time", solver.WallTime())
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        sol = [P[i] for i in range(len(P)) if solver.Value(x[i])]
        print(json.dumps(sol))


if __name__ == "__main__":
    parity = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    solve(parity, seconds)
