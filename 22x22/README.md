# 22x22 checkerboard no-three-in-line

Current certified lower bound:

```text
D_mono(22) >= 33
```

`config_33.json` is an independently found valid 33-point configuration on parity 0. Run:

```bash
python 22x22/verify_22x22.py
```

The exact upper proof targets 34 points and uses every grid line containing at least three allowed points. For even board size the two colors are congruent by reflection, so only parity 0 must be proved. The search is partitioned by the numbers of rows and columns containing exactly two selected points. Transposition reduces the full 36 count pairs to 21 cases.

Files:

- `config_33.json` — lower construction;
- `verify_22x22.py` — independent construction verifier;
- `prove_upper_22x22_partition.py` — exact CP-SAT partition solver;
- `.github/workflows/n22-exact-proof.yml` — public reproducible proof run.

The folder must be marked closed only after every one of the 21 upper-bound partitions returns `INFEASIBLE`; `UNKNOWN` is not a proof.
