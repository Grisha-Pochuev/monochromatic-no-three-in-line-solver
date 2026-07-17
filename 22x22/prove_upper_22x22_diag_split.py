#!/usr/bin/env python3
"""Complete compact CP-SAT subdivision for the 22x22 target-34 proof.

A hypothetical 34-point parity-0 configuration has between 12 and 17 rows with
occupancy two, the same range for columns, and between 13 and 17 slope +1
diagonals with occupancy two. Transposition lets us keep row_twos <=
column_twos, giving 21 * 5 = 105 complete, disjoint cases.

Every maximal grid line containing at least three allowed points is constrained
to have occupancy at most two. Therefore INFEASIBLE is a rigorous proof for
one subcase. UNKNOWN is only incomplete search data.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model

N = 22
PARITY = 0
TARGET = 34
MAX_SEED = 2_147_483_647
Point = tuple[int, int]
LineKey = tuple[int, int, int]


def canonical_line(a: Point, b: Point) -> LineKey:
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    g = math.gcd(abs(dx), abs(dy))
    aa, bb = dy // g, -dx // g
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb = -aa, -bb
    return aa, bb, aa * x1 + bb * y1


def exact_two_flags(model, chosen, groups, prefix):
    flags = []
    for number, members in enumerate(groups):
        count = sum(chosen[i] for i in members)
        flag = model.NewBoolVar(f"{prefix}_{number}_has_two")
        model.Add(count == 2).OnlyEnforceIf(flag)
        model.Add(count <= 1).OnlyEnforceIf(flag.Not())
        flags.append(flag)
    return flags


def build_model(row_twos: int, column_twos: int, diag_plus_twos: int):
    points = [(x, y) for y in range(N) for x in range(N) if (x + y) % 2 == PARITY]
    index = {point: i for i, point in enumerate(points)}
    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]

    line_members = defaultdict(set)
    for i, first in enumerate(points):
        for j in range(i + 1, len(points)):
            key = canonical_line(first, points[j])
            line_members[key].add(i)
            line_members[key].add(j)
    maximal_lines = [sorted(v) for v in line_members.values() if len(v) >= 3]
    for members in maximal_lines:
        model.Add(sum(chosen[i] for i in members) <= 2)

    rows = [[index[(x, y)] for x in range(N) if (x, y) in index] for y in range(N)]
    columns = [[index[(x, y)] for y in range(N) if (x, y) in index] for x in range(N)]
    diag_map = defaultdict(list)
    for i, (x, y) in enumerate(points):
        diag_map[x - y].append(i)
    diagonals_plus = [diag_map[key] for key in sorted(diag_map)]

    model.Add(sum(chosen) == TARGET)
    model.Add(sum(exact_two_flags(model, chosen, rows, "row")) == row_twos)
    model.Add(sum(exact_two_flags(model, chosen, columns, "column")) == column_twos)
    model.Add(sum(exact_two_flags(model, chosen, diagonals_plus, "diag_plus")) == diag_plus_twos)
    return model, points, chosen, len(maximal_lines), len(diagonals_plus)


def solve(row_twos, column_twos, diag_plus_twos, seconds, workers, seed):
    build_started = time.time()
    model, points, chosen, line_count, diag_count = build_model(row_twos, column_twos, diag_plus_twos)
    build_seconds = time.time() - build_started

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = int(seed % MAX_SEED)
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True

    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started
    result = {
        "board_size": N,
        "parity": PARITY,
        "target": TARGET,
        "row_twos": row_twos,
        "column_twos": column_twos,
        "diag_plus_twos": diag_plus_twos,
        "status": solver.StatusName(status),
        "build_seconds": build_seconds,
        "elapsed_seconds": elapsed,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "workers": workers,
        "requested_seed": seed,
        "effective_seed": int(seed % MAX_SEED),
        "allowed_points": len(points),
        "maximal_line_constraints": line_count,
        "slope_plus_diagonals": diag_count,
        "partition_completeness": "row_twos 12..17, column_twos row..17, diag_plus_twos 13..17",
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        result["solution"] = [list(points[i]) for i in range(len(points)) if solver.Value(chosen[i])]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--column-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--diag-plus-twos", type=int, required=True, choices=range(13, 18))
    parser.add_argument("--seconds", type=float, default=3000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.row_twos > args.column_twos:
        raise SystemExit("require row_twos <= column_twos")
    result = solve(args.row_twos, args.column_twos, args.diag_plus_twos, args.seconds, args.workers, args.seed)
    text = json.dumps(result, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if result["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
