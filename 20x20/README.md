# 20x20 checkerboard no-three-in-line

Exact certified result:

```text
D_mono(20) = 30
```

The 20x20 case is closed.

## Lower bound

- `config_30.json` is a valid 30-point monochromatic configuration on parity 0.
- `verify_20x20.py` checks the board, parity, distinctness, size, and absence of three collinear selected points.

Fast verification:

```bash
python 20x20/verify_20x20.py
```

## Upper-bound route

The rational four-direction LP certificate in `upper_certificate_31.json` has objective

```text
31433544 / 1000000 = 31.433544 < 32
```

so 32 points are impossible. Its heavy-line consequences reduce every hypothetical 31-point configuration to exact finite cases.

The main diagonal `x=y` must contain exactly two selected points. There are 190 possible pairs; 180-degree rotation reduces these to 100 canonical cases. The first exact run excluded 99 cases and left only the pair `(2,2),(17,17)`.

For that final case, the heavy-line intersection parameter `A` was exhausted completely:

- `A>=5` excluded;
- `A=4` excluded;
- `A=3` excluded by the 20-branch run recorded in `20x20/runs/2026-07-10-run-29102300788/`;
- `A=0,1,2` excluded by the final 20-branch run recorded in `20x20/runs/2026-07-10-run-29103139466/`.

The final run produced:

```text
expected branches: 20
records found:     20
INFEASIBLE:        20
UNKNOWN:            0
solutions:          0
```

Therefore no 31-point configuration exists. Together with `config_30.json`, this proves

```text
D_mono(20) = 30
```

## Final proof record

- Workflow: `.github/workflows/n20-case50-A012-20job-four-hour.yml`
- GitHub Actions run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29103139466
- Human-readable summary: `runs/2026-07-10-run-29103139466/SUMMARY.md`
- Machine-readable result: `runs/2026-07-10-run-29103139466/overall.json`

The final computation used 20 disjoint branches with `max-parallel: 20`, four CP-SAT workers per branch, and exact symmetry reductions. Every branch ended with the proof status `INFEASIBLE`; no branch ended as `UNKNOWN`.

## Reproduction notes

The final workflow can be run again from GitHub Actions. The stored JSON record contains the branch definitions, seeds, elapsed times, conflict counts, branch counts, and solver status for all 20 final partitions.

## Other exploratory searches

- `search_20x20_cpsat.py` is an unsharded CP-SAT feasibility search.
- `milp31_enhanced.py` is a SciPy/HiGHS search strengthened by exact consequences of the dual certificate.
- `local_mono_param.cpp` is a fast local search. Failure to find 31 by local search alone is evidence only; the closed result above comes from the complete exact partition.
