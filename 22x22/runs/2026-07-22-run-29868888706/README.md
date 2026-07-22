# GitHub Actions run 29868888706

Source: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29868888706

Overall artifact: `n22-final-two-overall`, artifact id `8516897994`, SHA-256 `8160e67070ea1428c90a20876313adfd52da843ceff78d466e05a8243fbd6ef0`.

The run executed twenty independent full-budget attempts over the final two exact profile children: ten attempts per child. The complete aggregate contains all 20 expected records and has no missing, duplicate, unexpected, contradictory, invalid-model, technical, or memory-guard records.

- child `652`: 10 × `UNKNOWN`;
- child `1132`: 5 × `INFEASIBLE`, 5 × `UNKNOWN`;
- exact selected status of child `1132`: `INFEASIBLE`;
- exact selected status of child `652`: `UNKNOWN`;
- cumulative exact exclusions: 2639 / 2640;
- sole remaining exact child: `652`, main-diagonal pair `40`;
- solver work: 104.30 job-hours.

One exact `INFEASIBLE` result is sufficient to exclude an entire child, regardless of the other randomised attempts. Therefore child `1132` is permanently closed. `UNKNOWN` is not a proof, so the certified status remains:

```text
33 <= D_mono(22) <= 34
```

The original run page retains the overall artifact and twenty shard artifacts containing the exact records, machine reports, and minute-by-minute memory logs. A separate full-archive action has been requested to copy those records and downloadable job logs into this folder.
