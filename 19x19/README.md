# 19x19 working package: 28 <= D_mono(19) <= 29

This folder records the current reproducible `19 x 19` state for the monochromatic no-three-in-line problem on checkerboard grids.

It does **not** mark the case as closed yet. The current verified bounds are:

```text
28 <= D_mono(19) <= 29
```

## Lower bound

`config_28.json` contains a directly checkable 28-point configuration on the even checkerboard colour class.

The verifier checks that:

- all points lie in the `19 x 19` grid;
- all points have the same checkerboard parity;
- there are exactly 28 distinct points;
- no three selected points are collinear.

So:

```text
D_mono(19) >= 28
```

## Upper bound

`upper_certificate.json` contains rational four-direction covering certificates for both checkerboard colour classes.

The certificate uses weights on:

- rows `y`;
- columns `x`;
- diagonals `x - y`;
- diagonals `x + y`.

Every allowed checkerboard point is covered by total weight at least `1`. Any no-three-in-line set has at most two points on each such line. Therefore twice the total line weight is an upper bound.

The verified bounds are:

```text
even colour: 3564/119 < 30
odd colour:  268/9    < 30
```

Since the number of selected points is an integer, both colour classes have at most 29 points:

```text
D_mono(19) <= 29
```

Together with the stored lower construction this gives:

```text
28 <= D_mono(19) <= 29
```

## How to verify

From the repository root run:

```bash
python 19x19/verify_19x19.py
```

Or from this folder run:

```bash
python verify_19x19.py
```

Expected final line:

```text
verified bounds: 28 <= D_mono(19) <= 29
```

## Optional search reproduction

`search_19x19_cpsat.py` is included as an optional search script. It requires OR-Tools.

Example:

```bash
python search_19x19_cpsat.py 0 600
```

This script is not needed to verify the stored bounds. The verification script checks the saved construction and the rational upper certificate directly.

## Status

This case remains open between 28 and 29. To close it exactly, one needs either:

1. a valid 29-point configuration, proving `D_mono(19) = 29`; or
2. a stronger upper certificate proving `D_mono(19) <= 28`.
