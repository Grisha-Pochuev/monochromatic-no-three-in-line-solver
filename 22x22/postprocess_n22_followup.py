#!/usr/bin/env python3
"""Archive an n=22 follow-up run and prepare the next exact step."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import validate_solution

TOTAL_CHILDREN = 2640
SMOKE_INFEASIBLE = 1864


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def insert_before(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def replace_section(text: str, heading: str, next_heading: str, block: str) -> str:
    start = text.find(heading)
    if start < 0:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    end = text.find(next_heading, start + len(heading))
    if end < 0:
        end = len(text)
    return text[:start] + block.rstrip() + "\n\n" + text[end:]


def make_schedule(overall: dict[str, object], run_id: int, run_url: str, seed_base: int) -> dict[str, object]:
    remaining = [int(value) for value in overall["remaining_child_ids"]]
    records = {int(record["child_id"]): record for record in overall["records"]}
    bins = [{"shard": shard, "ids": [], "prior_score_total": 0} for shard in range(20)]
    ranked = []
    for child_id in remaining:
        record = records[child_id]
        score = int(record.get("branches", 0)) + 2 * int(record.get("conflicts", 0))
        ranked.append((score, child_id))
    for score, child_id in sorted(ranked, reverse=True):
        target = min(bins, key=lambda item: (len(item["ids"]), int(item["prior_score_total"]), int(item["shard"])))
        target["ids"].append(child_id)
        target["prior_score_total"] = int(target["prior_score_total"]) + score
    for item in bins:
        item["count"] = len(item["ids"])
    return {
        "board_size": 22,
        "target": 34,
        "source_run_id": run_id,
        "source_run_url": run_url,
        "prior_smoke_infeasible_count": SMOKE_INFEASIBLE,
        "cumulative_infeasible_count": int(overall["cumulative_all_children_infeasible"]),
        "unknown_child_count": len(remaining),
        "shards": 20,
        "workers_per_solver": 4,
        "fallback_workers": 2,
        "total_seconds_per_shard": 21000,
        "memory_guard_mb": 13000,
        "max_seconds_per_child": 20700,
        "seed_base": seed_base,
        "balance_score": "latest branches + 2*conflicts; count-first greedy distribution",
        "assignments": bins,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--shards-dir", type=Path, required=True)
    parser.add_argument("--job-logs-dir", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--seed-base", type=int, default=2026072200)
    args = parser.parse_args()

    overall = read_json(args.overall)
    if int(overall["run_id"]) != args.run_id:
        raise ValueError("run id mismatch")
    if int(overall["expected_followup_children"]) != 170:
        raise ValueError("expected frontier is not 170")
    if int(overall["records_found"]) != 170:
        raise ValueError("not all 170 records were collected")
    if overall["missing_child_ids"] or overall["duplicate_child_ids"] or overall["unexpected_child_ids"]:
        raise ValueError("missing, duplicate, or unexpected child records")
    counts = overall["current_status_counts"]
    if int(counts.get("MODEL_INVALID", 0)) != 0:
        raise ValueError("MODEL_INVALID records present")
    if int(overall["technical_record_count"]) != 0:
        raise ValueError("technical records present")
    if int(overall["cumulative_all_children_infeasible"]) + len(overall["remaining_child_ids"]) != TOTAL_CHILDREN:
        raise ValueError("cumulative frontier does not cover all 2640 children")

    feasible = [
        record for record in overall["records"]
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]
    for record in feasible:
        validate_solution(record["solution"])

    machine_logs = list(args.shards_dir.rglob("machine-*.log"))
    memory_logs = list(args.shards_dir.rglob("memory-*.log"))
    if len(machine_logs) != 20 or len(memory_logs) != 20:
        raise ValueError(f"expected 20 machine and 20 memory logs, got {len(machine_logs)} and {len(memory_logs)}")

    args.archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.overall, args.archive_dir / "overall.json")
    shutil.copy2(args.summary, args.archive_dir / "SUMMARY.md")
    if (args.archive_dir / "shards").exists():
        shutil.rmtree(args.archive_dir / "shards")
    shutil.copytree(args.shards_dir, args.archive_dir / "shards")
    if args.job_logs_dir.exists():
        if (args.archive_dir / "job-logs").exists():
            shutil.rmtree(args.archive_dir / "job-logs")
        shutil.copytree(args.job_logs_dir, args.archive_dir / "job-logs")

    conclusion = str(overall["conclusion"])
    remaining = [int(value) for value in overall["remaining_child_ids"]]
    current_infeasible = int(counts.get("INFEASIBLE", 0))
    current_unknown = int(counts.get("UNKNOWN", 0))
    cumulative = int(overall["cumulative_all_children_infeasible"])
    remaining_pairs = len(overall["remaining_pair_indices"])
    newly_closed_pairs = len(overall["newly_closed_pair_indices"])

    archive_readme = f"""# GitHub Actions run {args.run_id}

Source: {args.run_url}

Overall artifact: `n22-profile-followup-overall`, id `{args.artifact_id}`, SHA-256 `{args.artifact_sha256}`.

This run reprocessed exactly the 170 exact profile children left by run `29770927206`.

- `INFEASIBLE`: {current_infeasible}
- `UNKNOWN`: {current_unknown}
- `FEASIBLE`/`OPTIMAL`: {int(counts.get('FEASIBLE', 0)) + int(counts.get('OPTIMAL', 0))}
- missing/duplicate/unexpected/model-invalid: 0
- technical records: 0
- memory-guard records: {int(overall['memory_guard_record_count'])}
- newly closed main-diagonal pairs: {newly_closed_pairs}
- remaining main-diagonal pairs: {remaining_pairs}
- remaining exact children: {len(remaining)}
- cumulative exact exclusions: {cumulative} / 2640
- solver work in this run: {float(overall['current_solver_job_hours']):.2f} job-hours

Files:

- `overall.json` — complete machine-readable aggregate;
- `SUMMARY.md` — independently generated collector summary;
- `shards/` — all shard records, machine reports, and minute-by-minute memory logs;
- `job-logs/` — downloaded GitHub Actions job logs.

Independent lower-bound check:

```bash
python 22x22/verify_22x22.py
```

`UNKNOWN` records are not treated as a proof.
"""
    (args.archive_dir / "README.md").write_text(archive_readme, encoding="utf-8")

    run_block = f"""### {args.run_id} — повтор по 170 остаткам

Ссылка:

```text
{args.run_url}
```

Архив:

```text
{args.archive_dir.as_posix()}/
```

Итог технически полный и проверенный:

```text
INFEASIBLE: {current_infeasible}
UNKNOWN:    {current_unknown}
FEASIBLE/OPTIMAL: {int(counts.get('FEASIBLE', 0)) + int(counts.get('OPTIMAL', 0))}
missing/duplicate/unexpected/MODEL_INVALID: 0
technical records: 0
```

Суммарно строго исключены {cumulative} из 2640 дочерних случаев; осталось {len(remaining)} случаев в {remaining_pairs} парах.
"""

    start_path = Path("START_HERE.md")
    start = start_path.read_text(encoding="utf-8")
    lines = start.splitlines()
    if len(lines) >= 3 and lines[2].startswith("Последнее существенное обновление:"):
        lines[2] = f"Последнее существенное обновление: **21 июля 2026 года**, после разбора прогона `{args.run_id}`."
        start = "\n".join(lines) + "\n"
    start = insert_before(start, "---\n\n## 6. Рациональный сертификат", run_block)

    root_path = Path("README.md")
    root = root_path.read_text(encoding="utf-8")
    n22_path = Path("22x22/README.md")
    n22 = n22_path.read_text(encoding="utf-8")
    n22_run_block = f"""### Run {args.run_id}

Archive: `{args.archive_dir.as_posix()}/`

The exact follow-up processed all 170 survivors from run `29770927206`:

- `INFEASIBLE`: {current_infeasible};
- `UNKNOWN`: {current_unknown};
- `FEASIBLE`/`OPTIMAL`: {int(counts.get('FEASIBLE', 0)) + int(counts.get('OPTIMAL', 0))};
- missing/duplicate/unexpected/model-invalid/technical: 0;
- newly closed main-diagonal pairs: {newly_closed_pairs};
- remaining main-diagonal pairs: {remaining_pairs};
- cumulative exact exclusions: {cumulative} / 2640.

Source run: {args.run_url}
"""
    n22 = insert_before(n22, "## Current follow-up attack", n22_run_block)

    if conclusion == "PROVED_D_MONO_22_EQUALS_33":
        if remaining or cumulative != TOTAL_CHILDREN:
            raise ValueError("proof conclusion conflicts with remaining frontier")
        root = root.replace("| `22×22` | `33 ≤ D_mono(22) ≤ 34` | active frontier |", "| `22×22` | `D_mono(22) = 33` | closed |")
        root = root.replace(
            "For the `22×22` case, the repository records a verified 33-point construction and an exact all-lines exclusion search for a possible 34th point. Run `29770927206` proved 606 of the 776 profile children infeasible, found no 34-point configuration, and left 170 exact children unresolved. Together with 1864 earlier exclusions, 2470 of all 2640 children are now closed; therefore the certified status remains `33 ≤ D_mono(22) ≤ 34`.",
            f"For the `22×22` case, the repository records an independently verified 33-point construction and a complete exact all-lines exclusion of all 2640 profile children. Run `{args.run_id}` closed the final frontier. Together these prove `D_mono(22) = 33`."
        )
        start = start.replace("| `22×22` | `33 ≤ D_mono(22) ≤ 34` | активный фронтир |", "| `22×22` | `D_mono(22) = 33` | закрыт |")
        start = start.replace("Активный размер: `22×22`.", "Активный размер: `23×23`.")
        n22 = n22.replace("33 <= D_mono(22) <= 34", "D_mono(22) = 33")
        n22 = replace_section(n22, "## Current follow-up attack", "## ", "## Closed result\n\nAll 2640 exact profile children are `INFEASIBLE`. Together with the independently verified 33-point construction, this proves `D_mono(22) = 33`.")
        Path("23x23").mkdir(exist_ok=True)
        Path("23x23/README.md").write_text(
            "# 23x23 checkerboard no-three-in-line\n\nActive frontier after closing 22x22. The first large run searches independently for a valid 35-point construction in both checkerboard colors. Every result must be verified against all grid lines.\n",
            encoding="utf-8",
        )
        Path("23x23/RUN_N23_LOWER_35_5H50").write_text(f"source n22 run {args.run_id}\n", encoding="utf-8")
    elif conclusion == "FOUND_VALID_34_POINT_CONFIGURATION":
        if not feasible:
            raise ValueError("feasible conclusion without a solution")
        solution = feasible[0]["solution"]
        write_json(Path("22x22/config_34.json"), {"board_size": 22, "target": 34, "points": solution})
        root = root.replace("| `22×22` | `33 ≤ D_mono(22) ≤ 34` | active frontier |", "| `22×22` | `D_mono(22) = 34` | closed |")
        start = start.replace("| `22×22` | `33 ≤ D_mono(22) ≤ 34` | активный фронтир |", "| `22×22` | `D_mono(22) = 34` | закрыт |")
        start = start.replace("Активный размер: `22×22`.", "Активный размер: `23×23`.")
        n22 = n22.replace("33 <= D_mono(22) <= 34", "D_mono(22) = 34")
        Path("23x23").mkdir(exist_ok=True)
        Path("23x23/README.md").write_text("# 23x23 checkerboard no-three-in-line\n\nActive frontier.\n", encoding="utf-8")
        Path("23x23/RUN_N23_LOWER_35_5H50").write_text(f"source n22 run {args.run_id}\n", encoding="utf-8")
    elif conclusion == "FOLLOWUP_RUN_INCOMPLETE":
        if not remaining:
            raise ValueError("incomplete conclusion without remaining children")
        schedule = make_schedule(overall, args.run_id, args.run_url, args.seed_base)
        write_json(Path("22x22/current_remaining_schedule.json"), schedule)
        shutil.copy2(args.overall, Path("22x22/current_prior_overall.json"))
        Path("22x22/RUN_N22_PROFILE_DYNAMIC_5H50").write_text(
            f"source_run_id={args.run_id}\nremaining={len(remaining)}\nseed_base={args.seed_base}\n",
            encoding="utf-8",
        )
        next_block = f"""## Current follow-up attack

The next workflow processes only the {len(remaining)} exact children still marked `UNKNOWN` after run `{args.run_id}`. It uses 20 balanced jobs, four solver workers, one solver process per machine, a 13 GB RSS guard, and up to 5 hours 50 minutes per job. Previously proved children are not recomputed.
"""
        n22 = replace_section(n22, "## Current follow-up attack", "## ", next_block)
        start = start.replace("Последний полностью проверенный запуск: `29770927206`.", f"Последний полностью проверенный запуск: `{args.run_id}`.")
        start = start.replace(".github/workflows/n22-profile-followup-170-5h50.yml", ".github/workflows/n22-profile-dynamic-5h50.yml")
        root = root.replace(
            "[latest exact run](https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29770927206)",
            f"[latest exact run]({args.run_url})",
        )
        old_para = "For the `22×22` case, the repository records a verified 33-point construction and an exact all-lines exclusion search for a possible 34th point. Run `29770927206` proved 606 of the 776 profile children infeasible, found no 34-point configuration, and left 170 exact children unresolved. Together with 1864 earlier exclusions, 2470 of all 2640 children are now closed; therefore the certified status remains `33 ≤ D_mono(22) ≤ 34`."
        new_para = f"For the `22×22` case, the repository records a verified 33-point construction and an exact all-lines exclusion search for a possible 34th point. Run `{args.run_id}` processed the complete 170-child frontier, strictly excluded {current_infeasible} more children, and left {len(remaining)} exact children unresolved. In total {cumulative} of all 2640 children are now closed; therefore the certified status remains `33 ≤ D_mono(22) ≤ 34`."
        root = root.replace(old_para, new_para)
    else:
        raise ValueError(f"cannot continue from conclusion {conclusion}")

    start_path.write_text(start, encoding="utf-8")
    root_path.write_text(root, encoding="utf-8")
    n22_path.write_text(n22, encoding="utf-8")
    print(json.dumps({
        "conclusion": conclusion,
        "current_infeasible": current_infeasible,
        "current_unknown": current_unknown,
        "cumulative_infeasible": cumulative,
        "remaining_children": len(remaining),
        "remaining_pairs": remaining_pairs,
        "archive_dir": args.archive_dir.as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
