#!/usr/bin/env python3
"""Verify the recorded 34-point near-solution and its unique bad line.

This deliberately does not certify a lower bound of 34: the file is a diagnostic
object with exactly one collinear triple.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "near_34_one_violation.json"


def canonical_line(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int, int]:
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    divisor = math.gcd(abs(dx), abs(dy))
    aa, bb = dy // divisor, -dx // divisor
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb = -aa, -bb
    return aa, bb, aa * x1 + bb * y1


def main() -> None:
    record = json.loads(DATA.read_text(encoding="utf-8"))
    n = int(record["board_size"])
    parity = int(record["parity"])
    points = [tuple(map(int, point)) for point in record["points"]]

    assert record["status"] == "diagnostic_not_a_valid_construction"
    assert len(points) == record["point_count"] == 34
    assert len(points) == len(set(points))
    assert all(0 <= x < n and 0 <= y < n for x, y in points)
    assert all((x + y) % 2 == parity for x, y in points)

    line_members: dict[tuple[int, int, int], set[tuple[int, int]]] = defaultdict(set)
    for first, second in itertools.combinations(points, 2):
        key = canonical_line(first, second)
        line_members[key].add(first)
        line_members[key].add(second)

    violations = {
        key: sorted(members)
        for key, members in line_members.items()
        if len(members) >= 3
    }
    assert violations == {(0, 1, 0): [(8, 0), (12, 0), (14, 0)]}

    print("OK: 34 distinct parity-0 points on 22x22.")
    print("OK: exactly one violating line, y = 0, with three selected points.")
    print("NOTE: this is a diagnostic near-solution, not a valid 34-point construction.")


if __name__ == "__main__":
    main()
