#!/usr/bin/env python3
"""Archive run 29770927206 and prepare a balanced rerun of its exact UNKNOWN children."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

PRIOR_SMOKE_INFEASIBLE = 1864
EXPECTED_SOURCE_RUN = 29770927206
EXPECTED_SOURCE_SHA = "ee20dc85b457ee4db457fcdc06f9ed3c1eee4269"
EXPECTED_LONG_INFEASIBLE = 606
EXPECTED_REMAINING = 170
SHARDS = 20


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def validate_prior(data: dict[str, object]) -> tuple[list[int], dict[int, dict[str, object]]]:
    if int(data.get("run_id", 0)) != EXPECTED_SOURCE_RUN:
        raise ValueError("unexpected source run id")
    if data.get("run_head_sha") != EXPECTED_SOURCE_SHA:
        raise ValueError("unexpected source run SHA")
    if data.get("conclusion") != "LONG_PROFILE_RUN_INCOMPLETE":
        raise ValueError("source run is not the expected incomplete exact run")
    if data.get("missing_child_ids") or data.get("duplicate_child_ids") or data.get("unexpected_child_ids"):
        raise ValueError("source run contains missing, duplicate, or unexpected records")

    counts = data.get("status_counts", {})
    expected_counts = {
        "INFEASIBLE": EXPECTED_LONG_INFEASIBLE,
        "UNKNOWN": EXPECTED_REMAINING,
        "FEASIBLE": 0,
        "OPTIMAL": 0,
        "MODEL_INVALID": 0,
    }
    if counts != expected_counts:
        raise ValueError(f"unexpected source status counts: {counts!r}")

    remaining = [int(value) for value in data.get("remaining_child_ids", [])]
    if len(remaining) != EXPECTED_REMAINING or len(set(remaining)) != EXPECTED_REMAINING:
        raise ValueError("expected 170 distinct remaining child ids")

    records = data.get("records", [])
    if len(records) != 776:
        raise ValueError("expected all 776 long-run records")
    by_id = {int(record["child_id"]): record for record in records}
    if len(by_id) != 776:
        raise ValueError("duplicate child ids in source records")
    if any(by_id[child_id].get("status") != "UNKNOWN" for child_id in remaining):
        raise ValueError("remaining ids are not exactly the UNKNOWN records")
    return sorted(remaining), by_id


def build_schedule(
    remaining: list[int],
    by_id: dict[int, dict[str, object]],
    source_url: str,
) -> dict[str, object]:
    bins = [{"shard": shard, "ids": [], "prior_score_total": 0} for shard in range(SHARDS)]

    def score(child_id: int) -> int:
        record = by_id[child_id]
        return max(1, int(record.get("branches", 0)) + 2 * int(record.get("conflicts", 0)))

    for child_id in sorted(remaining, key=lambda value: (-score(value), value)):
        target = min(
            bins,
            key=lambda item: (len(item["ids"]), int(item["prior_score_total"]), int(item["shard"])),
        )
        target["ids"].append(child_id)
        target["prior_score_total"] = int(target["prior_score_total"]) + score(child_id)

    for item in bins:
        item["count"] = len(item["ids"])
    counts = sorted(int(item["count"]) for item in bins)
    if counts != [8] * 10 + [9] * 10:
        raise ValueError(f"unexpected shard counts: {counts}")
    all_ids = [int(child_id) for item in bins for child_id in item["ids"]]
    if sorted(all_ids) != remaining:
        raise ValueError("follow-up schedule does not exactly cover remaining children")

    return {
        "board_size": 22,
        "target": 34,
        "source_run_id": EXPECTED_SOURCE_RUN,
        "source_run_url": source_url,
        "source_run_head_sha": EXPECTED_SOURCE_SHA,
        "prior_smoke_infeasible_count": PRIOR_SMOKE_INFEASIBLE,
        "prior_long_infeasible_count": EXPECTED_LONG_INFEASIBLE,
        "cumulative_infeasible_count": PRIOR_SMOKE_INFEASIBLE + EXPECTED_LONG_INFEASIBLE,
        "unknown_child_count": EXPECTED_REMAINING,
        "shards": SHARDS,
        "workers_per_solver": 4,
        "fallback_workers": 2,
        "total_seconds_per_shard": 21000,
        "memory_guard_mb": 13000,
        "max_seconds_per_child": 2500,
        "seed_base": 2026072100,
        "balance_score": "prior branches + 2*conflicts; count-first greedy distribution",
        "assignments": bins,
    }


def update_root_readme(path: Path, source_url: str) -> None:
    text = path.read_text(encoding="utf-8")
    row = (
        "| `22×22` | `33 ≤ D_mono(22) ≤ 34` | active frontier | "
        "`22x22/`, [latest exact run](" + source_url + ") |"
    )
    if "| `22×22` |" not in text:
        anchor = "| `21×21` | `D_mono(21) = 32` | closed | `21x21/`, `python 21x21/verify_21x21.py`, [final exact run](https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29531523646) |"
        if anchor not in text:
            raise ValueError("root README status-table anchor not found")
        text = text.replace(anchor, anchor + "\n" + row, 1)

    paragraph = (
        "For the `22×22` case, the repository records a verified 33-point construction and an exact "
        "all-lines exclusion search for a possible 34th point. Run `29770927206` proved 606 of the "
        "776 profile children infeasible, found no 34-point configuration, and left 170 exact "
        "children unresolved. Together with 1864 earlier exclusions, 2470 of all 2640 children are "
        "now closed; therefore the certified status remains `33 ≤ D_mono(22) ≤ 34`."
    )
    if "Run `29770927206` proved 606" not in text:
        anchor = "For the `21×21` case, the repository records a verified rotationally symmetric 32-point construction. The four-direction integer relaxation using rows, columns, and the two diagonal families excludes 33 points for both checkerboard colors. The final GitHub Actions run returned two `INFEASIBLE` results and zero `UNKNOWN` results. Together these prove `D_mono(21) = 32`. The final records are stored in `21x21/runs/2026-07-16-run-29531523646/`."
        if anchor not in text:
            raise ValueError("root README paragraph anchor not found")
        text = text.replace(anchor, anchor + "\n\n" + paragraph, 1)
    write_text(path, text)


def update_board_readme(path: Path, source_url: str) -> None:
    text = path.read_text(encoding="utf-8")
    replacement = f"""### Run 29770927206

Archive: `22x22/runs/2026-07-21-run-29770927206/`

The memory-safe 5h50 rerun processed all 776 survivors from run `29766054707`:

- `INFEASIBLE`: 606;
- `UNKNOWN`: 170;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/model-invalid: 0;
- newly closed main-diagonal pairs: 35;
- remaining main-diagonal pairs: 53;
- memory-guard records: 0.

Together with the 1864 children closed by run `29766054707`, exactly 2470 of the 2640 profile children are now proved impossible. The remaining 170 children are the only exact frontier for a 34-point configuration. Source run: {source_url}

## Current follow-up attack

Workflow:

```text
.github/workflows/n22-profile-followup-170-5h50.yml
```

It downloads and independently validates the aggregate record from run `29770927206`, archives it in the `22x22` folder, then schedules only the 170 remaining exact children.

Resource layout:

- 20 independent `ubuntu-latest` jobs;
- 4 CP-SAT workers per active child;
- 8 or 9 children per job;
- 21,000 seconds (5 hours 50 minutes) per shard;
- up to 2,500 seconds per child, roughly four times the previous average allowance;
- one solver subprocess at a time with a 13 GB RSS guard;
- a different seed base to diversify the exact search.

The board remains open until every surviving child is `INFEASIBLE` or a valid 34-point construction is found and independently checked.
"""
    pattern = r"## Current 5h50 attack\n.*\Z"
    if not re.search(pattern, text, flags=re.S):
        if "### Run 29770927206" in text:
            return
        raise ValueError("22x22 README current-attack section not found")
    text = re.sub(pattern, replacement, text, count=1, flags=re.S)
    write_text(path, text)


def update_start_here(path: Path, source_url: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"Последнее существенное обновление: .*",
        "Последнее существенное обновление: **21 июля 2026 года**, после разбора прогона `29770927206` и подготовки повторного запуска по 170 остаточным случаям.",
        text,
        count=1,
    )

    run_section = f"""### 29770927206 — длинный прогон по 776 остаткам

Ссылка:

```text
{source_url}
```

Архив:

```text
22x22/runs/2026-07-21-run-29770927206/
```

Прогон завершился технически чисто:

```text
INFEASIBLE: 606
UNKNOWN:    170
FEASIBLE:     0
missing:      0
MODEL_INVALID: 0
```

Дополнительно:

```text
новых закрытых пар: 35
оставшихся пар:     53
memory guard:        0
```

С учётом 1864 исключений предыдущего прогона строго закрыты 2470 из 2640 дочерних случаев. Остались ровно 170 `UNKNOWN`; доска пока не закрыта:

```text
33 ≤ D_mono(22) ≤ 34
```

"""
    if "### 29770927206" not in text:
        marker = "---\n\n## 6. Рациональный сертификат и profile-разбиение"
        if marker not in text:
            raise ValueError("START_HERE insertion marker not found")
        text = text.replace(marker, run_section + "---\n\n## 6. Рациональный сертификат и profile-разбиение", 1)

    section7 = """## 7. Подготовленный повторный прогон по 170 остаткам

Workflow:

```text
.github/workflows/n22-profile-followup-170-5h50.yml
```

Он берёт только 170 `UNKNOWN`-случаев из `29770927206` и не пересчитывает 2470 уже строгих исключений.

Распределение ресурсов:

- 20 независимых заданий `ubuntu-latest`;
- по 8 или 9 случаев на машину;
- 4 CP-SAT-потока на активный случай;
- 21 000 секунд на шард;
- до 2 500 секунд на один случай;
- балансировка по прошлой трудности `branches + 2*conflicts`;
- новый seed-base `2026072100`.

Защита памяти остаётся прежней: один subprocess, RSS-сторож 13 000 МБ, освобождение памяти после каждого случая, двухпоточный повтор только после технической ошибки, минутные журналы ресурсов и сохранение JSON после каждого случая.
"""
    pattern7 = r"## 7\. Подготовленный длинный прогон 5ч50м\n.*?\n---\n\n## 8\. Правила тяжёлых запусков"
    if re.search(pattern7, text, flags=re.S):
        text = re.sub(pattern7, section7 + "\n---\n\n## 8. Правила тяжёлых запусков", text, count=1, flags=re.S)

    current = """## 9. Текущая точка продолжения

Активный размер: `22×22`.

Последний полностью проверенный запуск: `29770927206`.

Следующий workflow:

```text
.github/workflows/n22-profile-followup-170-5h50.yml
```

Точка продолжения:

```text
Посчитать только 170 оставшихся profile-child. Если все они INFEASIBLE, вместе с проверенной 33-точечной конфигурацией получаем D_mono(22)=33. Если найдено 34 точки, независимо проверить конфигурацию и получить D_mono(22)=34. Иначе следующий запуск строить только по новому списку UNKNOWN и не пересчитывать 2470 уже закрытых случаев.
```
"""
    text = re.sub(r"## 9\. Текущая точка продолжения\n.*\Z", current, text, count=1, flags=re.S)
    write_text(path, text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-overall", type=Path, required=True)
    parser.add_argument("--prior-summary", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--root-readme", type=Path, default=Path("README.md"))
    parser.add_argument("--board-readme", type=Path, default=Path("22x22/README.md"))
    parser.add_argument("--start-here", type=Path, default=Path("START_HERE.md"))
    args = parser.parse_args()

    prior = read_json(args.prior_overall)
    remaining, by_id = validate_prior(prior)
    schedule = build_schedule(remaining, by_id, args.source_url)

    args.archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.prior_overall, args.archive_dir / "overall.json")
    shutil.copy2(args.prior_summary, args.archive_dir / "SUMMARY.md")
    write_text(args.archive_dir / "remaining_schedule.json", json.dumps(schedule, indent=2))

    archive_readme = f"""# GitHub Actions run 29770927206

Source: {args.source_url}

Artifact: `n22-profile-5h50-overall`, id `{args.artifact_id}`.

This run reprocessed exactly the 776 `UNKNOWN` profile children left by run `29766054707`.

- `INFEASIBLE`: 606
- `UNKNOWN`: 170
- `FEASIBLE`/`OPTIMAL`: 0
- missing/duplicate/model-invalid: 0
- newly closed main-diagonal pairs: 35
- remaining main-diagonal pairs: 53
- memory-guard records: 0

Cumulatively, 2470 of the 2640 exact children are now proved infeasible. The certified board status remains:

```text
33 <= D_mono(22) <= 34
```

Files:

- `overall.json` — complete machine-readable aggregate with all 776 records;
- `SUMMARY.md` — collector summary from the source run;
- `remaining_schedule.json` — balanced 20-shard schedule containing only the 170 exact survivors.

Independent lower-bound check:

```bash
python 22x22/verify_22x22.py
```

The source workflow and all 20 shard artifacts remain linked from the run page.
"""
    write_text(args.archive_dir / "README.md", archive_readme)

    update_root_readme(args.root_readme, args.source_url)
    update_board_readme(args.board_readme, args.source_url)
    update_start_here(args.start_here, args.source_url)

    print(json.dumps({
        "source_run": EXPECTED_SOURCE_RUN,
        "source_status_counts": prior["status_counts"],
        "cumulative_infeasible": PRIOR_SMOKE_INFEASIBLE + EXPECTED_LONG_INFEASIBLE,
        "remaining_children": len(remaining),
        "shard_counts": [item["count"] for item in schedule["assignments"]],
        "archive_dir": str(args.archive_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
