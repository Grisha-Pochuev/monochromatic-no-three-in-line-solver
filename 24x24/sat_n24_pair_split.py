#!/usr/bin/env python3
"""CaDiCaL pair-split proof search for n=24 target 37."""
from __future__ import annotations
import argparse, itertools, json, time
from pathlib import Path
from pysat.solvers import Solver
from sat_n24_target37 import N,TARGET,HIGH,build,validate,forced_saturated_specs,ids_on

def write(path,payload):
    path.write_text(json.dumps(payload,indent=2)+"\n")

def choose_split(case,ps):
    forced=set(forced_saturated_specs(case))
    # In all one-deficit cases except d=+-8, the certificate slack forces
    # x=0 to be saturated. It has only 12 allowed cells -> 66 pair leaves.
    if ("row",0) in forced:
        return ("row",0), ids_on(ps,("row",0))
    # The three harder cases (0, 8, 9) retain a saturated |d|=8 diagonal.
    spec=("diff",-8) if case==9 else ("diff",8)
    assert spec in forced
    return spec,ids_on(ps,spec)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",type=int,required=True,choices=range(20))
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    ps,lines,cnf=build(args.case)
    split_spec,split=choose_split(args.case,ps)
    pairs=list(itertools.combinations(split,2))

    payload={
        "board_size":N,"target":TARGET,"partition_case":args.case,
        "split_line":split_spec,"split_points":len(split),
        "total_pair_leaves":len(pairs),"closed_unsat":0,
        "status":"PARTIAL","sat_pair":None,"solution":[],
        "forced_saturated_lines":len(forced_saturated_specs(args.case)),
        "variables":cnf.nv,"clauses":len(cnf.clauses),
    }
    write(args.output,payload)

    solver=None;used=None
    for name in ("cadical195","cadical153","cadical103","glucose4","minisat22"):
        try:
            solver=Solver(name=name,bootstrap_with=cnf.clauses);used=name;break
        except Exception:
            pass
    if solver is None:
        payload["status"]="ERROR_NO_SOLVER";write(args.output,payload);return 2
    payload["solver"]=used
    t0=time.time()
    for k,(a,b) in enumerate(pairs):
        t=time.time();sat=solver.solve(assumptions=[a,b]);leaf_s=time.time()-t
        if sat:
            model=set(v for v in solver.get_model() if v>0)
            sol=[p for i,p in enumerate(ps) if i+1 in model]
            validate(sol)
            payload.update({"status":"SAT","sat_pair":[a,b],"solution":sol,
                            "leaf_index":k,"last_leaf_seconds":leaf_s,
                            "solve_seconds":time.time()-t0})
            write(args.output,payload);solver.delete()
            print(json.dumps(payload,indent=2));return 0
        payload["closed_unsat"]=k+1
        payload["last_leaf_index"]=k
        payload["last_leaf_seconds"]=leaf_s
        payload["solve_seconds"]=time.time()-t0
        if (k+1)%5==0 or k+1==len(pairs):
            write(args.output,payload)
            print(f"case={args.case} closed={k+1}/{len(pairs)} last={leaf_s:.3f}s",flush=True)

    solver.delete();payload["status"]="UNSAT";write(args.output,payload)
    print(json.dumps(payload,indent=2));return 0

if __name__=="__main__":
    raise SystemExit(main())
