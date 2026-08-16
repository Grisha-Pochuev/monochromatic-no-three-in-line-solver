#!/usr/bin/env python3
"""Discover and EXACTLY verify integer Farkas certificates for 94 weight-15 children.

The list CLOSED_CHILDREN was obtained by an LP screening of the current
rigorous weight-22 frontier. Screening alone is NOT a proof. This program
revisits every exact identity subcase of each listed count child, discovers a
nonnegative Farkas ray numerically, converts its support to an exact rational
solution, clears denominators to nonnegative INTEGER multipliers, and finally
checks with Python integers that all 242 point coefficients cancel and the
right-hand side is strictly negative.

There are 1,288 identity subcases. Every one is verified separately. No
symmetry (transpose or otherwise) is used for pruning, identification, or
certificate transport in this audit.

The numerical LP is only a certificate finder. Correctness is decided solely
by the final integer equalities/inequality. If exact reconstruction fails,
the program fails instead of declaring the subcase closed.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
import sympy as sy

import generate_refined_22_count as level22

N=22
TARGET=34
base=level22.base
POINTS=list(base.POINTS)
PID={p:i for i,p in enumerate(POINTS)}
assert len(POINTS)==242

CLOSED_CHILDREN=[
    (2,4),(4,4),(6,4),(11,1),(12,4),(13,3),(14,2),(15,3),(16,2),
    (21,4),(22,3),(23,2),(24,3),(25,2),(30,4),(31,3),(32,2),(33,3),
    (34,2),(39,4),(40,3),(41,2),(42,3),(43,2),(49,1),(50,1),(52,1),
    (53,1),(54,2),(55,1),(56,1),(57,2),(58,1),(59,1),(61,1),(62,1),
    (64,1),(65,1),(66,3),(75,4),(80,1),(93,4),(98,1),(111,3),(120,3),
    (129,4),(134,1),(147,4),(152,1),(165,3),(174,4),(175,3),(181,2),
    (184,2),(187,2),(190,2),(194,2),(198,1),(199,1),(200,1),(201,1),
    (216,2),(221,1),(222,1),(223,1),(224,1),(225,4),(226,3),(232,2),
    (235,2),(238,2),(241,2),(245,3),(247,3),(253,1),(256,1),(259,1),
    (262,1),(278,3),(296,3),(319,3),(321,3),(327,1),(330,1),(333,1),
    (336,1),(338,1),(339,1),(346,1),(347,1),(354,1),(388,1),(390,2),
    (394,1),
]
assert len(CLOSED_CHILDREN)==94

HEAVY35={i for i,(_f,_k,w,_g) in enumerate(base.GROUPS) if w>=35}
NEW24=tuple(level22.refined24.NEW24)
NEW22=tuple(level22.NEW22)
NEW15=tuple(i for i,(_f,_k,w,_g) in enumerate(base.GROUPS) if w==15)
assert len(NEW24)==6 and len(NEW22)==2 and len(NEW15)==4


def canon(a,b):
    x1,y1=a; x2,y2=b
    aa=y2-y1; bb=x1-x2; cc=-(aa*x1+bb*y1)
    g=math.gcd(math.gcd(abs(aa),abs(bb)),abs(cc))
    aa//=g; bb//=g; cc//=g
    if aa<0 or (aa==0 and bb<0): aa,bb,cc=-aa,-bb,-cc
    return aa,bb,cc


def all_maximal_lines():
    keys=set()
    for i,a in enumerate(POINTS):
        for b in POINTS[i+1:]:
            keys.add(canon(a,b))
    out=[]
    for aa,bb,cc in sorted(keys):
        members=[PID[p] for p in POINTS if aa*p[0]+bb*p[1]+cc==0]
        if len(members)>=3:
            out.append((('L',aa,bb,cc),members,2))
    return out


def group_members(index):
    """Return 0-based point indices by reconstructing the group geometrically.

    base.GROUPS[index][3] contains CNF variable IDs, not coordinate tuples.
    Reconstructing from (family,key) avoids depending on that encoding.
    """
    family,key,_weight,_variables=base.GROUPS[index]
    if family=='row':
        pts=[p for p in POINTS if p[1]==key]
    elif family=='col':
        pts=[p for p in POINTS if p[0]==key]
    elif family=='diff':
        pts=[p for p in POINTS if p[0]-p[1]==key]
    elif family=='sum':
        pts=[p for p in POINTS if p[0]+p[1]==key]
    else:
        raise AssertionError(f'bad group family {family!r}')
    return [PID[p] for p in pts]

BASE_ROWS=[]
BASE_B=[]
BASE_REFS=[]
for ref,members,rhs in all_maximal_lines():
    row={i:1 for i in members}
    BASE_ROWS.append(row); BASE_B.append(rhs); BASE_REFS.append(ref)
# target equality as two inequalities
BASE_ROWS.append({i:1 for i in range(242)}); BASE_B.append(TARGET); BASE_REFS.append(('T','<=34'))
BASE_ROWS.append({i:-1 for i in range(242)}); BASE_B.append(-TARGET); BASE_REFS.append(('T','>=34'))
# point bounds 0 <= x <= 1
for i,(x,y) in enumerate(POINTS):
    BASE_ROWS.append({i:1}); BASE_B.append(1); BASE_REFS.append(('B+',x,y))
    BASE_ROWS.append({i:-1}); BASE_B.append(0); BASE_REFS.append(('B-',x,y))


def sparse_from_rows(rows):
    rr=[]; cc=[]; dd=[]
    for r,row in enumerate(rows):
        for c,v in row.items():
            rr.append(r); cc.append(c); dd.append(v)
    return sp.csr_matrix((dd,(rr,cc)),shape=(len(rows),242),dtype=float)

BASE_A=sparse_from_rows(BASE_ROWS)
BASE_BV=np.asarray(BASE_B,dtype=float)


def identity_subcases(count22_index,k15):
    count24_index,k22=level22.CASES[count22_index]
    refined_index,k24=level22.refined24.CASES[count24_index]
    parent,extra35=level22.refined24.refined35.CASES[refined_index]
    fixed_under=set(base.BRANCHES[parent])|set(extra35)
    fixed_sat=set(HEAVY35)-fixed_under
    for u24t in itertools.combinations(NEW24,k24):
        u24=set(u24t); s24=set(NEW24)-u24
        for u22t in itertools.combinations(NEW22,k22):
            u22=set(u22t); s22=set(NEW22)-u22
            for u15t in itertools.combinations(NEW15,k15):
                u15=set(u15t); s15=set(NEW15)-u15
                yield fixed_under|u24|u22|u15, fixed_sat|s24|s22|s15


def build_identity(under,sat):
    rows=list(BASE_ROWS)
    bv=list(BASE_B)
    refs=list(BASE_REFS)
    for index in sorted(under):
        members=group_members(index)
        rows.append({i:1 for i in members}); bv.append(1)
        f,k,_w,_g=base.GROUPS[index]
        refs.append(('U',f,k))
    for index in sorted(sat):
        members=group_members(index)
        rows.append({i:-1 for i in members}); bv.append(-2)
        f,k,_w,_g=base.GROUPS[index]
        refs.append(('S-',f,k))
    A=sparse_from_rows(rows)
    return A,np.asarray(bv,dtype=float),refs,rows


def exact_certificate(under,sat):
    A,b,refs,rows=build_identity(under,sat)
    m=A.shape[0]
    # Find y>=0 with A^T y=0 and b^T y=-1.
    AF=sp.vstack([A.T,sp.csr_matrix(b.reshape(1,-1))],format='csr')
    beq=np.r_[np.zeros(242),-1.]
    res=linprog(np.ones(m),A_eq=AF,b_eq=beq,bounds=(0,None),method='highs',options={'presolve':True})
    if res.status!=0:
        raise AssertionError(f'failed to find Farkas ray: status={res.status} {res.message}')
    support=np.where(res.x>1e-9)[0]

    # Reconstruct the supported linear system exactly over Q.
    As=A[support,:]
    M=sp.vstack([As.T,sp.csr_matrix(b[support].reshape(1,-1))],format='csr')
    coo=M.tocoo()
    Ms=sy.MutableSparseMatrix(M.shape[0],M.shape[1],{
        (int(r),int(c)):int(round(v)) for r,c,v in zip(coo.row,coo.col,coo.data)
    })
    rhs=sy.Matrix([0]*242+[-1])
    solset=sy.linsolve((Ms,rhs))
    if solset is sy.EmptySet:
        raise AssertionError('exact supported system unexpectedly empty')
    sol=next(iter(solset))
    free=set().union(*(v.free_symbols for v in sol))
    if free:
        sol=tuple(v.subs({s:0 for s in free}) for v in sol)
    if any(v<0 for v in sol):
        raise AssertionError('exact reconstruction produced a negative multiplier')

    L=1
    for v in sol: L=math.lcm(L,int(v.q))
    mult=[int(v*L) for v in sol]
    g=0
    for q in mult: g=math.gcd(g,q)
    if g>1: mult=[q//g for q in mult]

    # Final proof check: Python integers only.
    coeff=[0]*242; rhs_sum=0; terms=[]
    for idx,q in zip(support,mult):
        if q==0: continue
        row=rows[int(idx)]
        for j,a in row.items(): coeff[j]+=q*int(a)
        rhs_sum+=q*int(b[int(idx)])
        terms.append((refs[int(idx)],q))
    if any(coeff):
        raise AssertionError(f'nonzero exact coefficient remains: max={max(map(abs,coeff))}')
    if rhs_sum>=0:
        raise AssertionError(f'Farkas rhs is not negative: {rhs_sum}')
    return terms,rhs_sum


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    records=[]; total=0
    for child_no,(parent,k15) in enumerate(CLOSED_CHILDREN):
        sub=0
        for under,sat in identity_subcases(parent,k15):
            terms,rhs=exact_certificate(under,sat)
            records.append({
                'count22_case':parent,
                'weight15_underfull_count':k15,
                'under_groups':[
                    [base.GROUPS[i][0],int(base.GROUPS[i][1]),int(base.GROUPS[i][2])]
                    for i in sorted(under)
                ],
                'rhs_sum':int(rhs),
                'terms':[[list(ref),int(q)] for ref,q in terms],
            })
            sub+=1; total+=1
        if sub==0: raise AssertionError('empty identity split')
        print(f'PASS child {child_no+1}/94 parent={parent} k15={k15} subcases={sub}',flush=True)
    assert total==1288, total
    if args.output:
        args.output.write_text(json.dumps({
            'n':22,'target':34,'children':CLOSED_CHILDREN,'identity_subcases':total,
            'certificates':records,
        },separators=(',',':'))+'\n',encoding='utf-8')
    print('PASS exact n22 weight15 Farkas children=94 identity_subcases=1288 symmetry=none points=242')

if __name__=='__main__':
    main()
