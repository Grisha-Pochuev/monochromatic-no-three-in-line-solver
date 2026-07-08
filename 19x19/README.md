# 19x19 closed package: D_mono(19) = 29

This folder records the exact verified `19 x 19` result for the monochromatic no-three-in-line problem on checkerboard grids.

The exact value is:

```text
D_mono(19) = 29
```

## Lower bound

`config_29.json` contains a directly checkable 29-point configuration on the even checkerboard colour class.

The verifier checks that:

- all points lie in the `19 x 19` grid;
- all points have the same checkerboard parity;
- there are exactly 29 distinct points;
- no three selected points are collinear.

So:

```text
D_mono(19) >= 29
```

The older `config_28.json` is kept only as a historical frontier record. It is no longer the best lower-bound construction.

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

Together with the stored 29-point construction this proves:

```text
D_mono(19) = 29
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
Result verified: D_mono(19) = 29
```

## Optional search reproduction

`search_19x19_cpsat.py` is included as an optional search script. It requires OR-Tools.

Example:

```bash
python search_19x19_cpsat.py 0 600
```

This script is not needed to verify the stored result. The verification script checks the saved construction and the rational upper certificate directly.

## Status

This case is closed in this repository.

The closure record has two parts:

1. a valid 29-point configuration in `config_29.json`;
2. a rational upper certificate in `upper_certificate.json` proving that 30 points are impossible.
