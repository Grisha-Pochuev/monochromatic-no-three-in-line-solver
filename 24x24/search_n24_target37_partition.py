#!/usr/bin/env python3
"""Exact 20-way partition of a hypothetical 37-point solution on 24x24.

The rational four-direction dual certificate with scale 213 has objective
8046/213 = 2682/71 < 38.  For a 37-point set the total weighted line
deficit is at most 8046 - 37*213 = 165.

Every line in HIGH_DIAGONALS has certificate weight >= 85.  Therefore:
- none can have occupancy 0 (cost at least 170);
- at most one can have occupancy 1 (two such deficits cost at least 170).
Hence every target-37 solution belongs to exactly one of 20 cases:
all 19 high diagonals have occupancy 2, or exactly one specified high
line has occupancy 1 and the other 18 have occupancy 2.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from ortools.sat.python import cp_model

N = 24
TARGET = 37
PARITY = 0

HIGH_DIAGONALS = (
    [("diff", d) for d in (0, -2, 2, -4, 4, -6, 6, -8, 8)]
    + [("sum", s) for s in (14,16,18,20,22,24,26,28,30,32)]
)
assert len(HIGH_DIAGONALS) == 19

def allowed_points():
    return [(x,y) for x in range(N) for y in range(N) if (x+y)%2 == PARITY]

def maximal_allowed_lines(points):
    index = {p:i for i,p in enumerate(points)}
    out = {}
    for i in range(len(points)):
        x1,y1 = points[i]
        for j in range(i+1,len(points)):
            x2,y2 = points[j]
            A=y2-y1; B=x1-x2
            g=math.gcd(abs(A),abs(B)); A//=g; B//=g
            if A<0 or (A==0 and B<0):
                A=-A; B=-B
            C=A*x1+B*y1
            out.setdefault((A,B,C),set()).update((i,j))
    return [sorted(v) for v in out.values() if len(v)>=3]

def validate(sol):
    if len(sol)!=TARGET or len(set(sol))!=TARGET:
        raise ValueError("wrong size")
    for i,a in enumerate(sol):
        for j in range(i+1,len(sol)):
            b=sol[j]
            for c in sol[j+1:]:
                if (b[0]-a[0])*(c[1]-a[1]) == (b[1]-a[1])*(c[0]-a[0]):
                    raise ValueError(f"collinear triple {a} {b} {c}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",type=int,required=True,choices=range(20))
    ap.add_argument("--seconds",type=float,default=600)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    pts=allowed_points()
    lines=maximal_allowed_lines(pts)
    model=cp_model.CpModel()
    x=[model.new_bool_var(f"p_{px}_{py}") for px,py in pts]
    for line in lines:
        model.add(sum(x[i] for i in line) <= 2)
    model.add(sum(x) == TARGET)

    line_vars=[]
    for typ,val in HIGH_DIAGONALS:
        if typ=="diff":
            ids=[i for i,(px,py) in enumerate(pts) if px-py==val]
        else:
            ids=[i for i,(px,py) in enumerate(pts) if px+py==val]
        line_vars.append(ids)

    if a.case == 0:
        for ids in line_vars:
            model.add(sum(x[i] for i in ids) == 2)
        case_desc="all_19_high_diagonals_saturated"
    else:
        special=a.case-1
        for j,ids in enumerate(line_vars):
            model.add(sum(x[i] for i in ids) == (1 if j==special else 2))
        case_desc=f"only_{HIGH_DIAGONALS[special]}_has_occupancy_1"

    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=a.seconds
    solver.parameters.num_search_workers=a.workers
    solver.parameters.random_seed=a.seed % 2147483647
    solver.parameters.randomize_search=True
    solver.parameters.cp_model_presolve=True
    solver.parameters.symmetry_level=2
    st=solver.solve(model)
    status=solver.status_name(st)
    sol=[]
    if status in {"FEASIBLE","OPTIMAL"}:
        sol=[p for i,p in enumerate(pts) if solver.value(x[i])]
        validate(sol)

    payload={
        "board_size":N,"target":TARGET,"parity":PARITY,
        "partition_case":a.case,"case_description":case_desc,
        "status":status,"solution":sol,"seed":a.seed,
        "wall_time":solver.wall_time,"branches":solver.num_branches,
        "conflicts":solver.num_conflicts,"line_constraints":len(lines),
    }
    a.output.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
