#!/usr/bin/env python3
"""Exhaustively test the weighted-threshold CNF encoder on small instances."""
from __future__ import annotations

import itertools

from exact_identity import weighted_threshold_var, require_weighted_at_least


class TinyCNF:
    def __init__(self,inputs: int):
        self.nvars=inputs
        self.clauses=[]
    def new(self):
        self.nvars+=1; return self.nvars
    def add(self,*lits):
        self.clauses.append(tuple(lits))


def clause_ok(clause,assignment):
    return any(assignment[abs(lit)] == (lit>0) for lit in clause)


def satisfying_extensions(cnf,input_values):
    first_aux=len(input_values)+1
    for bits in itertools.product((False,True),repeat=cnf.nvars-len(input_values)):
        a={i+1:v for i,v in enumerate(input_values)}
        for j,v in enumerate(bits,start=first_aux): a[j]=v
        if all(clause_ok(c,a) for c in cnf.clauses):
            yield a


def check_threshold(weights,threshold):
    n=len(weights)
    cnf=TinyCNF(n)
    result=weighted_threshold_var(cnf,[(i+1,w) for i,w in enumerate(weights)],threshold)
    for inputs in itertools.product((False,True),repeat=n):
        truth=sum(w for w,v in zip(weights,inputs) if v) >= threshold
        exts=list(satisfying_extensions(cnf,inputs))
        assert exts, (weights,threshold,inputs,'no extension')
        assert {a[result] for a in exts} == {truth}, (weights,threshold,inputs,truth)


def check_requirement(weights,threshold):
    n=len(weights)
    cnf=TinyCNF(n)
    require_weighted_at_least(cnf,[(i+1,w) for i,w in enumerate(weights)],threshold)
    for inputs in itertools.product((False,True),repeat=n):
        truth=sum(w for w,v in zip(weights,inputs) if v) >= threshold
        exists=any(satisfying_extensions(cnf,inputs))
        assert exists == truth, (weights,threshold,inputs,truth,exists)


def main():
    tests=[([2,3],1),([2,3],2),([2,3],4),([2,3],5),([1,2,4],3),([1,2,4],5)]
    for weights,t in tests:
        check_threshold(weights,t)
        check_requirement(weights,t)
    print(f'PASS weighted threshold exhaustive tests cases={len(tests)}')


if __name__=='__main__':
    main()
