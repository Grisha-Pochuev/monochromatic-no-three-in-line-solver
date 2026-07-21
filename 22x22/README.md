# 22x22 checkerboard no-three-in-line

Current certified bounds:

```text
33 <= D_mono(22) <= 34
```

`config_33.json` is an independently verified 33-point construction on parity 0. Run:

```bash
python 22x22/verify_22x22.py
```

For even board size the two colors are congruent by reflection, so only parity 0 must be proved.

## Exact upper-bound models

- `prove_upper_22x22_partition.py` — original point model with all maximal grid-line constraints;
- `prove_upper_22x22_pattern_model.py` — exact four-direction patterns plus all remaining lines;
- `upper_certificate_34_four_direction.json` — rational certificate with objective `6470/187`;
- `prove_upper_22x22_main_diagonal_pair.py` — all-line model split by the forced pair on `x=y`;
- `prove_upper_22x22_profile_child.py` — pair-conditional model split by both diagonal saturation counts;
- `run_n22_profile_smoke_shard.py` and `collect_n22_profile_smoke.py` — complete profile smoke infrastructure;
- `run_n22_profile_long_shard.py` and `collect_n22_profile_long.py` — memory-safe long-run infrastructure.

## Saved runs

### Run 29534667942

Archive: `22x22/runs/2026-07-17-run-29534667942/`

The long coarse-model run saved 20 of 21 partitions. Every saved partition was `UNKNOWN`; no 34-point configuration was found and no partition was proved impossible.

### Run 29561750178

Archive: `22x22/runs/2026-07-17-run-29561750178/`

The stronger exact-pattern workflow collected all 21 large partitions:

- `INFEASIBLE`: 0;
- `UNKNOWN`: 21;
- total solver work: 19.45 job-hours.

### Run 29575490884

Archive: `22x22/runs/2026-07-17-run-29575490884/`

The five-hour main-diagonal-pair run recovered all 121 canonical pair cases:

- `INFEASIBLE`: 33;
- `UNKNOWN`: 88;
- `FEASIBLE`/`OPTIMAL`: 0;
- total solver work: 86.31 job-hours;
- total branches: 4,196,533,425;
- total conflicts: 1,185,395,482.

No 34-point configuration was found, but the 88 `UNKNOWN` pairs mean the board is not closed. The 33 exact exclusions must not be recomputed.

### Run 29766054707

Archive: `22x22/runs/2026-07-20-run-29766054707/`

The complete pair/profile smoke finished successfully and collected all 2640 children:

- `INFEASIBLE`: 1864;
- `UNKNOWN`: 776;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/model-invalid: 0;
- newly closed parent pairs: 0;
- solver work: 4.77 job-hours;
- total branches: 368,668,487;
- total conflicts: 97,545,592.

The 1864 exact exclusions are final and must not be recomputed. The remaining 776 children are listed in the balanced long schedule stored with this run.

### Run 29770927206

Archive: `22x22/runs/2026-07-21-run-29770927206/`

The memory-safe 5h50 rerun processed all 776 survivors from run `29766054707`:

- `INFEASIBLE`: 606;
- `UNKNOWN`: 170;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/model-invalid: 0;
- newly closed main-diagonal pairs: 35;
- remaining main-diagonal pairs: 53;
- memory-guard records: 0.

Together with the 1864 children closed by run `29766054707`, exactly 2470 of the 2640 profile children are now proved impossible. The remaining 170 children are the only exact frontier for a 34-point configuration. Source run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29770927206

### Run 29795643015

Archive: `22x22/runs/2026-07-21-run-29795643015/`

The exact follow-up processed all 170 survivors from run `29770927206`:

- `INFEASIBLE`: 114;
- `UNKNOWN`: 56;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/unexpected/model-invalid/technical: 0;
- newly closed main-diagonal pairs: 23;
- remaining main-diagonal pairs: 30;
- cumulative exact exclusions: 2584 / 2640.

Source run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29795643015

### Run 29815441947

Archive: `22x22/runs/2026-07-21-run-29815441947/`

The exact follow-up processed all 56 survivors from run `29795643015`:

- `INFEASIBLE`: 46;
- `UNKNOWN`: 10;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing/duplicate/unexpected/model-invalid/technical: 0;
- newly closed main-diagonal pairs: 20;
- remaining main-diagonal pairs: 10;
- cumulative exact exclusions: 2630 / 2640.

Source run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29815441947

## Current follow-up attack

The next workflow processes only the 10 exact children still marked `UNKNOWN` after run `29815441947`. It uses 20 jobs (ten active and ten empty), four solver workers, one solver process per machine, a 13 GB RSS guard, and up to 5 hours 50 minutes per job. Previously proved children are not recomputed.

