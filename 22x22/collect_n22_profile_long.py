#!/usr/bin/env python3
"""Collect the 5h50 rerun of the 776 unresolved n22 profile children."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from prove_upper_22x22_profile_child import unresolved_pair_indices
from prove_upper_22x22_main_diagonal_pair import validate_solution

HERE = Path(__file__).resolve().parent
SCHEDULE_PATH = HERE / "runs/2026-07-20-run-29766054707/long_profile_schedule.json"
CHILDREN_PER_PAIR = 30


def load_schedule() -> dict[str, object]:
    data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    all_ids = [int(child_id) for item in data["assignments"] for child_id in item["ids"]]
    if len(all_ids) != 776 or len(set(all_ids)) != 776:
        raise ValueError("expected 776 distinct scheduled children")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-sha", default="")
    args = parser.parse_args()

    schedule = load_schedule()
    expected_ids = sorted(
        int(child_id)
        for item in schedule["assignments"]
        for child_id in item["ids"]
    )
    expected_set = set(expected_ids)

    paths = sorted(args.input_dir.rglob("child-*.json"))
    # Ignore attempt JSONs; only final records are named child-NNNN.json.
    paths = [path for path in paths if "-attempt-" not in path.name]
    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]

    by_id: dict[int, dict[str, object]] = {}
    duplicates: list[int] = []
    unexpected: list[int] = []
    for record in records:
        child_id = int(record["child_id"])
        if child_id not in expected_set:
            unexpected.append(child_id)
            continue
        if child_id in by_id:
            duplicates.append(child_id)
        else:
            by_id[child_id] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    missing = [child_id for child_id in expected_ids if child_id not in by_id]
    ordered = [by_id[child_id] for child_id in expected_ids if child_id in by_id]
    status_counts = {
        status: sum(record.get("status") == status for record in ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    technical_records = [
        record for record in ordered
        if record.get("final_technical_status") is not None
    ]
    memory_guard_records = [
        record for record in ordered
        if any(
            bool(attempt.get("memory_guard_triggered"))
            for attempt in record.get("attempts", [])
        )
    ]
    feasible = [
        record for record in ordered
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]

    # Every child not scheduled here was already exact-INFEASIBLE in run 29766054707.
    current_status = {int(record["child_id"]): record.get("status") for record in ordered}
    unresolved = unresolved_pair_indices()
    pair_remaining: dict[int, list[int]] = defaultdict(list)
    for child_id in expected_ids:
        pair_position = child_id // CHILDREN_PER_PAIR
        pair_index = unresolved[pair_position]
        if current_status.get(child_id) != "INFEASIBLE":
            pair_remaining[pair_index].append(child_id)
    newly_closed_pairs = sorted(
        pair_index for pair_index in unresolved
        if not pair_remaining[pair_index]
    )
    remaining_pairs = sorted(
        pair_index for pair_index in unresolved
        if pair_remaining[pair_index]
    )
    remaining_children = sorted(
        child_id for child_id in expected_ids
        if current_status.get(child_id) != "INFEASIBLE"
    )

    if feasible:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif (
        not missing
        and not duplicates
        and not unexpected
        and status_counts["MODEL_INVALID"] == 0
        and not remaining_children
    ):
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif missing or duplicates or unexpected or status_counts["MODEL_INVALID"]:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "LONG_PROFILE_RUN_INCOMPLETE"

    peak_values = [
        float(attempt.get("peak_rss_mb", 0.0))
        for record in ordered
        for attempt in record.get("attempts", [])
    ]
    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "source_smoke_run_id": 29766054707,
        "conclusion": conclusion,
        "expected_long_children": len(expected_ids),
        "records_found": len(ordered),
        "missing_child_ids": missing,
        "duplicate_child_ids": sorted(set(duplicates)),
        "unexpected_child_ids": sorted(set(unexpected)),
        "status_counts": status_counts,
        "technical_record_count": len(technical_records),
        "memory_guard_record_count": len(memory_guard_records),
        "maximum_peak_rss_mb": max(peak_values or [0.0]),
        "newly_closed_pair_indices": newly_closed_pairs,
        "remaining_pair_indices": remaining_pairs,
        "remaining_child_ids": remaining_children,
        "total_solver_job_hours": sum(
            float(record.get("elapsed_seconds", 0.0)) for record in ordered
        ) / 3600.0,
        "total_branches": sum(int(record.get("branches", 0)) for record in ordered),
        "total_conflicts": sum(int(record.get("conflicts", 0)) for record in ordered),
        "records": ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# n22 5h50 profile-survivor run",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- scheduled children: {len(expected_ids)}",
        f"- records found: {len(ordered)}",
        f"- INFEASIBLE: {status_counts['INFEASIBLE']}",
        f"- UNKNOWN: {status_counts['UNKNOWN']}",
        f"- FEASIBLE/OPTIMAL: {status_counts['FEASIBLE'] + status_counts['OPTIMAL']}",
        f"- missing: {len(missing)}",
        f"- technical records: {len(technical_records)}",
        f"- memory-guard records: {len(memory_guard_records)}",
        f"- maximum recorded child RSS: {overall['maximum_peak_rss_mb']:.1f} MB",
        f"- newly closed main-diagonal pairs: {len(newly_closed_pairs)}",
        f"- remaining main-diagonal pairs: {len(remaining_pairs)}",
        f"- remaining exact children: {len(remaining_children)}",
        f"- solver work: {overall['total_solver_job_hours']:.2f} job-hours",
        "",
        "The 1864 children excluded by run 29766054707 were not recomputed.",
        "Each long child ran as a separate process with four CP-SAT workers and a",
        "13 GB parent-side RSS guard; memory failures were eligible for a two-worker retry.",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend([
            "",
            "All 2640 profile children are now exact-INFEASIBLE. Together with the",
            "verified 33-point construction this proves `D_mono(22)=33`.",
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
        "status_counts": status_counts,
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
