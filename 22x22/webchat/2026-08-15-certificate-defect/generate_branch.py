#!/usr/bin/env python3
"""Safe exact SAT branches for the n=22 parity-0 target-34 question.

The branch split is derived only from the verified rational four-direction
certificate with denominator 187 and target-34 slack 112.  Among certificate
lines of weight at least 40, the three lines of weight >112 are always
saturated.  Any other underfull line spends at least its weight from the
112-unit defect budget, so at most two such lines can be underfull and a pair
is possible only when its two weights sum to at most 112.  Enumerating the
actual underfull subset gives exactly 140 complete branches.

No transpose lex-leader, row/column orientation cut, or heuristic restriction
is used.
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

POINTS = [(x, y) for y in range(N) for x in range(N) if (x + y) % 2 == 0]
PID = {p: i + 1 for i, p in enumerate(POINTS)}
Point = tuple[int, int]


def canonical_line(a: Point, b: Point) -> tuple[int,int,int]:
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


def certificate_groups() -> list[tuple[str,int,int,list[int]]]:
    result = []
    for y, w in enumerate(ROW):
        result.append(('row', y, w, [PID[p] for p in POINTS if p[1] == y]))
    for x, w in enumerate(COL):
        result.append(('col', x, w, [PID[p] for p in POINTS if p[0] == x]))
    for d, w in DIFF.items():
        result.append(('diff', d, w, [PID[p] for p in POINTS if p[0] - p[1] == d]))
    for s, w in SUM.items():
        result.append(('sum', s, w, [PID[p] for p in POINTS if p[0] + p[1] == s]))
    assert len(result) == 87
    return result

GROUPS = certificate_groups()


def point_excess(p: Point) -> int:
    x, y = p
    value = ROW[y] + COL[x] + DIFF[x-y] + SUM[x+y] - Q
    assert value >= 0
    return value


def branch_subsets() -> list[tuple[int,...]]:
    heavy = [i for i, (_fam,_key,w,_g) in enumerate(GROUPS) if w >= 40]
    forced = {i for i in heavy if GROUPS[i][2] > SLACK}
    candidates = [i for i in heavy if i not in forced]
    result: list[tuple[int,...]] = [()]
    result.extend((i,) for i in candidates)
    for a, b in itertools.combinations(candidates, 2):
        if GROUPS[a][2] + GROUPS[b][2] <= SLACK:
            result.append((a,b))
    assert len(heavy) == 37
    assert len(forced) == 3
    assert len(candidates) == 34
    assert len(result) == 140
    return result

BRANCHES = branch_subsets()


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

    def threshold_var(self, variables: list[int], k: int) -> int:
        """Return a variable equivalent to sum(variables) >= k."""
        if k <= 0:
            z = self.new(); self.add(z); return z
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
                # (A or (x and B)) -> s
                if A:
                    self.add(-A, s)
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
        return old[k]

    def require_at_least(self, variables: list[int], k: int) -> None:
        if k <= 0:
            return
        self.add(self.threshold_var(variables, k))

    def require_at_most(self, variables: list[int], k: int) -> None:
        if k >= len(variables):
            return
        self.add(-self.threshold_var(variables, k + 1))

    def exact_cardinality(self, variables: list[int], k: int) -> None:
        self.require_at_least(variables, k)
        self.require_at_most(variables, k)

    def weighted_at_most(self, items: list[tuple[int,int]], bound: int) -> None:
        """Exact overflow-detecting threshold DP for positive integer weights."""
        items = [(x,w) for x,w in items if w > 0]
        if bound < 0:
            self.add_clause([])
            return
        old = [0] * (bound + 1)
        for x, w in items:
            if w > bound:
                self.add(-x)
                continue
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


def make_saturation_var(cnf: CNF, variables: list[int], name: str) -> int:
    """Boolean sat <-> at least two selected points on this certificate line.

    The global collinear-triple clauses imply at most two on every group of
    length >=3; groups of length 1 or 2 are naturally at most two.  Thus sat
    is exactly the occupancy-two flag.
    """
    sat = cnf.new()
    # sat -> count >= 2: forbid count 0 or 1 when sat is true.
    cnf.add_clause([-sat] + variables)
    for omit in range(len(variables)):
        cnf.add_clause([-sat] + variables[:omit] + variables[omit+1:])
    # count >= 2 -> sat.
    for a, b in itertools.combinations(variables, 2):
        cnf.add(-a, -b, sat)
    return sat


def build(branch_index: int) -> tuple[CNF, dict]:
    if not 0 <= branch_index < len(BRANCHES):
        raise SystemExit(f'branch index must be 0..{len(BRANCHES)-1}')
    underfull = set(BRANCHES[branch_index])
    spent = sum(GROUPS[i][2] for i in underfull)
    residual = SLACK - spent
    assert residual >= 0

    cnf = CNF()

    # Exact original geometry: every maximal same-parity grid line has <=2.
    for line in maximal_lines():
        for a, b, c in itertools.combinations(line, 3):
            cnf.add(-a, -b, -c)

    # Ask exactly for the only unresolved integer target.
    cnf.exact_cardinality(list(range(1, len(POINTS) + 1)), TARGET)

    # Occupancy-two flags for all four certificate families.
    sat = []
    for family, key, weight, variables in GROUPS:
        sat.append(make_saturation_var(cnf, variables, f'{family}_{key}'))

    heavy = [i for i, (_fam,_key,w,_g) in enumerate(GROUPS) if w >= 40]
    for i in heavy:
        if i in underfull:
            cnf.add(-sat[i])
        else:
            cnf.add(sat[i])

    # After spending at least the weights of the explicitly underfull heavy
    # lines, threshold cover cuts constrain every remaining certificate line.
    positive_weights = sorted({w for _f,_k,w,_g in GROUPS if w > 0}, reverse=True)
    for threshold in positive_weights:
        eligible = [i for i, (_f,_k,w,_g) in enumerate(GROUPS)
                    if i not in underfull and w >= threshold]
        if not eligible:
            continue
        max_under = residual // threshold
        required_saturated = len(eligible) - max_under
        if required_saturated > 0:
            cnf.require_at_least([sat[i] for i in eligible], required_saturated)

    # Generic occupancy-count consequences of 34 points distributed over the
    # four parallel line families.
    row_sat = sat[0:22]
    col_sat = sat[22:44]
    diff_sat = sat[44:65]   # 21 even differences -20..20
    sum_sat = sat[65:87]    # 22 even sums 0..42
    cnf.require_at_least(row_sat, 12);  cnf.require_at_most(row_sat, 17)
    cnf.require_at_least(col_sat, 12);  cnf.require_at_most(col_sat, 17)
    cnf.require_at_least(diff_sat, 13); cnf.require_at_most(diff_sat, 17)
    cnf.require_at_least(sum_sat, 12);  cnf.require_at_most(sum_sat, 17)

    # Certificate identity D + E = 112.  The fixed underfull lines already
    # spend at least 'spent', so selected point-cover excess is <= residual.
    excess_items = [(PID[p], point_excess(p)) for p in POINTS if point_excess(p) > 0]
    cnf.weighted_at_most(excess_items, residual)

    meta = {
        'branch': branch_index,
        'underfull': [
            {'family': GROUPS[i][0], 'key': GROUPS[i][1], 'weight': GROUPS[i][2]}
            for i in sorted(underfull)
        ],
        'minimum_defect_spent': spent,
        'residual_budget': residual,
        'vars': cnf.nvars,
        'clauses': len(cnf.clauses),
    }
    return cnf, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    cnf, meta = build(args.index)
    cnf.write(args.output)
    print(meta)


if __name__ == '__main__':
    main()
