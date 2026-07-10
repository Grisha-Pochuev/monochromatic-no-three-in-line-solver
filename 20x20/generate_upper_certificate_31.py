"""Regenerate the verifier-friendly LP dual certificate for 20x20.

Requires scipy and numpy. The final certificate is checked using exact integer
arithmetic by verify_20x20.py; trusting floating-point LP output is unnecessary.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

N = 20
PARITY = 0
DEFAULT_DENOMINATOR = 1_000_000


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    A = y2 - y1
    B = x1 - x2
    C = -(A * x1 + B * y1)
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C)) or 1
    A //= g
    B //= g
    C //= g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return A, B, C


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "upper_certificate_31.json",
    )
    parser.add_argument("--denominator", type=int, default=DEFAULT_DENOMINATOR)
    args = parser.parse_args()

    points = [(x, y) for x in range(N) for y in range(N) if (x + y) % 2 == PARITY]
    line_map = {}
    for i, p in enumerate(points):
        for q in points[i + 1 :]:
            key = canonical_line(p, q)
            if key in line_map:
                continue
            A, B, C = key
            members = tuple(
                j for j, (x, y) in enumerate(points) if A * x + B * y + C == 0
            )
            if len(members) >= 3:
                line_map[key] = members

    lines = sorted(line_map.items())
    incidence = lil_matrix((len(points), len(lines)), dtype=float)
    for j, (_, members) in enumerate(lines):
        for i in members:
            incidence[i, j] = 1.0

    result = linprog(
        c=np.full(len(lines), 2.0),
        A_ub=-incidence.tocsr(),
        b_ub=-np.ones(len(points)),
        bounds=(0, None),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    denominator = args.denominator
    scaled = np.where(
        result.x > 1e-10,
        np.ceil(result.x * denominator - 1e-9),
        0,
    ).astype(np.int64)

    cover = np.asarray(incidence.tocsr() @ scaled).reshape(-1).astype(np.int64)
    upper_numerator = 2 * int(scaled.sum())
    if int(cover.min()) < denominator:
        raise AssertionError((int(cover.min()), denominator))
    if upper_numerator >= 32 * denominator:
        raise AssertionError((upper_numerator, 32 * denominator))

    weights = []
    for j in np.nonzero(scaled)[0]:
        (A, B, C_left), _ = lines[int(j)]
        weights.append([int(A), int(B), int(-C_left), int(scaled[j])])
    weights.sort()

    min_index = int(np.argmin(cover))
    certificate = {
        "N": N,
        "parity": PARITY,
        "kind": "all_line_dual_lp_certificate_v2",
        "meaning": (
            "Integer dual weights scaled by denominator. Each listed grid line "
            "has capacity two; every parity-0 point has cover at least denominator."
        ),
        "denominator": denominator,
        "upper_numerator": upper_numerator,
        "upper_bound": f"{upper_numerator}/{denominator}",
        "min_cover_numerator": int(cover[min_index]),
        "min_cover_point": list(points[min_index]),
        "weights": weights,
    }
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {args.output}: {len(weights)} nonzero lines, "
        f"upper={upper_numerator}/{denominator}, min_cover={int(cover.min())}/{denominator}"
    )


if __name__ == "__main__":
    main()
