"""Exact, safely sharded CP-SAT attack on the unresolved 20x20 target 31.

The LP dual certificate leaves a gap below 32 of only 433544/1000000.
Therefore every certificate line whose weight exceeds that gap must be full
(occupancy exactly two) in any 31-point solution. In particular, the main
20-point diagonal x=y must contain exactly two selected points.

We partition the existence question by that pair. There are C(20,2)=190 pairs.
A 180-degree rotation maps pair (a,b) to (19-b,19-a), so keeping the
lexicographically smaller representative leaves 100 complete symmetry classes.
The workflow distributes those 100 exact cases over 20 runners.
"""

import argparse
import itertools
import json
import math
import time
from pathlib import Path

from ortools.sat.python import cp_model

N = 20
PARITY = 0
TARGET = 31
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


def build_geometry():
    points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
    point_index = {p: i for i, p in enumerate(points)}
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
    lines = sorted(set(line_map.values()), key=lambda z: (-len(z), z))
    return points, point_index, lines


def load_certificate(points):
    data = json.loads((HERE / "upper_certificate_31.json").read_text(encoding="utf-8"))
    if data.get("kind") != "all_line_dual_lp_certificate_v2":
        raise ValueError("expected all_line_dual_lp_certificate_v2")
    denominator = int(data["denominator"])
    weights = [tuple(map(int, row)) for row in data["weights"]]
    upper_numerator = 2 * sum(weight for _, _, _, weight in weights)
    if upper_numerator != int(data["upper_numerator"]):
        raise ValueError("certificate upper numerator mismatch")
    gap = upper_numerator - TARGET * denominator
    if not (0 <= gap < denominator):
        raise ValueError(("certificate does not prove an upper bound of 31", gap))

    cover = []
    for x, y in points:
        value = sum(weight for A, B, C, weight in weights if A * x + B * y == C)
        if value < denominator:
            raise ValueError(("undercovered point", (x, y), value, denominator))
        cover.append(value)

    weighted_lines = []
    for A, B, C, weight in weights:
        members = tuple(i for i, (x, y) in enumerate(points) if A * x + B * y == C)
        weighted_lines.append((members, weight, (A, B, C)))
    return denominator, upper_numerator, gap, cover, weighted_lines


def verify_solution(solution):
    if len(solution) != TARGET or len(set(solution)) != TARGET:
        raise AssertionError("wrong solution size")
    for p in solution:
        if not (0 <= p[0] < N and 0 <= p[1] < N and (p[0] + p[1]) % 2 == PARITY):
            raise AssertionError(("invalid point", p))
    for a, b, c in itertools.combinations(solution, 3):
        if (b[0] - a[0]) * (c[1] - a[1]) == (b[1] - a[1]) * (c[0] - a[0]):
            raise AssertionError(("collinear triple", a, b, c))


def canonical_diagonal_pairs():
    result = []
    for pair in itertools.combinations(range(N), 2):
        rotated = (N - 1 - pair[1], N - 1 - pair[0])
        if pair <= rotated:
            result.append(pair)
    if len(result) != 100:
        raise AssertionError(len(result))
    return result


def solve_case(
    case_id,
    pair,
    points,
    point_index,
    lines,
    denominator,
    gap,
    cover,
    weighted_lines,
    seconds,
    workers,
    seed,
    log_search_progress,
):
    model = cp_model.CpModel()
    chosen = [model.NewBoolVar(f"p_{x}_{y}") for x, y in points]

    for members in lines:
        model.Add(sum(chosen[i] for i in members) <= 2)
    model.Add(sum(chosen) == TARGET)

    forced_lines = 0
    for members, weight, _ in weighted_lines:
        if weight > gap:
            model.Add(sum(chosen[i] for i in members) == 2)
            forced_lines += 1

    excess_terms = [
        (cover[i] - denominator) * chosen[i]
        for i in range(len(points))
        if cover[i] > denominator
    ]
    if excess_terms:
        model.Add(sum(excess_terms) <= gap)

    model.Add(sum(cover[i] * chosen[i] for i in range(len(points))) >= TARGET * denominator)

    selected_x = set(pair)
    for x in range(N):
        model.Add(chosen[point_index[(x, x)]] == (1 if x in selected_x else 0))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed + case_id
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.log_search_progress = log_search_progress

    started = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - started
    status_name = solver.StatusName(status)
    record = {
        "case_id": case_id,
        "main_diagonal_pair": list(pair),
        "status": status_name,
        "elapsed_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "forced_certificate_lines": forced_lines,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [points[i] for i in range(len(points)) if solver.Value(chosen[i])]
        verify_solution(solution)
        record["solution"] = [list(p) for p in solution]
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, default=20)
    parser.add_argument("--seconds-per-case", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260710)
    parser.add_argument("--max-cases", type=int, default=0, help="0 means all assigned cases")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log-search-progress", action="store_true")
    args = parser.parse_args()

    if not 0 <= args.shard_index < args.shard_count:
        raise ValueError((args.shard_index, args.shard_count))

    points, point_index, lines = build_geometry()
    denominator, upper_numerator, gap, cover, weighted_lines = load_certificate(points)

    main_diag_weight = sum(
        weight for members, weight, key in weighted_lines if key == (1, -1, 0)
    )
    if main_diag_weight <= gap:
        raise AssertionError(("main diagonal is not forced full", main_diag_weight, gap))

    all_cases = canonical_diagonal_pairs()
    assigned = [
        (case_id, pair)
        for case_id, pair in enumerate(all_cases)
        if case_id % args.shard_count == args.shard_index
    ]
    if args.max_cases > 0:
        assigned = assigned[: args.max_cases]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    found = None
    for case_id, pair in assigned:
        print(
            f"case {case_id}/99 pair={pair} shard={args.shard_index}/{args.shard_count} ",
            f"time_limit={args.seconds_per_case}s",
            flush=True,
        )
        record = solve_case(
            case_id,
            pair,
            points,
            point_index,
            lines,
            denominator,
            gap,
            cover,
            weighted_lines,
            args.seconds_per_case,
            args.workers,
            args.seed,
            args.log_search_progress,
        )
        records.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
        if "solution" in record:
            found = record
            break

    summary = {
        "N": N,
        "parity": PARITY,
        "target": TARGET,
        "method": "certificate-forced main-diagonal pair partition",
        "certificate_upper_numerator": upper_numerator,
        "certificate_denominator": denominator,
        "certificate_gap_numerator": gap,
        "canonical_case_count": len(all_cases),
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "assigned_case_count": len(assigned),
        "completed_case_count": len(records),
        "infeasible_case_count": sum(r["status"] == "INFEASIBLE" for r in records),
        "unknown_case_count": sum(r["status"] == "UNKNOWN" for r in records),
        "solution_found": found is not None,
        "cases": records,
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("summary", json.dumps({k: v for k, v in summary.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
