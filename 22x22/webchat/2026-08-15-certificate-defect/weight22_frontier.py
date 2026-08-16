#!/usr/bin/env python3
"""Rigorous closed/open frontier after weight-22 defect splitting.

Solver run 31918747065 examined all 395 count-refined weight-22 children:
43 UNSAT, 352 TIMEOUT, 0 SAT, 0 ERROR.  TIMEOUT is deliberately not closed.

Independent exact integer Farkas audit run 31919145658 proves 39 children.
The two proof sets overlap on 38 children.  Their union therefore closes 44
children and leaves 351 open before considering any later strengthening run.
"""

TOTAL=395
SOLVER_RUN=31918747065
FARKAS_AUDIT_RUN=31919145658

SOLVER_UNSAT={
    68,70,82,91,106,113,122,139,142,154,163,167,179,211,230,246,249,
    251,266,271,273,275,277,280,298,306,311,313,315,317,320,323,325,
    343,345,351,353,358,360,364,366,368,391,
}

FARKAS_UNSAT={
    68,82,91,103,106,113,122,139,142,154,163,167,179,230,246,249,266,
    271,273,275,277,280,298,306,311,313,315,317,320,323,343,345,351,
    353,358,360,364,366,391,
}

assert len(SOLVER_UNSAT)==43
assert len(FARKAS_UNSAT)==39
assert len(SOLVER_UNSAT & FARKAS_UNSAT)==38
assert SOLVER_UNSAT-FARKAS_UNSAT=={70,211,251,325,368}
assert FARKAS_UNSAT-SOLVER_UNSAT=={103}

CLOSED=set(SOLVER_UNSAT)|set(FARKAS_UNSAT)
OPEN=[i for i in range(TOTAL) if i not in CLOSED]

assert len(CLOSED)==44
assert len(OPEN)==351
