#!/usr/bin/env python3
"""Collect the 21 exact row/column subcases covering n=22 child 652."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import validate_solution
from prove_upper_22x22_rowcol_subcase import ROWCOL_CASES

TOTAL_CHILDREN = 2640


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-overall", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-sha", default="")
    args = parser.parse_args()

    prior = read_json(args.prior_overall)
    if prior.get("remaining_child_ids") != [652]:
        raise ValueError("prior aggregate must contain only child 652")
    if int(prior.get("cumulative_all_children_infeasible", -1)) != 2639:
        raise ValueError("prior aggregate must contain 2639 exact exclusions")
    prior_records = prior["records"]
    prior_by_id = {int(record["child_id"]): record for record in prior_records}
    if len(prior_by_id) != 776:
        raise ValueError("prior aggregate must contain all 776 long-run records")

    paths = sorted(args.input_dir.rglob("subcase-*.json"))
    paths = [path for path in paths if "-attempt-" not in path.name and "-summary" not in path.name]
    observed: dict[int, dict[str, object]] = {}
    duplicates: list[int] = []
    unexpected: list[int] = []
    for path in paths:
        record = read_json(path)
        subcase_id = int(record["subcase_id"])
        if not 0 <= subcase_id < len(ROWCOL_CASES):
            unexpected.append(subcase_id)
            continue
        expected_row, expected_column = ROWCOL_CASES[subcase_id]
        if int(record.get("child_id", -1)) != 652:
            unexpected.append(subcase_id)
            continue
        if int(record.get("row_twos", -1)) != expected_row or int(record.get("column_twos", -1)) != expected_column:
            unexpected.append(subcase_id)
            continue
        if subcase_id in observed:
            duplicates.append(subcase_id)
        else:
            observed[subcase_id] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    expected_ids = list(range(len(ROWCOL_CASES)))
    missing = [subcase_id for subcase_id in expected_ids if subcase_id not in observed]
    ordered = [observed[subcase_id] for subcase_id in expected_ids if subcase_id in observed]
    counts = {
        status: sum(record.get("status") == status for record in ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    feasible = [record for record in ordered if record.get("status") in {"FEASIBLE", "OPTIMAL"}]
    technical = [record for record in ordered if record.get("final_technical_status") is not None]
    memory_guard = [
        record for record in ordered
        if any(bool(attempt.get("memory_guard_triggered")) for attempt in record.get("attempts", []))
    ]
    remaining_subcases = [
        int(record["subcase_id"])
        for record in ordered
        if record.get("status") != "INFEASIBLE"
    ]
    technical_failure = bool(missing or duplicates or unexpected or counts["MODEL_INVALID"])
    if feasible:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif not technical_failure and not remaining_subcases:
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif technical_failure:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "ROWCOL_SPLIT_INCOMPLETE"

    selected_child_record: dict[str, object]
    if feasible:
        selected_child_record = feasible[0]
    elif not remaining_subcases:
        selected_child_record = dict(prior_by_id[652])
        selected_child_record.update({
            "status": "INFEASIBLE",
            "proof_method": "exhaustive_exact_row_column_twos_partition",
            "rowcol_subcase_count": len(ROWCOL_CASES),
            "rowcol_all_subcases_infeasible": True,
        })
    else:
        unresolved_records = [observed[subcase_id] for subcase_id in remaining_subcases]
        selected_child_record = max(
            unresolved_records,
            key=lambda record: int(record.get("branches", 0)) + 2 * int(record.get("conflicts", 0)),
        )
        selected_child_record = dict(selected_child_record)
        selected_child_record["status"] = "UNKNOWN"
        selected_child_record["remaining_rowcol_subcase_ids"] = remaining_subcases

    combined_by_id = dict(prior_by_id)
    combined_by_id[652] = selected_child_record
    combined_ordered = [combined_by_id[child_id] for child_id in sorted(combined_by_id)]
    cumulative_long_infeasible = sum(record.get("status") == "INFEASIBLE" for record in combined_ordered)
    cumulative_all = 1864 + cumulative_long_infeasible
    remaining_child_ids = [] if selected_child_record.get("status") == "INFEASIBLE" else [652]
    remaining_pair_indices = [] if not remaining_child_ids else [40]

    peak_values = [
        float(attempt.get("peak_rss_mb", 0.0))
        for record in ordered
        for attempt in record.get("attempts", [])
    ]
    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "prior_run_id": int(prior["run_id"]),
        "conclusion": conclusion,
        "expected_subcases": len(ROWCOL_CASES),
        "records_found": len(observed),
        "missing_subcase_ids": missing,
        "duplicate_subcase_ids": sorted(set(duplicates)),
        "unexpected_subcase_ids": sorted(set(unexpected)),
        "status_counts": counts,
        "technical_record_count": len(technical),
        "memory_guard_record_count": len(memory_guard),
        "maximum_peak_rss_mb": max(peak_values or [0.0]),
        "remaining_rowcol_subcase_ids": remaining_subcases,
        "remaining_child_ids": remaining_child_ids,
        "remaining_pair_indices": remaining_pair_indices,
        "cumulative_all_children_infeasible": cumulative_all,
        "solver_job_hours": sum(float(record.get("elapsed_seconds", 0.0)) for record in ordered) / 3600.0,
        "total_branches": sum(int(record.get("branches", 0)) for record in ordered),
        "total_conflicts": sum(int(record.get("conflicts", 0)) for record in ordered),
        "subcase_records": ordered,
        "records": combined_ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# n22 child-652 row/column split",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- expected exact subcases: {len(ROWCOL_CASES)}",
        f"- records found: {len(observed)}",
        f"- INFEASIBLE: {counts['INFEASIBLE']}",
        f"- UNKNOWN: {counts['UNKNOWN']}",
        f"- FEASIBLE/OPTIMAL: {counts['FEASIBLE'] + counts['OPTIMAL']}",
        f"- missing: {len(missing)}",
        f"- technical records: {len(technical)}",
        f"- memory-guard records: {len(memory_guard)}",
        f"- remaining row/column subcases: {remaining_subcases}",
        f"- cumulative exact exclusions: {cumulative_all} / {TOTAL_CHILDREN}",
        f"- solver work: {overall['solver_job_hours']:.2f} job-hours",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend([
            "",
            "All 21 exact row/column subcases covering child 652 are INFEASIBLE.",
            "Together with the independently verified 33-point construction, this proves `D_mono(22)=33`.",
        ])
    elif conclusion == "FOUND_VALID_34_POINT_CONFIGURATION":
        lines.extend([
            "",
            "A valid 34-point configuration was found and independently checked.",
        ])
    else:
        lines.extend(["", "`UNKNOWN` is not treated as a proof."])
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "conclusion": conclusion,
        "status_counts": counts,
        "remaining_rowcol_subcase_ids": remaining_subcases,
        "cumulative_all_children_infeasible": cumulative_all,
    }, indent=2))
    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
