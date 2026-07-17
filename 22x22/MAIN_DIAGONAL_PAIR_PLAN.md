# 22×22: complete main-diagonal-pair partition

Date: 17 July 2026

## Exact structural reduction

The rational four-direction certificate in
`upper_certificate_34_four_direction.json` has denominator `187` and objective

```text
6470 / 187 = 34.598930...
```

For a hypothetical 34-point configuration, the total certificate slack is

```text
6470 - 34*187 = 112.
```

Any certificate line with integer weight greater than `112` must therefore be
saturated: it must contain exactly two selected points. There are exactly three
such lines:

```text
x-y = -2  weight 115
x-y =  0  weight 117
x-y =  2  weight 115
```

In particular, the main diagonal `x=y` contains exactly two selected points.

There are `C(22,2)=231` possible selected pairs on `x=y`. Rotation by 180
degrees maps a pair `{a,b}` to `{21-a,21-b}` and preserves the complete problem.
The 231 raw pairs form exactly 121 orbits, so it is sufficient and necessary to
check 121 canonical representatives.

## Exact engine

`prove_upper_22x22_main_diagonal_pair.py` contains:

- all 242 allowed parity-0 points;
- all 2455 maximal grid-line constraints;
- target size 34;
- exact verification of the rational certificate;
- saturation of the three forced heavy diagonals;
- the certificate excess inequality;
- a fixed canonical selected pair on `x=y`;
- exact row, column, and diagonal occupancy-count consequences;
- the safe symmetry break `row_twos <= column_twos`, because transposition
  preserves every fixed pair on `x=y`.

`INFEASIBLE` is a complete proof for one canonical pair. `UNKNOWN` is only an
incomplete search result. A found 34-point solution is independently checked
inside the engine and again by the collector.

## Five-hour workflow

Workflow:

```text
.github/workflows/n22-main-diagonal-pairs-five-hour.yml
```

The 121 cases are distributed deterministically over 20 shards. Nineteen
shards receive six cases and one receives seven. Each shard has a five-hour
job limit and an internal solver deadline of 17,400 seconds, leaving time to
write JSON and upload artifacts.

Before the long jobs, the workflow:

1. verifies the known 33-point construction;
2. verifies the rational certificate exactly;
3. verifies that there are 121 canonical pairs;
4. runs short engine and shard smoke tests.

The collector requires every canonical case exactly once. It records one of:

```text
PROVED_D_MONO_22_EQUALS_33
FOUND_VALID_34_POINT_CONFIGURATION
INCOMPLETE_WITH_UNKNOWN_CASES
TECHNICAL_FAILURE
```

If unknown cases remain, the next exact refinement is to run only those pair
indices and split each by the number of saturated slope `+1` diagonals,
covering the complete range 13 through 17.
