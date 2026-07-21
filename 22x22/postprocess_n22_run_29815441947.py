#!/usr/bin/env python3
"""Archive and validate GitHub Actions run 29815441947, then prepare its exact remainder."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from prove_upper_22x22_main_diagonal_pair import validate_solution

RUN_ID = 29815441947
RUN_URL = (
    "https://github.com/Grisha-Pochuev/"
    "monochromatic-no-three-in-line-solver/actions/runs/29815441947"
)
TOTAL_CHILDREN = 2640
EXPECTED_CURRENT = 56
EXPECTED_INFEASIBLE = 46
EXPECTED_UNKNOWN = 10
EXPECTED_CUMULATIVE = 2630
EXPECTED_REMAINING_PAIRS = 10


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def replace_section(text: str, heading: str, next_heading: str, block: str) -> str:
    start = text.find(heading)
    if start < 0:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    end = text.find(next_heading, start + len(heading))
    if end < 0:
        end = len(text)
    return text[:start] + block.rstrip() + "\n\n" + text[end:]


def insert_before(text: str, marker: str, block: str) -> str:
    if block.splitlines()[0] in text:
        return text
    if marker not in text:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def make_schedule(overall: dict[str, object], seed_base: int) -> dict[str, object]:
    remaining = [int(value) for value in overall["remaining_child_ids"]]
    records = {int(record["child_id"]): record for record in overall["records"]}
    bins = [{"shard": shard, "ids": [], "prior_score_total": 0} for shard in range(20)]
    ranked: list[tuple[int, int]] = []
    for child_id in remaining:
        record = records[child_id]
        score = int(record.get("branches", 0)) + 2 * int(record.get("conflicts", 0))
        ranked.append((score, child_id))
    for score, child_id in sorted(ranked, reverse=True):
        target = min(
            bins,
            key=lambda item: (
                len(item["ids"]),
                int(item["prior_score_total"]),
                int(item["shard"]),
            ),
        )
        target["ids"].append(child_id)
        target["prior_score_total"] = int(target["prior_score_total"]) + score
    for item in bins:
        item["count"] = len(item["ids"])
    return {
        "board_size": 22,
        "target": 34,
        "source_run_id": RUN_ID,
        "source_run_url": RUN_URL,
        "prior_smoke_infeasible_count": 1864,
        "cumulative_infeasible_count": EXPECTED_CUMULATIVE,
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


def replace_n22_root_paragraph(text: str) -> str:
    prefix = "For the `22×22` case,"
    start = text.find(prefix)
    if start < 0:
        raise ValueError("root README n22 paragraph not found")
    end = text.find("\n\n", start)
    if end < 0:
        end = len(text)
    replacement = (
        "For the `22×22` case, the repository records a verified 33-point "
        "construction and an exact all-lines exclusion search for a possible "
        "34th point. Run `29815441947` processed the complete 56-child frontier, "
        "strictly excluded 46 more children, and left 10 exact children unresolved. "
        "In total 2630 of all 2640 children are now closed; therefore the certified "
        "status remains `33 ≤ D_mono(22) ≤ 34`."
    )
    return text[:start] + replacement + text[end:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overall", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--shards-dir", type=Path, required=True)
    parser.add_argument("--job-logs-dir", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--seed-base", type=int, default=2026072300)
    args = parser.parse_args()

    overall = read_json(args.overall)
    if int(overall["run_id"]) != RUN_ID:
        raise ValueError("run id mismatch")
    if int(overall["expected_followup_children"]) != EXPECTED_CURRENT:
        raise ValueError("expected frontier is not 56")
    if int(overall["records_found"]) != EXPECTED_CURRENT:
        raise ValueError("not all 56 records were collected")
    if overall["missing_child_ids"] or overall["duplicate_child_ids"] or overall["unexpected_child_ids"]:
        raise ValueError("missing, duplicate, or unexpected child records")

    counts = overall["current_status_counts"]
    expected_counts = {
        "INFEASIBLE": EXPECTED_INFEASIBLE,
        "UNKNOWN": EXPECTED_UNKNOWN,
        "FEASIBLE": 0,
        "OPTIMAL": 0,
        "MODEL_INVALID": 0,
    }
    if counts != expected_counts:
        raise ValueError(f"unexpected status counts: {counts}")
    if int(overall["technical_record_count"]) != 0:
        raise ValueError("technical records present")
    if int(overall["cumulative_all_children_infeasible"]) != EXPECTED_CUMULATIVE:
        raise ValueError("unexpected cumulative exclusion count")
    if len(overall["remaining_child_ids"]) != EXPECTED_UNKNOWN:
        raise ValueError("unexpected remaining child count")
    if len(overall["remaining_pair_indices"]) != EXPECTED_REMAINING_PAIRS:
        raise ValueError("unexpected remaining pair count")
    if EXPECTED_CUMULATIVE + len(overall["remaining_child_ids"]) != TOTAL_CHILDREN:
        raise ValueError("frontier does not cover all 2640 children")

    feasible = [
        record
        for record in overall["records"]
        if record.get("status") in {"FEASIBLE", "OPTIMAL"}
    ]
    for record in feasible:
        validate_solution(record["solution"])
    if feasible:
        raise ValueError("unexpected feasible 34-point configuration")

    machine_logs = list(args.shards_dir.rglob("machine-*.log"))
    memory_logs = list(args.shards_dir.rglob("memory-*.log"))
    job_logs = list(args.job_logs_dir.glob("*.log"))
    if len(machine_logs) != 20 or len(memory_logs) != 20:
        raise ValueError(
            f"expected 20 machine and memory logs, got {len(machine_logs)} and {len(memory_logs)}"
        )
    if len(job_logs) < 22:
        raise ValueError(f"expected at least 22 GitHub job logs, got {len(job_logs)}")

    if args.archive_dir.exists():
        shutil.rmtree(args.archive_dir)
    args.archive_dir.mkdir(parents=True)
    shutil.copy2(args.overall, args.archive_dir / "overall.json")
    shutil.copy2(args.summary, args.archive_dir / "SUMMARY.md")
    shutil.copytree(args.shards_dir, args.archive_dir / "shards")
    shutil.copytree(args.job_logs_dir, args.archive_dir / "job-logs")

    archive_readme = f"""# GitHub Actions run {RUN_ID}

Source: {RUN_URL}

Overall artifact: `n22-profile-dynamic-overall`, id `{args.artifact_id}`, SHA-256 `{args.artifact_sha256}`.

This run processed exactly the 56 exact profile children left by run `29795643015`.

- `INFEASIBLE`: 46
- `UNKNOWN`: 10
- `FEASIBLE`/`OPTIMAL`: 0
- missing/duplicate/unexpected/model-invalid: 0
- technical records: 0
- memory-guard records: {int(overall['memory_guard_record_count'])}
- newly closed main-diagonal pairs: {len(overall['newly_closed_pair_indices'])}
- remaining main-diagonal pairs: {len(overall['remaining_pair_indices'])}
- remaining exact children: {len(overall['remaining_child_ids'])}
- cumulative exact exclusions: {int(overall['cumulative_all_children_infeasible'])} / 2640
- solver work in this run: {float(overall['current_solver_job_hours']):.2f} job-hours

Files:

- `overall.json` — independently regenerated machine-readable aggregate;
- `SUMMARY.md` — independently generated collector summary;
- `shards/` — all twenty shard records, machine reports, and minute-by-minute memory logs;
- `job-logs/` — downloaded GitHub Actions job logs.

Independent lower-bound check:

```bash
python 22x22/verify_22x22.py
```

`UNKNOWN` records are not treated as a proof.
"""
    (args.archive_dir / "README.md").write_text(archive_readme, encoding="utf-8")

    write_json(Path("22x22/current_prior_overall.json"), overall)
    schedule = make_schedule(overall, args.seed_base)
    write_json(Path("22x22/current_remaining_schedule.json"), schedule)

    start_path = Path("START_HERE.md")
    start = start_path.read_text(encoding="utf-8")
    lines = start.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("Последнее существенное обновление:"):
            lines[index] = (
                "Последнее существенное обновление: **21 июля 2026 года**, "
                "после разбора прогона `29815441947`."
            )
            break
    start = "\n".join(lines) + "\n"
    run_block = f"""### 29815441947 — повтор по 56 остаткам

Ссылка:

```text
{RUN_URL}
```

Архив:

```text
{args.archive_dir.as_posix()}/
```

Итог технически полный и независимо пересобран:

```text
INFEASIBLE: 46
UNKNOWN:    10
FEASIBLE/OPTIMAL: 0
missing/duplicate/unexpected/MODEL_INVALID: 0
technical records: 0
```

Суммарно строго исключены 2630 из 2640 дочерних случаев; осталось 10 случаев в 10 парах. Доска пока не закрыта.
"""
    start = insert_before(start, "---\n\n## 6. Рациональный сертификат", run_block)
    section7 = """## 7. Подготовленный повторный прогон по 10 остаткам

Workflow:

```text
.github/workflows/n22-profile-dynamic-5h50.yml
```

Он берёт только 10 `UNKNOWN`-случаев из `29815441947` и не пересчитывает 2630 уже строгих исключений.

Распределение ресурсов:

- 20 заданий `ubuntu-latest`, из них десять содержат по одному трудному случаю;
- 4 потока CP-SAT на активный случай;
- 21 000 секунд на задание;
- до 20 700 секунд на один случай;
- один решатель на машину;
- RSS-сторож 13 000 МБ;
- seed-base `2026072300`.

Каждый результат сохраняется отдельно; `UNKNOWN` не считается доказательством.
"""
    start = replace_section(start, "## 7.", "## 8.", section7)
    start_path.write_text(start, encoding="utf-8")

    root_path = Path("README.md")
    root = root_path.read_text(encoding="utf-8")
    root = root.replace(
        "https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29795643015",
        RUN_URL,
    )
    root = replace_n22_root_paragraph(root)
    root_path.write_text(root, encoding="utf-8")

    n22_path = Path("22x22/README.md")
    n22 = n22_path.read_text(encoding="utf-8")
    n22_run_block = f"""### Run 29815441947

Archive: `{args.archive_dir.as_posix()}/`

The exact follow-up processed all 56 survivors from run `29795643015`:

- `INFEASIBLE`: 46;
- `UNKNOWN`: 10;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/unexpected/model-invalid/technical: 0;
- newly closed main-diagonal pairs: {len(overall['newly_closed_pair_indices'])};
- remaining main-diagonal pairs: 10;
- cumulative exact exclusions: 2630 / 2640.

Source run: {RUN_URL}
"""
    n22 = insert_before(n22, "## Current follow-up attack", n22_run_block)
    next_attack = """## Current follow-up attack

The next workflow processes only the 10 exact children still marked `UNKNOWN` after run `29815441947`. It uses 20 jobs (ten active and ten empty), four solver workers, one solver process per machine, a 13 GB RSS guard, and up to 5 hours 50 minutes per job. Previously proved children are not recomputed.
"""
    n22 = replace_section(n22, "## Current follow-up attack", "## ", next_attack)
    n22_path.write_text(n22, encoding="utf-8")

    print(
        json.dumps(
            {
                "conclusion": overall["conclusion"],
                "current_infeasible": EXPECTED_INFEASIBLE,
                "current_unknown": EXPECTED_UNKNOWN,
                "cumulative_infeasible": EXPECTED_CUMULATIVE,
                "remaining_children": EXPECTED_UNKNOWN,
                "remaining_pairs": EXPECTED_REMAINING_PAIRS,
                "archive_dir": args.archive_dir.as_posix(),
                "machine_logs": len(machine_logs),
                "memory_logs": len(memory_logs),
                "job_logs": len(job_logs),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
