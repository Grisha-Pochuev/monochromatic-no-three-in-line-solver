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

## Current 5h50 attack

Workflow:

```text
.github/workflows/n22-profile-survivors-5h50.yml
```

It processes only the 776 `UNKNOWN` children from run `29766054707`.

Resource layout:

- 20 independent `ubuntu-latest` jobs;
- 4 CP-SAT workers per active child, using all four virtual CPUs of each runner;
- 38 or 39 children per job;
- 21,000 seconds (5 hours 50 minutes) wall budget per shard;
- workload balanced from the smoke-run score `branches + 2*conflicts`;
- only one solver process at a time on each machine.

Memory safeguards:

- every child runs in a separate subprocess, so memory is returned after each case;
- parent-side RSS guard at 13,000 MB, leaving headroom on a 16 GB runner;
- a memory-stopped child can be retried with two workers;
- `MALLOC_ARENA_MAX=2` and hidden numerical-library threads are disabled;
- memory, CPU and disk snapshots are logged once per minute;
- partial JSON is written after every child and artifacts upload with `if: always()`.

The folder may be marked closed with value 33 only after every remaining child returns `INFEASIBLE`. `UNKNOWN` is not a proof.
