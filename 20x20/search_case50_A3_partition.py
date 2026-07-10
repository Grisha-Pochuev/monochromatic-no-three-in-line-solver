"""Exact CP-SAT solver for one disjoint partition of the remaining n20 A=3 frontier.

Every job fixes the case-50 main-diagonal pair, all certificate-forced heavy
lines, A=3, one half-board profile (L,T), and an exact interval for the
north-west quadrant count Q.  Optional exact C and interval B constraints are
used only to split a known micro-profile into disjoint pieces.

INFEASIBLE is a proof for the entire requested partition. UNKNOWN only means
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
    L: int,
    T: int,
    q_min: int,
    q_max: int,
    seconds: float,
    workers: int,
    seed: int,
    output: Path,
    C: int | None = None,
    b_min: int | None = None,
    b_max: int | None = None,
) -> None:
    if q_min > q_max:
        raise ValueError((q_min, q_max))
    if (b_min is None) != (b_max is None):
        raise ValueError("b_min and b_max must be supplied together")

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

    q_expr = sum(
        chosen[i]
        for i, (x, y) in enumerate(points)
        if x < 10 and y < 10
    )
    model.Add(q_expr >= q_min)
    model.Add(q_expr <= q_max)

    if C is not None:
        model.Add(
            sum(
                chosen[i]
                for i, (x, y) in enumerate(points)
                if 5 <= x < 15 and 5 <= y < 15
            )
            == C
        )

    if b_min is not None and b_max is not None:
        b_expr = sum(chosen[i] for i, (x, y) in enumerate(points) if x < 5)
        model.Add(b_expr >= b_min)
        model.Add(b_expr <= b_max)

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
        "A": 3,
        "L": L,
        "T": T,
        "Q_min": q_min,
        "Q_max": q_max,
        "C": C,
        "B_min": b_min,
        "B_max": b_max,
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

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-id", required=True)
    parser.add_argument("--L", type=int, required=True)
    parser.add_argument("--T", type=int, required=True)
    parser.add_argument("--q-min", type=int, required=True)
    parser.add_argument("--q-max", type=int, required=True)
    parser.add_argument("--C", type=int)
    parser.add_argument("--b-min", type=int)
    parser.add_argument("--b-max", type=int)
    parser.add_argument("--seconds", type=float, default=10400.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260720)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    solve(
        branch_id=args.branch_id,
        L=args.L,
        T=args.T,
        q_min=args.q_min,
        q_max=args.q_max,
        C=args.C,
        b_min=args.b_min,
        b_max=args.b_max,
        seconds=args.seconds,
        workers=args.workers,
        seed=args.seed,
        output=args.output,
    )
