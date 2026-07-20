# 22x22 checkerboard no-three-in-line

Current certified bounds:

```text
33 <= D_mono(22) <= 34
```

`config_33.json` is an independently verified 33-point construction on parity 0. Run:

```bash
python 22x22/verify_22x22.py
```

For even board size the two colors are congruent by reflection, so only parity 0 must be proved. A 34-point candidate has between 12 and 17 rows with two points and between 12 and 17 columns with two points. Transposition reduces the complete count-pair partition to 21 cases.

## Exact upper-bound models

- `prove_upper_22x22_partition.py` — the original point model with all maximal grid-line constraints;
- `prove_upper_22x22_pattern_model.py` — exact row, column, and slope `+1/-1` diagonal patterns, plus all remaining line constraints;
- `upper_certificate_34_four_direction.json` — rational certificate with objective `6470/187`;
- `prove_upper_22x22_main_diagonal_pair.py` — compact all-line model split by the forced selected pair on `x=y`;
- `run_n22_main_diagonal_shard.py` — deterministic 20-shard runner for all 121 canonical pair cases;
- `collect_n22_main_diagonal_results.py` — completeness and solution validator;
- `.github/workflows/n22-exact-proof.yml` — long baseline workflow;
- `.github/workflows/n22-pattern-one-hour.yml` — one-hour comparison workflow;
- `.github/workflows/n22-main-diagonal-pairs-five-hour.yml` — complete five-hour main-diagonal-pair run.

## Saved runs

### Run 29534667942

Archive: `22x22/runs/2026-07-17-run-29534667942/`

The long coarse-model run saved 20 of 21 partitions. Every saved partition was `UNKNOWN`; no 34-point configuration was found and no partition was proved impossible.

### Run 29561750178

Archive: `22x22/runs/2026-07-17-run-29561750178/`

The stronger exact-pattern workflow completed successfully and collected all 21 partitions, including `(17,17)`:

- `INFEASIBLE`: 0;
- `UNKNOWN`: 21;
- `FEASIBLE`/`OPTIMAL`: 0;
- total solver work: 19.45 job-hours;
- total branches: 171,178,946;
- total conflicts: 20,825,701.

This run did not close 22x22. A long repeat of the unchanged pattern model is not recommended.

### Run 29575490884

Archive: `22x22/runs/2026-07-17-run-29575490884/`

The five-hour main-diagonal-pair run preserved all 20 shard artifacts. The final collection job failed technically, but the 121 case records were recovered and checked manually:

- expected and recovered cases: 121/121;
- `INFEASIBLE`: 33;
- `UNKNOWN`: 88;
- `FEASIBLE`/`OPTIMAL`: 0;
- total solver work: 86.31 job-hours;
- total branches: 4,196,533,425;
- total conflicts: 1,185,395,482.

No 34-point configuration was found, but the 88 `UNKNOWN` cases mean the board is not closed. The 33 exact exclusions are reusable and should not be recomputed.

The red workflow status came from the collector: it imported the OR-Tools-based proof module while the collect job had not installed OR-Tools. The raw shard calculations were not lost.

## Current exact frontier

The rational four-direction certificate has denominator `187`, objective numerator `6470`, and only `112` units of slack at target 34. It forces the three diagonals `x-y=-2,0,2` to contain exactly two points. Therefore the selected pair on `x=y` gives a complete finite partition.

There are 231 raw pairs and 121 canonical cases after 180-degree rotation. Run `29575490884` strictly excluded 33 of these cases. The next run must process only the 88 remaining cases and subdivide each by the complete saturated slope `+1` diagonal count range `13..17`.

Detailed derivation: `MAIN_DIAGONAL_PAIR_PLAN.md`.

The folder may be marked closed with value 33 only after every remaining child case returns `INFEASIBLE`. `UNKNOWN` is not a proof.
