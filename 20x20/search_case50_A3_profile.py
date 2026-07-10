"""Exact CP-SAT solver for one remaining profile of n20 case 50, A=3.

The model fixes the main-diagonal pair (2,2),(17,17), all certificate-forced
heavy lines, A=3 heavy-line intersections, and optional half/quadrant counts.
Every constraint is exact; UNKNOWN only means that the time limit was reached.
"""

import argparse
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from search_case50_heavy_intersections import (
    DEN,
    GAP,
    TARGET,
    geometry,
    load_certificate,
)


def solve(L: int, T: int, seconds: float, workers: int, seed: int, output: Path, Q: int | None = None, C: int | None = None):
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

    for x in range(20):
        model.Add(chosen[index[(x, x)]] == (1 if x in (2, 17) else 0))

    model.Add(sum(chosen[i] for i in intersections) == 3)
    model.Add(sum(chosen[i] for i, (x, y) in enumerate(points) if x < 10) == L)
    model.Add(sum(chosen[i] for i, (x, y) in enumerate(points) if y < 10) == T)

    if Q is not None:
        model.Add(sum(chosen[i] for i, (x, y) in enumerate(points) if x < 10 and y < 10) == Q)
    if C is not None:
        model.Add(sum(chosen[i] for i, (x, y) in enumerate(points) if 5 <= x < 15 and 5 <= y < 15) == C)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2

    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started

    record = {
        "A": 3,
        "L": L,
        "T": T,
        "Q": Q,
        "C": C,
        "status": solver.StatusName(status),
        "elapsed_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": workers,
        "seed": seed,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        record["solution"] = [list(points[i]) for i in range(len(points)) if solver.Value(chosen[i])]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, required=True)
    parser.add_argument("--T", type=int, required=True)
    parser.add_argument("--Q", type=int)
    parser.add_argument("--C", type=int)
    parser.add_argument("--seconds", type=float, default=10400.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260710)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    solve(args.L, args.T, args.seconds, args.workers, args.seed, args.output, args.Q, args.C)
