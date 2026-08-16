# n=22 certificate-defect frontier — updated 2026-08-16

This file records the current symmetry-safe target-34 attack. Nothing here
changes the certified board status until the complete frontier is excluded.

## Board status

```text
33 <= D_mono(22) <= 34
```

The 33-point construction remains `22x22/config_33.json`. The rational
four-direction certificate `22x22/upper_certificate_34_four_direction.json`
has denominator 187, objective numerator 6470, and target-34 slack 112.

## Heavy-line parent partition

`generate_branch.py` and `verify_partition.py` give a complete 140-case
partition by the actual underfull subset among certificate lines of weight at
least 40. No transpose lex-leader or row/column orientation assumption is
used.

Run `31895454066`:

```text
140 / 140 records
64 UNSAT
76 TIMEOUT
0 SAT
0 ERROR
```

The exact-defect follow-up run `31895926125` proved seven more parents UNSAT:

```text
41 47 55 67 98 104 123
```

Thus 71/140 original parent cases are rigorously excluded and 69 survive.

## Weight-35 refinement and Farkas overlap

The 69 surviving parents split completely by the four weight-35 lines
`row 2`, `row 19`, `col 2`, `col 19` into 175 refined cases.

Run `31896568122`:

```text
175 / 175 records
24 UNSAT
151 TIMEOUT
0 SAT
0 ERROR
```

Solver-UNSAT refined indices:

```text
11 12 13 14 66 67 68 69 75 76 77 78 94 95 96 97 98 99 131 132 133 134 135 136
```

The independent exact integer Farkas audit `31897006416` covers exactly these
16 refined indices:

```text
11 12 13 14 94 95 96 97 98 99 131 132 133 134 135 136
```

Therefore the Farkas set is a subset of the 24 solver-UNSAT cases:

```text
intersection = 16
union        = 24
survivors    = 151
```

The Farkas certificates independently confirm 16 solver exclusions but do not
reduce the 151-case remainder further.

## Weight-24 count refinement

The six next certificate lines of weight 24 are:

```text
row 3, row 18, col 3, col 18, diff -16, diff 16
```

`generate_refined_24_count.py` splits the 151 survivors by the exact number of
these six lines that are underfull, giving 261 complete children.

Run `31897269984` proved 17 children UNSAT and left 244 TIMEOUT; no SAT case
was found. The exact closed child indices are stored in
`generate_refined_22_count.py`.

## Weight-22 frontier

The only weight-22 certificate lines are `sum=6` and `sum=36`. The 244
weight-24 survivors split into 395 complete weight-22 children.

The rigorous union of three independent exclusion sources is recorded in
`weight22_frontier.py`:

- run `31918747065`: 43 solver-UNSAT, 352 TIMEOUT, no SAT;
- exact integer Farkas audit `31919145658`: 39 Farkas-UNSAT, with 38 overlapping
  the first solver set and one Farkas-only child;
- exact-identity run `31918874582`: 55 solver-UNSAT, adding 13 new children
  beyond the preceding union.

After taking the exact union, **57/395 weight-22 children are rigorously closed
and 338 remain open**.

The strengthened formulas use the exact certificate identity

```text
D + E = 112
```

where `D` is line defect and `E` is selected-point cover excess. The lower
half of this equality is encoded by `exact_identity.py`; its weighted-threshold
encoding was exhaustively audited successfully in run `31897447939`.

## Weight-15 frontier

The 338 open weight-22 parents split by the exact number of underfull weight-15
lines (`row/col 4` and `row/col 17`) into 723 complete children.

`weight15_frontier.py` records:

- exact Farkas audit run `31919694722`: 94 children closed;
- solver run `31919924181` on the remaining children: 8 additional UNSAT,
  621 TIMEOUT, no SAT.

The two sets are disjoint by construction. Therefore **102/723 are closed and
621 remain open**.

## Weight-8 frontier

The 621 open weight-15 parents split by the exact number of underfull weight-8
lines into 1,943 complete children.

Exact integer Farkas audits, all without symmetry, closed:

```text
k8=4:  95   run 31919955840
k8=3: 134   run 31920209088
k8=2: 142   run 31920410133
k8=1: 103   run 31920752842
k8=0:   0   run 31920859228
```

Thus **474/1,943** are rigorously Farkas-UNSAT and 1,469 remained open at this
stage. This state is encoded in `weight8_frontier.py`.

## Residual-tightened weight-8 SAT run

`residual_tightening.py` adds only consequences of the exact remaining defect
budget. Run `31921064464` processed exactly the 1,469 rigorous-open weight-8
children with this tightened encoding:

```text
1469 / 1469 records
12 UNSAT
1457 TIMEOUT
0 SAT
0 ERROR
```

The 12 UNSAT indices in `generate_weight8_open_tight.OPEN_TRIPLES` are:

```text
807 860 863 986 1125 1167 1169 1172 1180 1188 1190 1243
```

The compact machine-readable result is committed as
`results/run-31921064464-overall-weight8-open-tight.json`. The current exact
1457-parent frontier is encoded in `weight8_tight_frontier.py`.

Its remaining k8 distribution is:

```text
k8=0: 619
k8=1: 435
k8=2: 232
k8=3: 112
k8=4:  59
```

## Final positive-weight split: weight 3

The only positive certificate lines not yet explicitly processed are:

```text
row 6, row 15, col 6, col 15
```

all of weight 3. `generate_refined_3_count_tight.py` splits each of the 1,457
current parents by the exact number `k3=0..4` of these lines that are
underfull, subject only to the remaining defect budget. After this split no
unprocessed positive-weight certificate line remains.

Audit run `31948905325` completed successfully:

```text
parents:  1457
children: 6676
k3=0:     1457
k3=1:     1457
k3=2:     1371
k3=3:     1261
k3=4:     1130
symmetry: none
```

The same audit also rechecked the residual-tightening arithmetic for every
residual `R=0..112` and all positive certificate weights.

**These 6,676 weight-3 children are the current complete rigorous frontier.**
They have been partitioned and audited, but have not yet all been proved
UNSAT. Hence the board is not closed yet.

## Current continuation point

Start with `HANDOFF.md`. The next attack should operate only on the 6,676
children generated by `generate_refined_3_count_tight.py`. Since weight 3 is
the last positive certificate level, further refinement should use exact
zero-occupancy charges, selected-point cover excess, exact Farkas certificates,
or proof-producing SAT runs rather than another positive-weight line level.

## Rigor rules

- `SAT` would require independent checking as a valid 34-point construction.
- `TIMEOUT` / `UNKNOWN` is never a proof and always remains in the frontier.
- The old unconditional transpose lex rule is forbidden.
- No result above uses that unsafe transpose pruning.
- Numerical LP infeasibility counts only after exact rational/integer
  certification.
- Final publication-quality closure should replay all final UNSAT leaves with
  proof traces and an independent checker.
