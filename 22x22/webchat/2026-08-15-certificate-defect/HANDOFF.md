# Handoff: n=22 monochromatic no-three-in-line

Current certified board status remains

```text
33 <= D_mono(22) <= 34
```

Do **not** claim `D_mono(22)=33` yet.

## Start here

Read `STATUS.md`, then:

- `verify_partition.py`
- `generate_branch.py`
- `generate_branch_exact.py`
- `generate_refined_35_v2.py`
- `verify_farkas_16.py`

All work is on branch `webchat/n22-certificate-defect-2026-08-15`.

## Proven progress

The rational four-direction certificate has denominator 187, numerator 6470 and target-34 defect budget 112.  It yields a symmetry-safe complete partition into 140 parent cases; no transpose lex-leader is used.

Run `31895454066`: 140/140 processed, 64 UNSAT, 76 TIMEOUT, 0 SAT, 0 ERROR.

The exact-defect follow-up run `31895926125` closed seven more parent cases (`41 47 55 67 98 104 123`).  Therefore **71/140 parent cases are excluded and 69 parent cases remain**.

Those 69 parents are refined by the four weight-35 certificate lines (`row 2`, `row 19`, `col 2`, `col 19`) into **175 complete refined cases**.

Strengthened run `31896568122` completed successfully:

```text
175 / 175 records
24 UNSAT
151 TIMEOUT
0 SAT
0 ERROR
```

UNSAT refined indices:

```text
11 12 13 14 66 67 68 69 75 76 77 78 94 95 96 97 98 99 131 132 133 134 135 136
```

The raw summary is committed at `results/run-31896568122-overall-refined35-v2.json`.

Separately, `verify_farkas_16.py` gives exact integer Farkas certificates for 16 refined cases.  Audit run `31897006416` completed successfully.  These are proof-quality exclusions independent of SAT solving.  Before quoting a single final count of open refined leaves, explicitly compute the overlap between these 16 Farkas cases and the 24 SAT-solver UNSAT indices.

## Best next step

1. Compute the exact union of the 24 solver-UNSAT refined cases and the 16 exact-Farkas cases.
2. Produce the exact remaining refined-case list.
3. Attack only that remainder, preferably by further **certificate-defect** subdivision rather than returning to the old pair-on-main-diagonal partition.
4. Preserve the rigor rule: `TIMEOUT` is not a proof; avoid the old transpose symmetry bug; rationalize any LP exclusion exactly.
5. For final closure, replay all remaining UNSAT leaves with proof traces and an independent checker.
