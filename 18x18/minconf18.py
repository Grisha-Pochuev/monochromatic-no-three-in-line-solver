#!/usr/bin/env python3
"""CP-SAT minimum-conflict model for 28 points on parity-0 half of 18x18."""
import json
import math
import sys

from ortools.sat.python import cp_model


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
    idx = {pt: i for i, pt in enumerate(pts)}
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

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(len(pts))]
    slacks = []
    for li, line in enumerate(lines):
        slack = model.NewIntVar(0, len(line) - 2, f"s{li}")
        model.Add(sum(x[idx[pt]] for pt in line) <= 2 + slack)
        slacks.append(slack)
    model.Add(sum(x) == target)
    model.Minimize(sum(slacks))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 8
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    objective = solver.ObjectiveValue() if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) else None
    print("status", solver.StatusName(status), "obj", objective, "bound", solver.BestObjectiveBound(), "time", solver.WallTime(), "conf", solver.NumConflicts(), "branches", solver.NumBranches(), flush=True)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        sol = [pts[i] for i in range(len(pts)) if solver.Value(x[i])]
        print(json.dumps(sol), flush=True)


if __name__ == "__main__":
    main()
