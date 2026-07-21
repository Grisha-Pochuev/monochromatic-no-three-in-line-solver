#!/usr/bin/env python3
"""Collect a follow-up run over the exact n=22 profile-child survivors."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from prove_upper_22x22_profile_child import unresolved_pair_indices
from prove_upper_22x22_main_diagonal_pair import validate_solution

CHILDREN_PER_PAIR = 30
PRIOR_SMOKE_INFEASIBLE = 1864


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--prior-overall", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-sha", default="")
    args = parser.parse_args()

    schedule = read_json(args.schedule)
    prior = read_json(args.prior_overall)
    expected_ids = sorted(
        int(child_id)
        for item in schedule["assignments"]
        for child_id in item["ids"]
    )
    if len(expected_ids) != int(schedule["unknown_child_count"]):
        raise ValueError("follow-up schedule count mismatch")
    if expected_ids != sorted(int(value) for value in prior["remaining_child_ids"]):
        raise ValueError("schedule is not exactly the prior remaining frontier")

    paths = sorted(args.input_dir.rglob("child-*.json"))
    paths = [path for path in paths if "-attempt-" not in path.name]
    current_records = [read_json(path) for path in paths]

    expected_set = set(expected_ids)
    current_by_id: dict[int, dict[str, object]] = {}
    duplicates: list[int] = []
    unexpected: list[int] = []
    for record in current_records:
        child_id = int(record["child_id"])
        if child_id not in expected_set:
            unexpected.append(child_id)
            continue
        if child_id in current_by_id:
            duplicates.append(child_id)
        else:
            current_by_id[child_id] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    missing = [child_id for child_id in expected_ids if child_id not in current_by_id]
    current_ordered = [current_by_id[child_id] for child_id in expected_ids if child_id in current_by_id]
    current_counts = {
        status: sum(record.get("status") == status for record in current_ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }

    prior_records = prior["records"]
    prior_by_id = {int(record["child_id"]): record for record in prior_records}
    if len(prior_by_id) != 776:
        raise ValueError("prior aggregate must contain all 776 long records")
    combined_by_id = dict(prior_by_id)
    combined_by_id.update(current_by_id)
    combined_ordered = [combined_by_id[child_id] for child_id in sorted(combined_by_id)]
    cumulative_counts = {
        status: sum(record.get("status") == status for record in combined_ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }

    feasible = [
        record for record in current_ordered
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]
    technical_records = [
        record for record in current_ordered
        if record.get("final_technical_status") is not None
    ]
    memory_guard_records = [
        record for record in current_ordered
        if any(bool(attempt.get("memory_guard_triggered")) for attempt in record.get("attempts", []))
    ]

    unresolved_pairs = unresolved_pair_indices()
    pair_remaining: dict[int, list[int]] = defaultdict(list)
    for child_id, record in combined_by_id.items():
        pair_position = child_id // CHILDREN_PER_PAIR
        pair_index = unresolved_pairs[pair_position]
        if record.get("status") != "INFEASIBLE":
            pair_remaining[pair_index].append(child_id)
    prior_remaining_pairs = set(int(value) for value in prior["remaining_pair_indices"])
    remaining_pairs = sorted(pair_remaining)
    newly_closed_pairs = sorted(prior_remaining_pairs - set(remaining_pairs))
    remaining_children = sorted(
        child_id for child_id, record in combined_by_id.items()
        if record.get("status") != "INFEASIBLE"
    )

    technical_failure = bool(
        missing
        or duplicates
        or unexpected
        or current_counts["MODEL_INVALID"]
    )
    if feasible:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif not technical_failure and not remaining_children:
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif technical_failure:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "FOLLOWUP_RUN_INCOMPLETE"

    peak_values = [
        float(attempt.get("peak_rss_mb", 0.0))
        for record in current_ordered
        for attempt in record.get("attempts", [])
    ]
    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "prior_run_id": int(schedule["source_run_id"]),
        "prior_run_url": schedule.get("source_run_url", ""),
        "conclusion": conclusion,
        "expected_followup_children": len(expected_ids),
        "records_found": len(current_ordered),
        "missing_child_ids": missing,
        "duplicate_child_ids": sorted(set(duplicates)),
        "unexpected_child_ids": sorted(set(unexpected)),
        "current_status_counts": current_counts,
        "cumulative_long_status_counts": cumulative_counts,
        "prior_smoke_infeasible_count": PRIOR_SMOKE_INFEASIBLE,
        "cumulative_all_children_infeasible": PRIOR_SMOKE_INFEASIBLE + cumulative_counts["INFEASIBLE"],
        "technical_record_count": len(technical_records),
        "memory_guard_record_count": len(memory_guard_records),
        "maximum_peak_rss_mb": max(peak_values or [0.0]),
        "newly_closed_pair_indices": newly_closed_pairs,
        "remaining_pair_indices": remaining_pairs,
        "remaining_child_ids": remaining_children,
        "current_solver_job_hours": sum(float(record.get("elapsed_seconds", 0.0)) for record in current_ordered) / 3600.0,
        "current_total_branches": sum(int(record.get("branches", 0)) for record in current_ordered),
        "current_total_conflicts": sum(int(record.get("conflicts", 0)) for record in current_ordered),
        "records": combined_ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# n22 profile follow-up run",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- scheduled children: {len(expected_ids)}",
        f"- records found: {len(current_ordered)}",
        f"- current INFEASIBLE: {current_counts['INFEASIBLE']}",
        f"- current UNKNOWN: {current_counts['UNKNOWN']}",
        f"- current FEASIBLE/OPTIMAL: {current_counts['FEASIBLE'] + current_counts['OPTIMAL']}",
        f"- missing: {len(missing)}",
        f"- technical records: {len(technical_records)}",
        f"- memory-guard records: {len(memory_guard_records)}",
        f"- maximum recorded child RSS: {overall['maximum_peak_rss_mb']:.1f} MB",
        f"- newly closed main-diagonal pairs: {len(newly_closed_pairs)}",
        f"- remaining main-diagonal pairs: {len(remaining_pairs)}",
        f"- remaining exact children: {len(remaining_children)}",
        f"- cumulative exact exclusions: {overall['cumulative_all_children_infeasible']} / 2640",
        f"- current solver work: {overall['current_solver_job_hours']:.2f} job-hours",
        "",
        "No child proved infeasible in an earlier run was recomputed.",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend([
            "",
            "All 2640 exact profile children are now INFEASIBLE. Together with the",
            "independently verified 33-point construction this proves `D_mono(22)=33`.",
        ])
    elif conclusion == "FOUND_VALID_34_POINT_CONFIGURATION":
        lines.extend([
            "",
            "A valid 34-point configuration was found and independently checked.",
            "Together with the existing upper bound this proves `D_mono(22)=34`.",
        ])
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "conclusion": conclusion,
        "current_status_counts": current_counts,
        "cumulative_all_children_infeasible": overall["cumulative_all_children_infeasible"],
        "missing": missing,
        "newly_closed_pairs": newly_closed_pairs,
        "remaining_pairs": len(remaining_pairs),
        "remaining_children": len(remaining_children),
        "memory_guard_records": len(memory_guard_records),
    }, indent=2))
    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
