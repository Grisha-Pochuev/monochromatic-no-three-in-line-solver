"""Exact refinement of the single unresolved n20 diagonal-pair case.

Case 50 fixes the two selected points on x=y to (2,2) and (17,17).
The dual certificate forces 13 heavy diagonals to have occupancy exactly two.
Let A be the number of selected points lying at an intersection of two heavy
lines. Double counting gives outside_heavy_union = A + 5, so only A=0..4
remain after the earlier exclusion A>=5.
"""

import argparse
import itertools
import math
import time
from pathlib import Path

from ortools.sat.python import cp_model

N = 20
TARGET = 31
DEN = 1_000_000
UPPER = 31_433_544
GAP = UPPER - TARGET * DEN
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


def geometry():
    points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == 0]
    index = {p: i for i, p in enumerate(points)}
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
    return points, index, sorted(set(line_map.values()))


def load_certificate(points):
    import json

    data = json.loads((HERE / "upper_certificate_31.json").read_text(encoding="utf-8"))
    weights = [tuple(map(int, row)) for row in data["weights"]]
    cover = [
        sum(w for A, B, C, w in weights if A * x + B * y == C)
        for x, y in points
    ]
    weighted_lines = []
    for A, B, C, weight in weights:
        members = tuple(i for i, (x, y) in enumerate(points) if A * x + B * y == C)
        weighted_lines.append((members, weight, (A, B, C)))
    return cover, weighted_lines


def solve(intersection_count, seconds, workers, seed):
    points, index, lines = geometry()
    cover, weighted_lines = load_certificate(points)
    heavy = [members for members, weight, _ in weighted_lines if weight > GAP]
    intersections = [
        i for i in range(len(points)) if sum(i in members for members in heavy) == 2
    ]

    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]

    for members in lines:
        model.Add(sum(chosen[i] for i in members) <= 2)
    model.Add(sum(chosen) == TARGET)

    for members, weight, _ in weighted_lines:
        if weight > GAP:
            model.Add(sum(chosen[i] for i in members) == 2)

    excess = [
        (cover[i] - DEN) * chosen[i]
        for i in range(len(points))
        if cover[i] > DEN
    ]
    model.Add(sum(excess) <= GAP)

    for x in range(N):
        model.Add(chosen[index[(x, x)]] == (1 if x in (2, 17) else 0))

    model.Add(sum(chosen[i] for i in intersections) == intersection_count)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2

    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started
    print(
        {
            "A": intersection_count,
            "status": solver.StatusName(status),
            "elapsed_seconds": elapsed,
            "conflicts": solver.NumConflicts(),
            "branches": solver.NumBranches(),
        }
    )
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [points[i] for i in range(len(points)) if solver.Value(chosen[i])]
        print({"solution": solution})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--A", type=int, required=True, choices=range(5))
    parser.add_argument("--seconds", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260710)
    args = parser.parse_args()
    solve(args.A, args.seconds, args.workers, args.seed + args.A)
