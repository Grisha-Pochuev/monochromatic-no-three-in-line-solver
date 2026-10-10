#!/usr/bin/env python3
"""Complementary-orientation ("gap") model for n=22 target-34 profile children.

Old model O = base & row_twos<=column_twos & above <=lex below  (proved INFEASIBLE).
Safe model S = base & row_twos<=column_twos.
Base is invariant under transpose T. If x in S\\O and row_twos==column_twos then T(x) in O,
contradiction. Hence S\\O is contained in
G = base & row_twos < column_twos & below <=lex above.
INFEASIBLE(G) + INFEASIBLE(O) => INFEASIBLE(S).
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove_upper_22x22_profile_child as M
from ortools.sat.python import cp_model

_orig_lex = M.add_lex_less_or_equal
def _reversed_lex_and_strict(model, left, right, prefix):
    # left=above, right=below; impose below <=lex above
    _orig_lex(model, right, left, prefix + "_rev")
M.add_lex_less_or_equal = _reversed_lex_and_strict
_orig_build = M.build_model
def build_model(pi, pt, mt):
    model, points, selected, meta = _orig_build(pi, pt, mt)
    if meta.get("analytic_infeasible"):
        return model, points, selected, meta
    rows = [sum(selected[p] for p in points if p[1] == k) for k in range(M.N)]
    # strict r<c via fresh flags (re-derive two-flags)
    def twos(groups, name):
        fl = []
        for i, g in enumerate(groups):
            b = model.NewBoolVar(f"{name}{i}"); c = sum(selected[p] for p in g)
            model.Add(c == 2).OnlyEnforceIf(b); model.Add(c <= 1).OnlyEnforceIf(b.Not()); fl.append(b)
        return fl
    r = twos([[p for p in points if p[1] == k] for k in range(M.N)], "gr")
    c = twos([[p for p in points if p[0] == k] for k in range(M.N)], "gc")
    model.Add(sum(r) + 1 <= sum(c))
    meta["gap_model"] = "row_twos<column_twos & below<=lex above"
    return model, points, selected, meta
M.build_model = build_model
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--child-id", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=60); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261010); ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    rec = M.solve_child(a.child_id, a.seconds, a.workers, a.seed)
    rec["proof_method"] = "cp_sat_gap_complementary_orientation"
    t = json.dumps(rec, indent=1); print(t)
    if a.output: a.output.write_text(t)
