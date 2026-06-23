# 18x18 status

Current status: closed in this repository record.

Exact value recorded after the `n18 search` GitHub Actions recalculation:

```text
D_mono(18) = 27
```

Equivalently, the recorded bounds now meet:

```text
27 <= D_mono(18) <= 27
```

What is already included here:

- a verified 27-point construction on parity 0;
- two 28-point near misses with conflict objective 2;
- CP-SAT feasibility search for a 28-point configuration;
- CP-SAT minimum-conflict search for 28 points;
- HiGHS MILP feasibility search;
- exact row-by-row C++ DFS with optional sharding;
- local swap search;
- the GitHub Actions workflow `.github/workflows/n18-search.yml` for reproducing the recalculation.

Earlier focused run summary:

- HiGHS MILP, 300 seconds: no feasible 28-point solution found, no proof of infeasibility.
- CP-SAT feasibility, 300 seconds: status UNKNOWN.
- CP-SAT minimum conflict, 300 seconds: found a 28-point near miss with objective 2.
- C++ DFS: more than 133 million nodes explored before interruption, no 28-point solution found, not exhaustive.
- Local swap: best conflict count 2, no valid 28-point configuration found.

Updated interpretation after the GitHub Actions recalculation: the `18x18` case is recorded as closed with exact value `27`. The 27-point lower-bound configuration is stored in `18x18/data/lower_bound_27.json`, and the exclusion of a 28-point configuration is tied to the reproducible `n18 search` workflow and its run artifacts/logs.
