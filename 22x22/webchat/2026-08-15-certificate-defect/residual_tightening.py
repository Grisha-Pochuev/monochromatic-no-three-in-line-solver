#!/usr/bin/env python3
"""Safe branch-local consequences of the exact identity D+E=112.

Suppose defect-count branching has already fixed all certificate levels with
weight >= `processed_min_weight`, and `residual` is 112 minus the minimum
defect forced by those exact counts.

Everything not yet charged is nonnegative.  Therefore:
* a selected point with cover excess > residual is impossible;
* at an already-counted level, an empty line would add one extra copy of its
  weight beyond the counted underfull contribution, so if weight>residual it
  cannot be empty;
* at an unprocessed level, occupancy 0 costs 2*weight and occupancy 1 costs
  weight.  Hence weight>residual forces saturation (occupancy 2), while
  2*weight>residual forbids occupancy 0.

These are logical consequences only; they do not use symmetry and do not
change the represented search space.
"""
from __future__ import annotations


def add_residual_tightening(cnf, base, residual: int, processed_min_weight: int) -> dict:
    if residual < 0:
        cnf.add()  # explicit contradiction
        return {'residual':residual,'forbidden_points':0,'nonempty_groups':0,'forced_saturated_groups':0}

    forbidden_points=0
    for p in base.POINTS:
        excess=base.point_excess(p)
        if excess > residual:
            cnf.add(-base.PID[p])
            forbidden_points+=1

    nonempty_groups=0
    forced_saturated_groups=0
    for family,key,weight,variables in base.GROUPS:
        if weight <= 0:
            continue
        if weight >= processed_min_weight:
            # This level's base underfull contribution is already included in
            # the branch minimum.  Zero occupancy would add another `weight`.
            if weight > residual:
                cnf.add(*variables)
                nonempty_groups+=1
        else:
            # This level has not yet been charged into the branch minimum.
            if weight > residual:
                sat=base.make_saturation_var(cnf,variables,f'residual_sat_{family}_{key}')
                cnf.add(sat)
                forced_saturated_groups+=1
            elif 2*weight > residual:
                cnf.add(*variables)
                nonempty_groups+=1

    return {
        'residual':residual,
        'processed_min_weight':processed_min_weight,
        'forbidden_points':forbidden_points,
        'nonempty_groups':nonempty_groups,
        'forced_saturated_groups':forced_saturated_groups,
    }
