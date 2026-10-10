#!/usr/bin/env python3
"""Exact verification of the Farkas certificates for 402 reopened n=22 profile children.

For each child the linear relaxation of the symmetry-safe child model (all maximal
lines <= 2, total 34, fixed main-diagonal pair, rational-certificate excess/defect
constraints, 0/1/2 occupancy states for the four weighted families, profile counts,
row_twos <= column_twos; NO lexicographic cut) is rebuilt as rows a.x <= b.
The certificate gives nonnegative rationals y_r. With c = sum y_r a_r and
B = sum y_r b_r, every x in [0,1]^n satisfies c.x >= sum_i min(0,c_i).
If sum_i min(0,c_i) > B the relaxation, hence the child, is infeasible.
All arithmetic uses fractions.Fraction.
"""
import gzip, json, sys
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from farkas_child import build_lp

def check(child, mult):
    rows, n = build_lp(child)
    c = [Fraction(0)] * n; B = Fraction(0)
    for r, ystr in mult.items():
        y = Fraction(ystr)
        if y < 0: return False, "negative multiplier"
        d, b = rows[int(r)]
        B += y * b
        for k, a in d.items(): c[k] += y * a
    low = sum(min(Fraction(0), ci) for ci in c)
    return low > B, str(low - B)

def main():
    path = HERE / "farkas_reopened_402.jsonl.gz"
    ok = 0; bad = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rec = json.loads(line)
            good, margin = check(rec["child"], rec["multipliers"])
            if good: ok += 1
            else: bad.append(rec["child"])
    print(json.dumps({"verified": ok, "failed": bad}))
    if bad or ok != 402: sys.exit(1)

if __name__ == "__main__":
    main()
