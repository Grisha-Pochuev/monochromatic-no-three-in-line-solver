# n22 pair/profile smoke run 29766054707

Run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29766054707

Head SHA: `dcf182cb9a8bfc76a62cded4eec9e366cc64d86c`

The complete profile partition finished successfully.

- expected and collected children: 2640/2640;
- `INFEASIBLE`: 1864;
- `UNKNOWN`: 776;
- `FEASIBLE`/`OPTIMAL`: 0;
- missing children: 0;
- duplicate children: 0;
- `MODEL_INVALID`: 0;
- newly closed main-diagonal pairs: 0;
- remaining main-diagonal pairs: 88;
- total solver work: 4.77 job-hours;
- total branches: 368,668,487;
- total conflicts: 97,545,592.

No 34-point configuration was found. Because 776 exact profile children remain `UNKNOWN`, the certified status remains:

```text
33 <= D_mono(22) <= 34
```

The 1864 exact exclusions must not be recomputed. The next long run processes only the 776 remaining children. `long_profile_input.json` stores their smoke difficulty scores (`branches + 2*conflicts`) so they can be balanced across 20 independent runners.

Source artifact:

- artifact id: `8471536105`;
- SHA-256: `e0dbded2cb7524812ad602eefd228bc4804377b8dd676aca3364debb209d9f38`.
