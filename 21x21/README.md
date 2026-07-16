# 21x21 checkerboard no-three-in-line

Exact certified result:

```text
D_mono(21) = 32
```

The `21×21` case is closed.

## Lower bound

- `config_32.json` is a valid 32-point configuration on parity 1.
- The construction is invariant under 180-degree rotation.
- `verify_21x21.py` independently checks the board, parity, distinctness, rotational symmetry, size, and absence of three collinear selected points.

Run:

```bash
python 21x21/verify_21x21.py
```

## Upper bound

Every genuine no-three-in-line configuration has at most two selected points on each:

- row;
- column;
- diagonal of slope `+1`;
- diagonal of slope `-1`.

`prove_upper_21x21_four_direction.py` keeps only these necessary constraints. This is a relaxation of the full problem, so excluding 33 points in this weaker integer model is enough to exclude 33 points in the genuine problem.

The exact CP-SAT search was run separately for both checkerboard parities. Both searches returned `INFEASIBLE`:

```text
parity 0: INFEASIBLE, 37.31 seconds
parity 1: INFEASIBLE,  0.38 seconds
UNKNOWN:  0
```

Therefore no 33-point configuration exists. Together with `config_32.json`, this proves:

```text
D_mono(21) = 32
```

## Final proof record

- Workflow: `.github/workflows/n21-four-direction-proof.yml`
- GitHub Actions run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29531523646
- Human-readable summary: `runs/2026-07-16-run-29531523646/SUMMARY.md`
- Machine-readable result: `runs/2026-07-16-run-29531523646/overall.json`

## Why the professor's letter helped

Thomas Prellberg reported a 32-point example for `n=21` and said that searches among configurations with rotational symmetry were productive. That suggested separating the task into two simpler parts:

1. search directly for a rotationally symmetric 32-point construction;
2. test whether the four-direction integer relaxation alone already excludes 33.

Both steps succeeded. The lower configuration in this folder was found independently from the description in the letter; no coordinates were supplied in the correspondence.
