#!/usr/bin/env python3
"""Run one full-budget exact row/column subcase for n=22 child 652."""
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
ENGINE = HERE / "prove_upper_22x22_rowcol_subcase.py"


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
    subcase_id: int,
    seconds: float,
    workers: int,
    seed: int,
    memory_guard_mb: int,
    output_dir: Path,
    attempt: int,
) -> tuple[dict[str, object], dict[str, object]]:
    attempt_output = output_dir / f"subcase-{subcase_id:02d}-attempt-{attempt}.json"
    attempt_log = output_dir / f"subcase-{subcase_id:02d}-attempt-{attempt}.log"
    command = [
        sys.executable,
        str(ENGINE),
        "--subcase-id", str(subcase_id),
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
            "child_id": 652,
            "subcase_id": subcase_id,
            "status": "UNKNOWN",
            "proof_method": "no_mathematical_result_from_child_process",
            "elapsed_seconds": time.monotonic() - started,
            "branches": 0,
            "conflicts": 0,
        }

    metadata = {
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
    return record, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subcase-id", type=int, required=True)
    parser.add_argument("--total-seconds", type=float, default=21000.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--fallback-workers", type=int, default=2)
    parser.add_argument("--memory-guard-mb", type=int, default=13000)
    parser.add_argument("--artifact-buffer-seconds", type=float, default=180.0)
    parser.add_argument("--seed-base", type=int, default=2026072700)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if not 0 <= args.subcase_id < 21:
        raise SystemExit("subcase-id must be in 0..20")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    usable = max(30.0, args.total_seconds - args.artifact_buffer_seconds)
    attempts: list[dict[str, object]] = []
    record, metadata = run_attempt(
        args.subcase_id,
        usable,
        args.workers,
        args.seed_base + args.subcase_id,
        args.memory_guard_mb,
        args.output_dir,
        1,
    )
    attempts.append(metadata)

    if metadata["technical_status"] is not None:
        remaining = args.total_seconds - (time.monotonic() - (time.monotonic() - metadata["wall_seconds"])) - args.artifact_buffer_seconds
        if remaining >= 90.0:
            retry_seconds = max(60.0, min(usable / 2.0, remaining))
            retry_record, retry_metadata = run_attempt(
                args.subcase_id,
                retry_seconds,
                args.fallback_workers,
                args.seed_base + 100000 + args.subcase_id,
                args.memory_guard_mb,
                args.output_dir,
                2,
            )
            attempts.append(retry_metadata)
            record = retry_record

    record["attempts"] = attempts
    record["final_technical_status"] = attempts[-1]["technical_status"]
    final_path = args.output_dir / f"subcase-{args.subcase_id:02d}.json"
    final_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    summary = {
        "board_size": 22,
        "target": 34,
        "child_id": 652,
        "subcase_id": args.subcase_id,
        "status": record.get("status"),
        "final_technical_status": record.get("final_technical_status"),
        "maximum_peak_rss_mb": max(float(a.get("peak_rss_mb", 0.0)) for a in attempts),
        "record": record,
    }
    (args.output_dir / f"subcase-{args.subcase_id:02d}-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    if record.get("status") == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
