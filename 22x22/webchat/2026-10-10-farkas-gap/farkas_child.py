"""Exact Farkas (LP-infeasibility) certificates for n=22 safe profile children.
LP = linear relaxation of the symmetry-safe child model (no lex cut)."""
import sys, json, time
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import prove_upper_22x22_profile_child as M
from prove_upper_22x22_main_diagonal_pair import canonical_main_diagonal_pairs

def build_lp(child,rc=None):
    pi,pt,mt=M.decode_child(child); pair=canonical_main_diagonal_pairs()[pi]
    pts=M.allowed_points(); lines=M.build_maximal_lines(pts); cert=M.load_certificate()
    den=int(cert['denominator']); slack=int(cert['slack_numerator']); W=M.certificate_weights(cert)
    resid=slack-sum(M.point_cover((c,c),W)-den for c in pair)
    var={}
    def v(name):
        if name not in var: var[name]=len(var)
        return var[name]
    for p in pts: v(('p',p))
    R=[]  # (coeffs dict, sense, rhs) sense in '<=','=='
    for l in lines.values(): R.append(({v(('p',pts[i])):1 for i in l},'<=',2))
    R.append(({v(('p',p)):1 for p in pts},'==',34))
    ps=set(pair)
    for c in range(22): R.append(({v(('p',(c,c))):1},'==',int(c in ps)))
    exc={p:M.point_cover(p,W)-den for p in pts if p[0]!=p[1]}
    R.append(({v(('p',p)):e for p,e in exc.items() if e>0},'<=',resid))
    for t in sorted({e for e in exc.values() if e>0}):
        R.append(({v(('p',p)):1 for p,e in exc.items() if e>=t},'<=',resid//t))
    fam=[]
    for k in range(22): fam.append(('row',k,[p for p in pts if p[1]==k]))
    for k in range(22): fam.append(('column',k,[p for p in pts if p[0]==k]))
    for (f,k) in sorted(W):
        if f=='diag_plus': fam.append((f,k,[p for p in pts if p[0]-p[1]==k]))
        if f=='diag_minus': fam.append((f,k,[p for p in pts if p[0]+p[1]==k]))
    defect={}
    for f,k,g in fam:
        z=[v(('z',f,k,s)) for s in range(3)]
        R.append(({z[0]:1,z[1]:1,z[2]:1},'==',1))
        d={v(('p',p)):1 for p in g}; d[z[1]]=d.get(z[1],0)-1; d[z[2]]=-2
        R.append((d,'==',0))
        w=W[(f,k)]
        if w>resid: R.append(({z[2]:1},'==',1))
        if w: defect[z[1]]=defect.get(z[1],0)+w; defect[z[0]]=defect.get(z[0],0)+2*w
    R.append((defect,'<=',resid))
    def z2(f): return [var[('z',f,k,2)] for (ff,k,_) in fam if ff==f]
    rz,cz=z2('row'),z2('column')
    R.append(({i:1 for i in rz},'<=',17)); R.append(({i:-1 for i in rz},'<=',-12))
    R.append(({i:1 for i in cz},'<=',17)); R.append(({i:-1 for i in cz},'<=',-12))
    d={i:1 for i in rz}
    for i in cz: d[i]=d.get(i,0)-1
    R.append((d,'<=',0))
    if rc:
        R.append(({i:1 for i in rz},'==',rc[0])); R.append(({i:1 for i in cz},'==',rc[1]))
    R.append(({i:1 for i in z2('diag_plus')},'==',pt)); R.append(({i:1 for i in z2('diag_minus')},'==',mt))
    # expand to <= rows
    rows=[]
    for d,s,b in R:
        rows.append((d,b))
        if s=='==': rows.append(({k:-c for k,c in d.items()},-b))
    return rows,len(var)

def farkas(child,rc=None):
    rows,n=build_lp(child,rc); m=len(rows)
    # vars: y (m, 0..1), u (n, <=0). c=A^T y. maximize sum u - b^T y  s.t. u_i - c_i <=0
    I=[];J=[];V=[]
    for r,(d,b) in enumerate(rows):
        for k,c in d.items(): I.append(k);J.append(r);V.append(-c)
    for i in range(n): I.append(i);J.append(m+i);V.append(1)
    A=coo_matrix((V,(I,J)),shape=(n,m+n)).tocsr()
    obj=np.concatenate([np.array([b for _,b in rows],float),-np.ones(n)])
    res=linprog(obj,A_ub=A,b_ub=np.zeros(n),bounds=[(0,1)]*m+[(None,0)]*n,method='highs')
    margin=-res.fun
    if margin<=1e-7: return {'child':child,'rc':rc,'lp_infeasible':False,'margin':margin}
    y=[Fraction(max(0.0,float(val))).limit_denominator(10**6) for val in res.x[:m]]
    c=[Fraction(0)]*n; rhs=Fraction(0)
    for yr,(d,b) in zip(y,rows):
        if yr:
            rhs+=yr*b
            for k,cc in d.items(): c[k]+=yr*cc
    lhs=sum(min(Fraction(0),ci) for ci in c)  # min over [0,1]^n of c.x
    ok=lhs>rhs
    return {'child':child,'rc':rc,'lp_infeasible':True,'float_margin':margin,'exact_margin':str(lhs-rhs),'exact_ok':ok,
            'multipliers':{r:str(yr) for r,yr in enumerate(y) if yr}}
if __name__=='__main__':
    for ch in map(int,sys.argv[1:]):
        t=time.time(); r=farkas(ch); r.pop('multipliers',None); r['sec']=round(time.time()-t,1); print(json.dumps(r),flush=True)
