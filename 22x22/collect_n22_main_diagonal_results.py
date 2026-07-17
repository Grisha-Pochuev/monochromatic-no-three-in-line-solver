#!/usr/bin/env python3
"""Collect and validate all 121 canonical main-diagonal pair records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import canonical_main_diagonal_pairs


def independently_validate_solution(solution: list[list[int]]) -> None:
    points = [tuple(map(int, point)) for point in solution]
    if len(points) != 34 or len(set(points)) != 34:
        raise ValueError("solution size or distinctness failure")
    for x, y in points:
        if not (0 <= x < 22 and 0 <= y < 22):
            raise ValueError(f"point outside board: {(x, y)}")
        if (x + y) % 2 != 0:
            raise ValueError(f"wrong parity: {(x, y)}")
    for i in range(len(points)):
        x1, y1 = points[i]
        for j in range(i + 1, len(points)):
            x2, y2 = points[j]
            for k in range(j + 1, len(points)):
                x3, y3 = points[k]
                determinant = (
                    (x2 - x1) * (y3 - y1)
                    - (y2 - y1) * (x3 - x1)
                )
                if determinant == 0:
                    raise ValueError(
                        f"collinear triple: {points[i]}, {points[j]}, {points[k]}"
                    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-id", type=str, default="")
    parser.add_argument("--run-url", type=str, default="")
    parser.add_argument("--run-sha", type=str, default="")
    args = parser.parse_args()

    expected_pairs = canonical_main_diagonal_pairs()
    paths = sorted(args.input_dir.rglob("case-*.json"))
    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]

    by_index: dict[int, dict[str, object]] = {}
    duplicates: list[int] = []
    mismatched_pairs: list[dict[str, object]] = []
    for record in records:
        index = int(record["canonical_case_index"])
        if index in by_index:
            duplicates.append(index)
            continue
        by_index[index] = record
        if not (0 <= index < len(expected_pairs)):
            mismatched_pairs.append({"case_index": index, "reason": "out_of_range"})
            continue
        if tuple(record["main_diagonal_pair"]) != expected_pairs[index]:
            mismatched_pairs.append({
                "case_index": index,
                "expected": list(expected_pairs[index]),
                "found": record["main_diagonal_pair"],
            })
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            independently_validate_solution(record["solution"])

    missing = [index for index in range(len(expected_pairs)) if index not in by_index]
    ordered = [by_index[index] for index in sorted(by_index)]
    status_counts = {
        status: sum(record.get("status") == status for record in ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    feasible = [
        record for record in ordered
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]
    invalid = status_counts["MODEL_INVALID"]

    if feasible:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif (
        len(ordered) == len(expected_pairs)
        and status_counts["INFEASIBLE"] == len(expected_pairs)
        and not duplicates
        and not mismatched_pairs
    ):
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif missing or duplicates or mismatched_pairs or invalid:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "INCOMPLETE_WITH_UNKNOWN_CASES"

    total_elapsed = sum(float(record.get("elapsed_seconds", 0.0)) for record in ordered)
    total_branches = sum(int(record.get("branches", 0)) for record in ordered)
    total_conflicts = sum(int(record.get("conflicts", 0)) for record in ordered)

    hardest_unknown = sorted(
        (
            record for record in ordered
            if record.get("status") == "UNKNOWN"
        ),
        key=lambda record: (
            int(record.get("conflicts", 0)),
            int(record.get("branches", 0)),
        ),
        reverse=True,
    )[:15]

    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "board_size": 22,
        "target": 34,
        "verified_lower_bound": 33,
        "partition": "121 canonical pairs on x=y under 180-degree rotation",
        "certificate": "22x22/upper_certificate_34_four_direction.json",
        "model": "all 2455 maximal lines plus rational-certificate consequences",
        "conclusion": conclusion,
        "expected_cases": len(expected_pairs),
        "records_found": len(ordered),
        "missing_case_indices": missing,
        "duplicate_case_indices": sorted(set(duplicates)),
        "mismatched_pairs": mismatched_pairs,
        "status_counts": status_counts,
        "total_solver_job_hours": total_elapsed / 3600.0,
        "total_branches": total_branches,
        "total_conflicts": total_conflicts,
        "hardest_unknown_cases": hardest_unknown,
        "records": ordered,
    }
    args.overall.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Five-hour n22 main-diagonal pair run",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- expected canonical cases: {len(expected_pairs)}",
        f"- records found: {len(ordered)}",
        f"- INFEASIBLE: {status_counts['INFEASIBLE']}",
        f"- UNKNOWN: {status_counts['UNKNOWN']}",
        f"- FEASIBLE/OPTIMAL: {status_counts['FEASIBLE'] + status_counts['OPTIMAL']}",
        f"- MODEL_INVALID: {status_counts['MODEL_INVALID']}",
        f"- missing cases: {len(missing)}",
        f"- duplicate cases: {len(set(duplicates))}",
        f"- total solver work: {total_elapsed / 3600.0:.2f} job-hours",
        f"- total branches: {total_branches:,}",
        f"- total conflicts: {total_conflicts:,}",
        "",
        "The rational certificate forces x-y = -2, 0, 2 to contain exactly two points.",
        "The selected pair on x=y therefore gives a complete partition. The 231 raw pairs",
        "reduce to 121 cases under 180-degree rotation, and every canonical case must be",
        "present exactly once for a complete proof.",
        "",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend([
            "All 121 canonical cases are `INFEASIBLE`, so no 34-point configuration exists.",
            "Together with the verified 33-point construction, this proves `D_mono(22)=33`.",
        ])
    elif feasible:
        lines.extend([
            "A valid 34-point configuration was found and independently checked by the collector.",
            "The saved solution must be promoted to a standalone configuration file and verifier.",
        ])
    elif conclusion == "INCOMPLETE_WITH_UNKNOWN_CASES":
        lines.extend([
            "The run is technically complete but some mathematical cases remain `UNKNOWN`.",
            "The next run should target only those case indices and subdivide them by the",
            "number of saturated slope +1 diagonals (13 through 17).",
        ])
    else:
        lines.append("The run has a technical completeness problem; inspect missing or invalid records.")

    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "conclusion": conclusion,
        "records_found": len(ordered),
        "status_counts": status_counts,
        "missing": missing,
        "duplicates": sorted(set(duplicates)),
        "mismatched_pairs": mismatched_pairs,
    }, indent=2))

    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
