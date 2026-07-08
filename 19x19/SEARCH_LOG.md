# Search log for the 19x19 case

The folder previously recorded the cautious frontier:

```text
28 <= D_mono(19) <= 29
```

A later CP-SAT feasibility run on the even checkerboard colour class found a 29-point configuration. The result is stored in `config_29.json`.

The upper bound is not based on trusting the search. It is checked by the rational certificate in `upper_certificate.json`, which proves that 30 points are impossible on both checkerboard colour classes.

Therefore the case is now closed in this repository:

```text
D_mono(19) = 29
```

Verification command:

```bash
python verify_19x19.py
```
