#!/usr/bin/env python3
"""Reusable exact encoding of the n=22 certificate identity D + E = 112.

`weighted_at_least` implements an exact threshold dynamic program for positive
integer weights.  It is used to add the lower half of the identity.  Existing
models already contain the upper half through their defect/excess budgets.

For target 34, independently of any partition,

    line_defect D + selected_point_cover_excess E = 112.

Here D is computed over the 87 four-direction certificate lines.  If `sat_i`
means occupancy 2 and `zero_i` means occupancy 0, line i contributes
w_i * ((not sat_i) + zero_i).
"""
from __future__ import annotations


def weighted_threshold_var(cnf, items: list[tuple[int,int]], threshold: int) -> int:
    """Return a variable exactly equivalent to weighted_sum(items)>=threshold."""
    if threshold <= 0:
        z=cnf.new(); cnf.add(z); return z
    if any(w <= 0 for _x,w in items):
        raise ValueError('weighted threshold requires positive weights')
    if sum(w for _x,w in items) < threshold:
        z=cnf.new(); cnf.add(-z); return z

    old=[0]*(threshold+1)
    old_total=0
    for x,w in items:
        new=[0]*(threshold+1)
        new_total=old_total+w
        for t in range(1,min(threshold,new_total)+1):
            s=cnf.new(); new[t]=s
            A=old[t] if t <= min(threshold,old_total) else 0
            if t <= w:
                B_true=True; B=0
            else:
                B_true=False
                need=t-w
                B=old[need] if 1 <= need <= min(threshold,old_total) else 0

            # A -> s and (x & B) -> s.  For B=true, x -> s.
            if A: cnf.add(-A,s)
            if B_true: cnf.add(-x,s)
            elif B: cnf.add(-x,-B,s)

            # s -> A or x.
            if A: cnf.add(-s,A,x)
            else: cnf.add(-s,x)

            # If B is not the constant true, also s -> A or B.
            if not B_true:
                if A and B: cnf.add(-s,A,B)
                elif A: cnf.add(-s,A)
                elif B: cnf.add(-s,B)
                else: cnf.add(-s)
        old=new; old_total=new_total

    result=old[threshold]
    assert result
    return result


def require_weighted_at_least(cnf,items: list[tuple[int,int]],threshold: int) -> None:
    if threshold <= 0: return
    cnf.add(weighted_threshold_var(cnf,items,threshold))


def add_n22_exact_identity(cnf, base, make_zero_var, complement) -> None:
    """Add the explicit lower half D+E>=112 using fresh exact occupancy flags."""
    items=[]

    # Selected-point cover excess E.
    for p in base.POINTS:
        excess=base.point_excess(p)
        if excess > 0:
            items.append((base.PID[p],excess))

    # Exact line defect D.  Fresh flags avoid reliance on auxiliary numbering
    # in the caller's existing encoding.
    for family,key,weight,variables in base.GROUPS:
        if weight <= 0: continue
        sat=base.make_saturation_var(cnf,variables,f'exactid_sat_{family}_{key}')
        zero=make_zero_var(cnf,variables)
        items.append((complement(cnf,sat),weight))
        items.append((zero,weight))

    require_weighted_at_least(cnf,items,base.SLACK)
