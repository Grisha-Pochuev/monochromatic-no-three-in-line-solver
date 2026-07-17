#!/usr/bin/env python3
"""Run one of 20 complete shards of the 121 canonical x=y pair cases."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import (
    canonical_main_diagonal_pairs,
    solve_case,
)


def write_summary(
    path: Path,
    shard: int,
    shards: int,
    case_indices: list[int],
    records: list[dict[str, object]],
    started: float,
    total_budget: float,
) -> None:
    payload = {
        "board_size": 22,
        "target": 34,
        "partition": "canonical_main_diagonal_pair_under_180_rotation",
        "shard": shard,
        "shards": shards,
        "assigned_case_indices": case_indices,
        "assigned_case_count": len(case_indices),
        "completed_case_count": len(records),
        "statuses": {
            status: sum(record.get("status") == status for record in records)
            for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
        },
        "elapsed_wall_seconds": time.monotonic() - started,
        "requested_total_seconds": total_budget,
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, default=20)
    parser.add_argument("--total-seconds", type=float, default=17_400.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=2026071700)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if not (0 <= args.shard < args.shards):
        raise SystemExit("invalid shard")
    if args.shards != 20:
        raise SystemExit("this workflow is validated for exactly 20 shards")

    all_cases = canonical_main_diagonal_pairs()
    case_indices = list(range(args.shard, len(all_cases), args.shards))
    if not case_indices:
        raise SystemExit("empty shard")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / f"shard-{args.shard:02d}-summary.json"
    started = time.monotonic()
    deadline = started + args.total_seconds
    records: list[dict[str, object]] = []

    for position, case_index in enumerate(case_indices):
        remaining_cases = len(case_indices) - position
        remaining_wall = deadline - time.monotonic()
        usable = max(1.0, remaining_wall - 120.0)
        seconds = max(1.0, usable / remaining_cases)

        pair = all_cases[case_index]
        seed = args.seed_base + case_index
        record = solve_case(
            pair=pair,
            seconds=seconds,
            workers=args.workers,
            requested_seed=seed,
        )
        record["shard"] = args.shard
        record["shard_position"] = position
        record["allocated_seconds"] = seconds
        records.append(record)

        case_path = args.output_dir / f"case-{case_index:03d}.json"
        case_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        write_summary(
            summary_path,
            args.shard,
            args.shards,
            case_indices,
            records,
            started,
            args.total_seconds,
        )

        if record["status"] in {"FEASIBLE", "OPTIMAL", "MODEL_INVALID"}:
            break

    write_summary(
        summary_path,
        args.shard,
        args.shards,
        case_indices,
        records,
        started,
        args.total_seconds,
    )

    if any(record["status"] == "MODEL_INVALID" for record in records):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
