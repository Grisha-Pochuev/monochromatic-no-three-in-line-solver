#!/usr/bin/env python3
"""SAT search for a 37-point monochromatic no-three-in-line set on 24x24.

The 20 partition cases are exhaustive once the rational four-direction
upper certificate is used.  In the 19 one-deficit cases we also add every
further certificate line that is forced to be saturated by the remaining
integer slack budget.  These extra equalities are logical consequences,
not heuristic restrictions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

N=24
TARGET=37
PARITY=0
SCALE=213
TOTAL_WEIGHT=4023
TARGET_BUDGET=2*TOTAL_WEIGHT-TARGET*SCALE  # 165

ROW_W=[80,63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63,80]
DIFF_W={
    0:117,-2:115,2:115,-4:109,4:109,-6:99,6:99,-8:85,8:85,
    -10:72,10:72,-12:60,12:60,-14:44,14:44,-16:24,16:24,
    -18:0,18:0,-20:0,20:0,-22:0,22:0,
}
SUM_W={
    0:0,2:0,4:0,6:26,8:48,10:66,12:80,14:93,16:106,18:118,
    20:126,22:130,24:130,26:126,28:118,30:106,32:93,34:80,
    36:66,38:48,40:26,42:0,44:0,46:0,
}
HIGH=(
    [("diff",d) for d in (0,-2,2,-4,4,-6,6,-8,8)]
    + [("sum",s) for s in (14,16,18,20,22,24,26,28,30,32)]
)

def line_weight(spec):
    typ,val=spec
    if typ in ("row","col"):
        return ROW_W[val]
    if typ=="diff":
        return DIFF_W[val]
    if typ=="sum":
        return SUM_W[val]
    raise ValueError(spec)

def certificate_lines():
    out=[]
    out += [("row",i) for i,w in enumerate(ROW_W) if w]
    out += [("col",i) for i,w in enumerate(ROW_W) if w]
    out += [("diff",d) for d,w in DIFF_W.items() if w]
    out += [("sum",s) for s,w in SUM_W.items() if w]
    return out

def points():
    return [(x,y) for x in range(N) for y in range(N) if (x+y)%2==PARITY]

def ids_on(ps,spec):
    typ,val=spec
    if typ=="row":
        return [i+1 for i,(x,y) in enumerate(ps) if x==val]
    if typ=="col":
        return [i+1 for i,(x,y) in enumerate(ps) if y==val]
    if typ=="diff":
        return [i+1 for i,(x,y) in enumerate(ps) if x-y==val]
    if typ=="sum":
        return [i+1 for i,(x,y) in enumerate(ps) if x+y==val]
    raise ValueError(spec)

def maximal_lines(ps):
    mp={}
    for i,(x1,y1) in enumerate(ps):
        for j in range(i+1,len(ps)):
            x2,y2=ps[j]
            A=y2-y1; B=x1-x2
            g=math.gcd(abs(A),abs(B)); A//=g; B//=g
            if A<0 or (A==0 and B<0):
                A=-A; B=-B
            C=A*x1+B*y1
            mp.setdefault((A,B,C),set()).update((i,j))
    return [sorted(s) for s in mp.values() if len(s)>=3]

def validate(sol):
    assert len(sol)==TARGET and len(set(sol))==TARGET
    for a,b,c in itertools.combinations(sol,3):
        assert (b[0]-a[0])*(c[1]-a[1]) != (b[1]-a[1])*(c[0]-a[0])

def forced_saturated_specs(case):
    """Certificate lines forced to occupancy 2 in a target-37 partition case."""
    forced=set()
    special=None if case==0 else HIGH[case-1]
    # The 20-case partition itself.
    for h in HIGH:
        if h!=special:
            forced.add(h)
    if special is not None:
        residual=TARGET_BUDGET-line_weight(special)
        # Any additional deficit on a line of weight > residual would
        # exceed the total target-37 slack budget.
        for spec in certificate_lines():
            if spec!=special and line_weight(spec)>residual:
                forced.add(spec)
    return sorted(forced)

def build(case):
    ps=points()
    lines=maximal_lines(ps)
    vpool=IDPool(start_from=len(ps)+1)
    cnf=CNF()

    for line in lines:
        lits=[i+1 for i in line]
        for a,b,c in itertools.combinations(lits,3):
            cnf.append([-a,-b,-c])

    eq=CardEnc.equals(lits=list(range(1,len(ps)+1)),bound=TARGET,
                      vpool=vpool,encoding=EncType.cardnetwrk)
    cnf.extend(eq.clauses)

    special=None if case==0 else HIGH[case-1]

    # Force every line that the exact integer slack argument says is saturated.
    for spec in forced_saturated_specs(case):
        ids=ids_on(ps,spec)
        ge=CardEnc.atleast(lits=ids,bound=2,vpool=vpool,encoding=EncType.seqcounter)
        cnf.extend(ge.clauses)

    if special is not None:
        ids=ids_on(ps,special)
        ge=CardEnc.atleast(lits=ids,bound=1,vpool=vpool,encoding=EncType.seqcounter)
        le=CardEnc.atmost(lits=ids,bound=1,vpool=vpool,encoding=EncType.seqcounter)
        cnf.extend(ge.clauses); cnf.extend(le.clauses)

    return ps,lines,cnf

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",type=int,required=True,choices=range(20))
    ap.add_argument("--solver",default="cadical195")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    t0=time.time()
    ps,lines,cnf=build(args.case)
    build_s=time.time()-t0
    status="UNKNOWN"; sol=[]
    solver=None
    tried=[]
    for name in (args.solver,"cadical153","cadical103","glucose4","minisat22"):
        if name in tried: continue
        tried.append(name)
        try:
            solver=Solver(name=name,bootstrap_with=cnf.clauses); used=name; break
        except Exception:
            solver=None
    if solver is None:
        raise RuntimeError(f"no SAT solver available; tried {tried}")

    t1=time.time(); sat=solver.solve(); solve_s=time.time()-t1
    if sat:
        model=set(l for l in solver.get_model() if l>0)
        sol=[p for i,p in enumerate(ps) if i+1 in model]
        validate(sol); status="SAT"
    else:
        status="UNSAT"
    stats=solver.accum_stats(); solver.delete()

    payload={
        "board_size":N,"target":TARGET,"parity":PARITY,
        "partition_case":args.case,
        "special_high_line":None if args.case==0 else HIGH[args.case-1],
        "forced_saturated_lines":len(forced_saturated_specs(args.case)),
        "status":status,"solution":sol,
        "solver":used,"points":len(ps),"maximal_lines":len(lines),
        "variables":cnf.nv,"clauses":len(cnf.clauses),
        "build_seconds":build_s,"solve_seconds":solve_s,"stats":stats,
    }
    args.output.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
