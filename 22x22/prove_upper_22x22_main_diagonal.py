#!/usr/bin/env python3
"""Complete exact partition of the 22x22 target-34 problem by x=y pattern.

Every genuine solution has at most two selected points on the main diagonal.
All subsets of that diagonal of sizes 0, 1, and 2 are covered. 180-degree
rotation identifies equivalent subsets, leaving 133 canonical cases.
Each case still includes every maximal grid line containing at least three
allowed parity-0 points, so INFEASIBLE is a rigorous proof for that case.
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


def canonical_diagonal_patterns() -> list[tuple[int, ...]]:
    """All size 0/1/2 subsets of {0,...,21}, modulo x -> 21-x."""
    raw: list[tuple[int, ...]] = [()]
    raw.extend((x,) for x in range(N))
    raw.extend((a, b) for a in range(N) for b in range(a + 1, N))
    canonical: set[tuple[int, ...]] = set()
    for pattern in raw:
        rotated = tuple(sorted(N - 1 - x for x in pattern))
        canonical.add(min(pattern, rotated))
    return sorted(canonical, key=lambda p: (len(p), p))


def build_lines(points: list[Point]) -> list[list[int]]:
    members: dict[LineKey, set[int]] = defaultdict(set)
    for i, first in enumerate(points):
        for j in range(i + 1, len(points)):
            key = canonical_line(first, points[j])
            members[key].add(i)
            members[key].add(j)
    return [sorted(group) for group in members.values() if len(group) >= 3]


def build_model(case_id: int):
    patterns = canonical_diagonal_patterns()
    if not 0 <= case_id < len(patterns):
        raise ValueError(f"case-id must be in 0..{len(patterns)-1}")
    pattern = patterns[case_id]

    points = [(x, y) for y in range(N) for x in range(N) if (x + y) % 2 == PARITY]
    index = {point: i for i, point in enumerate(points)}
    lines = build_lines(points)

    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]
    for group in lines:
        model.Add(sum(chosen[i] for i in group) <= 2)
    model.Add(sum(chosen) == TARGET)

    selected_x = set(pattern)
    for x in range(N):
        model.Add(chosen[index[(x, x)]] == (1 if x in selected_x else 0))

    return model, points, chosen, pattern, len(lines), len(patterns)


def solve(case_id: int, seconds: float, workers: int, seed: int) -> dict[str, object]:
    build_started = time.time()
    model, points, chosen, pattern, line_count, case_count = build_model(case_id)
    build_seconds = time.time() - build_started

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed % MAX_SEED
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
        "parity": PARITY,
        "target": TARGET,
        "partition": "complete_main_diagonal_pattern_mod_180_rotation",
        "case_id": case_id,
        "case_count": case_count,
        "main_diagonal_pattern": list(pattern),
        "main_diagonal_occupancy": len(pattern),
        "maximal_line_constraints": line_count,
        "status": solver.StatusName(status),
        "build_seconds": build_seconds,
        "elapsed_seconds": elapsed,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "workers": workers,
        "requested_seed": seed,
        "effective_seed": seed % MAX_SEED,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        record["solution"] = [list(points[i]) for i in range(len(points)) if solver.Value(chosen[i])]
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=2500.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list-cases", action="store_true")
    args = parser.parse_args()

    if args.list_cases:
        print(json.dumps([list(p) for p in canonical_diagonal_patterns()], indent=2))
        return

    record = solve(args.case_id, args.seconds, args.workers, args.seed)
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
