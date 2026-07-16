#!/usr/bin/env python3
"""Exact four-direction upper proof for the 21x21 checkerboard problem.

Any genuine no-three-in-line set satisfies the row, column, slope +1 diagonal,
and slope -1 diagonal capacities used here. Therefore proving that this relaxed
integer model has no 33-point solution proves D_mono(21) <= 32.

CP-SAT uses integer constraints. INFEASIBLE is a complete proof for the selected
parity; UNKNOWN is not a proof and must never be recorded as a closed result.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model


N = 21
TARGET = 33


def build_model(
    parity: int,
) -> tuple[cp_model.CpModel, list[tuple[int, int]], list[cp_model.IntVar]]:
    points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == parity]
    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]

    key_functions = (
        lambda p: ("row", p[1]),
        lambda p: ("column", p[0]),
        lambda p: ("diag_plus", p[0] - p[1]),
        lambda p: ("diag_minus", p[0] + p[1]),
    )

    for key_function in key_functions:
        groups: dict[tuple[str, int], list[int]] = defaultdict(list)
        for i, point in enumerate(points):
            groups[key_function(point)].append(i)
        for members in groups.values():
            model.Add(sum(chosen[i] for i in members) <= 2)

    model.Add(sum(chosen) == TARGET)
    return model, points, chosen


def solve(parity: int, seconds: float, workers: int, seed: int) -> dict[str, object]:
    model, points, chosen = build_model(parity)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.log_search_progress = True

    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started

    record: dict[str, object] = {
        "board_size": N,
        "parity": parity,
        "allowed_points": len(points),
        "target": TARGET,
        "relaxation": ["rows", "columns", "diagonals_slope_+1", "diagonals_slope_-1"],
        "status": solver.StatusName(status),
        "elapsed_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": workers,
        "seed": seed,
    }

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        record["solution"] = [
            list(points[i]) for i in range(len(points)) if solver.Value(chosen[i])
        ]

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parity", type=int, required=True, choices=(0, 1))
    parser.add_argument("--seconds", type=float, default=18000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    record = solve(args.parity, args.seconds, args.workers, args.seed)
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    if record["status"] == "INFEASIBLE":
        return
    if record["status"] == "UNKNOWN":
        raise SystemExit(2)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
