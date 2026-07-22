# Local web-chat attack on n=22 child 652

Date: 2026-07-22

This folder preserves the part of the local web-chat computation that survived the runtime restart. It did not use GitHub Actions.

## Scope

The script `n22_milp.py` builds a symmetry-safe SciPy/HiGHS MILP for the final historical child `652`:

- board size `22`, parity `0`, target `34`;
- all maximal grid-line constraints;
- fixed main-diagonal pair `(2,2),(3,3)`;
- exact `16/16` saturation counts in the two diagonal directions;
- rational-certificate excess and defect constraints;
- selected affine-copy bounds inherited from previously solved smaller boards;
- no unconditional transpose lexicographic cut.

The experiment parameter `A` counts selected points in the 12 intersections of the mandatory diagonal families
`x-y in {-2,2}` and `x+y in {16,18,20,22,24,26}`.

## Preserved partial result

`a2_triage.jsonl` contains the first 10 of the 36 transpose-canonical choices for `A=2`, each given a five-second HiGHS limit.

- checked: 10 / 36;
- proved `INFEASIBLE`: 7;
- time-limit `UNKNOWN`: 3;
- feasible 34-point configurations: 0.

Strictly excluded canonical choices:

```text
0: (7,9), (8,10)
2: (7,9), (9,11)
3: (7,9), (10,8)
4: (7,9), (10,12)
5: (7,9), (11,9)
7: (7,9), (12,10)
9: (7,9), (13,11)
```

Unresolved at the five-second limit:

```text
1: (7,9), (9,7)
6: (7,9), (11,13)
8: (7,9), (12,14)
```

## Important limitation

This is a partial frontier record, not a closure of `A=2` and not a proof that 34 points are impossible. The remaining 26 canonical choices were not preserved after the local runtime restart. `UNKNOWN` is not treated as a proof.

The certified board status therefore remains:

```text
33 <= D_mono(22) <= 34
```

## Reproduction

The script requires NumPy and SciPy with HiGHS MILP support. Example:

```bash
python 22x22/webchat/2026-07-22-a-parameter/n22_milp.py \
  --mode a2 --time 5 \
  --out 22x22/webchat/2026-07-22-a-parameter/a2_triage_new.jsonl
```

File digests at commit time:

```text
n22_milp.py      sha256:f358598a6c8949401380157defc484a9af0b69c85a89b10b8cb322eb843c4ee5
a2_triage.jsonl sha256:14216c1e703b353c9ca901ff9989ffaa22daa857d69d54cf08bf883b9032b918
```
