#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, time
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix

N=22; PARITY=0; TARGET=34; DEN=187; SLACK=112
ROW_W=[63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63]
COL_W=ROW_W[:]
PLUS_W={-20:0,-18:0,-16:24,-14:44,-12:60,-10:72,-8:85,-6:99,-4:109,-2:115,0:117,2:115,4:109,6:99,8:85,10:72,12:60,14:44,16:24,18:0,20:0}
MINUS_W={0:0,2:0,4:0,6:22,8:40,10:54,12:67,14:80,16:92,18:100,20:104,22:104,24:100,26:92,28:80,30:67,32:54,34:40,36:22,38:0,40:0,42:0}
D_SMALL={10:15,11:16,17:26,18:27,19:29,20:30,21:32}

POINTS=[(x,y) for y in range(N) for x in range(N) if (x+y)%2==PARITY]
PID={p:i for i,p in enumerate(POINTS)}


def line_key(a,b):
    x1,y1=a; x2,y2=b
    dx=x2-x1; dy=y2-y1
    g=math.gcd(abs(dx),abs(dy))
    A=dy//g; B=-dx//g
    if A<0 or (A==0 and B<0): A=-A;B=-B
    return (A,B,A*x1+B*y1)

@lru_cache(None)
def maximal_lines():
    d=defaultdict(set)
    for i in range(len(POINTS)):
        for j in range(i+1,len(POINTS)):
            k=line_key(POINTS[i],POINTS[j]); d[k].add(i);d[k].add(j)
    return [tuple(sorted(v)) for v in d.values() if len(v)>=3]

ROWS=[[PID[(x,y)] for x in range(N) if (x+y)%2==0] for y in range(N)]
COLS=[[PID[(x,y)] for y in range(N) if (x+y)%2==0] for x in range(N)]
PLUS_KEYS=sorted(PLUS_W)
MINUS_KEYS=sorted(MINUS_W)
PLUS=[[PID[p] for p in POINTS if p[0]-p[1]==k] for k in PLUS_KEYS]
MINUS=[[PID[p] for p in POINTS if p[0]+p[1]==k] for k in MINUS_KEYS]

A_POINTS=[]
for d in (-2,2):
    for s in (16,18,20,22,24,26):
        p=((s+d)//2,(s-d)//2)
        assert p in PID
        A_POINTS.append(p)
A_POINTS=sorted(A_POINTS)
A_SET=set(A_POINTS)


def transpose_p(p): return (p[1],p[0])

def canonical_a2_pairs():
    reps={}
    for a,b in combinations(A_POINTS,2):
        q=tuple(sorted((a,b)))
        tq=tuple(sorted((transpose_p(a),transpose_p(b))))
        rep=min(q,tq)
        reps[rep]=rep
    return sorted(reps)


def point_cover(p):
    x,y=p
    return ROW_W[y]+COL_W[x]+PLUS_W[x-y]+MINUS_W[x+y]

def point_excess(p): return point_cover(p)-DEN

@lru_cache(None)
def affine_constraints(m):
    # Only copies where target parity corresponds to one checkerboard parity class:
    # sums of coordinates of both basis vectors are odd.
    M=D_SMALL[m]
    lim=21//(m-1)+1
    sets=set()
    rng=range(-lim,lim+1)
    for ux,uy,vx,vy in product(rng,rng,rng,rng):
        if ux==uy==0 or vx==vy==0: continue
        if ux*vy-uy*vx==0: continue
        if (ux+uy)%2!=1 or (vx+vy)%2!=1: continue
        corners=[(0,0),((m-1)*ux,(m-1)*uy),((m-1)*vx,(m-1)*vy),((m-1)*(ux+vx),(m-1)*(uy+vy))]
        minx=min(x for x,y in corners); maxx=max(x for x,y in corners)
        miny=min(y for x,y in corners); maxy=max(y for x,y in corners)
        if maxx-minx>21 or maxy-miny>21: continue
        for ox in range(-minx,22-maxx):
            for oy in range(-miny,22-maxy):
                ids=[]
                ok=True
                for i in range(m):
                    for j in range(m):
                        x=ox+i*ux+j*vx; y=oy+i*uy+j*vy
                        if not (0<=x<N and 0<=y<N): ok=False;break
                        if (x+y)%2==0: ids.append(PID[(x,y)])
                    if not ok: break
                if ok:
                    sets.add(tuple(sorted(ids)))
    return [(s,M) for s in sorted(sets)]

class Builder:
    def __init__(self):
        self.nx=len(POINTS)
        self.rows=[]; self.cols=[]; self.data=[]; self.lb=[];self.ub=[]
        self.var_names=[f"p_{x}_{y}" for x,y in POINTS]
    def newbin(self,name):
        i=self.nx;self.nx+=1;self.var_names.append(name);return i
    def add(self,coeff,lb=-np.inf,ub=np.inf):
        r=len(self.lb)
        for j,v in coeff.items():
            if v:
                self.rows.append(r);self.cols.append(j);self.data.append(float(v))
        self.lb.append(float(lb));self.ub.append(float(ub))
    def solve(self,time_limit=30.0,disp=False):
        A=coo_matrix((self.data,(self.rows,self.cols)),shape=(len(self.lb),self.nx)).tocsc()
        c=np.zeros(self.nx)
        res=milp(c,integrality=np.ones(self.nx),bounds=Bounds(np.zeros(self.nx),np.ones(self.nx)),
                 constraints=LinearConstraint(A,np.array(self.lb),np.array(self.ub)),
                 options={'time_limit':float(time_limit),'mip_rel_gap':0.0,'presolve':True,'disp':disp})
        return res


def build_model(A_exact=None,A_fixed=None,extra_affine=(10,11,19,20,21), row_twos=None,col_twos=None, omit_orientation=True):
    b=Builder()
    # all maximal lines
    for line in maximal_lines(): b.add({i:1 for i in line},ub=2)
    b.add({i:1 for i in range(len(POINTS))},lb=TARGET,ub=TARGET)
    # main diagonal pair (2,2),(3,3)
    for k in range(N): b.add({PID[(k,k)]:1},lb=int(k in (2,3)),ub=int(k in (2,3)))
    # certificate positive excess + threshold cuts
    excess={i:max(0,point_excess(p)) for i,p in enumerate(POINTS)}
    b.add({i:e for i,e in excess.items() if e>0},ub=SLACK)
    for t in sorted(set(e for e in excess.values() if e>0)):
        b.add({i:1 for i,e in excess.items() if e>=t},ub=SLACK//t)
    # certificate defect budget (redundant but useful)
    fam=[]
    for k,g in enumerate(ROWS): fam.append((ROW_W[k],g))
    for k,g in enumerate(COLS): fam.append((COL_W[k],g))
    for k,g in zip(PLUS_KEYS,PLUS): fam.append((PLUS_W[k],g))
    for k,g in zip(MINUS_KEYS,MINUS): fam.append((MINUS_W[k],g))
    # sum w*(2-count)<=112 -> -sum w*count <=112-2sumw
    coeff=defaultdict(float); const=0
    for w,g in fam:
        const+=2*w
        for i in g: coeff[i]-=w
    b.add(dict(coeff),ub=SLACK-const)
    # force lines whose weight exceeds residual after fixed positive-excess points
    fixed_selected={(2,2),(3,3)}
    if A_fixed: fixed_selected.update(A_fixed)
    used=sum(max(0,point_excess(p)) for p in fixed_selected)
    residual=SLACK-used
    for k,g in enumerate(ROWS):
        if ROW_W[k]>residual: b.add({i:1 for i in g},lb=2,ub=2)
    for k,g in enumerate(COLS):
        if COL_W[k]>residual: b.add({i:1 for i in g},lb=2,ub=2)
    for k,g in zip(PLUS_KEYS,PLUS):
        if PLUS_W[k]>residual: b.add({i:1 for i in g},lb=2,ub=2)
    for k,g in zip(MINUS_KEYS,MINUS):
        if MINUS_W[k]>residual: b.add({i:1 for i in g},lb=2,ub=2)
    # two-flags for rows/cols/diags
    def flags(groups,prefix):
        out=[]
        for gi,g in enumerate(groups):
            t=b.newbin(f'{prefix}_{gi}_two'); out.append(t)
            # count<=1+t; count>=2t
            d={i:1 for i in g};d[t]=-1;b.add(d,ub=1)
            d={i:1 for i in g};d[t]=-2;b.add(d,lb=0)
        return out
    rt=flags(ROWS,'row'); ct=flags(COLS,'col'); pt=flags(PLUS,'plus'); mt=flags(MINUS,'minus')
    b.add({i:1 for i in pt},lb=16,ub=16)
    b.add({i:1 for i in mt},lb=16,ub=16)
    b.add({i:1 for i in rt},lb=12,ub=17)
    b.add({i:1 for i in ct},lb=12,ub=17)
    if not omit_orientation:
        d={i:1 for i in rt};
        for i in ct:d[i]=d.get(i,0)-1
        b.add(d,ub=0)
    if row_twos is not None: b.add({i:1 for i in rt},lb=row_twos,ub=row_twos)
    if col_twos is not None: b.add({i:1 for i in ct},lb=col_twos,ub=col_twos)
    # A
    if A_exact is not None: b.add({PID[p]:1 for p in A_POINTS},lb=A_exact,ub=A_exact)
    if A_fixed is not None:
        fixed=set(A_fixed)
        for p in A_POINTS: b.add({PID[p]:1},lb=int(p in fixed),ub=int(p in fixed))
    # prior solved-board affine constraints
    for m in extra_affine:
        for ids,M in affine_constraints(m): b.add({i:1 for i in ids},ub=M)
    return b


def verify_solution(x):
    sel=[POINTS[i] for i,v in enumerate(x[:len(POINTS)]) if v>0.5]
    assert len(sel)==34 and len(set(sel))==34
    assert all((x+y)%2==0 for x,y in sel)
    bad=[]
    for a,b,c in combinations(sel,3):
        if (b[0]-a[0])*(c[1]-a[1])==(b[1]-a[1])*(c[0]-a[0]): bad.append((a,b,c));break
    return sel,bad


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['a2','a1','a0','one'],default='a2')
    ap.add_argument('--time',type=float,default=20)
    ap.add_argument('--index',type=int)
    ap.add_argument('--out',type=Path,default=Path('/mnt/data/n22_local/results.jsonl'))
    args=ap.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.mode=='a2': cases=canonical_a2_pairs()
    elif args.mode=='a1': cases=[(p,) for p in A_POINTS if p[0]<p[1]]
    elif args.mode=='a0': cases=[tuple()]
    else:
        allc=canonical_a2_pairs();cases=[allc[args.index]]
    for idx,case in enumerate(cases):
        if args.index is not None and args.mode!='one' and idx!=args.index: continue
        t=time.time(); b=build_model(A_exact=len(case),A_fixed=case)
        res=b.solve(args.time)
        rec={'mode':args.mode,'index':idx,'case':case,'status':int(res.status),'message':res.message,'time':time.time()-t,'nvars':b.nx,'ncons':len(b.lb),'fun':None if res.fun is None else float(res.fun)}
        if res.x is not None:
            sel,bad=verify_solution(res.x);rec['solution']=sel;rec['bad']=bad
        print(json.dumps(rec,default=list),flush=True)
        with args.out.open('a',encoding='utf8') as f:f.write(json.dumps(rec,default=list)+'\n')

if __name__=='__main__': main()
