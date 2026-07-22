#!/usr/bin/env python3
"""Collect the complete 21-case row/column split of final n=22 child 652."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from prove_upper_22x22_final_child_rowcol import FINAL_CHILD_ID, subcases
from prove_upper_22x22_main_diagonal_pair import validate_solution


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-sha", default="")
    args = parser.parse_args()

    expected = set(range(len(subcases())))
    paths = sorted(args.input_dir.rglob("subcase-*.json"))
    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    by_id: dict[int, dict[str, object]] = {}
    duplicates: list[int] = []
    unexpected: list[int] = []
    for record in records:
        subcase_id = int(record["subcase_id"])
        if int(record.get("parent_child_id", -1)) != FINAL_CHILD_ID or subcase_id not in expected:
            unexpected.append(subcase_id)
            continue
        if subcase_id in by_id:
            duplicates.append(subcase_id)
        else:
            by_id[subcase_id] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    missing = sorted(expected - set(by_id))
    ordered = [by_id[index] for index in sorted(by_id)]
    counts = {
        status: sum(record.get("status") == status for record in ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    feasible = [record for record in ordered if record.get("status") in {"FEASIBLE", "OPTIMAL"}]
    technical_failure = bool(missing or duplicates or unexpected or counts["MODEL_INVALID"])
    if feasible and not technical_failure:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif not technical_failure and len(ordered) == len(expected) and counts["INFEASIBLE"] == len(expected):
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif technical_failure:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "ROWCOL_SPLIT_INCOMPLETE"

    remaining = [
        {
            "subcase_id": int(record["subcase_id"]),
            "row_twos": int(record["row_twos"]),
            "column_twos": int(record["column_twos"]),
            "status": str(record["status"]),
        }
        for record in ordered
        if record.get("status") != "INFEASIBLE"
    ]
    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "parent_child_id": FINAL_CHILD_ID,
        "partition": "exact_row_twos_x_exact_column_twos",
        "expected_subcases": len(expected),
        "records_found": len(ordered),
        "missing_subcase_ids": missing,
        "duplicate_subcase_ids": sorted(set(duplicates)),
        "unexpected_subcase_ids": sorted(set(unexpected)),
        "status_counts": counts,
        "remaining_subcases": remaining,
        "conclusion": conclusion,
        "solver_job_hours": sum(float(record.get("elapsed_seconds", 0.0)) for record in ordered) / 3600.0,
        "total_branches": sum(int(record.get("branches", 0)) for record in ordered),
        "total_conflicts": sum(int(record.get("conflicts", 0)) for record in ordered),
        "validated_solutions": feasible,
        "records": ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# n22 final child 652 row/column split",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- expected subcases: {len(expected)}",
        f"- records found: {len(ordered)}",
        f"- INFEASIBLE: {counts['INFEASIBLE']}",
        f"- UNKNOWN: {counts['UNKNOWN']}",
        f"- FEASIBLE/OPTIMAL: {counts['FEASIBLE'] + counts['OPTIMAL']}",
        f"- MODEL_INVALID: {counts['MODEL_INVALID']}",
        f"- missing: {len(missing)}",
        f"- remaining subcases: {len(remaining)}",
        f"- solver work: {overall['solver_job_hours']:.2f} job-hours",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend(["", "All 21 subcases are INFEASIBLE. This closes final child 652 and proves `D_mono(22)=33` together with the verified 33-point construction."])
    elif conclusion == "FOUND_VALID_34_POINT_CONFIGURATION":
        lines.extend(["", "A valid 34-point configuration was found and independently checked."])
    else:
        lines.extend(["", "UNKNOWN is not treated as a proof."])
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"conclusion": conclusion, "counts": counts, "remaining": remaining}, indent=2))
    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
