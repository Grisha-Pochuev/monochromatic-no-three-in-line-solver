# n=22 web-chat certificate and LP triage

Date: 2026-07-23

This folder preserves the reproducible part of the local web-chat research performed after the transpose-symmetry audit. No GitHub Actions run was used to generate these files.

## Certified result: A <= 2 for child 652

For the historical child `652`, the main diagonal is fixed to `(2,2),(3,3)` and the two diagonal saturation counts are `16/16`.

Let `A` be the number of selected points at intersections of

```text
x-y in {-2, 2}
x+y in {16, 18, 20, 22, 24, 26}
```

The file `a_bound_803_273_compact.min.json` is a rational dual certificate proving

```text
A <= 803/273 < 3
```

and hence, because `A` is integral,

```text
A <= 2.
```

Verify it with:

```bash
python verify_a_bound_803_273.py a_bound_803_273_compact.min.json
```

Expected output ends with:

```text
Certificate verified exactly.
Therefore A <= 803/273 < 3, so every integral configuration has A <= 2.
```

This certificate uses exact integer/rational arithmetic and does not use the unsafe unconditional transpose lexicographic cut.

## Numerical LP triage of the audited frontier

`lpscan_dom_all.jsonl.gz.b64` is a base64-encoded gzip archive. Decode it with:

```bash
base64 -d lpscan_dom_all.jsonl.gz.b64 > lpscan_dom_all.jsonl.gz
gzip -dc lpscan_dom_all.jsonl.gz > lpscan_dom_all.jsonl
```

It contains 1,130 records corresponding to the profile children reopened by the transpose-symmetry audit.

Numerical SciPy/HiGHS status counts:

```text
LP status 2 (reported infeasible): 443
LP status 0 (LP optimum found):    687
```

Breakdown by the historical status:

```text
among the 443 numerical LP-infeasible records:
  old INFEASIBLE: 312
  old UNKNOWN:    131

among the 687 records with an LP optimum:
  old INFEASIBLE: 42
  old UNKNOWN:    645
```

Important: these 443 numerical LP infeasibility results are a **triage set**, not yet 443 certified mathematical exclusions. Each one needs an independently checked rational dual certificate before it can be counted as a proof.

`lpscan_dom_summary.json` stores the counts and both child-id lists in an easily inspectable form.

## Line-domain data

`line_domains.json.gz.b64` is a base64-encoded gzip archive of the exact allowed occupancy domains used to strengthen the LP models for the audited children. Decode it analogously:

```bash
base64 -d line_domains.json.gz.b64 > line_domains.json.gz
gzip -dc line_domains.json.gz > line_domains.json
```

## Exploratory dual-rationalization log

`exact_dual_support2.out` is retained as an investigation log. It contains a promising numerical objective below 34, but it also explicitly reports:

```text
exact stationarity False
```

Therefore this file is **not a valid exact certificate** and must not be cited as a proof. It is useful only as a starting point for future rational reconstruction.

## Certified board status

No valid 34-point configuration was found and the remaining frontier is not fully certified infeasible. The rigorous status remains:

```text
33 <= D_mono(22) <= 34
```

## File hashes

```text
a_bound_803_273_compact.min.json  a0780b95310943ad4d595e8f6c3fecff6f9dcb4c6a2fc4937cf4bdeec79be146
verify_a_bound_803_273.py           b7d2bf799e55415f8e12d121083fe5a4ad10e14f8f6a19df3fbec72ea463e200
lpscan_dom_all.jsonl                37d740e3f3b2ddb61ea0a05a1588507d31a67bd1c3c1b0832fbe7487375460b0
line_domains.json                   f680767993db1b5dc9f3625969c503d04e12443a961c8738fb088cd25a2b4903
exact_dual_support2.out             14394f6a4f447d4afa2c6e2d384f578f1a8b610435f7ade94f7f569bc1bf48ad
```
