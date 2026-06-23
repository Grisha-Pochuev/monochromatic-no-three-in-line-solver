import json
import math
from fractions import Fraction
from pathlib import Path

N = 19
LOWER = 28
HERE = Path(__file__).resolve().parent


def canonical_line(p, q):
    x1, y1 = p
    x2, y2 = q
    A = y2 - y1
    B = x1 - x2
    C = -(A * x1 + B * y1)
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
    A //= g
    B //= g
    C //= g
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
    return A, B, C


def F(s):
    return Fraction(s)


def get_weight(table, key):
    return F(table.get(str(key), "0"))


def verify_lower_config():
    data = json.loads((HERE / "config_28.json").read_text(encoding="utf-8"))
    points = [tuple(p) for p in data["points"]]
    assert data["N"] == N
    assert len(points) == LOWER
    assert len(set(points)) == LOWER
    for x, y in points:
        assert 0 <= x < N and 0 <= y < N
        assert (x + y) % 2 == data["parity"]
    bad = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            line = canonical_line(points[i], points[j])
            for k in range(j + 1, len(points)):
                if canonical_line(points[i], points[k]) == line:
                    bad.append((points[i], points[j], points[k]))
    assert not bad, bad[:5]
    print("lower bound verified: 28-point configuration has no three collinear points")


def verify_upper_one(name, cert):
    parity = 0 if name == "even" else 1
    min_cover = None
    min_point = None
    for x in range(N):
        for y in range(N):
            if (x + y) % 2 != parity:
                continue
            cover = (
                get_weight(cert["row_y"], y)
                + get_weight(cert["column_x"], x)
                + get_weight(cert["diag_x_minus_y"], x - y)
                + get_weight(cert["diag_x_plus_y"], x + y)
            )
            if min_cover is None or cover < min_cover:
                min_cover = cover
                min_point = (x, y)
            assert cover >= 1, (name, (x, y), cover)
    total_weight = sum(
        F(v)
        for key in ["row_y", "column_x", "diag_x_minus_y", "diag_x_plus_y"]
        for v in cert[key].values()
    )
    upper = 2 * total_weight
    assert upper == F(cert["upper_bound"]), (name, upper, cert["upper_bound"])
    assert upper < 30, (name, upper)
    print(f"upper bound verified for {name}: {upper} < 30, min cover {min_cover} at {min_point}")


def verify_upper_certificates():
    data = json.loads((HERE / "upper_certificate.json").read_text(encoding="utf-8"))
    for name, cert in data["certificates"].items():
        verify_upper_one(name, cert)
    print("upper bound verified: D_mono(19) <= 29")


if __name__ == "__main__":
    verify_lower_config()
    verify_upper_certificates()
    print("verified bounds: 28 <= D_mono(19) <= 29")
