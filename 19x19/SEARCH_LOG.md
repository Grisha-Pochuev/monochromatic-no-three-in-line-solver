# Search log for the 19x19 working package

A CP-SAT maximization run on the even checkerboard colour class found a 28-point configuration quickly.

The same run did not reproduce a 29-point configuration within the local time window used here, so this folder deliberately records the cautious verified state:

```text
28 <= D_mono(19) <= 29
```

The upper bound is not based on trusting the search. It is checked by the rational certificate in `upper_certificate.json`.

Verification command:

```bash
python verify_19x19.py
```
