#!/usr/bin/env python3
"""Strengthened, safe SAT branch for excluding 34 points on 22x22.

All reductions used here are rigorous consequences of already verified data:
* original all-lines no-three-in-line constraints;
* exact rational n=22 four-direction certificate 6470/187 < 35;
* exact values for embedded 17x17..21x21 boards;
* 180-degree rotation, which preserves parity 0 on an even board.

In particular, this file does NOT use the invalid transpose lex-leader that
was identified in the July symmetry audit.
"""
from __future__ import annotations

import argparse
import itertools
import math
from collections import defaultdict
from pathlib import Path

N = 22
TARGET = 34
Q = 187
OBJECTIVE = 6470
SLACK = OBJECTIVE - TARGET * Q  # 112

ROW = [63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63]
COL = ROW[:]
DIFF = {-20:0,-18:0,-16:24,-14:44,-12:60,-10:72,-8:85,-6:99,-4:109,
        -2:115,0:117,2:115,4:109,6:99,8:85,10:72,12:60,14:44,16:24,
        18:0,20:0}
SUM = {0:0,2:0,4:0,6:22,8:40,10:54,12:67,14:80,16:92,18:100,
       20:104,22:104,24:100,26:92,28:80,30:67,32:54,34:40,36:22,
       38:0,40:0,42:0}
SMALL = {17:26, 18:27, 19:29, 20:30, 21:32}

POINTS = [(x, y) for y in range(N) for x in range(N) if (x + y) % 2 == 0]
PID = {p: i + 1 for i, p in enumerate(POINTS)}


def canonical_line(a: tuple[int,int], b: tuple[int,int]) -> tuple[int,int,int]:
    x1, y1 = a
    x2, y2 = b
    aa = y2 - y1
    bb = x1 - x2
    cc = -(aa * x1 + bb * y1)
    g = math.gcd(math.gcd(abs(aa), abs(bb)), abs(cc))
    aa, bb, cc = aa // g, bb // g, cc // g
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb, cc = -aa, -bb, -cc
    return aa, bb, cc


def maximal_lines() -> list[tuple[int,...]]:
    by_eq: dict[tuple[int,int,int], set[int]] = defaultdict(set)
    for i, a in enumerate(POINTS):
        for j in range(i + 1, len(POINTS)):
            key = canonical_line(a, POINTS[j])
            by_eq[key].add(i + 1)
            by_eq[key].add(j + 1)
    result = [tuple(sorted(v)) for v in by_eq.values() if len(v) >= 3]
    assert len(result) == 2455
    assert sum(math.comb(len(line), 3) for line in result) == 33946
    return result


def branch_pairs() -> list[tuple[int,int]]:
    result = []
    for a, b in itertools.combinations(range(N), 2):
        pair = (a, b)
        rotated = tuple(sorted((N - 1 - a, N - 1 - b)))
        if pair <= rotated:
            result.append(pair)
    assert len(result) == 121
    return result


def excess(p: tuple[int,int]) -> int:
    x, y = p
    value = ROW[y] + COL[x] + DIFF[x-y] + SUM[x+y] - Q
    assert value >= 0
    return value


def four_groups() -> list[tuple[int,list[int],str]]:
    out = []
    for y in range(N):
        out.append((ROW[y], [PID[p] for p in POINTS if p[1] == y], f'row={y}'))
    for x in range(N):
        out.append((COL[x], [PID[p] for p in POINTS if p[0] == x], f'col={x}'))
    for d, w in DIFF.items():
        out.append((w, [PID[p] for p in POINTS if p[0]-p[1] == d], f'diff={d}'))
    for s, w in SUM.items():
        out.append((w, [PID[p] for p in POINTS if p[0]+p[1] == s], f'sum={s}'))
    return out


class CNF:
    def __init__(self) -> None:
        self.nvars = len(POINTS)
        self.clauses: list[list[int]] = []

    def new(self) -> int:
        self.nvars += 1
        return self.nvars

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def add_clause(self, lits) -> None:
        self.clauses.append(list(lits))

    def at_most_two(self, variables: list[int]) -> None:
        """Sequential threshold encoding of sum(variables) <= 2."""
        if len(variables) <= 2:
            return
        old1 = 0
        old2 = 0
        for x in variables:
            new1 = self.new()
            new2 = self.new()
            if old1:
                self.add(-old1, new1)
            self.add(-x, new1)
            if old2:
                self.add(-old2, new2)
                self.add(-x, -old2)       # a third true variable is forbidden
            if old1:
                self.add(-x, -old1, new2)
            # For a valid point assignment the auxiliaries can always be set
            # to the actual prefix thresholds.  Conversely three true inputs
            # force old2 before the third and hit the overflow clause above.
            old1, old2 = new1, new2

    def threshold_var(self, variables: list[int], k: int) -> int:
        """Return a variable exactly equivalent to sum(variables) >= k."""
        if k <= 0:
            raise ValueError('k must be positive')
        if k > len(variables):
            z = self.new(); self.add(-z); return z
        old = [0] * (k + 1)
        for i, x in enumerate(variables, start=1):
            new = [0] * (k + 1)
            for j in range(1, min(k, i) + 1):
                s = self.new()
                new[j] = s
                A = old[j]
                B_true = (j == 1)
                B = 0 if B_true else old[j-1]
                if A:
                    self.add(-A, s)
                if B_true:
                    self.add(-x, s)
                elif B:
                    self.add(-x, -B, s)
                # reverse directions: s -> A or (x & B)
                if A:
                    self.add(-s, A, x)
                else:
                    self.add(-s, x)
                if B_true:
                    pass
                elif A and B:
                    self.add(-s, A, B)
                elif A:
                    self.add(-s, A)
                elif B:
                    self.add(-s, B)
                else:
                    self.add(-s)
            old = new
        return old[k]

    def at_least_k(self, variables: list[int], k: int) -> None:
        if k <= 0:
            return
        t = self.threshold_var(variables, k)
        self.add(t)

    def complement(self, x: int) -> int:
        z = self.new()
        self.add(z, x)
        self.add(-z, -x)
        return z

    def weighted_exact(self, items: list[tuple[int,int]], target: int) -> None:
        """Exact DP encoding of sum(weight_i * literal_i) == target.

        We only need thresholds up to target+1.  The final two unit clauses
        require >=target and forbid >=target+1.
        """
        if target < 0:
            self.add()  # impossible branch
            return
        items = [(x,w) for x,w in items if w > 0]
        if target == 0:
            for x, _ in items:
                self.add(-x)
            return
        cap = target + 1
        old = [0] * (cap + 1)
        for x, w in items:
            new = [0] * (cap + 1)
            for t in range(1, cap + 1):
                s = self.new()
                new[t] = s
                A = old[t]
                B_true = (t <= w)
                B = 0 if B_true else old[t-w]
                if A:
                    self.add(-A, s)
                if B_true:
                    self.add(-x, s)
                elif B:
                    self.add(-x, -B, s)
                if A:
                    self.add(-s, A, x)
                else:
                    self.add(-s, x)
                if B_true:
                    pass
                elif A and B:
                    self.add(-s, A, B)
                elif A:
                    self.add(-s, A)
                elif B:
                    self.add(-s, B)
                else:
                    self.add(-s)
            old = new
        self.add(old[target])
        self.add(-old[target+1])

    def write(self, path: Path) -> None:
        with path.open('w', encoding='ascii') as out:
            out.write(f'p cnf {self.nvars} {len(self.clauses)}\n')
            for clause in self.clauses:
                out.write(' '.join(map(str, clause)) + ' 0\n')


def build(index: int) -> tuple[CNF, tuple[int,int], int]:
    pairs = branch_pairs()
    if not 0 <= index < len(pairs):
        raise SystemExit('branch index must be 0..120')
    a, b = pairs[index]
    chosen_diag = {a, b}
    fixed_excess = excess((a,a)) + excess((b,b))
    residual = SLACK - fixed_excess
    assert residual >= 0

    cnf = CNF()

    # Original geometry, written as a compact sequential <=2 constraint for
    # every maximal grid line containing at least three parity-even points.
    for line in maximal_lines():
        cnf.at_most_two(list(line))

    # The rational certificate proves that any all-lines solution has <35
    # points.  Thus 'at least 34' is exactly the target-34 question.
    cnf.at_least_k(list(range(1, len(POINTS)+1)), TARGET)

    # The main difference diagonal has weight 117 > global slack 112, hence
    # it is saturated in every 34-point solution.  Fix its exact pair.
    for k in range(N):
        cnf.add(PID[(k,k)] if k in chosen_diag else -PID[(k,k)])

    # Exact smaller-board consequences.  Every contiguous embedded m x m
    # board contains at most D_mono(m) selected points; with total >=34 this
    # is equivalently a small lower bound on the points outside that board.
    all_ids = set(range(1, len(POINTS)+1))
    for m, bound in SMALL.items():
        need_outside = TARGET - bound
        for ox in range(N-m+1):
            for oy in range(N-m+1):
                inside = {PID[p] for p in POINTS if ox <= p[0] < ox+m and oy <= p[1] < oy+m}
                outside = sorted(all_ids - inside)
                cnf.at_least_k(outside, need_outside)

    # Reconstruct line occupancies for every nonzero-weight line of the exact
    # dual certificate.  h1 = [line has >=1 point], h2 = [line has >=2].
    # Since original geometry already gives <=2, defect is
    #   (2-count) = (not h2) + (not h1).
    cert_items: list[tuple[int,int]] = []
    for weight, variables, _name in four_groups():
        if weight <= 0:
            continue
        h1 = cnf.threshold_var(variables, 1)
        h2 = cnf.threshold_var(variables, 2)
        d1 = cnf.complement(h2)
        d2 = cnf.complement(h1)
        cert_items.append((d1, weight))
        cert_items.append((d2, weight))

    # Point cover excesses are the other side of the same exact certificate
    # identity.  Main-diagonal variables are already fixed, so subtract their
    # known contribution and keep only non-main variables here.
    for p in POINTS:
        if p[0] == p[1]:
            continue
        e = excess(p)
        if e:
            cert_items.append((PID[p], e))

    # Algebraic identity for exactly 34 points:
    #   weighted line defect + selected point excess = 112.
    # After fixing the main-diagonal pair, its excess is already known.
    cnf.weighted_exact(cert_items, residual)

    return cnf, (a,b), residual


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    cnf, pair, residual = build(args.index)
    cnf.write(args.output)
    print(f'branch={args.index} pair={pair[0]},{pair[1]} residual={residual} vars={cnf.nvars} clauses={len(cnf.clauses)}')


if __name__ == '__main__':
    main()
