# Exact 21x21 proof

GitHub Actions run: https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29531523646

Conclusion: `PROVED_D_MONO_21_EQUALS_32`

- verified lower construction: 32 points, parity 1;
- parity records: 2/2;
- target tested: 33 points;
- parity 0: `INFEASIBLE` in 37.31 seconds;
- parity 1: `INFEASIBLE` in 0.38 seconds;
- `UNKNOWN`: 0;
- 33-point solutions: 0.

The upper proof uses only rows, columns, and the two diagonal families of slopes `+1` and `-1`. This is a relaxation of the full no-three-in-line problem. Since even this weaker integer model cannot contain 33 points for either checkerboard color, the true optimum is at most 32. Together with the verified 32-point construction, this proves:

```text
D_mono(21) = 32
```
