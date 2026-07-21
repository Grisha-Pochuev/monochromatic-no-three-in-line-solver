#!/usr/bin/env python3
"""Run one balanced shard of an n=22 profile-child follow-up schedule."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_n22_profile_long_shard import run_attempt


def load_schedule(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if int(data.get("board_size", 0)) != 22 or int(data.get("target", 0)) != 34:
        raise ValueError("unexpected board or target")
    assignments = data.get("assignments", [])
    if len(assignments) != int(data.get("shards", 0)):
        raise ValueError("schedule shard count mismatch")
    all_ids = [int(child_id) for item in assignments for child_id in item["ids"]]
    if len(all_ids) != int(data.get("unknown_child_count", -1)):
        raise ValueError("schedule child count mismatch")
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("schedule contains duplicate child ids")
    return data


def write_summary(
    path: Path,
    schedule: dict[str, object],
    shard: int,
    assigned: list[int],
    records: list[dict[str, object]],
    started: float,
    total_seconds: float,
) -> None:
    completed_ids = [int(record["child_id"]) for record in records]
    completed_set = set(completed_ids)
    status_counts = {
        status: sum(record.get("status") == status for record in records)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    payload = {
        "board_size": 22,
        "target": 34,
        "source_run_id": int(schedule["source_run_id"]),
        "source_run_url": schedule.get("source_run_url", ""),
        "schedule_unknown_child_count": int(schedule["unknown_child_count"]),
        "shard": shard,
        "assigned_child_ids": assigned,
        "assigned_count": len(assigned),
        "completed_child_ids": completed_ids,
        "completed_count": len(records),
        "missing_child_ids": [child_id for child_id in assigned if child_id not in completed_set],
        "status_counts": status_counts,
        "memory_guard_count": sum(
            any(bool(attempt.get("memory_guard_triggered")) for attempt in record.get("attempts", []))
            for record in records
        ),
        "maximum_peak_rss_mb": max(
            [
                float(attempt.get("peak_rss_mb", 0.0))
                for record in records
                for attempt in record.get("attempts", [])
            ] or [0.0]
        ),
        "elapsed_wall_seconds": time.monotonic() - started,
        "requested_total_seconds": total_seconds,
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--total-seconds", type=float, default=21000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--fallback-workers", type=int, default=2)
    parser.add_argument("--memory-guard-mb", type=int, default=13000)
    parser.add_argument("--max-seconds", type=float, default=2500.0)
    parser.add_argument("--artifact-buffer-seconds", type=float, default=180.0)
    parser.add_argument("--seed-base", type=int, default=2026072100)
    parser.add_argument("--max-children", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    schedule = load_schedule(args.schedule)
    assignments = schedule["assignments"]
    if not 0 <= args.shard < len(assignments):
        raise SystemExit("invalid shard")
    assignment = assignments[args.shard]
    if int(assignment["shard"]) != args.shard:
        raise ValueError("shard index mismatch in schedule")
    assigned = [int(value) for value in assignment["ids"]]
    if args.max_children > 0:
        assigned = assigned[: args.max_children]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / f"shard-{args.shard:02d}-summary.json"
    started = time.monotonic()
    deadline = started + args.total_seconds
    records: list[dict[str, object]] = []

    for position, child_id in enumerate(assigned):
        pending = assigned[position:]
        usable = deadline - time.monotonic() - args.artifact_buffer_seconds
        if usable < 30.0:
            break
        remaining_count = len(pending)
        allocated = max(30.0, min(args.max_seconds, usable / remaining_count))
        reserve_for_others = 30.0 * (remaining_count - 1)
        allocated = min(allocated, max(30.0, usable - reserve_for_others))

        attempts: list[dict[str, object]] = []
        record, metadata = run_attempt(
            child_id=child_id,
            seconds=allocated,
            workers=args.workers,
            seed=args.seed_base + child_id,
            memory_guard_mb=args.memory_guard_mb,
            output_dir=args.output_dir,
            attempt=1,
        )
        attempts.append(metadata)

        if metadata["technical_status"] is not None:
            retry_usable = deadline - time.monotonic() - args.artifact_buffer_seconds
            if retry_usable >= 90.0:
                retry_seconds = min(max(60.0, allocated / 2.0), retry_usable)
                retry_record, retry_metadata = run_attempt(
                    child_id=child_id,
                    seconds=retry_seconds,
                    workers=args.fallback_workers,
                    seed=args.seed_base + 100000 + child_id,
                    memory_guard_mb=args.memory_guard_mb,
                    output_dir=args.output_dir,
                    attempt=2,
                )
                attempts.append(retry_metadata)
                record = retry_record

        record["shard"] = args.shard
        record["shard_position"] = position
        record["followup_source_run_id"] = int(schedule["source_run_id"])
        record["attempts"] = attempts
        record["final_technical_status"] = attempts[-1]["technical_status"]
        records.append(record)

        final_path = args.output_dir / f"child-{child_id:04d}.json"
        final_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        write_summary(summary_path, schedule, args.shard, assigned, records, started, args.total_seconds)

        if record.get("status") in {"FEASIBLE", "OPTIMAL", "MODEL_INVALID"}:
            break

    write_summary(summary_path, schedule, args.shard, assigned, records, started, args.total_seconds)
    if any(record.get("status") == "MODEL_INVALID" for record in records):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
