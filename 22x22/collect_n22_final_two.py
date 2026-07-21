#!/usr/bin/env python3
"""Collect 20 independent replicas for the final two exact n=22 cases."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import validate_solution

TOTAL_CHILDREN = 2640
PRIOR_SMOKE_INFEASIBLE = 1864


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_unknown(record: dict[str, object]) -> tuple[int, int, float]:
    return (
        int(record.get("branches", 0)) + 2 * int(record.get("conflicts", 0)),
        int(record.get("branches", 0)),
        float(record.get("elapsed_seconds", 0.0)),
    )


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
    remaining_ids = sorted(int(value) for value in schedule["remaining_child_ids"])
    if remaining_ids != [652, 1132]:
        raise ValueError("unexpected final frontier")
    if sorted(int(value) for value in prior["remaining_child_ids"]) != remaining_ids:
        raise ValueError("prior aggregate does not match the final frontier")
    prior_records = prior["records"]
    prior_by_id = {int(record["child_id"]): record for record in prior_records}
    if len(prior_by_id) != 776:
        raise ValueError("prior aggregate must contain all 776 long-run records")

    expected = {
        (int(item["child_id"]), int(item["replica"])): int(item["shard"])
        for item in schedule["assignments"]
    }
    if len(expected) != 20:
        raise ValueError("expected 20 unique child/replica assignments")

    paths = sorted(args.input_dir.rglob("child-*-replica-*-shard-*.json"))
    records = [read_json(path) for path in paths]
    observed: dict[tuple[int, int], dict[str, object]] = {}
    duplicates: list[tuple[int, int]] = []
    unexpected: list[tuple[int, int]] = []
    for record in records:
        key = (int(record["child_id"]), int(record["replica"]))
        if key not in expected or int(record.get("shard", -1)) != expected.get(key, -2):
            unexpected.append(key)
            continue
        if key in observed:
            duplicates.append(key)
        else:
            observed[key] = record
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}:
            validate_solution(record["solution"])

    missing = sorted(key for key in expected if key not in observed)
    grouped: dict[int, list[dict[str, object]]] = defaultdict(list)
    for (child_id, _replica), record in observed.items():
        grouped[child_id].append(record)

    selected: dict[int, dict[str, object]] = {}
    contradictions: list[int] = []
    replica_status_counts: dict[str, dict[str, int]] = {}
    for child_id in remaining_ids:
        child_records = grouped.get(child_id, [])
        counts = Counter(str(record.get("status")) for record in child_records)
        replica_status_counts[str(child_id)] = dict(sorted(counts.items()))
        feasible = [
            record for record in child_records
            if record.get("status") in {"FEASIBLE", "OPTIMAL"}
        ]
        infeasible = [
            record for record in child_records
            if record.get("status") == "INFEASIBLE"
        ]
        if feasible and infeasible:
            contradictions.append(child_id)
            selected[child_id] = feasible[0]
        elif feasible:
            selected[child_id] = feasible[0]
        elif infeasible:
            selected[child_id] = infeasible[0]
        elif child_records:
            selected[child_id] = max(child_records, key=score_unknown)
        else:
            selected[child_id] = prior_by_id[child_id]

    combined_by_id = dict(prior_by_id)
    combined_by_id.update(selected)
    combined_ordered = [combined_by_id[child_id] for child_id in sorted(combined_by_id)]
    cumulative_counts = {
        status: sum(record.get("status") == status for record in combined_ordered)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    feasible_final = [
        record for record in selected.values()
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]
    technical_records = [
        record for record in records
        if record.get("final_technical_status") is not None
    ]
    memory_guard_records = [
        record for record in records
        if any(bool(attempt.get("memory_guard_triggered")) for attempt in record.get("attempts", []))
    ]

    pair_remaining: dict[int, list[int]] = defaultdict(list)
    for child_id, record in combined_by_id.items():
        if record.get("status") != "INFEASIBLE":
            pair_remaining[int(record["pair_index"])].append(child_id)
    prior_remaining_pairs = set(int(value) for value in prior["remaining_pair_indices"])
    remaining_pairs = sorted(pair_remaining)
    newly_closed_pairs = sorted(prior_remaining_pairs - set(remaining_pairs))
    remaining_children = sorted(
        child_id for child_id, record in combined_by_id.items()
        if record.get("status") != "INFEASIBLE"
    )

    complete_replica_set = not missing and not duplicates and not unexpected
    technical_failure = bool(
        contradictions
        or any(record.get("status") == "MODEL_INVALID" for record in records)
    )
    if feasible_final and not contradictions:
        conclusion = "FOUND_VALID_34_POINT_CONFIGURATION"
    elif not remaining_children and not technical_failure:
        conclusion = "PROVED_D_MONO_22_EQUALS_33"
    elif technical_failure:
        conclusion = "TECHNICAL_FAILURE"
    else:
        conclusion = "FOLLOWUP_RUN_INCOMPLETE"

    peak_values = [
        float(attempt.get("peak_rss_mb", 0.0))
        for record in records
        for attempt in record.get("attempts", [])
    ]
    overall = {
        "run_id": args.run_id,
        "run_url": args.run_url,
        "run_head_sha": args.run_sha,
        "prior_run_id": int(schedule["source_run_id"]),
        "prior_run_url": schedule.get("source_run_url", ""),
        "conclusion": conclusion,
        "expected_replica_records": len(expected),
        "records_found": len(observed),
        "missing_replica_assignments": [list(key) for key in missing],
        "duplicate_replica_assignments": [list(key) for key in sorted(set(duplicates))],
        "unexpected_replica_assignments": [list(key) for key in sorted(set(unexpected))],
        "complete_replica_set": complete_replica_set,
        "replica_status_counts": replica_status_counts,
        "contradictory_child_ids": contradictions,
        "selected_final_statuses": {
            str(child_id): str(selected[child_id].get("status"))
            for child_id in remaining_ids
        },
        "cumulative_long_status_counts": cumulative_counts,
        "prior_smoke_infeasible_count": PRIOR_SMOKE_INFEASIBLE,
        "cumulative_all_children_infeasible": PRIOR_SMOKE_INFEASIBLE + cumulative_counts["INFEASIBLE"],
        "technical_record_count": len(technical_records),
        "memory_guard_record_count": len(memory_guard_records),
        "maximum_peak_rss_mb": max(peak_values or [0.0]),
        "newly_closed_pair_indices": newly_closed_pairs,
        "remaining_pair_indices": remaining_pairs,
        "remaining_child_ids": remaining_children,
        "current_solver_job_hours": sum(float(record.get("elapsed_seconds", 0.0)) for record in records) / 3600.0,
        "current_total_branches": sum(int(record.get("branches", 0)) for record in records),
        "current_total_conflicts": sum(int(record.get("conflicts", 0)) for record in records),
        "replica_records": records,
        "records": combined_ordered,
    }
    args.overall.write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# n22 final-two replicated run",
        "",
        f"Conclusion: `{conclusion}`",
        "",
        f"- expected replica records: {len(expected)}",
        f"- replica records found: {len(observed)}",
        f"- complete replica set: {complete_replica_set}",
        f"- child 652 replica statuses: {replica_status_counts.get('652', {})}",
        f"- child 1132 replica statuses: {replica_status_counts.get('1132', {})}",
        f"- selected final statuses: {overall['selected_final_statuses']}",
        f"- missing replica assignments: {len(missing)}",
        f"- technical records: {len(technical_records)}",
        f"- memory-guard records: {len(memory_guard_records)}",
        f"- maximum recorded child RSS: {overall['maximum_peak_rss_mb']:.1f} MB",
        f"- newly closed main-diagonal pairs: {len(newly_closed_pairs)}",
        f"- remaining exact children: {len(remaining_children)}",
        f"- cumulative exact exclusions: {overall['cumulative_all_children_infeasible']} / {TOTAL_CHILDREN}",
        f"- solver work in this run: {overall['current_solver_job_hours']:.2f} job-hours",
    ]
    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        lines.extend([
            "",
            "Both final exact profile children are INFEASIBLE. Together with the",
            "independently verified 33-point construction this proves `D_mono(22)=33`.",
        ])
    elif conclusion == "FOUND_VALID_34_POINT_CONFIGURATION":
        lines.extend([
            "",
            "A valid 34-point configuration was found and independently checked.",
            "Together with the existing upper bound this proves `D_mono(22)=34`.",
        ])
    else:
        lines.extend([
            "",
            "`UNKNOWN` is not treated as a proof.",
        ])
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "conclusion": conclusion,
        "replica_status_counts": replica_status_counts,
        "selected_final_statuses": overall["selected_final_statuses"],
        "cumulative_all_children_infeasible": overall["cumulative_all_children_infeasible"],
        "remaining_child_ids": remaining_children,
        "missing_replica_assignments": len(missing),
        "technical_records": len(technical_records),
    }, indent=2))
    if conclusion == "TECHNICAL_FAILURE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
