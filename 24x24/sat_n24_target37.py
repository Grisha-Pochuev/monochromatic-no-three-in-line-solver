#!/usr/bin/env python3
"""SAT search for a 37-point monochromatic no-three-in-line set on 24x24.

The 20 partition cases are exhaustive once the rational four-direction
upper certificate is used:
  * case 0: all 19 high-weight diagonals contain exactly 2 points;
  * case j=1..19: high diagonal j-1 contains exactly 1 point and all
    other high diagonals contain exactly 2 points.

This script uses a pure CNF encoding and CaDiCaL via python-sat.
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
HIGH=(
    [("diff",d) for d in (0,-2,2,-4,4,-6,6,-8,8)]
    + [("sum",s) for s in (14,16,18,20,22,24,26,28,30,32)]
)

def points():
    return [(x,y) for x in range(N) for y in range(N) if (x+y)%2==PARITY]

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

def build(case):
    ps=points()
    lines=maximal_lines(ps)
    vpool=IDPool(start_from=len(ps)+1)
    cnf=CNF()

    # One Boolean variable i+1 for each allowed point. Every maximal
    # line may contain at most two selected points.
    for line in lines:
        lits=[i+1 for i in line]
        # Pairwise triple clauses are compact here and keep the geometry transparent.
        for a,b,c in itertools.combinations(lits,3):
            cnf.append([-a,-b,-c])

    # Exactly 37 points. Cardinality network is robust for this size.
    eq=CardEnc.equals(lits=list(range(1,len(ps)+1)), bound=TARGET,
                      vpool=vpool, encoding=EncType.cardnetwrk)
    cnf.extend(eq.clauses)

    special=None if case==0 else case-1
    for j,(typ,val) in enumerate(HIGH):
        ids=[i+1 for i,(x,y) in enumerate(ps)
             if (x-y==val if typ=="diff" else x+y==val)]
        bound=1 if j==special else 2
        # <=2 is already implied by all-line clauses; only the lower side is new.
        ge=CardEnc.atleast(lits=ids,bound=bound,vpool=vpool,encoding=EncType.seqcounter)
        cnf.extend(ge.clauses)
        if bound==1:
            # exactly 1: all-line constraints only give <=2, so add <=1.
            le=CardEnc.atmost(lits=ids,bound=1,vpool=vpool,encoding=EncType.seqcounter)
            cnf.extend(le.clauses)
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
    tried=[]
    names=[args.solver,"cadical153","cadical103","glucose4","minisat22"]
    solver=None
    for name in names:
        if name in tried: continue
        tried.append(name)
        try:
            solver=Solver(name=name, bootstrap_with=cnf.clauses)
            used=name
            break
        except Exception:
            solver=None
    if solver is None:
        raise RuntimeError(f"no requested SAT solver available; tried {tried}")

    t1=time.time()
    sat=solver.solve()
    solve_s=time.time()-t1
    if sat:
        model=set(l for l in solver.get_model() if l>0)
        sol=[p for i,p in enumerate(ps) if i+1 in model]
        validate(sol)
        status="SAT"
    else:
        status="UNSAT"
    stats=solver.accum_stats()
    solver.delete()

    payload={
        "board_size":N,"target":TARGET,"parity":PARITY,
        "partition_case":args.case,
        "special_high_line":None if args.case==0 else HIGH[args.case-1],
        "status":status,"solution":sol,
        "solver":used,"points":len(ps),"maximal_lines":len(lines),
        "variables":cnf.nv,"clauses":len(cnf.clauses),
        "build_seconds":build_s,"solve_seconds":solve_s,
        "stats":stats,
    }
    args.output.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
