#!/usr/bin/env python3
"""Exact n=22 target-34 search split by the selected pair on x=y.

A rational four-direction certificate has denominator 187 and objective 6470/187.
For 34 selected points its total slack is only 112/187. Therefore every
certificate line whose integer weight exceeds 112 must contain exactly two
selected points. These are x-y = -2, 0, 2. In particular x=y contains exactly
two points, so fixing its pair gives a complete finite partition.

The 231 pairs on x=y reduce to 121 canonical cases under 180-degree rotation.
Every case still contains all maximal grid-line constraints, so INFEASIBLE is
a complete proof for that case. UNKNOWN is saved as an incomplete result.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

N = 22
PARITY = 0
TARGET = 34
MAX_SEED = 2_147_483_647
HERE = Path(__file__).resolve().parent
CERTIFICATE_PATH = HERE / "upper_certificate_34_four_direction.json"

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


def allowed_points() -> list[Point]:
    return [
        (x, y)
        for y in range(N)
        for x in range(N)
        if (x + y) % 2 == PARITY
    ]


def build_maximal_lines(points: list[Point]) -> dict[LineKey, tuple[int, ...]]:
    members: dict[LineKey, set[int]] = defaultdict(set)
    for i, first in enumerate(points):
        for j in range(i + 1, len(points)):
            key = canonical_line(first, points[j])
            members[key].add(i)
            members[key].add(j)
    return {
        key: tuple(sorted(indices))
        for key, indices in members.items()
        if len(indices) >= 3
    }


def rotate_pair(pair: tuple[int, int]) -> tuple[int, int]:
    a, b = pair
    return tuple(sorted((N - 1 - a, N - 1 - b)))


def canonical_main_diagonal_pairs() -> list[tuple[int, int]]:
    """Return one representative of each 180-degree orbit of x=y pairs."""
    representatives = {
        min(pair, rotate_pair(pair))
        for pair in itertools.combinations(range(N), 2)
    }
    result = sorted(representatives)
    assert len(result) == 121
    return result


def load_certificate() -> dict[str, object]:
    data = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
    if int(data["board_size"]) != N or int(data["parity"]) != PARITY:
        raise ValueError("certificate board/parity mismatch")
    if int(data["target"]) != TARGET:
        raise ValueError("certificate target mismatch")
    return data


def certificate_weights(data: dict[str, object]) -> dict[tuple[str, int], int]:
    families = data["families"]
    assert isinstance(families, dict)
    result: dict[tuple[str, int], int] = {}
    for index, weight in enumerate(families["rows"]):
        result[("row", index)] = int(weight)
    for index, weight in enumerate(families["columns"]):
        result[("column", index)] = int(weight)
    for key, weight in families["diag_plus"].items():
        result[("diag_plus", int(key))] = int(weight)
    for key, weight in families["diag_minus"].items():
        result[("diag_minus", int(key))] = int(weight)
    return result


def point_cover(point: Point, weights: dict[tuple[str, int], int]) -> int:
    x, y = point
    return (
        weights.get(("row", y), 0)
        + weights.get(("column", x), 0)
        + weights.get(("diag_plus", x - y), 0)
        + weights.get(("diag_minus", x + y), 0)
    )


def verify_certificate() -> dict[str, object]:
    data = load_certificate()
    denominator = int(data["denominator"])
    objective = int(data["objective_numerator"])
    slack = int(data["slack_numerator"])
    weights = certificate_weights(data)
    points = allowed_points()

    computed_objective = 2 * sum(weights.values())
    covers = [point_cover(point, weights) for point in points]
    expected_slack = objective - TARGET * denominator

    if computed_objective != objective:
        raise ValueError(
            f"certificate objective mismatch: {computed_objective} != {objective}"
        )
    if min(covers) < denominator:
        raise ValueError(
            f"certificate leaves a point undercovered: {min(covers)} < {denominator}"
        )
    if expected_slack != slack:
        raise ValueError(f"certificate slack mismatch: {expected_slack} != {slack}")

    heavy = sorted(
        (family, key, weight)
        for (family, key), weight in weights.items()
        if weight > slack
    )
    expected_heavy = [
        ("diag_plus", -2, 115),
        ("diag_plus", 0, 117),
        ("diag_plus", 2, 115),
    ]
    if heavy != expected_heavy:
        raise ValueError(f"unexpected heavy lines: {heavy}")

    return {
        "status": "VALID",
        "allowed_points": len(points),
        "denominator": denominator,
        "objective_numerator": objective,
        "objective_value": objective / denominator,
        "target_slack_numerator": slack,
        "minimum_point_cover": min(covers),
        "heavy_lines": heavy,
        "canonical_pair_count": len(canonical_main_diagonal_pairs()),
    }


def add_exact_two_flags(
    model: cp_model.CpModel,
    selected: dict[Point, cp_model.IntVar],
    groups: Iterable[list[Point]],
    prefix: str,
) -> list[cp_model.IntVar]:
    flags: list[cp_model.IntVar] = []
    for index, group in enumerate(groups):
        count = sum(selected[point] for point in group)
        flag = model.NewBoolVar(f"{prefix}_{index}_has_two")
        model.Add(count == 2).OnlyEnforceIf(flag)
        model.Add(count <= 1).OnlyEnforceIf(flag.Not())
        flags.append(flag)
    return flags


def build_model(
    pair: tuple[int, int],
) -> tuple[
    cp_model.CpModel,
    list[Point],
    dict[Point, cp_model.IntVar],
    dict[str, object],
]:
    if pair not in canonical_main_diagonal_pairs():
        raise ValueError(f"pair is not canonical: {pair}")

    certificate = load_certificate()
    weights = certificate_weights(certificate)
    denominator = int(certificate["denominator"])
    slack = int(certificate["slack_numerator"])

    points = allowed_points()
    lines = build_maximal_lines(points)

    model = cp_model.CpModel()
    selected = {
        point: model.NewBoolVar(f"p_{point[0]}_{point[1]}")
        for point in points
    }

    for members in lines.values():
        model.Add(sum(selected[points[i]] for i in members) <= 2)
    model.Add(sum(selected.values()) == TARGET)

    heavy_line_keys: list[LineKey] = []
    for (family, key), weight in weights.items():
        if weight <= slack:
            continue
        if family == "diag_plus":
            members = [point for point in points if point[0] - point[1] == key]
        elif family == "diag_minus":
            members = [point for point in points if point[0] + point[1] == key]
        elif family == "row":
            members = [point for point in points if point[1] == key]
        elif family == "column":
            members = [point for point in points if point[0] == key]
        else:
            raise ValueError(f"unknown certificate family: {family}")
        model.Add(sum(selected[point] for point in members) == 2)
        if len(members) >= 2:
            heavy_line_keys.append(canonical_line(members[0], members[-1]))

    excess_terms = []
    for point in points:
        excess = point_cover(point, weights) - denominator
        if excess < 0:
            raise ValueError(f"negative certificate excess at {point}: {excess}")
        if excess:
            excess_terms.append(excess * selected[point])
    model.Add(sum(excess_terms) <= slack)

    pair_set = set(pair)
    for coordinate in range(N):
        model.Add(selected[(coordinate, coordinate)] == int(coordinate in pair_set))

    rows = [[point for point in points if point[1] == y] for y in range(N)]
    columns = [[point for point in points if point[0] == x] for x in range(N)]
    diag_plus_keys = sorted({x - y for x, y in points})
    diag_minus_keys = sorted({x + y for x, y in points})
    diag_plus = [
        [point for point in points if point[0] - point[1] == key]
        for key in diag_plus_keys
    ]
    diag_minus = [
        [point for point in points if point[0] + point[1] == key]
        for key in diag_minus_keys
    ]

    row_twos = add_exact_two_flags(model, selected, rows, "row")
    column_twos = add_exact_two_flags(model, selected, columns, "column")
    plus_twos = add_exact_two_flags(model, selected, diag_plus, "diag_plus")
    minus_twos = add_exact_two_flags(model, selected, diag_minus, "diag_minus")

    model.Add(sum(row_twos) >= 12)
    model.Add(sum(row_twos) <= 17)
    model.Add(sum(column_twos) >= 12)
    model.Add(sum(column_twos) <= 17)
    model.Add(sum(row_twos) <= sum(column_twos))
    model.Add(sum(plus_twos) >= 13)
    model.Add(sum(plus_twos) <= 17)
    model.Add(sum(minus_twos) >= 12)
    model.Add(sum(minus_twos) <= 17)

    metadata = {
        "allowed_points": len(points),
        "maximal_line_constraints": len(lines),
        "certificate_denominator": denominator,
        "certificate_objective_numerator": int(certificate["objective_numerator"]),
        "certificate_slack_numerator": slack,
        "heavy_line_count": len(heavy_line_keys),
        "canonical_pair_count": len(canonical_main_diagonal_pairs()),
    }
    return model, points, selected, metadata


def validate_solution(solution: list[list[int]]) -> None:
    points = [tuple(map(int, point)) for point in solution]
    if len(points) != TARGET or len(set(points)) != TARGET:
        raise ValueError("solution size or distinctness failure")
    for x, y in points:
        if not (0 <= x < N and 0 <= y < N):
            raise ValueError(f"point outside board: {(x, y)}")
        if (x + y) % 2 != PARITY:
            raise ValueError(f"wrong parity: {(x, y)}")
    line_counts: dict[LineKey, set[Point]] = defaultdict(set)
    for first, second in itertools.combinations(points, 2):
        key = canonical_line(first, second)
        line_counts[key].add(first)
        line_counts[key].add(second)
    bad = [key for key, members in line_counts.items() if len(members) >= 3]
    if bad:
        raise ValueError(f"solution contains a collinear triple on line {bad[0]}")


def solve_case(
    pair: tuple[int, int],
    seconds: float,
    workers: int,
    requested_seed: int,
) -> dict[str, object]:
    build_started = time.time()
    model, points, selected, metadata = build_model(pair)
    build_seconds = time.time() - build_started

    effective_seed = int(requested_seed % MAX_SEED)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, float(seconds))
    solver.parameters.num_search_workers = int(workers)
    solver.parameters.random_seed = effective_seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True

    solve_started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - solve_started
    status_name = solver.StatusName(status)

    record: dict[str, object] = {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "main_diagonal_pair": list(pair),
        "canonical_case_index": canonical_main_diagonal_pairs().index(pair),
        "status": status_name,
        "build_seconds": build_seconds,
        "elapsed_seconds": elapsed,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "workers": workers,
        "requested_seed": requested_seed,
        "effective_seed": effective_seed,
        "model": "all_lines_plus_rational_certificate_main_diagonal_pair",
        **metadata,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [
            list(point)
            for point in points
            if solver.Value(selected[point])
        ]
        validate_solution(solution)
        record["solution"] = solution
        record["solution_independently_validated"] = True
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-index", type=int)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-certificate-only", action="store_true")
    parser.add_argument("--list-cases", action="store_true")
    args = parser.parse_args()

    if args.verify_certificate_only:
        print(json.dumps(verify_certificate(), indent=2))
        return

    cases = canonical_main_diagonal_pairs()
    if args.list_cases:
        print(json.dumps(
            [{"case_index": i, "pair": list(pair)} for i, pair in enumerate(cases)],
            indent=2,
        ))
        return

    if args.case_index is None or not (0 <= args.case_index < len(cases)):
        raise SystemExit("--case-index must be in 0..120")

    record = solve_case(
        pair=cases[args.case_index],
        seconds=args.seconds,
        workers=args.workers,
        requested_seed=args.seed,
    )
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
