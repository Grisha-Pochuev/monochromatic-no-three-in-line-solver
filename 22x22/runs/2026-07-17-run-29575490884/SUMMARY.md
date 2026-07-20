# Recovered results for five-hour n22 main-diagonal run 29575490884

Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29575490884

Head SHA: `b880d58a6a23aa8ac0401abe9586ae217c7ec8fe`

## Human-readable result

The GitHub Actions run ended with a red workflow status, but the mathematical shard computation was preserved completely. All 20 shard artifacts were uploaded, and together they contain exactly one record for each of the 121 canonical main-diagonal pair cases.

- expected cases: 121;
- recovered records: 121;
- missing cases: 0;
- duplicate cases: 0;
- `INFEASIBLE`: 33;
- `UNKNOWN`: 88;
- `FEASIBLE`/`OPTIMAL`: 0;
- total solver work: 86.31 job-hours;
- total branches: 4,196,533,425;
- total conflicts: 1,185,395,482.

No 34-point configuration was found. However, 88 canonical pair cases remain `UNKNOWN`, so the upper bound 33 is not proved. The certified status remains:

```text
33 <= D_mono(22) <= 34
```

## What was proved

Thirty-three canonical selected-pair cases on the forced main diagonal `x=y` are strictly impossible. These exact exclusions must not be recomputed in later runs.

The full lists of excluded and unresolved case indices are stored in `overall.json`. Raw per-case JSON remains available in the 20 GitHub Actions shard artifacts.

## Why GitHub displayed a red cross

The verification/smoke job and all 20 shard jobs produced artifacts. The final collector did not produce the overall artifact. The collect job did not install pinned OR-Tools, while `collect_n22_main_diagonal_results.py` imports the proof module, which imports OR-Tools.

This was a technical aggregation failure, not loss of the mathematical search. The results in this archive were reconstructed directly from all 20 shard artifacts. The workflow has been corrected so the collect job installs `ortools==9.15.6755`.

## Next exact step

Do not repeat all 121 cases. Preserve the 33 `INFEASIBLE` cases and run only the 88 `UNKNOWN` pair indices. Subdivide every unresolved pair by the complete range

```text
number of slope +1 diagonals containing exactly two selected points = 13, 14, 15, 16, 17.
```

This gives at most 440 child cases before immediate exclusions. A short smoke run should first determine how many child cases close quickly; only the surviving children should receive a long run.
