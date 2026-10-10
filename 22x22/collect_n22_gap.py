#!/usr/bin/env python3
"""Collect the n=22 gap run: every one of the 727 children must appear exactly once."""
import argparse, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prove_upper_22x22_main_diagonal_pair import validate_solution
ap = argparse.ArgumentParser()
ap.add_argument("--input-dir", type=Path, required=True); ap.add_argument("--overall", type=Path, required=True)
ap.add_argument("--summary", type=Path, required=True); ap.add_argument("--run-url", default="")
a = ap.parse_args()
sched = json.loads((HERE / "webchat/2026-10-10-farkas-gap/gap_schedule.json").read_text())
expected = {c for s in sched["assignments"] for c in s["ids"]}
res = {}
for f in sorted(a.input_dir.rglob("shard-*-summary.json")):
    for c, r in json.loads(f.read_text())["results"].items():
        c = int(c)
        if c in res: raise SystemExit(f"duplicate child {c}")
        res[c] = r
missing = sorted(expected - set(res))
inf = sorted(c for c, r in res.items() if r["status"] == "INFEASIBLE")
sol = sorted(c for c, r in res.items() if r["status"] in ("FEASIBLE", "OPTIMAL"))
for c in sol: validate_solution(res[c]["solution"])
unk = sorted(c for c in expected if c not in inf and c not in sol)
overall = {"run_url": a.run_url, "expected": len(expected), "collected": len(res), "missing": missing,
           "infeasible_count": len(inf), "solution_children": sol, "remaining_count": len(unk),
           "infeasible_child_ids": inf, "remaining_child_ids": unk,
           "solutions": {str(c): res[c]["solution"] for c in sol}}
a.overall.write_text(json.dumps(overall, indent=1))
a.summary.write_text(f"# n22 gap run\n\n- expected: {len(expected)}\n- collected: {len(res)}\n- missing: {len(missing)}\n"
                     f"- INFEASIBLE: {len(inf)}\n- FEASIBLE (34 points!): {len(sol)}\n- remaining: {len(unk)}\n- run: {a.run_url}\n")
print(a.summary.read_text())
