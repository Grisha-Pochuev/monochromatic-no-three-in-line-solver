#!/usr/bin/env python3
"""Exact pattern-based upper search for the 22x22 checkerboard problem.

The target is 34 selected parity-0 points.  Instead of exposing only one Boolean
variable per point, the model also chooses one complete pattern (zero, one, or
two selected points) on every row, column, slope +1 diagonal, and slope -1
diagonal.  All four pattern families are channelled to the same point variables.
This is logically equivalent to the ordinary four-direction capacity constraints,
but it propagates much more strongly in CP-SAT.

Every remaining maximal grid line containing at least three allowed points is
also constrained to contain at most two selected points.  Thus INFEASIBLE is a
complete proof for the requested row/column saturation-count partition.
UNKNOWN is useful search data but is not a proof.
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

Point = tuple[int, int]
LineKey = tuple[int, int, int]


def canonical_line(a: Point, b: Point) -> LineKey:
    x1, y1 = a
    x2, y2 = b
    dx = x2 - x1
    dy = y2 - y1
    divisor = math.gcd(abs(dx), abs(dy))
    aa = dy // divisor
    bb = -dx // divisor
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb = -aa, -bb
    return aa, bb, aa * x1 + bb * y1


def patterns(values: list[int]) -> list[tuple[int, ...]]:
    """All subsets of size at most two, represented by local indices."""
    result: list[tuple[int, ...]] = [()]
    result.extend((value,) for value in values)
    result.extend(
        (values[i], values[j])
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return result


def add_pattern_family(
    model: cp_model.CpModel,
    selected: dict[Point, cp_model.IntVar],
    groups: dict[int, list[Point]],
    prefix: str,
    exact_twos: int | None,
) -> None:
    two_pattern_variables: list[cp_model.IntVar] = []

    for key, group in sorted(groups.items()):
        local_indices = list(range(len(group)))
        group_patterns = patterns(local_indices)
        pattern_variables = [
            model.NewBoolVar(f"{prefix}_{key}_pattern_{index}")
            for index in range(len(group_patterns))
        ]
        model.AddExactlyOne(pattern_variables)

        for local_index, point in enumerate(group):
            containing = [
                variable
                for pattern, variable in zip(group_patterns, pattern_variables)
                if local_index in pattern
            ]
            model.Add(selected[point] == sum(containing))

        two_pattern_variables.extend(
            variable
            for pattern, variable in zip(group_patterns, pattern_variables)
            if len(pattern) == 2
        )

    if exact_twos is not None:
        model.Add(sum(two_pattern_variables) == exact_twos)


def build_model(
    row_twos: int,
    column_twos: int,
) -> tuple[
    cp_model.CpModel,
    list[Point],
    dict[Point, cp_model.IntVar],
    int,
]:
    points = [
        (x, y)
        for y in range(N)
        for x in range(N)
        if (x + y) % 2 == PARITY
    ]
    model = cp_model.CpModel()
    selected = {
        point: model.NewBoolVar(f"point_{point[0]}_{point[1]}")
        for point in points
    }

    rows: dict[int, list[Point]] = {
        y: [point for point in points if point[1] == y]
        for y in range(N)
    }
    columns: dict[int, list[Point]] = {
        x: [point for point in points if point[0] == x]
        for x in range(N)
    }
    diagonals_plus: dict[int, list[Point]] = defaultdict(list)
    diagonals_minus: dict[int, list[Point]] = defaultdict(list)
    for point in points:
        x, y = point
        diagonals_plus[x - y].append(point)
        diagonals_minus[x + y].append(point)

    add_pattern_family(model, selected, rows, "row", row_twos)
    add_pattern_family(model, selected, columns, "column", column_twos)
    add_pattern_family(model, selected, diagonals_plus, "diag_plus", None)
    add_pattern_family(model, selected, diagonals_minus, "diag_minus", None)

    model.Add(sum(selected.values()) == TARGET)

    line_members: dict[LineKey, set[int]] = defaultdict(set)
    for i, first in enumerate(points):
        for j in range(i + 1, len(points)):
            key = canonical_line(first, points[j])
            line_members[key].add(i)
            line_members[key].add(j)

    remaining_line_count = 0
    for key, member_indices in line_members.items():
        if len(member_indices) < 3:
            continue
        aa, bb, _ = key
        # These four directions are already represented exactly by patterns.
        if aa == 0 or bb == 0 or abs(aa) == abs(bb):
            continue
        model.Add(sum(selected[points[index]] for index in member_indices) <= 2)
        remaining_line_count += 1

    return model, points, selected, remaining_line_count


def effective_seed(seed: int) -> int:
    # OR-Tools random_seed is a signed 32-bit integer.
    return int(seed % 2_147_483_647)


def solve(
    row_twos: int,
    column_twos: int,
    seconds: float,
    workers: int,
    seed: int,
) -> dict[str, object]:
    build_started = time.time()
    model, points, selected, remaining_line_count = build_model(
        row_twos,
        column_twos,
    )
    build_seconds = time.time() - build_started

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = effective_seed(seed)
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True

    solve_started = time.time()
    status = solver.Solve(model)
    elapsed_seconds = time.time() - solve_started

    record: dict[str, object] = {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "row_twos": row_twos,
        "column_twos": column_twos,
        "model": "four_direction_exact_patterns_plus_all_remaining_lines",
        "allowed_points": len(points),
        "remaining_full_line_constraints": remaining_line_count,
        "status": solver.StatusName(status),
        "build_seconds": build_seconds,
        "elapsed_seconds": elapsed_seconds,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": workers,
        "requested_seed": seed,
        "effective_seed": effective_seed(seed),
        "parity_reduction": "parity 1 is the reflection x -> 21-x of parity 0",
        "transpose_reduction": "only row_twos <= column_twos is checked",
    }

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        record["solution"] = [
            list(point)
            for point in points
            if solver.Value(selected[point])
        ]

    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--column-twos", type=int, required=True, choices=range(12, 18))
    parser.add_argument("--seconds", type=float, default=21_000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.row_twos > args.column_twos:
        raise SystemExit("require row_twos <= column_twos")

    record = solve(
        args.row_twos,
        args.column_twos,
        args.seconds,
        args.workers,
        args.seed,
    )
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)
    # UNKNOWN is deliberately a successful job outcome so its JSON artifact is
    # preserved without presenting a technical red failure.  The collector is
    # responsible for deciding whether the mathematical proof is complete.


if __name__ == "__main__":
    main()
