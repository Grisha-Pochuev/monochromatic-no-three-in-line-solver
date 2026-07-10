# Final n20 case50 A=0,1,2 run

GitHub Actions run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29103139466

Conclusion: `PROVED_FINAL_A0_A2_INFEASIBLE_DMONO20_EQUALS_30`

- expected disjoint branches: 20
- records found: 20
- infeasible: 20
- unknown: 0
- solutions: 0

Together with the previously committed exclusions of the other 99 diagonal pairs, `A>=5`, `A=4`, and `A=3`, the complete `A=0,1,2` exclusion proves:

```text
D_mono(20) = 30
```

The lower bound is supplied by the verified 30-point configuration in `20x20/config_30.json`. The upper bound is supplied by the complete exact partition excluding every possible 31-point configuration.
