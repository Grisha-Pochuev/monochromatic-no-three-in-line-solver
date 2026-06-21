# 18x18 status

Current status: not closed.

Known rigorous bounds recorded for this package:

```text
27 <= D_mono(18) <= 28
```

What is already included here:

- a verified 27-point construction on parity 0;
- two 28-point near misses with conflict objective 2;
- CP-SAT feasibility search for a 28-point configuration;
- CP-SAT minimum-conflict search for 28 points;
- HiGHS MILP feasibility search;
- exact row-by-row C++ DFS with optional sharding;
- local swap search.

Initial focused run summary:

- HiGHS MILP, 300 seconds: no feasible 28-point solution found, no proof of infeasibility.
- CP-SAT feasibility, 300 seconds: status UNKNOWN.
- CP-SAT minimum conflict, 300 seconds: found a 28-point near miss with objective 2.
- C++ DFS: more than 133 million nodes explored before interruption, no 28-point solution found, not exhaustive.
- Local swap: best conflict count 2, no valid 28-point configuration found.

Interpretation: evidence currently points toward `D_mono(18)=27`, but this is not yet a proof. Closing the case requires either a complete exhaustive search/certificate excluding 28, or a valid 28-point construction.
