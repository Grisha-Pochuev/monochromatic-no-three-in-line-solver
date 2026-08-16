# Handoff: n=22 monochromatic no-three-in-line

Current certified board status remains

```text
33 <= D_mono(22) <= 34
```

Do **not** claim `D_mono(22)=33` yet.

All current work is on branch:

```text
webchat/n22-certificate-defect-2026-08-15
```

## Start here

Read `STATUS.md`, then the current frontier files in this order:

```text
weight22_frontier.py
weight15_frontier.py
weight8_frontier.py
weight8_tight_frontier.py
generate_refined_3_count_tight.py
verify_refined_3_count_tight.py
```

For the exact certificate identity also read:

```text
exact_identity.py
residual_tightening.py
```

## Proven progress

The original safe defect partition has 140 parents. Runs `31895454066` and
`31895926125` rigorously exclude 71, leaving 69. No unsafe transpose rule is
used.

The 69 parents split into 175 weight-35 cases. Run `31896568122` proved 24
UNSAT. The 16 exact Farkas cases from audit `31897006416` are **all contained
inside those 24**:

```text
Farkas indices:
11 12 13 14 94 95 96 97 98 99 131 132 133 134 135 136

intersection = 16
union        = 24
open         = 151
```

The 151 survivors were then refined only by certificate-defect structure:

```text
weight 24: 151 parents -> 261 children
run 31897269984: 17 UNSAT -> 244 open

weight 22: 244 parents -> 395 children
combined solver + exact Farkas + exact-identity union: 57 UNSAT -> 338 open
see weight22_frontier.py

weight 15: 338 parents -> 723 children
94 exact Farkas + 8 solver UNSAT -> 621 open
see weight15_frontier.py

weight 8: 621 parents -> 1943 children
474 exact Farkas UNSAT -> 1469 open
see weight8_frontier.py
```

The residual-tightened SAT run `31921064464` then processed exactly those
1,469 open weight-8 cases:

```text
12 UNSAT
1457 TIMEOUT
0 SAT
0 ERROR
```

The 12 exact open indices are:

```text
807 860 863 986 1125 1167 1169 1172 1180 1188 1190 1243
```

The exact result is committed in
`results/run-31921064464-overall-weight8-open-tight.json`, and the current
1,457-parent frontier is `weight8_tight_frontier.py`.

## Current frontier

The last positive certificate weight is 3, on exactly four lines:

```text
row 6, row 15, col 6, col 15
```

`generate_refined_3_count_tight.py` gives a complete disjoint count split of
the current 1,457 parents. Audit run `31948905325` passed:

```text
1457 parents -> 6676 children
k3=0: 1457
k3=1: 1457
k3=2: 1371
k3=3: 1261
k3=4: 1130
symmetry: none
```

After this level there are no unprocessed positive-weight certificate lines.
The 6,676 children are therefore the current exact computational frontier.
They are **not** yet all UNSAT.

## Best next step

Attack only these 6,676 weight-3 children. The most promising strict routes
are now:

1. scan them for LP infeasibility and rationalize every useful case into exact
   integer Farkas certificates;
2. run the residual-tightened exact-identity SAT encoding on the remaining
   children, preferably with proof traces for final survivors;
3. if more subdivision is necessary, split by exact zero occupancy / selected
   point cover excess, not by any unsafe symmetry rule.

Preserve the rigor rules: `TIMEOUT` is never proof; do not restore the old
transpose lex-leader; numerical infeasibility counts only after exact
certification; any SAT model must be independently checked as an actual
34-point configuration.
