#!/usr/bin/env python3
"""Search for a 35-point monochromatic no-three-in-line set on 23x23."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from ortools.sat.python import cp_model

N = 23
TARGET = 35


def allowed_points(parity: int) -> list[tuple[int, int]]:
    return [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == parity]


def maximal_allowed_lines(points: list[tuple[int, int]]) -> list[list[int]]:
    index = {point: i for i, point in enumerate(points)}
    lines: list[list[int]] = []
    for dx in range(0, N):
        for dy in range(-(N - 1), N):
            if dx == 0 and dy <= 0:
                continue
            if dx == 0 and abs(dy) != 1:
                continue
            if dx > 0 and math.gcd(dx, abs(dy)) != 1:
                continue
            if dx == 0:
                step_x, step_y = 0, 1
            else:
                step_x, step_y = dx, dy
            for x in range(N):
                for y in range(N):
                    px, py = x - step_x, y - step_y
                    if 0 <= px < N and 0 <= py < N:
                        continue
                    current: list[int] = []
                    xx, yy = x, y
                    while 0 <= xx < N and 0 <= yy < N:
                        idx = index.get((xx, yy))
                        if idx is not None:
                            current.append(idx)
                        xx += step_x
                        yy += step_y
                    if len(current) >= 3:
                        lines.append(current)
    unique: dict[tuple[int, ...], list[int]] = {}
    for line in lines:
        unique[tuple(line)] = line
    return list(unique.values())


def validate(points: list[tuple[int, int]], parity: int) -> None:
    if len(points) != TARGET or len(set(points)) != TARGET:
        raise ValueError("wrong solution size or duplicates")
    if any(not (0 <= x < N and 0 <= y < N) or (x + y) % 2 != parity for x, y in points):
        raise ValueError("point outside board or wrong parity")
    for i, a in enumerate(points):
        for j in range(i + 1, len(points)):
            b = points[j]
            for k in range(j + 1, len(points)):
                c = points[k]
                if (b[0] - a[0]) * (c[1] - a[1]) == (b[1] - a[1]) * (c[0] - a[0]):
                    raise ValueError(f"collinear triple: {a}, {b}, {c}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parity", type=int, choices=[0, 1], required=True)
    parser.add_argument("--seconds", type=float, default=20700.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    points = allowed_points(args.parity)
    lines = maximal_allowed_lines(points)
    model = cp_model.CpModel()
    chosen = [model.new_bool_var(f"p_{x}_{y}") for x, y in points]
    for line in lines:
        model.add(sum(chosen[i] for i in line) <= 2)
    model.add(sum(chosen) >= TARGET)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed % 2_147_483_647
    solver.parameters.randomize_search = True
    status_code = solver.solve(model)
    status = solver.status_name(status_code)
    solution: list[tuple[int, int]] = []
    if status in {"FEASIBLE", "OPTIMAL"}:
        solution = [point for i, point in enumerate(points) if solver.value(chosen[i])]
        validate(solution, args.parity)

    payload = {
        "board_size": N,
        "target": TARGET,
        "parity": args.parity,
        "status": status,
        "solution": solution,
        "seed": args.seed,
        "workers": args.workers,
        "seconds_limit": args.seconds,
        "wall_time": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "allowed_points": len(points),
        "line_constraints": len(lines),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
