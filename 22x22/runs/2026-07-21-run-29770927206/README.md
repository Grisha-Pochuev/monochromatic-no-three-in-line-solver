# GitHub Actions run 29770927206

Source: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29770927206

Artifact: `n22-profile-5h50-overall`, id `8479986610`.

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
