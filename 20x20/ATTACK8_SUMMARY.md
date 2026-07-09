# 20x20 attack round 8

Status: not closed. Honest bound remains:

```text
30 <= D_mono(20) <= 31
```

Input state: `n20_attack_round7.zip` / `ATTACK7_SUMMARY.md`.

Round 7 coarse frontier:

```text
total proof-front leaves: 19632
closed after round 7: 15731
open after round 7: 3901
coverage after round 7: 80.1%
```

Previous chat step after round 7 had already reported +242 closed leaves, bringing coverage to about 81.36%.

This round used the same LP leaf model but increased recursive branching depth on the remaining open leaves:

- `T=2`, branch depth 4: 31 leaves closed from the round7 state.
- `T=3`, branch depth 4: 436 leaves closed from the round7 state.
- `T=0` and `T=1`: no closure found by this LP branching layer.
- `T=4`: not processed, because the round7 zip does not contain the decoded list of 753 hard T=4 leaves.

Total newly certified closed leaves relative to round7:

```text
31 + 436 = 467
```

Accounting relative to round7:

```text
closed: 15731 + 467 = 16198
open:   19632 - 16198 = 3434
coverage: 16198 / 19632 = 82.5081499592502%
```

Increment relative to the previous chat status (`~81.36%`):

```text
+225 leaves
+1.146 percentage points
```

Remaining open mass after this round:

```text
T=0: 1
T=1: 42
T=2: 688
T=3: 1950
T=4: 753

Total open: 3434
```

A short local C++ min-conflicts search for a 31-point configuration was also tried. It did not find a valid 31-point configuration; the best observed near-configuration in that short run had violation cost 2. This is only search evidence, not a proof.

Best next work:

1. Recover or regenerate the explicit T=4 hard-leaf list.
2. Continue T=3 with stronger branching / learned cuts.
3. Try exact CP-SAT/PySAT leaf closers outside this limited web-chat environment.
4. Keep the bound honest: the case is not solved until either a 31-configuration is found or all 31 branches are certified impossible.
