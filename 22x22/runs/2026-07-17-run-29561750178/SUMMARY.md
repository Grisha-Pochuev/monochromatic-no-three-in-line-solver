# One-hour 22x22 exact-pattern run 29561750178

Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29561750178

## Result

The workflow completed technically successfully and independently verified the known 33-point construction.
All 21 exact upper-bound partitions were collected, including `(17,17)`, which was missing from the previous long-run summary.

- target: 34 points;
- model: exact patterns for rows, columns, and both slope `+1/-1` diagonal families, plus all remaining grid-line constraints;
- collected partitions: 21/21;
- `INFEASIBLE`: 0;
- `UNKNOWN`: 21;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing or invalid partitions: 0;
- solver work: 19.45 job-hours;
- total branches: 171,178,946;
- total conflicts: 20,825,701.

Therefore the certified mathematical status remains:

```text
33 <= D_mono(22) <= 34
```

The run neither found a 34-point configuration nor proved that 34 points are impossible.

## Comparison with run 29534667942

The baseline coarse model stored 20/21 partitions, 116.67 job-hours, 1,400,985,547 branches, and 682,897,212 conflicts. Because the budgets differ (about one hour versus about six hours per partition), raw totals are not a measure of proof progress.

Normalized by solver job-hour:

- branches: about 8.80 million/hour now versus 12.01 million/hour in the baseline (about 27% lower);
- conflicts: about 1.07 million/hour now versus 5.85 million/hour in the baseline (about 82% lower).

This shows that the exact-pattern encoding materially changed the search dynamics, but the absence of any `INFEASIBLE` partition means there is not yet evidence that simply extending the same run to six hours would close the board.

The most search-intensive current partitions were:

- `(14,14)`: 30,163,405 branches and 9,422,937 conflicts;
- `(12,17)`: 18,875,536 branches and 4,879,994 conflicts.

## Recommended next step

Do not repeat the unchanged model for six hours yet. Add a provably complete subdivision by the number of slope `+1` diagonals containing exactly two selected points. First test it on `(14,14)`, `(12,17)`, and several representative easier partitions. If needed, add the analogous slope `-1` statistic or exact boundary-diagonal profiles.

`overall.json` contains one record for every one of the 21 partitions, the seeds, timings, branches, conflicts, and the source artifact digest.
