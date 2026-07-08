# 20x20 checkerboard no-three-in-line attack package

Current certified frontier:

```text
30 <= D_mono(20) <= 31
```

## Files

- `config_30.json` — verified 30-point monochromatic no-three-in-line configuration on parity 0.
- `upper_certificate_31.json` — rational four-direction LP dual certificate proving `D_mono(20) <= 31`.
- `verify_20x20.py` — independent checker for the lower construction and upper certificate.
- `search_20x20_cpsat.py` — optional CP-SAT feasibility search for target 31.

## Reproduce

```bash
python verify_20x20.py
python search_20x20_cpsat.py 31 300 8 1
```

The first command is a fast certificate check. The second command is an exploratory search for a 31-point configuration; it is not a proof unless CP-SAT returns infeasible with a reproducible full search record.
