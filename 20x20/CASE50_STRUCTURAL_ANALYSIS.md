# Structural analysis of the last 20x20 branch

Date: 2026-07-10

This note studies the only unresolved canonical branch left by workflow run `29070428756`:

```text
case_id = 50
forced main-diagonal points = (2,2), (17,17)
```

The certified global status remains

```text
30 <= D_mono(20) <= 31.
```

## 1. Thirteen certificate lines are forced full

The all-line dual certificate has denominator `1000000` and objective

```text
31433544 / 1000000 = 31.433544.
```

For a hypothetical 31-point solution the available slack is therefore

```text
433544 / 1000000.
```

Every certificate line of weight greater than `433544` must have occupancy exactly two. There are thirteen such lines:

```text
x-y = -6,-4,-2,0,2,4,6
x+y = 14,16,18,20,22,24
```

Thus the unresolved branch is not a general 31-point search. It must satisfy thirteen exact diagonal equations simultaneously.

## 2. Incidence identity

Classify a selected point by how many of the thirteen forced lines contain it.

Because the forced lines consist of two slope families, a point can lie on zero, one, or two forced lines. Let

```text
A = selected points on an intersection of two forced lines
B = selected points on exactly one forced line
C = selected points on none of the forced lines
```

The thirteen lines each contain exactly two selected points, so the total forced-line incidence is 26:

```text
2A + B = 26.
```

The solution has 31 points:

```text
A + B + C = 31.
```

Subtracting gives the exact identity

```text
C = A + 5.
```

Therefore every hypothetical 31-point solution must place at least five points completely outside the thirteen heavy diagonals.

## 3. Exact exclusion of A >= 5

The complete no-three-in-line CP-SAT model for case 50 was augmented by the equality fixing `A` and checked separately.

The values

```text
A = 5,6,7,8,9,10,11,12,13
```

were all proved `INFEASIBLE`.

Hence every hypothetical 31-point configuration in the last branch must satisfy

```text
0 <= A <= 4
5 <= C <= 9
C = A + 5.
```

This turns the last large branch into five mathematically meaningful structural classes:

```text
A = 0, 1, 2, 3, or 4.
```

The next exact attack should partition case 50 by these five values and then refine each class by the distribution of the `C=A+5` outside points under 180-degree rotation. The already excluded 99 diagonal-pair cases must not be rerun.

## Interpretation

The remaining candidate, if it exists, is forced to avoid the dense intersection core of the certificate. It can use at most four intersections of the heavy `x-y` and `x+y` diagonals, while placing at least five points outside all thirteen heavy diagonals. This is evidence of a strongly peripheral structure rather than a generic dense configuration.

This note records a reduction, not a closure of the 20x20 case.
