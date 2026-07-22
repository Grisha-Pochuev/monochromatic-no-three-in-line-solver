# GitHub Actions run 29918490062

Source: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29918490062

This run split the sole remaining exact child `652` into the 21 disjoint cases

```text
12 <= row_twos <= column_twos <= 17
```

and processed them for about two hours per case on exactly twenty solver jobs.

Verified result:

- exact subcases found: 21 / 21;
- `INFEASIBLE`: 4;
- `UNKNOWN`: 17;
- `FEASIBLE` / `OPTIMAL`: 0;
- `MODEL_INVALID`: 0;
- missing / duplicate / unexpected records: 0;
- solver work: 39.09 job-hours;
- total branches: 821,921,325;
- total conflicts: 502,969,578.

Strictly excluded subcases:

```text
5  = (row_twos=12, column_twos=17)
10 = (row_twos=13, column_twos=17)
17 = (row_twos=15, column_twos=17)
19 = (row_twos=16, column_twos=17)
```

Remaining subcase ids:

```text
0, 1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 20
```

No valid 34-point configuration was found. `UNKNOWN` is not a proof, so the certified board status remains

```text
33 <= D_mono(22) <= 34
```

The original run page retains the complete aggregate artifact and all twenty solver-slot artifacts with the exact records and resource logs.
