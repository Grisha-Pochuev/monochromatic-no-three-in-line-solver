# 20x20 attack round 9: exact GitHub Actions setup

Status remains honest:

```text
30 <= D_mono(20) <= 31
```

No 31-point configuration has yet been found, and 31 has not yet been excluded.

## Repaired upper certificate

The previous stored certificate was replaced by a verifier-friendly integer dual certificate generated from the all-line LP.

```text
denominator: 1000000
nonzero weighted lines: 65
minimum point cover: 1000001 / 1000000
LP objective: 31433544 / 1000000 = 31.433544 < 32
```

`verify_20x20.py` checks this using exact integer arithmetic. `generate_upper_certificate_31.py` reproduces the certificate with SciPy/HiGHS.

## New mathematical reduction

For a hypothetical 31-point set, the total dual slack is only

```text
31433544 - 31*1000000 = 433544.
```

Any weighted line whose weight exceeds `433544` must therefore attain full occupancy two. Thirteen certificate lines are forced full. In particular:

```text
main diagonal x-y=0
weight = 618026 > 433544
occupancy = 2
```

Thus a 31-point solution is completely classified by the pair of selected points on the main diagonal.

There are `C(20,2)=190` pairs. Rotation by 180 degrees sends `(a,b)` to `(19-b,19-a)`, so existence can be checked using 100 canonical representatives without losing any possible solution.

## Exact sharded solver

`search_20x20_diagonal_pairs.py`:

1. independently checks the integer certificate;
2. generates all 1717 grid-line constraints;
3. adds every forced-full consequence of the dual slack;
4. fixes one canonical main-diagonal pair;
5. runs CP-SAT on that exact branch;
6. writes a JSON record with `INFEASIBLE`, `UNKNOWN`, or a verified 31-point solution.

The partition is exhaustive and non-overlapping at the level of canonical symmetry classes. Failure due to a time limit is recorded as `UNKNOWN`, never as a proof.

## GitHub Actions workflow

`.github/workflows/n20-diagonal-pair-proof.yml` distributes the 100 cases across 20 runners:

```text
20 runners
4 CP-SAT workers per runner
5 exact pair cases per runner
```

The default full budget is `3300` seconds per case, about 275 minutes of solver time on each runner.

The collector produces `n20-diagonal-pair-overall`:

- `FOUND_31_POINT_CONFIGURATION` means `D_mono(20)=31`;
- `PROVED_NO_31_BY_COMPLETE_PAIR_PARTITION` means `D_mono(20)=30`;
- `INCOMPLETE_FRONTIER` gives the exact remaining case identifiers.

## Why GitHub Actions is now preferable

The web chat is best used for deriving reductions, checking mathematics, writing verifiers, and improving the branching scheme. It is not the right place for roughly 80 CPU cores running for several hours.

GitHub Actions is now useful because the computation is no longer 20 repetitions of one random search. Every runner owns a distinct exact part of a complete partition, so every `INFEASIBLE` result is permanent progress and every `UNKNOWN` result identifies a precise branch for the next attack.

## Next operation

Run the workflow first in `smoke` mode. If verification and one short branch succeed, run `full` with the defaults and preserve the overall artifact in the repository before the next round.
