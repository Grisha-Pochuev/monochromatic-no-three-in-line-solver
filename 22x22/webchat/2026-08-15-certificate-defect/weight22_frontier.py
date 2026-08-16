#!/usr/bin/env python3
"""Rigorous closed/open frontier after weight-22 defect splitting.

Run 31918747065 examined all 395 count-refined weight-22 children without the
lower half of the exact identity: 43 UNSAT, 352 TIMEOUT, 0 SAT, 0 ERROR.
TIMEOUT is deliberately not closed.

Independent exact integer Farkas audit run 31919145658 proves 39 children.
Those two proof sets have union size 44.

The stronger run 31918874582 added the independently audited exact certificate
identity D+E=112 to every one of the 395 children and returned 55 UNSAT,
340 TIMEOUT, 0 SAT, 0 ERROR.  Its UNSAT set contributes 13 children not in the
previous union.  The rigorous union therefore closes 57 of 395 and leaves
338 open.
"""

TOTAL=395
SOLVER_RUN=31918747065
FARKAS_AUDIT_RUN=31919145658
EXACT_IDENTITY_RUN=31918874582

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

EXACT_IDENTITY_UNSAT={
    29,47,68,82,88,91,100,103,109,113,122,136,139,142,145,154,157,
    163,167,179,211,220,230,246,249,251,266,271,273,275,277,280,298,
    306,311,313,315,317,320,323,325,343,345,351,353,358,360,364,366,
    368,370,375,386,387,391,
}

assert len(SOLVER_UNSAT)==43
assert len(FARKAS_UNSAT)==39
assert len(SOLVER_UNSAT & FARKAS_UNSAT)==38
assert SOLVER_UNSAT-FARKAS_UNSAT=={70,211,251,325,368}
assert FARKAS_UNSAT-SOLVER_UNSAT=={103}
assert len(EXACT_IDENTITY_UNSAT)==55

PREVIOUS_CLOSED=set(SOLVER_UNSAT)|set(FARKAS_UNSAT)
assert len(PREVIOUS_CLOSED)==44
assert EXACT_IDENTITY_UNSAT-PREVIOUS_CLOSED=={
    29,47,88,100,109,136,145,157,220,370,375,386,387,
}

CLOSED=PREVIOUS_CLOSED|set(EXACT_IDENTITY_UNSAT)
OPEN=[i for i in range(TOTAL) if i not in CLOSED]

assert len(CLOSED)==57
assert len(OPEN)==338
