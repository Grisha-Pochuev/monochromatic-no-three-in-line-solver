# Run 38029269220 — n22 gap run (727 children)

Workflow: `.github/workflows/n22-gap-727-5h50.yml` (20 shards × 5h40, ortools==9.15.6755).
Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/38029269220
Date: 2026-10-10, concluded `success`.

Model G = safe base & `row_twos < column_twos` & `below <=lex above`
(`22x22/prove_upper_22x22_profile_child_gap.py`, see `22x22/webchat/2026-10-10-farkas-gap/README.md`).

## Result

- expected / collected: 727 / 727, missing 0
- INFEASIBLE: **502**
- FEASIBLE (34 points): 0
- remaining (UNKNOWN only, no memory-guard or technical failures): **225**

By the complementary-orientation lemma, INFEASIBLE(G) together with the historical INFEASIBLE(O)
gives INFEASIBLE of the symmetry-safe child model. Hence these 502 children are strictly closed.

## Files

- `SUMMARY.md`, `overall.json` — collector output (artifact `n22-gap-overall`).
- `remaining_children.txt` — the 225 open child ids.
- `attempts.json` — every attempt per child (tag, status, time, seed, branches, conflicts, peak RSS).
- `shard_summaries.json` — per-shard child lists and final statuses.

Observed: INFEASIBLE times median 155 s, 90% ≤ 475 s, max 1085 s; peak RSS 256 MB with 4 workers.
Survivors received 828–3214 s of total solver time (median 1102 s) split over several attempts.

## Partition status after this run (2640 children)

1510 analytic + 402 exact Farkas + 502 gap-run = **2414 strict**; open: 225 gap children + child 652.
UNKNOWN is not a proof. Certified status: `33 <= D_mono(22) <= 34`.
