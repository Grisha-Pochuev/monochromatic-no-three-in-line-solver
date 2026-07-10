import json
import math
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
    assert data["kind"] == "all_line_dual_lp_certificate_v2"

    denominator = int(data["denominator"])
    assert denominator > 0
    weights = data["weights"]
    assert weights

    total = 0
    parsed = []
    for entry in weights:
        assert len(entry) == 4, entry
        A, B, C, weight = map(int, entry)
        assert (A, B) != (0, 0)
        assert weight >= 0
        total += weight
        parsed.append((A, B, C, weight))

    min_cover = None
    min_point = None
    for x in range(N):
        for y in range(N):
            if (x + y) % 2 != data["parity"]:
                continue
            cover = sum(weight for A, B, C, weight in parsed if A * x + B * y == C)
            if min_cover is None or cover < min_cover:
                min_cover = cover
                min_point = (x, y)
            assert cover >= denominator, ((x, y), cover, denominator)

    upper_numerator = 2 * total
    assert upper_numerator == int(data["upper_numerator"])
    assert upper_numerator < 32 * denominator
    assert min_cover == int(data["min_cover_numerator"])
    assert list(min_point) == data["min_cover_point"]

    print(
        "upper bound verified: "
        f"D_mono(20) <= 31 via {upper_numerator}/{denominator} < 32; "
        f"min cover {min_cover}/{denominator} at {min_point}"
    )


if __name__ == "__main__":
    verify_config_30()
    verify_upper_31()
    print("Current certified frontier: 30 <= D_mono(20) <= 31")
