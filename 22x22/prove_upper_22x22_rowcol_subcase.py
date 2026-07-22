#!/usr/bin/env python3
"""Exact third-level partition of the sole remaining n=22 child.

Child 652 already fixes the main-diagonal pair and the exact numbers of
slope +1 and slope -1 diagonals containing two selected points.  This module
partitions that child further by the exact numbers of rows and columns
containing two selected points.  Because the transpose symmetry break enforces
row_twos <= column_twos and both counts lie in 12..17, there are exactly 21
disjoint exhaustive subcases.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from prove_upper_22x22_main_diagonal_pair import MAX_SEED, N, PARITY, TARGET, validate_solution
from prove_upper_22x22_profile_child import build_model, decode_child

CHILD_ID = 652
ROWCOL_CASES = [(rows, columns) for rows in range(12, 18) for columns in range(rows, 18)]


def decode_subcase(subcase_id: int) -> tuple[int, int]:
    if not 0 <= subcase_id < len(ROWCOL_CASES):
        raise ValueError(f"subcase-id must be in 0..{len(ROWCOL_CASES) - 1}")
    return ROWCOL_CASES[subcase_id]


def add_exact_twos_count(model, selected, points, family: str, exact_count: int):
    flags = []
    for key in range(N):
        if family == "row":
            group = [point for point in points if point[1] == key]
        elif family == "column":
            group = [point for point in points if point[0] == key]
        else:
            raise ValueError("unknown family")
        count = sum(selected[point] for point in group)
        flag = model.NewBoolVar(f"rowcol_split_{family}_{key}_two")
        model.Add(count == 2).OnlyEnforceIf(flag)
        model.Add(count <= 1).OnlyEnforceIf(flag.Not())
        flags.append(flag)
    model.Add(sum(flags) == exact_count)


def solve_subcase(subcase_id: int, seconds: float, workers: int, requested_seed: int) -> dict[str, object]:
    row_twos, column_twos = decode_subcase(subcase_id)
    pair_index, plus_twos, minus_twos = decode_child(CHILD_ID)
    build_started = time.time()
    model, points, selected, metadata = build_model(pair_index, plus_twos, minus_twos)

    record: dict[str, object] = {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "child_id": CHILD_ID,
        "subcase_id": subcase_id,
        "subcase_count": len(ROWCOL_CASES),
        "partition": "child_652_x_exact_row_twos_x_exact_column_twos",
        "row_twos": row_twos,
        "column_twos": column_twos,
        "workers": workers,
        "requested_seed": requested_seed,
        "effective_seed": requested_seed % MAX_SEED,
        **metadata,
    }

    if bool(metadata.get("analytic_infeasible")):
        record.update({
            "build_seconds": time.time() - build_started,
            "status": "INFEASIBLE",
            "proof_method": "exact_certificate_defect_lower_bound",
            "elapsed_seconds": 0.0,
            "branches": 0,
            "conflicts": 0,
        })
        return record

    details = metadata["analytic_defect_details"]
    exact_minimum = (
        int(details["row_costs"][row_twos])
        + int(details["column_costs"][column_twos])
        + int(details["plus_cost"])
        + int(details["minus_cost"])
    )
    record["exact_rowcol_minimum_line_defect"] = exact_minimum
    residual = int(metadata["residual_certificate_slack"])
    if exact_minimum > residual:
        record.update({
            "build_seconds": time.time() - build_started,
            "status": "INFEASIBLE",
            "proof_method": "exact_row_column_certificate_defect_lower_bound",
            "elapsed_seconds": 0.0,
            "branches": 0,
            "conflicts": 0,
        })
        return record

    add_exact_twos_count(model, selected, points, "row", row_twos)
    add_exact_twos_count(model, selected, points, "column", column_twos)
    record["build_seconds"] = time.time() - build_started

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, seconds)
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = requested_seed % MAX_SEED
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_probing_level = 2
    solver.parameters.log_search_progress = True
    started = time.time()
    status = solver.Solve(model)
    record.update({
        "status": solver.StatusName(status),
        "proof_method": "cp_sat_all_lines_child_652_exact_row_column_twos",
        "elapsed_seconds": time.time() - started,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    })
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [list(point) for point in points if solver.Value(selected[point])]
        validate_solution(solution)
        record["solution"] = solution
        record["solution_independently_validated"] = True
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subcase-id", type=int)
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list-subcases", action="store_true")
    args = parser.parse_args()
    if args.list_subcases:
        print(json.dumps([
            {"subcase_id": index, "row_twos": values[0], "column_twos": values[1]}
            for index, values in enumerate(ROWCOL_CASES)
        ], indent=2))
        return
    if args.subcase_id is None:
        raise SystemExit("--subcase-id is required unless --list-subcases is used")
    record = solve_subcase(args.subcase_id, args.seconds, args.workers, args.seed)
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
