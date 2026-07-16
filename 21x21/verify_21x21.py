#!/usr/bin/env python3
"""Independent verifier for the 32-point 21x21 construction."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config_32.json"


def collinear(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> bool:
    return (b[0] - a[0]) * (c[1] - a[1]) == (c[0] - a[0]) * (b[1] - a[1])


def main() -> None:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    n = int(data["board_size"])
    parity = int(data["parity"])
    points = [tuple(map(int, point)) for point in data["points"]]

    assert data["point_count"] == 32
    assert len(points) == 32
    assert len(points) == len(set(points))
    assert all(0 <= x < n and 0 <= y < n for x, y in points)
    assert all((x + y) % 2 == parity for x, y in points)

    point_set = set(points)
    assert all((n - 1 - x, n - 1 - y) in point_set for x, y in points)

    for a, b, c in itertools.combinations(points, 3):
        assert not collinear(a, b, c), f"collinear triple: {a}, {b}, {c}"

    print("OK: valid 32-point parity-1 configuration on 21x21.")
    print("OK: invariant under 180-degree rotation.")
    print("OK: no three selected points are collinear.")


if __name__ == "__main__":
    main()
