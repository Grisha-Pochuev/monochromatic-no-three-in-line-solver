# N20 continuation notes

This file is the working memory for the unresolved `20x20` monochromatic no-three-in-line case.

Repository state before this note:

```text
30 <= D_mono(20) <= 31
```

The case is **not closed**.  The only remaining mathematical question is still:

```text
Does a 31-point monochromatic no-three-in-line configuration exist on 20x20?
```

## Already certified before the continuation

- A clean 30-point configuration for `20x20`, parity 0, is stored in `config_30.json`.
- `verify_20x20.py` verifies the board size, parity class, duplicate absence, and no-three-collinear condition for the 30-point configuration.
- The intended upper-bound side is `D_mono(20) <= 31` via a rational LP dual certificate.

## Local continuation attack, 2026-07-08 / 2026-07-09

Scope of this continuation:

- local computation only;
- no GitHub Actions run;
- no claim that `20x20` is solved;
- target was `31`, not rediscovering `30`.

The parity-0 model was rebuilt locally:

```text
points = 200
lines with >=3 parity-0 points = 1717
target = 31
```

## Strict exclusions obtained locally

The committed 30-point configuration is locally tight: simply adding one outside point always creates line violations.

More importantly, exact CP-SAT neighborhood checks gave the following working exclusions.

Any true 31-point solution, if it exists, must satisfy:

```text
overlap(config_30) <= 19
```

So a 31-point solution is not a small repair of the known 30-point configuration.

A C++ local search then found a 31-point near-configuration with one bad line, the main diagonal `x = y` containing five chosen points:

```text
(13,13), (14,14), (15,15), (17,17), (18,18)
```

Exact CP-SAT neighborhood checking proved that no true 31-point solution can share 20 or more points with this near-configuration:

```text
overlap(near31_diag5_candidate) <= 19
```

A later C++ run found another diverse 31-point near-configuration with only two bad lines and overlap 10 with `config_30`:

```json
[[0,6],[0,12],[1,3],[1,17],[2,10],[2,14],[3,1],[3,7],[4,12],[4,18],[5,3],[5,19],[6,0],[6,16],[8,0],[8,2],[9,5],[9,13],[12,8],[12,18],[13,1],[13,13],[14,16],[16,2],[16,4],[17,17],[17,19],[18,8],[18,10],[19,5],[19,9]]
```

Its two bad lines were:

```text
x - y + 2 = 0:
  (1,3), (14,16), (17,19)

x + y - 22 = 0:
  (4,18), (6,16), (9,13)
```

CP-SAT proved the full neighborhood exclusion around this candidate:

```text
k=31 INFEASIBLE
k=30 INFEASIBLE
...
k=20 INFEASIBLE
```

Thus any true 31-point solution must also satisfy:

```text
overlap(near31_two_bad_lines_candidate) <= 19
```

Current useful exclusions after this continuation:

```text
Any true 31-point solution must have:
  overlap(config_30) <= 19
  overlap(near31_diag5_candidate) <= 19
  overlap(near31_two_bad_lines_candidate) <= 19
```

## Portfolio searches that did not close the case

Several exact/search runs were tried after adding the known no-good neighborhoods.

They did **not** find a 31-point configuration and did **not** prove infeasibility:

```text
CP-SAT without LP implications: UNKNOWN after about 120s
CP-SAT with LP-derived implications: UNKNOWN after about 120s
PySAT/CaDiCaL with LP implications: UNKNOWN after 1,000,000 conflicts
DFS-style column search: timed local run, no solution found in that slice
```

These are search diagnostics only, not mathematical proof.

## Round 7 / 8 proof-front status, 2026-07-09

A later proof-front attack split the remaining 31-point impossibility attempt into `T`-families and applied LP leaf closing.

Round 7 coarse frontier:

```text
total proof-front leaves: 19632
closed after round 7: 15731
open after round 7: 3901
coverage after round 7: 80.1%
```

After additional LP branching from the same round7 state, round 8 reached:

```text
closed: 16198
open:   3434
coverage: 82.5081499592502%
```

Newly certified closed leaves relative to round7:

```text
T=2: 31 leaves closed by branch depth 4
T=3: 436 leaves closed by branch depth 4
T=0: no new closure
T=1: no new closure
T=4: not processed, because the explicit 753 hard-leaf list was not available in the round7 package
```

Remaining open mass after round 8:

```text
T=0: 1
T=1: 42
T=2: 688
T=3: 1950
T=4: 753

Total open: 3434
```

A short local C++ min-conflicts run also searched for a valid 31-point configuration. It did not find one; the best observed near-configuration in that short run had violation cost 2. This is only search evidence, not a proof.

See also: `ATTACK8_SUMMARY.md`.

## Certificate caution

During the local continuation, the stored `upper_certificate_31.json` was re-inspected and appeared suspicious under the current verifier convention.

Local check of the stored weights suggested:

```text
2 * sum(stored weights) did not match the declared upper_bound
some parity-0 points appeared to have cover < 1
```

A replacement all-line LP dual candidate was generated locally with:

```text
denominator = 1000000
nonzero weights = 65
min cover = 1000001/1000000
upper = 31433544/1000000 = 31.433544 < 32
```

This suggests the upper side `D_mono(20) <= 31` is repairable, but the committed certificate should be rechecked carefully before relying on it as a formal artifact.

Do **not** treat this note as a final certificate replacement.  The right next engineering step is to add a clean verifier-compatible replacement certificate and run `python 20x20/verify_20x20.py`.

## Interpretation

The search did not solve the case, but it changed the working picture.

A true 31-point configuration, if it exists, is not close to any of the three known good/near-good basins above.  The problem has moved away from “patch the known 30” and toward either:

```text
A. finding a rare, distant 31-point structure;
B. proving globally that 31 is impossible, giving D_mono(20) = 30.
```

Round 8 adds a more precise proof-front picture: the proof has reached about 82.5% coverage, but the remaining 17.5% is concentrated in hard branches, especially `T=3`, `T=4`, and the small but stubborn `T=0/T=1` cases.

## Recommended next work

Most useful next steps:

1. Recover or regenerate the explicit `T=4` hard-leaf list.
2. Continue `T=3` with stronger branching / learned cuts.
3. Try exact CP-SAT/PySAT leaf closers outside this limited web-chat environment.
4. Fix or replace `upper_certificate_31.json` with the verifier-compatible all-line LP dual certificate.
5. Keep collecting diverse near-31 candidates with low overlap against known basins.
6. For each near-31 candidate, run exact CP-SAT neighborhood exclusions `overlap >= k` downward.
7. Build a portfolio proof attempt using all proven dead-basin inequalities.
8. If local search keeps returning `UNKNOWN`, move from ad hoc runs to a reproducible sharded infeasibility proof for `target = 31`.

What not to do next:

- Do not call the case solved as `D_mono(20)=30`.
- Do not call the case solved as `D_mono(20)=31`.
- Do not spend main effort rediscovering 29 or 30.
- Do not treat “solver did not find 31” as a proof.
