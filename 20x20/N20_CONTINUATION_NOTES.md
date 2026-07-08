# N20 continuation notes

This continuation used the added project research note and switched from pure local repair to CP-SAT feasibility search.

Confirmed:

- Found a clean 30-point configuration for `20x20`, parity 0.
- Verified directly: all points are on the board, in one parity class, and no three selected points are collinear.
- Built a rational four-direction LP dual certificate with upper bound `15717979/500000 < 32`.

Current frontier:

```text
30 <= D_mono(20) <= 31
```

Unresolved:

- CP-SAT did not decide target 31 inside the short local runs available here.
- Next hard step is either find a 31-point configuration or produce a reproducible infeasibility proof/certificate for 31.
