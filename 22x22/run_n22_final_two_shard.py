#!/usr/bin/env python3
"""Run one independent full-budget replica for the final two n=22 cases."""
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
    if len(assignments) != int(data.get("shards", 0)) or len(assignments) != 20:
        raise ValueError("schedule shard count mismatch")
    expected_ids = sorted(int(value) for value in data.get("remaining_child_ids", []))
    if expected_ids != [652, 1132]:
        raise ValueError("unexpected final child frontier")
    pairs = set()
    counts = {child_id: 0 for child_id in expected_ids}
    for item in assignments:
        shard = int(item["shard"])
        child_id = int(item["child_id"])
        replica = int(item["replica"])
        if not 0 <= shard < 20:
            raise ValueError("invalid shard")
        if child_id not in counts:
            raise ValueError("unexpected child id")
        key = (child_id, replica)
        if key in pairs:
            raise ValueError("duplicate child/replica assignment")
        pairs.add(key)
        counts[child_id] += 1
    if any(count != int(data.get("replicas_per_child", 0)) for count in counts.values()):
        raise ValueError("replica count mismatch")
    return data


def write_summary(
    path: Path,
    *,
    schedule: dict[str, object],
    shard: int,
    child_id: int,
    replica: int,
    record: dict[str, object] | None,
    started: float,
    total_seconds: float,
) -> None:
    payload = {
        "board_size": 22,
        "target": 34,
        "source_run_id": int(schedule["source_run_id"]),
        "source_run_url": schedule.get("source_run_url", ""),
        "shard": shard,
        "child_id": child_id,
        "replica": replica,
        "completed": record is not None,
        "status": None if record is None else record.get("status"),
        "memory_guard_triggered": False if record is None else any(
            bool(attempt.get("memory_guard_triggered"))
            for attempt in record.get("attempts", [])
        ),
        "elapsed_wall_seconds": time.monotonic() - started,
        "requested_total_seconds": total_seconds,
        "record": record,
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
    parser.add_argument("--max-seconds", type=float, default=20700.0)
    parser.add_argument("--artifact-buffer-seconds", type=float, default=180.0)
    parser.add_argument("--seed-base", type=int, default=2026072600)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    schedule = load_schedule(args.schedule)
    assignments = schedule["assignments"]
    if not 0 <= args.shard < len(assignments):
        raise SystemExit("invalid shard")
    assignment = assignments[args.shard]
    if int(assignment["shard"]) != args.shard:
        raise ValueError("shard index mismatch")

    child_id = int(assignment["child_id"])
    replica = int(assignment["replica"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / f"shard-{args.shard:02d}-summary.json"
    started = time.monotonic()
    usable = args.total_seconds - args.artifact_buffer_seconds
    allocated = max(30.0, min(args.max_seconds, usable))
    seed = args.seed_base + replica * 100_000 + args.shard * 1_000 + child_id

    attempts: list[dict[str, object]] = []
    record, metadata = run_attempt(
        child_id=child_id,
        seconds=allocated,
        workers=args.workers,
        seed=seed,
        memory_guard_mb=args.memory_guard_mb,
        output_dir=args.output_dir,
        attempt=1,
    )
    attempts.append(metadata)

    if metadata["technical_status"] is not None:
        remaining = args.total_seconds - (time.monotonic() - started) - args.artifact_buffer_seconds
        if remaining >= 90.0:
            retry_seconds = min(max(60.0, allocated / 2.0), remaining)
            retry_record, retry_metadata = run_attempt(
                child_id=child_id,
                seconds=retry_seconds,
                workers=args.fallback_workers,
                seed=seed + 10_000_000,
                memory_guard_mb=args.memory_guard_mb,
                output_dir=args.output_dir,
                attempt=2,
            )
            attempts.append(retry_metadata)
            record = retry_record

    record["shard"] = args.shard
    record["replica"] = replica
    record["followup_source_run_id"] = int(schedule["source_run_id"])
    record["attempts"] = attempts
    record["final_technical_status"] = attempts[-1]["technical_status"]

    final_path = args.output_dir / (
        f"child-{child_id:04d}-replica-{replica:02d}-shard-{args.shard:02d}.json"
    )
    final_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    write_summary(
        summary_path,
        schedule=schedule,
        shard=args.shard,
        child_id=child_id,
        replica=replica,
        record=record,
        started=started,
        total_seconds=args.total_seconds,
    )
    if record.get("status") == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
