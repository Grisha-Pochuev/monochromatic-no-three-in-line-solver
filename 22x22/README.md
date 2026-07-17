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
- `.github/workflows/n22-exact-proof.yml` — long baseline workflow;
- `.github/workflows/n22-pattern-one-hour.yml` — one-hour comparison workflow.

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

This run did not close 22x22. The next exact step is a complete subdivision by a diagonal-profile statistic, starting with the number of slope `+1` diagonals containing two selected points. A six-hour repeat of the unchanged pattern model is not currently recommended.

The folder may be marked closed with value 33 only after every part of a complete target-34 partition returns `INFEASIBLE`. `UNKNOWN` is not a proof.
