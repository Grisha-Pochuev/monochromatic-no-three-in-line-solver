# 22×22 profile-split experiments — 20 July 2026

## Why the previous 88 pair cases are still too large

Run `29575490884` strictly excluded 33 of the 121 canonical selected pairs on
the forced main diagonal `x=y`, but left 88 pair cases `UNKNOWN`. Re-running
those 88 cases unchanged would repeat large search trees.

The exact occupancy identities give a complete second partition:

```text
diag_plus_twos  = 13, 14, 15, 16, 17
diag_minus_twos = 12, 13, 14, 15, 16, 17
```

Thus every unresolved pair has exactly 30 count-profile children, for 2640
formal children in total.

## New pair-conditional certificate consequences

The global rational certificate has denominator 187 and target-34 slack 112.
After fixing the selected pair on `x=y`, the excess contributed by those two
points can be subtracted. The remaining certificate slack is pair-dependent
and lies between 53 and 112 for the 88 unresolved pairs.

This gives several exact strengthenings:

1. Every certificate line with weight greater than the pair residual must be
   saturated.
2. The remaining selected off-diagonal points obey the reduced excess budget.
3. For every positive threshold `q`, at most `floor(residual/q)` selected
   points can have certificate excess at least `q`.
4. If a weighted line contains zero, one, or two selected points, its line
   defect is respectively `2w`, `w`, or `0`. The sum of all four-direction
   weighted line defects is at most the pair residual.
5. Transposition fixes the selected main-diagonal pair and preserves both
   diagonal count parameters, so a lexicographic transpose symmetry break is
   valid at the count-profile level.

## Exact arithmetic prefilter

For each child, a small dynamic program minimizes the possible weighted line
defect separately over rows, columns, slope `+1` diagonals, and slope `-1`
diagonals. It respects:

- the exact diagonal counts;
- the fixed selected pair;
- every line already forced saturated by its weight;
- the complete row/column count ranges and `row_twos <= column_twos`.

If the resulting minimum exceeds the pair residual, the child is rigorously
`INFEASIBLE` without running CP-SAT.

Local enumeration shows that this arithmetic test reduces the 2640 formal
children to about 1130 children that require actual search. In particular,
`diag_plus_twos = 13` is impossible for every unresolved pair, and most
`diag_plus_twos = 14` cases are also eliminated.

## Local CP-SAT experiments

Short local tests used all 2455 maximal grid-line constraints plus the new
certificate cuts.

- A 1.5-second test over the five `diag_plus_twos` values for all 88 pairs
  strictly excluded 145 of the 440 pair/plus-count children.
- On the nine smallest-residual pairs, a five-second test over the admissible
  `(diag_plus_twos, diag_minus_twos)` combinations excluded 41 of 81 children.
- The difficult child `(pair index 2, plus=16, minus=15)` became `INFEASIBLE`
  in about nine seconds with four CP-SAT workers.

These tests are exploratory timing evidence. The public GitHub Actions run is
needed to save a complete independently reproducible record.

## Exact-pattern warning

Fixing a complete pattern of which slope `+1` diagonals are empty, singleton,
or saturated can be powerful. However, transposition sends a pattern at key
`k` to the pattern at key `-k`. Therefore the count-level transpose symmetry
break must not be copied blindly into a child with a non-invariant exact
pattern. Exact pattern children must either be canonicalized in transpose
orbits or be solved without that lexicographic constraint.

The current profile smoke fixes only the two invariant counts, so its transpose
symmetry break is safe.

## Prepared smoke run

Workflow:

```text
.github/workflows/n22-profile-children-smoke.yml
```

It covers all 2640 formal children exactly once across 20 shards. Arithmetic
children finish immediately; the remaining children receive 20 seconds and
four CP-SAT workers each. Expected wall time is roughly 15–25 minutes.

The run can:

- find and independently verify a 34-point configuration;
- close additional main-diagonal pairs;
- in the best case close all 88 pairs and prove `D_mono(22)=33`;
- otherwise produce an exact list of surviving profile children for the next
  pattern-level run.
