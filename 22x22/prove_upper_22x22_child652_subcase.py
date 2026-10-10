#!/usr/bin/env python3
"""Symmetry-safe exact model for one subcase of historical child 652 (n=22, target 34).

Child 652 = main-diagonal pair (2,2),(3,3), diag_plus_twos = diag_minus_twos = 16.
It is partitioned into 21 x 3 = 63 disjoint subcases

    sum(row_twos) = r,  sum(column_twos) = c,  12 <= r <= c <= 17   (21 pairs)
    A = a,  a in {0, 1, 2}

where A counts selected points with x-y in {-2,2} and x+y in {16,...,26}.
Coverage: the safe base model already imposes 12 <= r, c <= 17 and r <= c; the exact
rational certificate in webchat/2026-07-23-certificate-lp-triage proves A <= 2.

Symmetry treatment (conditional lex):
  * r < c : NO lexicographic cut (only the complete orientation r <= c of the base);
  * r = c : the transpose T maps the subcase (r, r, a) onto itself (T swaps row/column
            twos, preserves the diagonal pair, the diagonal profiles, the certificate
            weights and A), so imposing  above <=lex below  inside it is sound.
UNKNOWN is never a proof.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove_upper_22x22_profile_child as M

CHILD = 652
A_DIFF = (-2, 2)
A_SUM = (16, 18, 20, 22, 24, 26)
_orig_lex = M.add_lex_less_or_equal
_orig_build = M.build_model


def subcases():
    out = []
    for r in range(12, 18):
        for c in range(r, 18):
            for a in range(3):
                out.append((r, c, a))
    return out


def make_build(r, c, a):
    def build_model(pi, pt, mt):
        M.add_lex_less_or_equal = _orig_lex if r == c else (lambda *x, **k: None)
        try:
            model, points, selected, meta = _orig_build(pi, pt, mt)
        finally:
            M.add_lex_less_or_equal = _orig_lex
        if meta.get("analytic_infeasible"):
            return model, points, selected, meta

        def twos(groups, name):
            fl = []
            for i, g in enumerate(groups):
                b = model.NewBoolVar(f"{name}{i}"); s = sum(selected[p] for p in g)
                model.Add(s == 2).OnlyEnforceIf(b); model.Add(s <= 1).OnlyEnforceIf(b.Not()); fl.append(b)
            return fl
        rt = twos([[p for p in points if p[1] == k] for k in range(M.N)], "sr")
        ct = twos([[p for p in points if p[0] == k] for k in range(M.N)], "sc")
        model.Add(sum(rt) == r); model.Add(sum(ct) == c)
        apts = [p for p in points if (p[0] - p[1]) in A_DIFF and (p[0] + p[1]) in A_SUM]
        assert len(apts) == 12, len(apts)
        model.Add(sum(selected[p] for p in apts) == a)
        meta.update({"subcase": {"row_twos": r, "column_twos": c, "A": a},
                     "transpose_symmetry_break": "conditional_lex_r_eq_c" if r == c else "none_r_lt_c",
                     "unconditional_transpose_lex_disabled": r != c})
        return model, points, selected, meta
    return build_model


def solve(r, c, a, seconds, workers, seed):
    assert 12 <= r <= c <= 17 and a in (0, 1, 2)
    M.build_model = make_build(r, c, a)
    try:
        rec = M.solve_child(CHILD, seconds, workers, seed)
    finally:
        M.build_model = _orig_build
    rec["proof_method"] = "cp_sat_child652_subcase_safe_conditional_lex"
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True); ap.add_argument("--c", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=60); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261011); ap.add_argument("--output", type=Path)
    x = ap.parse_args()
    rec = solve(x.r, x.c, x.a, x.seconds, x.workers, x.seed)
    t = json.dumps(rec, indent=1); print(t)
    if x.output: x.output.write_text(t)
