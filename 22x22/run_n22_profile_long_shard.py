#!/usr/bin/env python3
"""Run one balanced 5h50 shard of the 776 unresolved n22 profile children.

Each CP-SAT child runs in its own subprocess, so its memory is returned to the
operating system before the next child starts.  A parent-side RSS guard stops a
child before it can consume the whole 16 GB GitHub runner.  A memory-stopped or
crashed child is retried once with two workers when enough wall time remains.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEDULE_PATH = HERE / "runs/2026-07-20-run-29766054707/long_profile_schedule.json"
ENGINE_PATH = HERE / "prove_upper_22x22_profile_child.py"


def load_schedule() -> dict[str, object]:
    data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    assignments = data["assignments"]
    if data.get("source_run_id") != 29766054707:
        raise ValueError("unexpected source run")
    if data.get("unknown_child_count") != 776:
        raise ValueError("expected exactly 776 unresolved children")
    if len(assignments) != 20:
        raise ValueError("expected exactly 20 shard assignments")
    all_ids = [int(child_id) for item in assignments for child_id in item["ids"]]
    if len(all_ids) != 776 or len(set(all_ids)) != 776:
        raise ValueError("long schedule is incomplete or contains duplicates")
    return data


def read_rss_mb(pid: int) -> float:
    try:
        for line in Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        return 0.0
    return 0.0


def stop_process_group(process: subprocess.Popen[object], gentle_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + gentle_seconds
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.25)
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def truncate_log(path: Path, keep_bytes: int = 65536) -> None:
    if not path.exists() or path.stat().st_size <= keep_bytes:
        return
    with path.open("rb") as handle:
        handle.seek(-keep_bytes, os.SEEK_END)
        tail = handle.read()
    path.write_bytes(b"[earlier solver log truncated]\n" + tail)


def run_attempt(
    child_id: int,
    seconds: float,
    workers: int,
    seed: int,
    memory_guard_mb: int,
    output_dir: Path,
    attempt: int,
) -> tuple[dict[str, object], dict[str, object]]:
    attempt_output = output_dir / f"child-{child_id:04d}-attempt-{attempt}.json"
    attempt_log = output_dir / f"child-{child_id:04d}-attempt-{attempt}.log"
    command = [
        sys.executable,
        str(ENGINE_PATH),
        "--child-id", str(child_id),
        "--seconds", str(max(1.0, seconds)),
        "--workers", str(workers),
        "--seed", str(seed),
        "--output", str(attempt_output),
    ]
    started = time.monotonic()
    peak_rss_mb = 0.0
    memory_guard_triggered = False
    watchdog_triggered = False
    with attempt_log.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=HERE.parent,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env={
                **os.environ,
                "PYTHONUNBUFFERED": "1",
                "MALLOC_ARENA_MAX": "2",
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            },
        )
        hard_deadline = started + seconds + 90.0
        while process.poll() is None:
            rss_mb = read_rss_mb(process.pid)
            peak_rss_mb = max(peak_rss_mb, rss_mb)
            if rss_mb > memory_guard_mb:
                memory_guard_triggered = True
                stop_process_group(process)
                break
            if time.monotonic() > hard_deadline:
                watchdog_triggered = True
                stop_process_group(process)
                break
            time.sleep(2.0)
        return_code = process.wait()
    truncate_log(attempt_log)

    parsed = False
    if attempt_output.exists():
        try:
            record = json.loads(attempt_output.read_text(encoding="utf-8"))
            parsed = True
        except (json.JSONDecodeError, OSError):
            record = {}
    else:
        record = {}

    technical_status = None
    if memory_guard_triggered:
        technical_status = "MEMORY_GUARD"
    elif watchdog_triggered:
        technical_status = "PARENT_WATCHDOG"
    elif not parsed or return_code != 0:
        technical_status = "CHILD_PROCESS_FAILURE"

    if not parsed:
        record = {
            "board_size": 22,
            "target": 34,
            "child_id": child_id,
            "status": "UNKNOWN",
            "proof_method": "no_mathematical_result_from_child_process",
            "elapsed_seconds": time.monotonic() - started,
            "branches": 0,
            "conflicts": 0,
        }

    attempt_metadata = {
        "attempt": attempt,
        "workers": workers,
        "allocated_seconds": seconds,
        "wall_seconds": time.monotonic() - started,
        "peak_rss_mb": peak_rss_mb,
        "memory_guard_mb": memory_guard_mb,
        "memory_guard_triggered": memory_guard_triggered,
        "watchdog_triggered": watchdog_triggered,
        "return_code": return_code,
        "output_parsed": parsed,
        "technical_status": technical_status,
        "log_file": attempt_log.name,
    }
    return record, attempt_metadata


def write_summary(
    path: Path,
    shard: int,
    assigned: list[int],
    records: list[dict[str, object]],
    started: float,
    total_seconds: float,
) -> None:
    completed_ids = [int(record["child_id"]) for record in records]
    status_counts = {
        status: sum(record.get("status") == status for record in records)
        for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
    }
    payload = {
        "board_size": 22,
        "target": 34,
        "source_run_id": 29766054707,
        "shard": shard,
        "assigned_child_ids": assigned,
        "assigned_count": len(assigned),
        "completed_child_ids": completed_ids,
        "completed_count": len(records),
        "missing_child_ids": [child_id for child_id in assigned if child_id not in set(completed_ids)],
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
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--total-seconds", type=float, default=21000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--fallback-workers", type=int, default=2)
    parser.add_argument("--memory-guard-mb", type=int, default=13000)
    parser.add_argument("--base-seconds", type=float, default=180.0)
    parser.add_argument("--max-seconds", type=float, default=1800.0)
    parser.add_argument("--artifact-buffer-seconds", type=float, default=180.0)
    parser.add_argument("--seed-base", type=int, default=2026072000)
    parser.add_argument("--max-children", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    schedule = load_schedule()
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
        if usable >= args.base_seconds * remaining_count:
            proposed = usable / remaining_count
        else:
            proposed = usable / remaining_count
        allocated = max(30.0, min(args.max_seconds, proposed))
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
        record["attempts"] = attempts
        record["final_technical_status"] = attempts[-1]["technical_status"]
        records.append(record)
        final_path = args.output_dir / f"child-{child_id:04d}.json"
        final_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        write_summary(summary_path, args.shard, assigned, records, started, args.total_seconds)

        if record.get("status") in {"FEASIBLE", "OPTIMAL", "MODEL_INVALID"}:
            break

    write_summary(summary_path, args.shard, assigned, records, started, args.total_seconds)
    if any(record.get("status") == "MODEL_INVALID" for record in records):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
