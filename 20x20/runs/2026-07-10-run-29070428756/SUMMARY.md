# 20x20 exact diagonal-pair run 29070428756

Date: 2026-07-10

Workflow run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29070428756

Source commit: `c7ce3c4c60f63d818f4859f806cbaa36587e80bf`

## Result

Conclusion: `INCOMPLETE_FRONTIER`

| Measure | Result |
|---|---:|
| canonical cases | 100 |
| proved infeasible | 99 |
| unknown | 1 |
| missing | 0 |
| 31-point configurations found | 0 |

The complete 100-case partition therefore reduced the unresolved 20x20 problem to one exact canonical branch:

```text
case_id = 50
main-diagonal indices = [2, 17]
forced points = (2,2) and (17,17)
status = UNKNOWN
elapsed = 3301.168 seconds
conflicts = 492251
branches = 24664149
```

The solver reached its time limit on this branch. `UNKNOWN` is not evidence of feasibility or infeasibility.

## Mathematical status

The certified frontier remains

```text
30 <= D_mono(20) <= 31.
```

However, 99 of the 100 exhaustive diagonal-pair cases are now permanently recorded as infeasible. Any hypothetical 31-point configuration must belong to case 50, up to the 180-degree rotation already used by the canonical partition.

The next exact computation should target case 50 only; the other 99 cases do not need to be rerun.

## Archived files

- `overall.json`: collector output for all 100 cases.
- `shard_10.json`: the shard containing the single unresolved case and four additional infeasible cases.

Artifact provenance:

```text
overall artifact id: 8219562131
sha256: 87d0bc9055f9c0152910e48c4c5a8694ecf92c5eea4d80a7cc5686063eae6f95

shard-10 artifact id: 8219559960
sha256: cba5739bd02a3806445fb3ea69ca9a936e97ec8abcb2496aa7b03e91d4722d3d
```
