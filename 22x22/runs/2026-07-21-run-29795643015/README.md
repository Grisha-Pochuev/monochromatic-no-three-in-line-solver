# GitHub Actions run 29795643015

Source: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29795643015

Overall artifact: `n22-profile-followup-overall`, id `8487282032`, SHA-256 `27ad3c719b58312573f0dbba1ec9b113b4d27437b06c8eb9e6d11d9538c12cb4`.

This run reprocessed exactly the 170 exact profile children left by run `29770927206`.

- `INFEASIBLE`: 114
- `UNKNOWN`: 56
- `FEASIBLE`/`OPTIMAL`: 0
- missing/duplicate/unexpected/model-invalid: 0
- technical records: 0
- memory-guard records: 0
- newly closed main-diagonal pairs: 23
- remaining main-diagonal pairs: 30
- remaining exact children: 56
- cumulative exact exclusions: 2584 / 2640
- solver work in this run: 81.51 job-hours

Files:

- `overall.json` — complete machine-readable aggregate;
- `SUMMARY.md` — independently generated collector summary;
- `shards/` — all shard records, machine reports, and minute-by-minute memory logs;
- `job-logs/` — downloaded GitHub Actions job logs.

Independent lower-bound check:

```bash
python 22x22/verify_22x22.py
```

`UNKNOWN` records are not treated as a proof.
