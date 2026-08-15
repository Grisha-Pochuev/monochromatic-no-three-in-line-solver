# n=22 certificate-defect frontier — 2026-08-15

This file records the current symmetry-safe target-34 attack.  Nothing here
changes the certified board status until the complete frontier is excluded.

## Board status

```text
33 <= D_mono(22) <= 34
```

The 33-point construction remains `22x22/config_33.json`.  The rational
certificate `22x22/upper_certificate_34_four_direction.json` has denominator
187, objective numerator 6470, and target-34 slack 112.

## Complete 140-branch defect partition

`generate_branch.py` and `verify_partition.py` give a complete partition by
the actual underfull subset among the 37 certificate lines of weight at least
40.  Three lines of weights 115, 117, 115 are forced saturated; among the
other 34 heavy lines at most two can be underfull.  Exactly 140 cases result.
No transpose lex-leader or row/column orientation assumption is used.

Run `31895454066` returned:

```text
records: 140 / 140
UNSAT:   64
SAT:      0
TIMEOUT: 76
ERROR:    0
```

The 64 exact solver exclusions are:

```text
14 15 27 28 35 36 37 38 39 40 42 44 45 48 50 51 54 57 58 61 63 64
68 70 71 72 73 74 75 76 77 78 79 80 81 83 85 86 89 90 92 94 95 99
101 102 103 105 106 110 111 114 117 118 119 120 121 126 127 131 132
135 137 138
```

## Exact-defect follow-up

`generate_branch_exact.py` distinguishes occupancy 2/1/0 on certificate
lines and couples exact line defect with selected-point cover excess.
Run `31895926125` processed the 76 previous survivors and returned:

```text
records: 76 / 76
UNSAT:    7
SAT:      0
TIMEOUT: 69
ERROR:    0
```

Newly closed parent branches:

```text
41 47 55 67 98 104 123
```

Therefore 71 of the original 140 parent branches are now solver-excluded and
69 parent branches remain computationally open.

## Weight-35 refinement

The only additional certificate lines of weight exactly 35 are:

```text
row 2, row 19, column 2, column 19
```

The original 76-parent refinement had 182 complete children.  Removing the
seven newly proved-UNSAT parents leaves 69 parents and 175 complete refined
cases.  `generate_refined_35_v2.py` uses the latest stronger encoding,
including:

- exact occupancy-2 and occupancy-0 flags;
- exact parallel-family incidence identities;
- residual-defect implications;
- point-excess threshold cuts;
- the already proved contiguous 17x17..21x21 upper bounds;
- the coupled certificate defect/excess budget.

The strengthened 175-case workflow is run `31896568122`.

## Exact Farkas exclusions inside the refinement

A numerical LP scan of the 175 weight-35 cases found 16 infeasible cases.
These were rationalized exactly.  `verify_farkas_16.py` stores five integer
Farkas representatives and transports them only by parity-preserving board
symmetries.  The verifier uses integer arithmetic and the Python standard
library only.

The 16 refined cases covered are the four cases where exactly three of
`row2,row19,col2,col19` are underfull with no old >=40 underfull line, plus
all twelve cases where `sum=8` or `sum=34` is underfull together with exactly
two of those four weight-35 lines.

The independent audit workflow is run `31897006416`.

## Rigor rules

- `SAT` would have to be independently checked as a 34-point construction.
- `TIMEOUT` / `UNKNOWN` is never a proof.
- The old unconditional transpose lex rule remains forbidden.
- Numerical LP infeasibility is not counted unless rationalized and checked
  exactly; the 16 cases above have such integer Farkas certificates.
- A final publication-quality closure should replay the final UNSAT leaves
  with proof traces and an independent proof checker.
