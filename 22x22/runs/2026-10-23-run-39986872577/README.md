# Run 39986872577 — n22 round 3 (141 gap children + 44 subcases of child 652)

Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/39986872577
Started 2026-10-23 21:16 MSK, **cancelled by the owner 2026-10-24 10:47 MSK** (24 jobs finished, 38 cancelled,
89 of 185 items never started). Archived 2026-10-27.

- `SUMMARY.md`, `overall.json`: the workflow collector. It reads only finished job summaries: 51 INFEASIBLE.
- `recount.json`: recount from every per-attempt JSON in all shard artifacts, including jobs cancelled mid-run:
  **58 INFEASIBLE (gap 50/141, child 652 8/44)**, FEASIBLE 0. Every INFEASIBLE is a completed CP-SAT proof on the
  unchanged engines (`prove_upper_22x22_profile_child_gap.py`, `prove_upper_22x22_child652_subcase.py`).
- `remaining_keys.txt`: 127 open items (91 gap children + 36 subcases of 652), from recount.json.
- `attempts.json`: every attempt.

Partition status: 1510 + 402 + 502 + 84 + 50 = **2548 / 2640 strict**. Open: 91 gap children and child 652
(27 of 63 subcases closed: 19 in round 2, 8 here). UNKNOWN is not a proof. Certified: 33 <= D_mono(22) <= 34.
