#!/usr/bin/env python3
"""Collect n=22 round 2: every one of the 288 schedule items must appear exactly once."""
import argparse, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prove_upper_22x22_main_diagonal_pair import validate_solution
ap = argparse.ArgumentParser()
ap.add_argument("--input-dir", type=Path, required=True); ap.add_argument("--overall", type=Path, required=True)
ap.add_argument("--summary", type=Path, required=True); ap.add_argument("--run-url", default="")
a = ap.parse_args()
sched = json.loads((HERE / "webchat/2026-10-10-round2/round2_schedule.json").read_text())
def key(it): return f"gap-{it['child']:04d}" if it["kind"] == "gap" else f"c652-r{it['r']}-c{it['c']}-a{it['a']}"
expected = {key(it) for s in sched["assignments"] for it in s["items"]}
assert len(expected) == 288
res = {}
for f in sorted(a.input_dir.rglob("shard-*-summary.json")):
    for k, r in json.loads(f.read_text())["results"].items():
        if k in res: raise SystemExit(f"duplicate {k}")
        res[k] = r
missing = sorted(expected - set(res))
inf = sorted(k for k, r in res.items() if r["status"] == "INFEASIBLE")
sol = sorted(k for k, r in res.items() if r["status"] in ("FEASIBLE", "OPTIMAL"))
for k in sol: validate_solution(res[k]["solution"])
rem = sorted(k for k in expected if k not in inf and k not in sol)
gi = [k for k in inf if k.startswith("gap-")]; ci = [k for k in inf if k.startswith("c652-")]
overall = {"run_url": a.run_url, "expected": len(expected), "collected": len(res), "missing": missing,
           "infeasible_count": len(inf), "gap_infeasible": len(gi), "c652_infeasible": len(ci),
           "solution_keys": sol, "remaining_count": len(rem), "infeasible_keys": inf, "remaining_keys": rem,
           "solutions": {k: res[k]["solution"] for k in sol}}
a.overall.write_text(json.dumps(overall, indent=1))
a.summary.write_text(f"# n22 round 2\n\n- expected: {len(expected)} (225 gap + 63 child-652 subcases)\n- collected: {len(res)}\n"
                     f"- missing: {len(missing)}\n- INFEASIBLE: {len(inf)} (gap {len(gi)}/225, child 652 {len(ci)}/63)\n"
                     f"- FEASIBLE (34 points!): {len(sol)}\n- remaining: {len(rem)}\n- run: {a.run_url}\n")
print(a.summary.read_text())
