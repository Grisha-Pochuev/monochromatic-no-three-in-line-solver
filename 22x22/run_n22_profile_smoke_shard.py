#!/usr/bin/env python3
"""Run one of 20 shards of the complete 2640 n22 profile children."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from prove_upper_22x22_profile_child import child_count, solve_child


def write_summary(path, shard, shards, assigned, records, started):
    payload = {
        "board_size": 22,
        "target": 34,
        "partition": "unknown_pair_x_diag_plus_twos_x_diag_minus_twos",
        "shard": shard,
        "shards": shards,
        "assigned_child_ids": assigned,
        "assigned_count": len(assigned),
        "completed_count": len(records),
        "elapsed_wall_seconds": time.monotonic() - started,
        "status_counts": {
            status: sum(record.get("status") == status for record in records)
            for status in ("INFEASIBLE", "UNKNOWN", "FEASIBLE", "OPTIMAL", "MODEL_INVALID")
        },
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, default=20)
    parser.add_argument("--seconds-each", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=2026072000)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.shard < args.shards:
        raise SystemExit("invalid shard")

    assigned = list(range(args.shard, child_count(), args.shards))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / f"shard-{args.shard:02d}-summary.json"
    records = []
    started = time.monotonic()
    for position, child_id in enumerate(assigned):
        record = solve_child(
            child_id,
            args.seconds_each,
            args.workers,
            args.seed_base + child_id,
        )
        record["shard"] = args.shard
        record["shard_position"] = position
        records.append(record)
        (args.output_dir / f"child-{child_id:04d}.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        write_summary(
            summary_path,
            args.shard,
            args.shards,
            assigned,
            records,
            started,
        )
        if record["status"] in {"FEASIBLE", "OPTIMAL", "MODEL_INVALID"}:
            break
    write_summary(
        summary_path,
        args.shard,
        args.shards,
        assigned,
        records,
        started,
    )
    if any(record["status"] == "MODEL_INVALID" for record in records):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
