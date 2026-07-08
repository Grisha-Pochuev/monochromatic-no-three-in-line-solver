# 20x20 working package: 30 <= D_mono(20) <= 31

This folder records the current reproducible `20 x 20` frontier for the monochromatic no-three-in-line problem on checkerboard grids.

It does **not** mark the case as closed yet. The current verified bounds are:

```text
30 <= D_mono(20) <= 31
```

## Lower bound

`config_30.json` contains a directly checkable 30-point configuration on the even checkerboard colour class.

The verifier checks that:

* all points lie in the `20 x 20` grid;
* all points have the same checkerboard parity;
* there are exactly 30 distinct points;
* no three selected points are collinear.

So:

```text
D_mono(20) >= 30
```

## Upper bound

`upper_certificate_31.json` contains rational four-direction covering certificates for both checkerboard colour classes.

The certificate uses weights on:

* rows `y`;
* columns `x`;
* diagonals `x - y`;
* diagonals `x + y`.

Every allowed checkerboard point is covered by total weight at least `1`. Any no-three-in-line set has at most two points on each such line. Therefore twice the total line weight is an upper bound.

The verified bound for both colour classes is:

```text
1226/39 = 31.435897... < 32
```

Since the number of selected points is an integer:

```text
D_mono(20) <= 31
```

Together with the stored lower construction this gives:

```text
30 <= D_mono(20) <= 31
```

## Current unresolved question

The case is still open between 30 and 31. To close it exactly, one needs either:

1. a valid 31-point configuration, proving `D_mono(20) = 31`; or
2. a stronger upper certificate / exhaustive infeasibility record proving `D_mono(20) <= 30`.

## How to verify

From the repository root run:

```bash
python 20x20/verify_20x20.py
```

Expected final line:

```text
verified frontier: 30 <= D_mono(20) <= 31
```

This script checks both the stored 30-point configuration and the rational upper certificate directly. It does not rely on trusting the search that found the configuration.
