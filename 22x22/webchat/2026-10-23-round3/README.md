# n=22 round 3: 141 gap survivors + 44 open subcases of child 652

Date: 2026-10-23. Workflow `.github/workflows/n22-round3-185-60x5h40.yml`, trigger `22x22/RUN_N22_ROUND3_185_60X5H40`.

Change vs round 2: **60 jobs** in one run (max-parallel 20, so three waves, ~17–18 h of wall time), ~3 items per job.
So every item gets one long first attempt of about 5000–6800 s instead of ~1300–2100 s. Restarts lose learned clauses,
so a long single attempt is the point. Models and engines are unchanged
(`prove_upper_22x22_profile_child_gap.py`, `prove_upper_22x22_child652_subcase.py`), ortools==9.15.6755, 4 workers.
Schedule `round3_schedule.json` = `runs/2026-10-10-run-38052679030/remaining_keys.txt` round-robin over 60 jobs.
Runner `run_n22_round3_shard.py` (round-2 runner, new schedule, seed base 2026102300); collector `collect_n22_round3.py`.

UNKNOWN is not a proof.
