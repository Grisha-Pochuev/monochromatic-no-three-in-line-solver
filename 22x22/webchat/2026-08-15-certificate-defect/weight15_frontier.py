#!/usr/bin/env python3
"""Rigorous open frontier after the weight-15 count split.

The current weight-22 frontier has 338 rigorous open parents.  Splitting each
by the exact number of underfull weight-15 lines (row/col 4 and 17) gives 723
complete/disjoint children.

Run 31919694722 reconstructed and then checked exact nonnegative integer
Farkas multipliers for every exact geometric identity subcase of the 94 count
children listed below: 1,288 identity subcases in total.  No symmetry was used
in that audit.  Hence those 94 children are rigorously UNSAT and 629 remain.
"""
from __future__ import annotations

import generate_refined_15_count_exact as level15

FARKAS_AUDIT_RUN=31919694722

FARKAS_CLOSED_PAIRS={
    (2,4),(4,4),(6,4),(11,1),(12,4),(13,3),(14,2),(15,3),(16,2),
    (21,4),(22,3),(23,2),(24,3),(25,2),(30,4),(31,3),(32,2),(33,3),
    (34,2),(39,4),(40,3),(41,2),(42,3),(43,2),(49,1),(50,1),(52,1),
    (53,1),(54,2),(55,1),(56,1),(57,2),(58,1),(59,1),(61,1),(62,1),
    (64,1),(65,1),(66,3),(75,4),(80,1),(93,4),(98,1),(111,3),(120,3),
    (129,4),(134,1),(147,4),(152,1),(165,3),(174,4),(175,3),(181,2),
    (184,2),(187,2),(190,2),(194,2),(198,1),(199,1),(200,1),(201,1),
    (216,2),(221,1),(222,1),(223,1),(224,1),(225,4),(226,3),(232,2),
    (235,2),(238,2),(241,2),(245,3),(247,3),(253,1),(256,1),(259,1),
    (262,1),(278,3),(296,3),(319,3),(321,3),(327,1),(330,1),(333,1),
    (336,1),(338,1),(339,1),(346,1),(347,1),(354,1),(388,1),(390,2),
    (394,1),
}
assert len(FARKAS_CLOSED_PAIRS)==94

ALL_PAIRS=list(level15.CASES)
assert len(level15.OPEN_COUNT22)==338
assert len(ALL_PAIRS)==723
assert FARKAS_CLOSED_PAIRS <= set(ALL_PAIRS)

OPEN_PAIRS=[pair for pair in ALL_PAIRS if pair not in FARKAS_CLOSED_PAIRS]
assert len(OPEN_PAIRS)==629
