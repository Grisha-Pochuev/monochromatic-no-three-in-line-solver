# 20x20 attack round 10: full exact GitHub Actions launch

Date: 2026-07-10

The honest mathematical status before this run remains:

```text
30 <= D_mono(20) <= 31
```

## What is being launched

The existing exact reduction classifies every hypothetical 31-point solution by the two selected points on the forced-full main diagonal `x=y`.

After quotienting by 180-degree rotation, there are exactly 100 canonical cases. The one-shot workflow distributes them without overlap:

```text
20 GitHub Actions runners
5 exact cases per runner
4 CP-SAT workers per runner
3300 seconds per case
```

Thus every runner receives a different part of the complete search space. This is not twenty repetitions of the same random search.

## Interpretation of the result

The collector creates the artifact `n20-diagonal-pair-overall`.

- `FOUND_31_POINT_CONFIGURATION`: a configuration is independently checked and `D_mono(20)=31`.
- `PROVED_NO_31_BY_COMPLETE_PAIR_PARTITION`: all 100 cases are exactly infeasible and `D_mono(20)=30`.
- `INCOMPLETE_FRONTIER`: the artifact lists the exact cases that reached the time limit or were missing; all infeasible cases remain permanent certified progress.

## Launch mechanism

The workflow `.github/workflows/n20-diagonal-pair-proof-autostart.yml` is deliberately triggered only when `20x20/RUN_N20_DIAGONAL_PAIR_PROOF` changes on `main`. This prevents ordinary repository edits from accidentally starting another expensive full run.
