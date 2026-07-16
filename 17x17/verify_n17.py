#!/usr/bin/env python3
"""
Independent verification for the 17x17 monochromatic no-three-in-line result.

Run from this folder:

    python verify_n17.py

The script uses only the Python standard library.

It verifies:
1. both configurations contain 26 distinct points;
2. all points lie on the 17x17 board;
3. all points have the required parity;
4. no three selected points are collinear;
5. each rational covering certificate covers every allowed point with weight at least 1;
6. each certificate gives an upper bound strictly below 27.

Together with the explicit configurations, this proves:

    D_mono(17, even) = D_mono(17, odd) = D_mono(17) = 26.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path


N = 17
TARGET_SIZE = 26


def load_json(name: str) -> dict:
    return json.loads(Path(name).read_text(encoding="utf-8"))


def frac(value: str | int | float) -> Fraction:
    return Fraction(str(value))


def is_collinear(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> bool:
    return (b[0] - a[0]) * (c[1] - a[1]) == (b[1] - a[1]) * (c[0] - a[0])


def allowed_points(parity: int) -> list[tuple[int, int]]:
    return [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == parity]


def parse_weight_map(raw: dict[str, str]) -> dict[int, Fraction]:
    return {int(k): frac(v) for k, v in raw.items()}


def check_configuration(name: str, raw_points: list[list[int]], parity: int) -> None:
    points = [tuple(p) for p in raw_points]

    assert len(points) == TARGET_SIZE, f"{name}: expected {TARGET_SIZE} points, got {len(points)}"
    assert len(set(points)) == len(points), f"{name}: duplicate points found"

    for x, y in points:
        assert 0 <= x < N and 0 <= y < N, f"{name}: point {(x, y)} is outside the board"
        assert (x + y) % 2 == parity, f"{name}: point {(x, y)} has wrong parity"

    for a, b, c in combinations(points, 3):
        assert not is_collinear(a, b, c), f"{name}: collinear triple found: {a}, {b}, {c}"

    print(f"{name}: configuration verified ({len(points)} points, no collinear triple).")


def check_certificate(name: str, raw_certificate: dict, parity: int) -> None:
    row_y = parse_weight_map(raw_certificate["row_y"])
    column_x = parse_weight_map(raw_certificate["column_x"])
    diag_x_minus_y = parse_weight_map(raw_certificate["diag_x_minus_y"])
    diag_x_plus_y = parse_weight_map(raw_certificate["diag_x_plus_y"])

    total_weight = (
        sum(row_y.values(), Fraction(0))
        + sum(column_x.values(), Fraction(0))
        + sum(diag_x_minus_y.values(), Fraction(0))
        + sum(diag_x_plus_y.values(), Fraction(0))
    )
    upper_bound = 2 * total_weight

    stated_upper_bound = frac(raw_certificate["upper_bound"])
    assert upper_bound == stated_upper_bound, (
        f"{name}: computed upper bound {upper_bound} does not match stated {stated_upper_bound}"
    )
    assert upper_bound < TARGET_SIZE + 1, f"{name}: certificate does not prove upper bound below 27"

    min_cover = None
    worst_point = None

    for x, y in allowed_points(parity):
        cover = (
            row_y.get(y, Fraction(0))
            + column_x.get(x, Fraction(0))
            + diag_x_minus_y.get(x - y, Fraction(0))
            + diag_x_plus_y.get(x + y, Fraction(0))
        )
        if min_cover is None or cover < min_cover:
            min_cover = cover
            worst_point = (x, y)
        assert cover >= 1, f"{name}: point {(x, y)} has cover {cover}, below 1"

    print(
        f"{name}: certificate verified "
        f"(upper bound = {upper_bound} = {float(upper_bound):.12f}, "
        f"minimum cover = {min_cover} at {worst_point})."
    )


def main() -> None:
    configurations = load_json("configurations.json")
    certificates = load_json("certificates.json")["certificates"]

    even_points = configurations["color_classes"]["even"]["points"]
    odd_points = configurations["color_classes"]["odd"]["points"]

    check_configuration("even", even_points, parity=0)
    check_configuration("odd", odd_points, parity=1)

    check_certificate("even", certificates["even"], parity=0)
    check_certificate("odd", certificates["odd"], parity=1)

    print()
    print("Result verified:")
    print("D_mono(17, even) = D_mono(17, odd) = D_mono(17) = 26")


if __name__ == "__main__":
    main()
