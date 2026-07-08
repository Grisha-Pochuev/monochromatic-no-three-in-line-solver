import json
import math
from fractions import Fraction
from pathlib import Path

N = 20
VALUE = 30
HERE = Path(__file__).resolve().parent


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


def verify_config_30():
    data = json.loads((HERE / "config_30.json").read_text(encoding="utf-8"))
    points = [tuple(p) for p in data["points"]]
    assert data["N"] == N
    assert data["value"] == VALUE
    assert len(points) == VALUE
    assert len(set(points)) == VALUE
    for x, y in points:
        assert 0 <= x < N and 0 <= y < N
        assert (x + y) % 2 == data["parity"]
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            line = canonical_line(points[i], points[j])
            for k in range(j + 1, len(points)):
                if canonical_line(points[i], points[k]) == line:
                    raise AssertionError((points[i], points[j], points[k]))
    print("lower bound verified: 30-point configuration has no three collinear points")


def verify_upper_31():
    data = json.loads((HERE / "upper_certificate_31.json").read_text(encoding="utf-8"))
    assert data["N"] == N
    assert data["parity"] == 0
    weights = data["weights"]
    total = sum(Fraction(w["weight"]) for w in weights)
    min_cover = None
    min_point = None
    for x in range(N):
        for y in range(N):
            if (x + y) % 2 != data["parity"]:
                continue
            cover = Fraction(0)
            for w in weights:
                if w["A"] * x + w["B"] * y == w["C"]:
                    cover += Fraction(w["weight"])
            if min_cover is None or cover < min_cover:
                min_cover = cover
                min_point = (x, y)
            assert cover >= 1, ((x, y), cover)
    upper = 2 * total
    assert upper == Fraction(data["upper_bound"]), (upper, data["upper_bound"])
    assert upper < 32, upper
    print(f"upper bound verified: D_mono(20) <= 31 via {upper} < 32; min cover {min_cover} at {min_point}")


if __name__ == "__main__":
    verify_config_30()
    verify_upper_31()
    print("Current certified frontier: 30 <= D_mono(20) <= 31")
