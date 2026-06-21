#!/usr/bin/env python3
"""
Local-swap search for a 28-point monochromatic no-three-in-line configuration
on the parity-0 half of the 18x18 board.

This is a search tool, not a proof by itself. If it prints FOUND, verify the
printed configuration with verify_config18.py.
"""
import json
import math
import random
import sys
import time
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


def build(n, parity):
    pts = [(x, y) for x in range(n) for y in range(n) if (x + y) % 2 == parity]
    line_sets = {}
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            key = canonical_line(a, b)
            if key not in line_sets:
                A, B, C = key
                line = [r for r in pts if A * r[0] + B * r[1] + C == 0]
                if len(line) >= 3:
                    line_sets[key] = line
    lines = list(line_sets.values())
    point_lines = {pt: [] for pt in pts}
    for li, line in enumerate(lines):
        for pt in line:
            point_lines[pt].append(li)
    return pts, lines, point_lines


def load_base_config():
    path = Path(__file__).resolve().parent / "data" / "lower_bound_27.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [tuple(p) for p in data["points"]]


def main():
    n = 18
    parity = 0
    target = 28
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else int(time.time())
    random.seed(seed)

    pts, lines, point_lines = build(n, parity)
    print("pts", len(pts), "lines", len(lines), "target", target, "seed", seed, flush=True)

    base = load_base_config()
    m = len(lines)

    def init_counts(S):
        cnt = [0] * m
        for pt in S:
            for li in point_lines[pt]:
                cnt[li] += 1
        return cnt

    def total_conf(cnt):
        return sum(max(0, c - 2) for c in cnt)

    def delta_add(pt, cnt):
        return sum(1 for li in point_lines[pt] if cnt[li] >= 2)

    def delta_remove(pt, cnt):
        return -sum(1 for li in point_lines[pt] if cnt[li] >= 3)

    def apply_add(pt, cnt):
        for li in point_lines[pt]:
            cnt[li] += 1

    def apply_remove(pt, cnt):
        for li in point_lines[pt]:
            cnt[li] -= 1

    start = time.time()
    best = 10**9
    best_set = None
    restarts = 0

    while time.time() - start < seconds:
        restarts += 1
        if base and random.random() < 0.4:
            selected = set(base)
            rest = [pt for pt in pts if pt not in selected]
            selected.add(random.choice(rest))
        else:
            selected = set(random.sample(pts, target))

        cnt = init_counts(selected)
        conf = total_conf(cnt)
        temp = 2.0

        for step in range(50000):
            if time.time() - start >= seconds:
                break
            if conf == 0:
                print("FOUND", time.time() - start, "restart", restarts, "step", step, flush=True)
                print(json.dumps(sorted(selected)), flush=True)
                return 0
            if conf < best:
                best = conf
                best_set = set(selected)
                print("best", best, "time", time.time() - start, "restart", restarts, "step", step, flush=True)

            conflict_lines = [i for i, c in enumerate(cnt) if c > 2]
            bad_points = []
            for li in random.sample(conflict_lines, min(len(conflict_lines), 20)):
                for pt in lines[li]:
                    if pt in selected:
                        bad_points.append(pt)
            if not bad_points:
                bad_points = list(selected)

            current = list(selected)
            outside = [pt for pt in pts if pt not in selected]
            removals = random.sample(current, min(len(current), 8)) + random.sample(bad_points, min(len(bad_points), 12))
            additions = random.sample(outside, min(len(outside), 40))

            best_moves = []
            best_delta = 10**9
            for r in removals:
                dr = delta_remove(r, cnt)
                apply_remove(r, cnt)
                for a in additions:
                    delta = dr + delta_add(a, cnt)
                    if delta < best_delta:
                        best_delta = delta
                        best_moves = [(r, a, delta)]
                    elif delta == best_delta:
                        best_moves.append((r, a, delta))
                apply_add(r, cnt)

            if not best_moves:
                continue
            r, a, delta = random.choice(best_moves)
            if delta <= 0 or random.random() < math.exp(-delta / max(temp, 0.01)):
                apply_remove(r, cnt)
                selected.remove(r)
                apply_add(a, cnt)
                selected.add(a)
                conf += delta
            temp *= 0.9995

    print("NO best", best, "time", time.time() - start, "seed", seed)
    if best_set is not None:
        print(json.dumps(sorted(best_set)))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
