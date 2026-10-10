# n=22 round 2: 225 gap survivors + child 652 in 63 subcases

Date: 2026-10-10. Workflow `.github/workflows/n22-round2-288-5h40.yml`, trigger `22x22/RUN_N22_ROUND2_288_5H40`.
20 shards × 5h40, ortools==9.15.6755, 4 workers.

## Items (`round2_schedule.json`, 288 items, LPT-balanced by weight)

1. 225 gap children (`22x22/runs/2026-10-10-run-38029269220/remaining_children.txt`), model G
   (`prove_upper_22x22_profile_child_gap.py`), weight 1.
2. Child 652 (pair (2,2),(3,3), diag twos 16/16) split into 63 disjoint subcases, weight 1.5,
   engine `prove_upper_22x22_child652_subcase.py`:
   - `sum(row_twos)=r`, `sum(column_twos)=c`, `12 <= r <= c <= 17` (21 pairs; covers the safe base which
     already has 12..17 and r <= c);
   - `A = a`, `a in {0,1,2}`, A = selected points with `x-y in {-2,2}`, `x+y in {16,...,26}`;
     coverage by the exact certificate `A <= 803/273` (`webchat/2026-07-23-certificate-lp-triage/`);
   - symmetry: `r < c` — no lex cut; `r = c` — conditional lex `above <=lex below` (T maps the
     subcase (r,r,a) onto itself, so the cut is sound).

## Scheduler (`run_n22_round2_shard.py`)

Round 1: one long attempt per item with budget `(time left) × w / (weight of untried items)` —
about 1275 s per gap child and ~1900 s per 652 subcase at start, more when earlier items close.
Later rounds: survivors share the rest with fresh seeds (seed base 2026101100).
Collector `collect_n22_round2.py` requires all 288 keys exactly once and validates any solution.

## Note on the A-bound verifier

The committed `verify_a_bound_803_273.py` subtracted the lower-bound multipliers (`x >= 0`, `m >= 0`)
and therefore failed. The correct aggregation adds `m*x >= 0`; with this sign fix the certificate
verifies exactly (`-273*A >= -803`). Only valid inequalities are combined (line `<= 2` with m <= 0,
equalities total=34 and fixed main diagonal, `0 <= x <= 1`), so `A <= 2` holds.

UNKNOWN is not a proof.
