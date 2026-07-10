"""Exact CP-SAT solver for one partition of the final n20 case-50 frontier.

The earlier exact runs exclude A >= 3.  This solver covers A in {0,1,2}.
It fixes the only unresolved main-diagonal pair (2,2),(17,17), all dual-
certificate consequences, an exact left-half count L, and a disjoint interval
for the north-west quadrant count Q.

The constraints T >= L and L + T <= 31 are safe symmetry breaking.  Reflection
in x=y swaps L and T, while 180-degree rotation maps (L,T) to
(31-L,31-T).  Therefore every solution orbit has a representative satisfying
both inequalities.

INFEASIBLE proves the whole requested branch impossible. UNKNOWN only means
that the time limit was reached.
"""

import argparse
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from search_case50_heavy_intersections import DEN, GAP, TARGET, geometry, load_certificate
from search_20x20_diagonal_pairs import verify_solution


def solve(
    branch_id: str,
    intersection_count: int,
    left_count: int,
    q_min: int,
    q_max: int,
    seconds: float,
    workers: int,
    seed: int,
    output: Path,
) -> None:
    if intersection_count not in (0, 1, 2):
        raise ValueError("A must be 0, 1, or 2")
    if not 11 <= left_count <= 15:
        raise ValueError("canonical L must be in 11..15")
    if not 0 <= q_min <= q_max <= left_count:
        raise ValueError((q_min, q_max, left_count))

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

    model.Add(sum(chosen[i] for i in intersections) == intersection_count)

    left_expr = sum(chosen[i] for i, (x, y) in enumerate(points) if x < 10)
    top_expr = sum(chosen[i] for i, (x, y) in enumerate(points) if y < 10)
    q_expr = sum(
        chosen[i]
        for i, (x, y) in enumerate(points)
        if x < 10 and y < 10
    )

    model.Add(left_expr == left_count)
    model.Add(top_expr >= left_count)
    model.Add(top_expr <= TARGET - left_count)
    model.Add(q_expr >= q_min)
    model.Add(q_expr <= q_max)

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
        "branch_id": branch_id,
        "A": intersection_count,
        "L": left_count,
        "T_min": left_count,
        "T_max": TARGET - left_count,
        "Q_min": q_min,
        "Q_max": q_max,
        "status": solver.StatusName(status),
        "elapsed_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": workers,
        "seed": seed,
    }

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [points[i] for i in range(len(points)) if solver.Value(chosen[i])]
        verify_solution(solution)
        record["solution"] = [list(p) for p in solution]
        record["actual_T"] = sum(1 for x, y in solution if y < 10)
        record["actual_Q"] = sum(1 for x, y in solution if x < 10 and y < 10)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-id", required=True)
    parser.add_argument("--A", type=int, required=True, choices=(0, 1, 2))
    parser.add_argument("--L", type=int, required=True)
    parser.add_argument("--q-min", type=int, required=True)
    parser.add_argument("--q-max", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=13800.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260740)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    solve(
        branch_id=args.branch_id,
        intersection_count=args.A,
        left_count=args.L,
        q_min=args.q_min,
        q_max=args.q_max,
        seconds=args.seconds,
        workers=args.workers,
        seed=args.seed,
        output=args.output,
    )
