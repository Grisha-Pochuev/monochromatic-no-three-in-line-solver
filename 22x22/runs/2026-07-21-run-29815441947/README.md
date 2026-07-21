# GitHub Actions run 29815441947

Source: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29815441947

Overall artifact: `n22-profile-dynamic-overall`, id `8498787371`, SHA-256 `ba5d3c22821d096167f23b0d365c7a3ecabe612f9d2090a9a15527e91c6963bf`.

This run processed exactly the 56 exact profile children left by run `29795643015`.

- `INFEASIBLE`: 46
- `UNKNOWN`: 10
- `FEASIBLE`/`OPTIMAL`: 0
- missing/duplicate/unexpected/model-invalid: 0
- technical records: 0
- memory-guard records: 0
- newly closed main-diagonal pairs: 20
- remaining main-diagonal pairs: 10
- remaining exact children: 10
- cumulative exact exclusions: 2630 / 2640
- solver work in this run: 78.51 job-hours

Files:

- `overall.json` — independently regenerated machine-readable aggregate;
- `SUMMARY.md` — independently generated collector summary;
- `shards/` — all twenty shard records, machine reports, and minute-by-minute memory logs;
- `job-logs/` — downloaded GitHub Actions job logs.

Independent lower-bound check:

```bash
python 22x22/verify_22x22.py
```

`UNKNOWN` records are not treated as a proof.
