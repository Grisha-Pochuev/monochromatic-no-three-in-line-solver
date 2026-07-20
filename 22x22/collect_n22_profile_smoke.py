#!/usr/bin/env python3
"""Collect the complete 2640-child n22 profile smoke run."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from prove_upper_22x22_profile_child import (
    child_count,
    unresolved_pair_indices,
)
from prove_upper_22x22_main_diagonal_pair import validate_solution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-sha", default="")
    args = parser.parse_args()

    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(args.input_dir.rglob("child-*.json"))
    ]
    by_id = {}
    duplicates = []
    for record in records:
        child_id = int(record["child_id"])
        if child_id in by_id:
            duplicates.append(child_id)
        else:
            by_id[child_id] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    missing = [child_id for child_id in range(child_count()) if child_id not in by_id]
    ordered = [by_id[child_id] for child_id in sorted(by_id)]
    status_counts = {
        status: sum(record.get("status") == status for record in ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }

    pair_records = defaultdict(list)
    for record in ordered:
        pair_records[int(record["pair_index"])].append(record)
    closed_pairs = sorted(
        pair_index
        for pair_index in unresolved_pair_indices()
        if len(pair_records[pair_index]) == 30
        and all(record["status"] == "INFEASIBLE" for record in pair_records[pair_index])
    )
    remaining_pairs = sorted(
        pair_index
        for pair_index in unresolved_pair_indices()
        if pair_index not in closed_pairs
    )
    feasible = [
        record for record in ordered
        if record["status"] in {"FEASIBLE", "OPTIMAL"}
    ]

    if feasible:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif (
        not missing
        and not duplicates
        and status_counts["MODEL_INVALID"] == 0
        and len(closed_pairs) == 88
    ):
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif missing or duplicates or status_counts["MODEL_INVALID"]:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "PROFILE_SMOKE_INCOMPLETE"

    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "conclusion": conclusion,
        "expected_children": child_count(),
        "records_found": len(ordered),
        "missing_child_ids": missing,
        "duplicate_child_ids": sorted(set(duplicates)),
        "status_counts": status_counts,
        "newly_closed_pair_indices": closed_pairs,
        "remaining_pair_indices": remaining_pairs,
        "remaining_child_ids": [
            int(record["child_id"])
            for record in ordered
            if record["status"] == "UNKNOWN"
        ],
        "total_solver_job_hours": sum(
            float(record.get("elapsed_seconds", 0.0)) for record in ordered
        ) / 3600.0,
        "total_branches": sum(int(record.get("branches", 0)) for record in ordered),
        "total_conflicts": sum(int(record.get("conflicts", 0)) for record in ordered),
        "records": ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# n22 pair/profile smoke",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- expected children: {child_count()}",
        f"- records found: {len(ordered)}",
        f"- INFEASIBLE: {status_counts['INFEASIBLE']}",
        f"- UNKNOWN: {status_counts['UNKNOWN']}",
        f"- FEASIBLE/OPTIMAL: {status_counts['FEASIBLE'] + status_counts['OPTIMAL']}",
        f"- newly closed main-diagonal pairs: {len(closed_pairs)}",
        f"- remaining main-diagonal pairs: {len(remaining_pairs)}",
        f"- solver work: {overall['total_solver_job_hours']:.2f} job-hours",
        "",
        "Every one of the 88 prior UNKNOWN pairs was partitioned into 30 exact children:",
        "`diag_plus_twos = 13..17` and `diag_minus_twos = 12..17`.",
        "Analytic certificate-defect exclusions and CP-SAT INFEASIBLE statuses are exact.",
    ]
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "conclusion": conclusion,
        "status_counts": status_counts,
        "closed_pairs": closed_pairs,
        "missing": missing,
        "duplicates": sorted(set(duplicates)),
    }, indent=2))
    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
