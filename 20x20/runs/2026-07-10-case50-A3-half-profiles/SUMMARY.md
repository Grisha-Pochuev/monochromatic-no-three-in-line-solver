# 20x20 case 50: exact A=3 half-board profile reduction

Date: 2026-07-10

## Starting point

The single unresolved diagonal-pair branch fixes `(2,2)` and `(17,17)` on `x=y`.
The heavy-intersection refinement had already proved `A=4` infeasible, leaving `A=0,1,2,3`.

This round studies the exact class `A=3`.

Let:

- `L` = number of selected points with `x < 10` (left half),
- `T` = number of selected points with `y < 10` (top half).

Because the target size is 31, the complementary halves contain `31-L` and `31-T` points. Rotation by 180 degrees allows us to keep only `L <= 15`; reflection in `x=y` identifies `(L,T)` with `(T,L)`.

## Strict results

Exact CP-SAT checks proved the following left-half counts infeasible:

```text
L = 8, 9, 10, 11
```

Therefore only:

```text
L = 12, 13, 14, 15
```

remain up to 180-degree rotation.

A second exact split by `T` closed 22 of the 32 tested `(L,T)` profiles quickly. After quotienting by reflection in `x=y`, seven essential profiles remained for longer checking:

```text
(12,15)
(13,13)
(13,14)
(13,15)
(14,14)
(14,15)
(15,15)
```

The longer exact check then proved:

```text
(A,L,T) = (3,13,13) is INFEASIBLE.
```

## Current A=3 frontier

Up to the stated symmetries, only six half-board profiles remain:

```text
(12,15)
(13,14)
(13,15)
(14,14)
(14,15)
(15,15)
```

The corresponding reflected profiles `(T,L)` are equivalent and do not need separate proof runs.

No 31-point configuration was found. `UNKNOWN` profiles remain open and are not claimed infeasible.

## Interpretation

This is exact structural progress, not a heuristic search result. The original `A=3` class has been reduced to six explicit, symmetry-deduplicated profiles. Future computation should target only these six profiles and should not rerun the already excluded half-counts or `(13,13)` profile.
