# 21x21 checkerboard no-three-in-line

Exact result:

```text
D_mono(21) = 32
```

## Lower bound

- `config_32.json` is a 32-point configuration on parity 1.
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

`prove_upper_21x21_four_direction.py` keeps only these necessary constraints. This is a relaxation of the full problem, so excluding 33 points in this weaker model is enough to exclude 33 points in the genuine problem.

The exact CP-SAT search is run separately for both checkerboard parities. A branch counts as proved only when the solver status is `INFEASIBLE`; `UNKNOWN` is explicitly treated as incomplete.

The reproducible GitHub Actions workflow is:

```text
.github/workflows/n21-four-direction-proof.yml
```

## Why the professor's letter helped

Thomas Prellberg reported a 32-point example for `n=21` and said that searches among configurations with rotational symmetry were productive. That suggested separating the task into two much simpler parts:

1. search directly for a rotationally symmetric 32-point construction;
2. test whether the four-direction integer relaxation alone already excludes 33.

Both steps succeed. The lower configuration in this folder was found independently from the description in the letter; no coordinates were supplied in the correspondence.
