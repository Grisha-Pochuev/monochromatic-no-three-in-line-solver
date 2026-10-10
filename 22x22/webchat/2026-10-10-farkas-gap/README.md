# n=22: exact Farkas certificates and the complementary-orientation (gap) run

Date: 2026-10-10

## 1. 402 new strict exclusions

`farkas_child.py` builds the linear relaxation of the **symmetry-safe** profile-child model
(all maximal lines, rational certificate 6470/187 with excess/defect constraints, 0/1/2 occupancy
states, diagonal profiles, `row_twos <= column_twos`, **no lexicographic cut**).
For LP-infeasible children a HiGHS dual ray is rounded to rationals; any nonnegative multipliers with
positive exact margin are a valid Farkas certificate, so rounding needs no exactness.

`farkas_reopened_402.jsonl.gz` closes **402 of the 1130** children reopened by the symmetry audit.

```bash
python verify_farkas_402.py   # {"verified": 402, "failed": []}
```

Status inside the 2640-child partition: 1510 analytic + 402 Farkas = 1912 strict; 728 open
(727 below + child 652).

## 2. Gap lemma

Let base be the safe child model. It is invariant under transposition T (diagonal pair fixed,
diagonal profiles preserved, certificate weights symmetric).
Old runs proved `O = base & r<=c & above <=lex below` INFEASIBLE for all 727 children.
If `x` is in `base & r<=c` but not in `O`, then `r<c` (for `r=c`, `T(x)` lies in `O`) and `above >lex below`.
Hence it suffices to prove

```text
G = base & row_twos < column_twos & below <=lex above   is INFEASIBLE.
```

Engine: `22x22/prove_upper_22x22_profile_child_gap.py`.

## 3. Run

`gap_schedule.json` — 727 children in 20 shards. Workflow `.github/workflows/n22-gap-727-5h50.yml`,
trigger `22x22/RUN_N22_GAP_727_5H50`. Phase A: 120 s per child; phase B: remaining time on survivors.
UNKNOWN is not a proof. Certified status stays `33 <= D_mono(22) <= 34` until all 728 are closed.
