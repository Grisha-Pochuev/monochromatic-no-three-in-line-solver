#!/usr/bin/env python3
"""
Verify a monochromatic no-three-in-line configuration for the 18x18 board.

Usage:
    python verify_config18.py data/lower_bound_27.json
    python verify_config18.py data/near_miss_28_local.json
"""
import json
import math
import sys
from pathlib import Path


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    a = y2 - y1
    b = x1 - x2
    c = -(a * x1 + b * y1)
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    a //= g
    b //= g
    c //= g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


def all_monochromatic_lines(n, parity):
    board_points = [(x, y) for x in range(n) for y in range(n) if (x + y) % 2 == parity]
    line_map = {}
    for i, p in enumerate(board_points):
        for q in board_points[i + 1:]:
            line = canonical_line(p, q)
            if line not in line_map:
                a, b, c = line
                cells = [r for r in board_points if a * r[0] + b * r[1] + c == 0]
                if len(cells) >= 3:
                    line_map[line] = cells
    seen = set()
    lines = []
    for cells in line_map.values():
        key = tuple(sorted(cells))
        if key not in seen:
            seen.add(key)
            lines.append(list(key))
    return lines


def load_points(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return 18, 0, [tuple(p) for p in data]
    return int(data.get("n", 18)), int(data.get("parity", 0)), [tuple(p) for p in data["points"]]


def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_config18.py data/lower_bound_27.json")
        return 2

    path = sys.argv[1]
    n, parity, points = load_points(path)
    point_set = set(points)

    errors = []
    if len(point_set) != len(points):
        errors.append("duplicate points found")
    for x, y in points:
        if not (0 <= x < n and 0 <= y < n):
            errors.append(f"point outside board: {(x, y)}")
        if (x + y) % 2 != parity:
            errors.append(f"point has wrong parity: {(x, y)}")

    lines = all_monochromatic_lines(n, parity)
    conflicts = []
    for line in lines:
        used = [p for p in line if p in point_set]
        if len(used) >= 3:
            conflicts.append(used)

    print(f"n={n}, parity={parity}, points={len(points)}, checked_lines={len(lines)}")
    if errors:
        print("Basic errors:")
        for error in errors:
            print("  -", error)
    if conflicts:
        print(f"Conflicts: {len(conflicts)}")
        for conflict in conflicts[:20]:
            print("  -", conflict)
        if len(conflicts) > 20:
            print(f"  ... {len(conflicts) - 20} more")
    else:
        print("OK: no three selected points lie on the same monochromatic line.")

    return 1 if errors or conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
