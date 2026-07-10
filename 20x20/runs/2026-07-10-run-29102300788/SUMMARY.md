# n20 case 50, A=3: exact 20-job proof

Date: 2026-07-10

GitHub Actions run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29102300788

Conclusion: `PROVED_A3_INFEASIBLE`

The last unresolved diagonal-pair case fixes the main-diagonal points `(2,2)` and `(17,17)`. The dual certificate forces 13 heavy diagonals to contain exactly two selected points. Let `A` be the number of selected points lying at intersections of two heavy diagonals.

This run proves that the entire class `A=3` is infeasible.

## Exact run summary

- expected disjoint branches: 20
- records found: 20
- infeasible: 20
- unknown: 0
- solutions: 0
- workers per branch: 4
- time limit per branch: 10,400 seconds
- longest branch: `p1515_q6_7`, about 198.72 seconds

All 20 branches were exact and pairwise disjoint. Together they covered the remaining `A=3` frontier after the earlier half-board and quadrant reductions.

Therefore a hypothetical 31-point configuration for case 50 can only have:

- `A=0`,
- `A=1`, or
- `A=2`.

The board status remains:

`30 <= D_mono(20) <= 31`.

The complete machine-readable record is stored in `overall.json` in this directory.
