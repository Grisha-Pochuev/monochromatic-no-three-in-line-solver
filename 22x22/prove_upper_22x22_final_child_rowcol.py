#!/usr/bin/env python3
"""Exact row/column saturation split of the final n=22 child 652.

Child 652 already fixes main-diagonal pair index 40 and the exact numbers of
saturated diagonals in both diagonal directions.  The only remaining choices
for the four-direction occupancy profile include the numbers of rows and
columns containing exactly two selected points.  Transpose symmetry in the
parent model gives row_twos <= column_twos, so the 21 pairs
12 <= row_twos <= column_twos <= 17 form a complete disjoint partition.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from prove_upper_22x22_profile_child import build_model, decode_child
from prove_upper_22x22_main_diagonal_pair import MAX_SEED, N, PARITY, TARGET, validate_solution

FINAL_CHILD_ID = 652


def subcases() -> list[tuple[int, int]]:
    return [(row_twos, column_twos) for row_twos in range(12, 18) for column_twos in range(row_twos, 18)]


def add_exact_two_count(model, selected, points, groups, exact_count: int, prefix: str) -> None:
    flags = []
    for index, group in enumerate(groups):
        count = sum(selected[point] for point in group)
        is_two = model.NewBoolVar(f"{prefix}_{index}_is_two")
        model.Add(count == 2).OnlyEnforceIf(is_two)
        model.Add(count <= 1).OnlyEnforceIf(is_two.Not())
        flags.append(is_two)
    model.Add(sum(flags) == exact_count)


def solve_subcase(subcase_id: int, seconds: float, workers: int, requested_seed: int) -> dict[str, object]:
    cases = subcases()
    if not 0 <= subcase_id < len(cases):
        raise ValueError(f"subcase must be in 0..{len(cases)-1}")
    row_twos, column_twos = cases[subcase_id]
    pair_index, plus_twos, minus_twos = decode_child(FINAL_CHILD_ID)

    build_started = time.time()
    model, points, selected, metadata = build_model(pair_index, plus_twos, minus_twos)
    if bool(metadata.get("analytic_infeasible")):
        raise ValueError("final child unexpectedly analytic-infeasible before row/column split")

    rows = [[point for point in points if point[1] == y] for y in range(N)]
    columns = [[point for point in points if point[0] == x] for x in range(N)]
    add_exact_two_count(model, selected, points, rows, row_twos, "final_row")
    add_exact_two_count(model, selected, points, columns, column_twos, "final_column")
    build_seconds = time.time() - build_started

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, seconds)
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = requested_seed % MAX_SEED
    solver.parameters.randomize_search = True
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True

    started = time.time()
    status_code = solver.Solve(model)
    elapsed = time.time() - started
    status = solver.StatusName(status_code)
    solution: list[tuple[int, int]] = []
    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [point for point in points if solver.Value(selected[point])]
        validate_solution(solution)

    return {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "parent_child_id": FINAL_CHILD_ID,
        "subcase_id": subcase_id,
        "subcase_count": len(cases),
        "partition": "final_child_652_x_exact_row_twos_x_exact_column_twos",
        "pair_index": pair_index,
        "diag_plus_twos": plus_twos,
        "diag_minus_twos": minus_twos,
        "row_twos": row_twos,
        "column_twos": column_twos,
        "status": status,
        "solution": solution,
        "build_seconds": build_seconds,
        "elapsed_seconds": elapsed,
        "workers": workers,
        "requested_seed": requested_seed,
        "effective_seed": requested_seed % MAX_SEED,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "proof_method": "cp_sat_all_lines_final_child_exact_row_column_saturation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subcase", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=20700.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = solve_subcase(args.subcase, args.seconds, args.workers, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
