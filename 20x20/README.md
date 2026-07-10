# 20x20 checkerboard no-three-in-line

Current certified frontier:

```text
30 <= D_mono(20) <= 31
```

The unresolved question is whether a 31-point monochromatic configuration exists.

## Independently checked bounds

- `config_30.json` is a valid 30-point configuration on parity 0.
- `upper_certificate_31.json` is an integer-scaled dual LP certificate.
- `verify_20x20.py` checks both artifacts using exact integer arithmetic.
- `generate_upper_certificate_31.py` reproducibly rebuilds the LP certificate with SciPy/HiGHS.

Fast verification:

```bash
python 20x20/verify_20x20.py
```

The current dual objective is:

```text
31433544 / 1000000 = 31.433544 < 32
```

Therefore a no-three-in-line set has at most 31 points.

## Exact diagonal-pair attack

The certificate leaves only the slack

```text
31.433544 - 31 = 0.433544.
```

The main diagonal `x=y` has certificate weight `0.618026`, greater than that entire slack. Consequently every hypothetical 31-point solution must contain exactly two points on `x=y`.

There are 190 possible pairs. Rotation by 180 degrees identifies opposite pairs, leaving 100 complete canonical cases. `search_20x20_diagonal_pairs.py` solves those exact cases; it does not discard any possible 31-point solution.

The GitHub Actions workflow `.github/workflows/n20-diagonal-pair-proof.yml` distributes the 100 cases across 20 runners, five cases per runner, with four CP-SAT workers on each runner.

### Run it

In GitHub open:

```text
Actions -> n20 diagonal-pair proof -> Run workflow
```

First choose `smoke`. If it succeeds, run again with:

```text
mode = full
full_seconds_per_case = 3300
seed = 20260710
```

The final artifact `n20-diagonal-pair-overall` contains `SUMMARY.md` and `overall.json`.

Interpretation:

- `FOUND_31_POINT_CONFIGURATION` closes the case as `D_mono(20)=31`.
- `PROVED_NO_31_BY_COMPLETE_PAIR_PARTITION` closes it as `D_mono(20)=30`.
- `INCOMPLETE_FRONTIER` lists the exact unknown or missing pair cases for the next run.

## Other exploratory searches

- `search_20x20_cpsat.py` is an unsharded CP-SAT feasibility search.
- `milp31_enhanced.py` is a SciPy/HiGHS search strengthened by exact consequences of the repaired dual certificate.
- `local_mono_param.cpp` is a fast local search. Failure to find 31 is evidence only, not a proof.
