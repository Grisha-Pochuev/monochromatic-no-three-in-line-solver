#!/usr/bin/env python3
"""Exact partitioned proof that no 34-point monochromatic set exists on 22x22.

For even N the two checkerboard parities are congruent under the reflection
(x, y) -> (N - 1 - x, y), so it suffices to prove parity 0 infeasible.

At target 34 every row and column contains at most two points. The number of
rows containing exactly two points is therefore one of 12,...,17, and the same
holds for columns. Transposition exchanges those two counts, so it suffices to
check the 21 pairs row_twos <= column_twos.

Each job contains every maximal grid line with at least three allowed points,
not only rows, columns and the two main diagonal directions. CP-SAT status
INFEASIBLE is a complete proof for that partition; UNKNOWN is not a proof.
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

def canonical_line(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int, int]:
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    g = math.gcd(abs(dx), abs(dy))
    aa, bb = dy // g, -dx // g
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb = -aa, -bb
    return aa, bb, aa * x1 + bb * y1

def build_lines(points: list[tuple[int, int]]) -> list[list[int]]:
    members: dict[tuple[int, int, int], set[int]] = defaultdict(set)
    for i, a in enumerate(points):
        for j in range(i + 1, len(points)):
            key = canonical_line(a, points[j])
            members[key].add(i)
            members[key].add(j)
    return [sorted(group) for group in members.values() if len(group) >= 3]

def build_model(row_twos: int, column_twos: int):
    points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]
    index = {point: i for i, point in enumerate(points)}

    lines = build_lines(points)
    for group in lines:
        model.Add(sum(chosen[i] for i in group) <= 2)
    model.Add(sum(chosen) == TARGET)

    row_is_two = []
    for y in range(N):
        count = sum(chosen[index[(x, y)]] for x in range(N) if (x, y) in index)
        flag = model.NewBoolVar(f"row_{y}_has_two")
        model.Add(count == 2).OnlyEnforceIf(flag)
        model.Add(count <= 1).OnlyEnforceIf(flag.Not())
        row_is_two.append(flag)
    model.Add(sum(row_is_two) == row_twos)

    column_is_two = []
    for x in range(N):
        count = sum(chosen[index[(x, y)]] for y in range(N) if (x, y) in index)
        flag = model.NewBoolVar(f"column_{x}_has_two")
        model.Add(count == 2).OnlyEnforceIf(flag)
        model.Add(count <= 1).OnlyEnforceIf(flag.Not())
        column_is_two.append(flag)
    model.Add(sum(column_is_two) == column_twos)
    return model, points, chosen, len(lines)

def solve(row_twos: int, column_twos: int, seconds: float, workers: int, seed: int) -> dict[str, object]:
    model, points, chosen, line_count = build_model(row_twos, column_twos)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True
    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started
    record: dict[str, object] = {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "row_twos": row_twos,
        "column_twos": column_twos,
        "allowed_points": len(points),
        "maximal_line_constraints": line_count,
        "status": solver.StatusName(status),
        "elapsed_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": workers,
        "seed": seed,
        "parity_reduction": "parity 1 is the reflection x -> 21-x of parity 0",
        "transpose_reduction": "only row_twos <= column_twos is checked",
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        record["solution"] = [list(points[i]) for i in range(len(points)) if solver.Value(chosen[i])]
    return record

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--column-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--seconds", type=float, default=21000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.row_twos > args.column_twos:
        raise SystemExit("require row_twos <= column_twos")
    record = solve(args.row_twos, args.column_twos, args.seconds, args.workers, args.seed)
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
