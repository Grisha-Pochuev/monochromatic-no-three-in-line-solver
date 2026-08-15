#!/usr/bin/env python3
"""Generate one rigorously covering SAT branch for the n=22 monochromatic problem.

The formula asks for a 34-point parity-0 set with no collinear triple.
It uses only:
  * the original no-three-in-line constraints;
  * the already checked four-direction dual certificate for n=22;
  * 180-degree rotation to choose one representative of the two-point
    occupancy pattern on the forced main diagonal x-y=0.

No transpose lex-leader or row/column orientation cut is used.
"""
from __future__ import annotations

import argparse
import itertools
import math
from collections import defaultdict
from pathlib import Path

N = 22
TARGET = 34
PARITY = 0
Q = 187
OBJECTIVE_NUMERATOR = 6470
SLACK = OBJECTIVE_NUMERATOR - TARGET * Q  # 112

ROW = [63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63]
COL = ROW[:]
DIFF = {-20:0,-18:0,-16:24,-14:44,-12:60,-10:72,-8:85,-6:99,-4:109,
        -2:115,0:117,2:115,4:109,6:99,8:85,10:72,12:60,14:44,16:24,
        18:0,20:0}
SUM = {0:0,2:0,4:0,6:22,8:40,10:54,12:67,14:80,16:92,18:100,
       20:104,22:104,24:100,26:92,28:80,30:67,32:54,34:40,36:22,
       38:0,40:0,42:0}

POINTS = [(x, y) for y in range(N) for x in range(N) if (x + y) % 2 == PARITY]
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
            eq = canonical_line(a, POINTS[j])
            by_eq[eq].add(i + 1)
            by_eq[eq].add(j + 1)
    return [tuple(sorted(v)) for v in by_eq.values() if len(v) >= 3]


def branch_pairs() -> list[tuple[int,int]]:
    """Pairs on x=y modulo the safe 180-degree rotation k -> 21-k."""
    result = []
    for a, b in itertools.combinations(range(N), 2):
        pair = (a, b)
        rotated = tuple(sorted((N - 1 - a, N - 1 - b)))
        if pair <= rotated:
            result.append(pair)
    assert len(result) == 121
    return result


def excess(point: tuple[int,int]) -> int:
    x, y = point
    value = ROW[y] + COL[x] + DIFF[x-y] + SUM[x+y] - Q
    assert value >= 0
    return value


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

    def at_least_k(self, variables: list[int], k: int) -> None:
        """Exact threshold recurrence s[i,j] <-> (#true in prefix i >= j)."""
        old = [0] * (k + 1)
        for i, x in enumerate(variables, start=1):
            new = [0] * (k + 1)
            for j in range(1, min(k, i) + 1):
                s = self.new()
                new[j] = s
                A = old[j]
                B_true = (j == 1)
                B = 0 if B_true else old[j-1]

                # A -> s
                if A:
                    self.add(-A, s)
                # x & B -> s
                if B_true:
                    self.add(-x, s)
                elif B:
                    self.add(-x, -B, s)

                # s -> A or x
                if A:
                    self.add(-s, A, x)
                else:
                    self.add(-s, x)
                # s -> A or B
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
        self.add(old[k])

    def weighted_at_most(self, items: list[tuple[int,int]], bound: int) -> None:
        """Generalised sequential threshold encoding.

        State t means the prefix weight is at least t.  Only implications
        forced by a real prefix sum are needed for an at-most constraint.
        Overflow at bound+1 is forbidden.
        """
        old = [0] * (bound + 1)
        for x, w in items:
            assert 0 < w <= bound
            new = [0] * (bound + 1)
            for t in range(1, bound + 1):
                s = self.new()
                new[t] = s
                if old[t]:
                    self.add(-old[t], s)
                if t <= w:
                    self.add(-x, s)
                elif old[t-w]:
                    self.add(-x, -old[t-w], s)
            need = bound + 1 - w
            if need <= 0:
                self.add(-x)
            elif old[need]:
                self.add(-x, -old[need])
            old = new

    def write(self, path: Path) -> None:
        with path.open('w', encoding='ascii') as out:
            out.write(f'p cnf {self.nvars} {len(self.clauses)}\n')
            for clause in self.clauses:
                out.write(' '.join(map(str, clause)) + ' 0\n')


def build(branch_index: int, use_budget: bool) -> tuple[CNF, tuple[int,int]]:
    lines = maximal_lines()
    assert len(POINTS) == 242
    assert len(lines) == 2455
    assert sum(math.comb(len(line), 3) for line in lines) == 33946

    cnf = CNF()

    # Original condition: no line may contain three selected points.
    for line in lines:
        for a, b, c in itertools.combinations(line, 3):
            cnf.add(-a, -b, -c)

    # The four-direction rational certificate already proves < 35, so asking
    # for at least 34 is equivalent to asking for exactly 34 integer points.
    cnf.at_least_k(list(range(1, len(POINTS) + 1)), TARGET)

    # For target 34, certificate slack is 112.  Each of the three diff-lines
    # -2,0,+2 has dual weight >112, hence must be saturated.  Since the
    # original clauses impose <=2, we add >=2.  >=2 on m Boolean variables is
    # exactly the conjunction of the m clauses obtained by omitting one var.
    assert SLACK == 112
    assert all(DIFF[d] > SLACK for d in (-2, 0, 2))
    for d in (-2, 0, 2):
        variables = [PID[p] for p in POINTS if p[0] - p[1] == d]
        for omit in range(len(variables)):
            cnf.add_clause(variables[:omit] + variables[omit+1:])

    if use_budget:
        # A second exact consequence of the same rational certificate:
        # sum of point cover excesses is at most 112 in any 34-point solution.
        items = [(PID[p], excess(p)) for p in POINTS if excess(p) > 0]
        cnf.weighted_at_most(items, SLACK)

    pairs = branch_pairs()
    if not 0 <= branch_index < len(pairs):
        raise SystemExit(f'branch index must be 0..{len(pairs)-1}')
    a, b = pairs[branch_index]
    keep = {a, b}
    for k in range(N):
        v = PID[(k, k)]
        cnf.add(v if k in keep else -v)

    return cnf, (a, b)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--no-budget', action='store_true')
    args = ap.parse_args()
    cnf, pair = build(args.index, not args.no_budget)
    cnf.write(args.output)
    print(f'branch={args.index} pair={pair[0]},{pair[1]} vars={cnf.nvars} clauses={len(cnf.clauses)} budget={not args.no_budget}')


if __name__ == '__main__':
    main()
