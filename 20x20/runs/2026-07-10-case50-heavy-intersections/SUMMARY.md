# 20x20 case 50: heavy-intersection refinement

Date: 2026-07-10

The only unresolved canonical diagonal-pair case fixes the selected points on the main diagonal to:

```text
(2,2), (17,17)
```

The repaired dual certificate forces 13 heavy diagonals to contain exactly two selected points each:

```text
x-y = -6,-4,-2,0,2,4,6
x+y = 14,16,18,20,22,24
```

Let `A` be the number of selected points lying at intersections of one heavy `x-y` diagonal and one heavy `x+y` diagonal. Double counting the 26 incidences on the 13 full diagonals gives:

```text
outside_heavy_union = A + 5
```

Earlier exact work excludes `A >= 5`, leaving `A = 0,1,2,3,4`.

## New exact result

Using `search_case50_heavy_intersections.py` with all no-three-in-line constraints, the certificate equalities, the certificate excess inequality, and the fixed case-50 main-diagonal pair:

```bash
python 20x20/search_case50_heavy_intersections.py --A 4 --seconds 60 --workers 8
```

returned:

```text
A = 4
status = INFEASIBLE
elapsed approximately 14.67 seconds
conflicts = 1592
branches = 72266
```

Therefore the remaining hypothetical 31-point configuration must satisfy:

```text
A in {0,1,2,3}
outside_heavy_union in {5,6,7,8}
```

Short local checks of `A=0,1,2,3` reached the time limit and remain unresolved. They must not be treated as feasible or infeasible.

## Updated status

The mathematical frontier remains:

```text
30 <= D_mono(20) <= 31
```

But the single remaining canonical branch has now been reduced from five structural classes to four.