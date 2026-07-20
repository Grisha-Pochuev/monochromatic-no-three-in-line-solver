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
- `run_n22_profile_smoke_shard.py` and `collect_n22_profile_smoke.py` — complete profile smoke infrastructure.

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

## Current pair/profile attack

For every unresolved selected pair on `x=y`, the target-34 certificate leaves a pair-dependent residual slack between 53 and 112. This gives exact additional constraints:

- all certificate lines heavier than the residual are saturated;
- off-diagonal selected points obey the residual excess budget and threshold cuts;
- explicit 0/1/2 states on rows, columns and both diagonal families obey the weighted line-defect budget;
- transposition gives a safe lexicographic symmetry break at the count-profile level.

Every unresolved pair is partitioned completely by:

```text
diag_plus_twos  = 13..17
diag_minus_twos = 12..17
```

This gives 2640 formal children. An exact arithmetic defect calculation eliminates more than half before CP-SAT. Short local tests closed many additional children in seconds, including 41 of 81 admissible profile children among the nine smallest-residual pairs.

Prepared workflow:

```text
.github/workflows/n22-profile-children-smoke.yml
```

It checks all 2640 formal children exactly once across 20 shards. Arithmetic exclusions finish immediately; the remaining children receive 20 seconds and four CP-SAT workers. The result will identify newly closed pairs and the exact list of surviving profile children.

Detailed experiments and the exact-pattern symmetry warning are in `PROFILE_SPLIT_RESEARCH_2026-07-20.md`.

The folder may be marked closed with value 33 only after every remaining child returns `INFEASIBLE`. `UNKNOWN` is not a proof.
