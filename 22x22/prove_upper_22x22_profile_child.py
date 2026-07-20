#!/usr/bin/env python3
"""Exact target-34 child search for unresolved n=22 main-diagonal pairs.

Each child fixes one of the 88 UNKNOWN canonical pairs from run 29575490884,
the number of slope +1 diagonals containing exactly two points (13..17), and
the analogous slope -1 count (12..17).

The model adds pair-conditional consequences of the exact rational certificate:
a residual excess budget, conditional saturation of heavy certificate lines,
exact 0/1/2 occupancy states with a weighted line-defect budget, threshold
cardinality cuts for point excess, and a transpose lexicographic symmetry break.
All maximal grid lines remain constrained, so INFEASIBLE is an exact proof.
Some children are rejected before CP-SAT by an exact certificate-defect lower
bound over the four weighted line families.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from prove_upper_22x22_main_diagonal_pair import (
    MAX_SEED,
    N,
    PARITY,
    TARGET,
    allowed_points,
    build_maximal_lines,
    canonical_main_diagonal_pairs,
    certificate_weights,
    load_certificate,
    point_cover,
    validate_solution,
)

HERE = Path(__file__).resolve().parent
PRIOR_RESULT = HERE / "runs/2026-07-17-run-29575490884/overall.json"
CHILDREN_PER_PAIR = 30
Point = tuple[int, int]


def unresolved_pair_indices() -> list[int]:
    data = json.loads(PRIOR_RESULT.read_text(encoding="utf-8"))
    result = [int(value) for value in data["unknown_case_indices"]]
    if len(result) != 88 or len(set(result)) != 88:
        raise ValueError("expected exactly 88 distinct UNKNOWN pair indices")
    if any(not 0 <= value < 121 for value in result):
        raise ValueError("UNKNOWN pair index outside 0..120")
    return result


def child_count() -> int:
    return len(unresolved_pair_indices()) * CHILDREN_PER_PAIR


def decode_child(child_id: int) -> tuple[int, int, int]:
    unresolved = unresolved_pair_indices()
    if not 0 <= child_id < len(unresolved) * CHILDREN_PER_PAIR:
        raise ValueError(f"child-id must be in 0..{len(unresolved) * CHILDREN_PER_PAIR - 1}")
    pair_position, remainder = divmod(child_id, CHILDREN_PER_PAIR)
    plus_offset, minus_offset = divmod(remainder, 6)
    return unresolved[pair_position], 13 + plus_offset, 12 + minus_offset


def add_occupancy_state(model, selected, group, name):
    count = sum(selected[point] for point in group)
    zero = model.NewBoolVar(f"{name}_zero")
    one = model.NewBoolVar(f"{name}_one")
    two = model.NewBoolVar(f"{name}_two")
    model.AddExactlyOne(zero, one, two)
    model.Add(count == 0).OnlyEnforceIf(zero)
    model.Add(count == 1).OnlyEnforceIf(one)
    model.Add(count == 2).OnlyEnforceIf(two)
    return zero, one, two


def add_lex_less_or_equal(model, left, right, prefix):
    if len(left) != len(right):
        raise ValueError("lex vectors have different lengths")
    prefix_equal = model.NewBoolVar(f"{prefix}_prefix_equal_0")
    model.Add(prefix_equal == 1)
    for index, (left_value, right_value) in enumerate(zip(left, right)):
        model.Add(left_value <= right_value).OnlyEnforceIf(prefix_equal)
        item_equal = model.NewBoolVar(f"{prefix}_item_equal_{index}")
        model.Add(left_value == right_value).OnlyEnforceIf(item_equal)
        model.Add(left_value != right_value).OnlyEnforceIf(item_equal.Not())
        next_prefix_equal = model.NewBoolVar(f"{prefix}_prefix_equal_{index + 1}")
        model.AddBoolAnd([prefix_equal, item_equal]).OnlyEnforceIf(next_prefix_equal)
        model.AddBoolOr([prefix_equal.Not(), item_equal.Not()]).OnlyEnforceIf(next_prefix_equal.Not())
        prefix_equal = next_prefix_equal


def family_minimum_defect(weights, exact_twos, fixed_minimum, forced_twos):
    infinity = 10**30
    states = {(0, 0): 0}
    for key, weight in weights.items():
        minimum = max(fixed_minimum.get(key, 0), 2 if key in forced_twos else 0)
        next_states = {}
        for (twos_used, occupancy_used), cost in states.items():
            for occupancy in range(minimum, 3):
                new_twos = twos_used + int(occupancy == 2)
                new_occupancy = occupancy_used + occupancy
                if new_twos > exact_twos or new_occupancy > TARGET:
                    continue
                new_cost = cost + weight * (2 - occupancy)
                state = (new_twos, new_occupancy)
                if new_cost < next_states.get(state, infinity):
                    next_states[state] = new_cost
        states = next_states
    return states.get((exact_twos, TARGET), infinity)


def analytic_minimum_defect(pair, plus_twos, minus_twos, residual, weights):
    row_weights = {key: weight for (family, key), weight in weights.items() if family == "row"}
    column_weights = {key: weight for (family, key), weight in weights.items() if family == "column"}
    plus_weights = {key: weight for (family, key), weight in weights.items() if family == "diag_plus"}
    minus_weights = {key: weight for (family, key), weight in weights.items() if family == "diag_minus"}
    forced_rows = {key for key, weight in row_weights.items() if weight > residual}
    forced_columns = {key for key, weight in column_weights.items() if weight > residual}
    forced_plus = {key for key, weight in plus_weights.items() if weight > residual}
    forced_minus = {key for key, weight in minus_weights.items() if weight > residual}
    fixed_rows = {coordinate: 1 for coordinate in pair}
    fixed_columns = dict(fixed_rows)
    fixed_plus = {0: 2}
    fixed_minus = {2 * coordinate: 1 for coordinate in pair}
    row_costs = {count: family_minimum_defect(row_weights, count, fixed_rows, forced_rows) for count in range(12, 18)}
    column_costs = {count: family_minimum_defect(column_weights, count, fixed_columns, forced_columns) for count in range(12, 18)}
    plus_cost = family_minimum_defect(plus_weights, plus_twos, fixed_plus, forced_plus)
    minus_cost = family_minimum_defect(minus_weights, minus_twos, fixed_minus, forced_minus)
    row_column_cost = min(
        row_costs[row_count] + column_costs[column_count]
        for row_count in range(12, 18)
        for column_count in range(row_count, 18)
    )
    total = row_column_cost + plus_cost + minus_cost
    return total, {
        "row_costs": row_costs,
        "column_costs": column_costs,
        "plus_cost": plus_cost,
        "minus_cost": minus_cost,
        "row_column_minimum": row_column_cost,
    }


def build_model(pair_index, plus_twos, minus_twos):
    pair = canonical_main_diagonal_pairs()[pair_index]
    points = allowed_points()
    lines = build_maximal_lines(points)
    certificate = load_certificate()
    denominator = int(certificate["denominator"])
    slack = int(certificate["slack_numerator"])
    weights = certificate_weights(certificate)
    pair_excess = sum(point_cover((coordinate, coordinate), weights) - denominator for coordinate in pair)
    residual = slack - pair_excess
    if residual < 0:
        raise ValueError("fixed pair exceeds certificate slack")
    minimum_defect, defect_details = analytic_minimum_defect(pair, plus_twos, minus_twos, residual, weights)
    metadata = {
        "main_diagonal_pair": list(pair),
        "pair_index": pair_index,
        "diag_plus_twos": plus_twos,
        "diag_minus_twos": minus_twos,
        "pair_excess": pair_excess,
        "residual_certificate_slack": residual,
        "analytic_minimum_line_defect": minimum_defect,
        "analytic_defect_details": defect_details,
        "maximal_line_constraints": len(lines),
    }
    if minimum_defect > residual:
        metadata["analytic_infeasible"] = True
        return cp_model.CpModel(), points, {}, metadata

    model = cp_model.CpModel()
    selected = {point: model.NewBoolVar(f"p_{point[0]}_{point[1]}") for point in points}
    for member_indices in lines.values():
        model.Add(sum(selected[points[index]] for index in member_indices) <= 2)
    model.Add(sum(selected.values()) == TARGET)
    pair_set = set(pair)
    for coordinate in range(N):
        model.Add(selected[(coordinate, coordinate)] == int(coordinate in pair_set))

    off_diagonal = [point for point in points if point[0] != point[1]]
    off_diagonal_excess = {point: point_cover(point, weights) - denominator for point in off_diagonal}
    model.Add(sum(excess * selected[point] for point, excess in off_diagonal_excess.items() if excess > 0) <= residual)
    for threshold in sorted({value for value in off_diagonal_excess.values() if value > 0}):
        model.Add(sum(selected[point] for point, excess in off_diagonal_excess.items() if excess >= threshold) <= residual // threshold)

    families = []
    for key in range(N):
        families.append(("row", key, weights[("row", key)], [p for p in points if p[1] == key]))
    for key in range(N):
        families.append(("column", key, weights[("column", key)], [p for p in points if p[0] == key]))
    plus_keys = sorted(key for family, key in weights if family == "diag_plus")
    minus_keys = sorted(key for family, key in weights if family == "diag_minus")
    for key in plus_keys:
        families.append(("diag_plus", key, weights[("diag_plus", key)], [p for p in points if p[0] - p[1] == key]))
    for key in minus_keys:
        families.append(("diag_minus", key, weights[("diag_minus", key)], [p for p in points if p[0] + p[1] == key]))

    states = {}
    for family, key, weight, group in families:
        state = add_occupancy_state(model, selected, group, f"{family}_{key}")
        states[(family, key)] = state
        if weight > residual:
            model.Add(state[2] == 1)
    model.Add(sum(weight * (states[(family, key)][1] + 2 * states[(family, key)][0]) for family, key, weight, _ in families) <= residual)

    row_twos = [states[("row", key)][2] for key in range(N)]
    column_twos = [states[("column", key)][2] for key in range(N)]
    plus_two_flags = [states[("diag_plus", key)][2] for key in plus_keys]
    minus_two_flags = [states[("diag_minus", key)][2] for key in minus_keys]
    model.Add(sum(row_twos) >= 12)
    model.Add(sum(row_twos) <= 17)
    model.Add(sum(column_twos) >= 12)
    model.Add(sum(column_twos) <= 17)
    model.Add(sum(row_twos) <= sum(column_twos))
    model.Add(sum(plus_two_flags) == plus_twos)
    model.Add(sum(minus_two_flags) == minus_twos)

    above = []
    below = []
    for y in range(N):
        for x in range(y):
            if (x + y) % 2 == PARITY:
                above.append(selected[(x, y)])
                below.append(selected[(y, x)])
    add_lex_less_or_equal(model, above, below, "transpose")
    metadata["analytic_infeasible"] = False
    metadata["allowed_points"] = len(points)
    return model, points, selected, metadata


def solve_child(child_id, seconds, workers, requested_seed):
    pair_index, plus_twos, minus_twos = decode_child(child_id)
    build_started = time.time()
    model, points, selected, metadata = build_model(pair_index, plus_twos, minus_twos)
    build_seconds = time.time() - build_started
    record = {
        "board_size": N,
        "parity_proved": PARITY,
        "target": TARGET,
        "child_id": child_id,
        "child_count": child_count(),
        "partition": "unknown_pair_x_diag_plus_twos_x_diag_minus_twos",
        "build_seconds": build_seconds,
        "workers": workers,
        "requested_seed": requested_seed,
        "effective_seed": requested_seed % MAX_SEED,
        **metadata,
    }
    if bool(metadata["analytic_infeasible"]):
        record.update({
            "status": "INFEASIBLE",
            "proof_method": "exact_certificate_defect_lower_bound",
            "elapsed_seconds": 0.0,
            "branches": 0,
            "conflicts": 0,
        })
        return record
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
        "proof_method": "cp_sat_all_lines_with_certificate_profile_cuts",
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child-id", type=int)
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260720)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list-children", action="store_true")
    args = parser.parse_args()
    if args.list_children:
        print(json.dumps([
            {"child_id": child_id, "pair_index": decode_child(child_id)[0], "diag_plus_twos": decode_child(child_id)[1], "diag_minus_twos": decode_child(child_id)[2]}
            for child_id in range(child_count())
        ], indent=2))
        return
    if args.child_id is None:
        raise SystemExit("--child-id is required unless --list-children is used")
    record = solve_child(args.child_id, args.seconds, args.workers, args.seed)
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
