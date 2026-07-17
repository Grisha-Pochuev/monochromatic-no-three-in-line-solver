# Partial results for exact 22x22 run 29534667942

Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29534667942

## What was established

- The independent verification of the 33-point construction succeeded.
- 20 of the 21 upper-bound partitions finished their 21,000-second solver budget and saved result JSON files.
- All 20 saved partitions returned `UNKNOWN`.
- No partition returned `FEASIBLE` or `OPTIMAL`, so the run found no 34-point counterexample.
- No partition returned `INFEASIBLE`, so the run did not prove the upper bound 33.
- Partition `(row_twos, column_twos) = (17,17)` was still running when this partial record was collected.

The certified status therefore remains:

```text
33 <= D_mono(22) <= 34
```

## Aggregate work saved

- collected partitions: 20/21
- solver time represented: 116.67 job-hours
- total branches: 1,400,985,547
- total conflicts: 682,897,212
- constraints per partition: 2,455 maximal grid-line constraints
- workers per partition: 4

Red job crosses mean that the solver timed out with `UNKNOWN` and the script deliberately exited nonzero. They do not mean that a 34-point configuration was found or that the mathematical model was invalid.

## Partition records

| row-twos | column-twos | status | seconds | branches | conflicts |
|---:|---:|---|---:|---:|---:|
| 12 | 12 | UNKNOWN | 21000.1 | 34,906,222 | 2,568,086 |
| 12 | 13 | UNKNOWN | 21000.1 | 39,054,268 | 2,077,229 |
| 12 | 14 | UNKNOWN | 21000.1 | 41,792,717 | 2,051,657 |
| 12 | 15 | UNKNOWN | 21000.1 | 219,613,008 | 161,393,561 |
| 12 | 16 | UNKNOWN | 21001.1 | 31,298,239 | 2,056,296 |
| 12 | 17 | UNKNOWN | 21000.4 | 25,817,476 | 1,892,917 |
| 13 | 13 | UNKNOWN | 21000.1 | 35,240,201 | 1,924,825 |
| 13 | 14 | UNKNOWN | 21000.1 | 44,127,582 | 2,056,412 |
| 13 | 15 | UNKNOWN | 21000.1 | 53,830,089 | 21,760,531 |
| 13 | 16 | UNKNOWN | 21000.1 | 27,766,791 | 1,982,601 |
| 13 | 17 | UNKNOWN | 21001.3 | 163,826,934 | 120,523,845 |
| 14 | 14 | UNKNOWN | 21000.1 | 58,458,298 | 2,087,999 |
| 14 | 15 | UNKNOWN | 21000.1 | 70,915,430 | 32,929,727 |
| 14 | 16 | UNKNOWN | 21000.1 | 29,002,690 | 1,948,698 |
| 14 | 17 | UNKNOWN | 21000.1 | 166,560,290 | 116,936,397 |
| 15 | 15 | UNKNOWN | 21000.1 | 214,864,525 | 158,185,360 |
| 15 | 16 | UNKNOWN | 21000.1 | 37,827,549 | 2,140,206 |
| 15 | 17 | UNKNOWN | 21000.1 | 24,927,067 | 1,913,089 |
| 16 | 16 | UNKNOWN | 21000.1 | 54,093,178 | 2,100,414 |
| 16 | 17 | UNKNOWN | 21000.1 | 27,062,993 | 1,879,773 |

## Most search-intensive partitions by branches

- `(12,15)`: 219,613,008 branches, 161,393,561 conflicts
- `(15,15)`: 214,864,525 branches, 158,185,360 conflicts
- `(14,17)`: 166,560,290 branches, 116,936,397 conflicts
- `(13,17)`: 163,826,934 branches, 120,523,845 conflicts
- `(14,15)`: 70,915,430 branches, 32,929,727 conflicts

## Interpretation and next step

The row/column saturation split is much too coarse: every completed class remained open after the full GitHub Actions budget. Repeating the same run with new seeds is unlikely to be an efficient proof strategy.

The next exact run should subdivide each `(row_twos, column_twos)` class by an additional symmetry-compatible statistic, for example the number of slope `+1` diagonals containing two selected points. A short smoke run should first compare several candidate subdivisions before another full 21,000-second run.

Raw machine-readable records are stored in `partial_results.json`.
