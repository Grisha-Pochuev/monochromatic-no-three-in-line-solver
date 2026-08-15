#!/usr/bin/env python3
"""Dependency-free exact verification of 16 n=22 refined LP exclusions.

Five integer Farkas certificates are stored below in compressed form.  Four
parity-preserving board symmetries (identity, transpose, 180-degree rotation,
and anti-diagonal reflection) carry them to exactly 16 weight-35 refined
cases:

* all four cases with no old underfull >=40 line and exactly three of
  row2,row19,col2,col19 underfull;
* for each of sum=8 and sum=34, all six cases with that sum-line underfull
  and exactly two of row2,row19,col2,col19 underfull.

For every transformed certificate, nonnegative integer multipliers combine
valid inequalities a_j x <= b_j so that every variable coefficient cancels
exactly while the weighted right-hand side is negative.  Thus 0 <= negative,
a contradiction.  No floating-point arithmetic and no SAT solver are used by
this verifier.
"""
from __future__ import annotations

import base64
import itertools
import json
import math
import zlib

N = 22
TARGET = 34
POINTS = [(x,y) for y in range(N) for x in range(N) if (x+y)%2 == 0]
PID = {p:i for i,p in enumerate(POINTS)}
assert len(POINTS) == 242

ROW = [63,48,35,24,15,8,3,0,0,0,0,0,0,0,0,3,8,15,24,35,48,63]
COL = ROW[:]
DIFF = {-20:0,-18:0,-16:24,-14:44,-12:60,-10:72,-8:85,-6:99,-4:109,
        -2:115,0:117,2:115,4:109,6:99,8:85,10:72,12:60,14:44,16:24,
        18:0,20:0}
SUM = {0:0,2:0,4:0,6:22,8:40,10:54,12:67,14:80,16:92,18:100,
       20:104,22:104,24:100,26:92,28:80,30:67,32:54,34:40,36:22,
       38:0,40:0,42:0}

# zlib-compressed, base85-encoded JSON with five representative integer
# certificates.  The verifier below decodes it and checks every integer.
DATA_B85 = r'''c-rk-O^+nE4gD{Dt^tbFSJeW^!RH*4lQCE<>~U;hy*6fM9R!B|drD$;58q?=Os^M7E`1b>q9lrv-YZeRA3h!4sZNLI50C$Rcs{&Kc{)5k{QCIt^ziBV!}CwSJv<%Wef#?+`{Acg58uE4?!(i=;ho5I`26YnhsPg2fBg9V$A=HU{X3OS@7u%UFaJ7BI;C<y?FCu)(s#dn+&|rKZT$H3{^|42hj(|Ispp5spL;V~{l6Wid6H?qpQLV;hCrsfA<_0CnTKEol{-b9F3Ovz`f6R`1e;0)!JSDoL!~Z(O3T(k!CIS01(c)@qoCH1EvTj_x;x4Ws%328ZkGu)O1;0^W#|P7BkDaMS9KBkO2ae^k(^A;!<3hpC7jPqlJ2J!1lwTI=UX#^MoN%0t|Tki?OoQ`WeMS>e(+-uDU3Y_oea%yX0rGFP$}$ZtwE>4xHdC2gpw{{@|O@uX%2zJA=tGvMCFJ!Y%oD&&Bp-5E{I=DrW3}SYS5|9Z6;|!XL0j5A45-2sXJuf1O9%P4uAbi%7@LgdEg(L#CD^jrIVxw$sV9xW*gH<^v&JDwwK*Wy{x_5PDQcrFJ;BD&ZOVJy%d$ob8j82XR;3Ebt>>#rjyf0IpOzZs-Qmia`M)(oKe3`4I6KuEz@ZY?v3O3g4O2{wx?pn;?j%BcXcZl-&HJU(kFA$C;p{au-JMrxq+=<dsMD|VEDaYb!li_squL%MRg;`@-oWVkG%`3A3O;%S7DnnR<L&fmfI+M7xXgtpbNkWq*2I(G-^Y+6SM6$-Vus1(8~}6T>w!)g3MLe=GLi%LEOs_#a#elOd5quER$qfR$Tz=iUgUetdsCU7GBAuF^??}wgwc;;{br2XXUMDrM-u@I_14id9zdA?WoE)s+`R<1kH_Hg+@O1azAp?SjmK*8oB>tVtl&hKY>p>9Nnfh&xlXcd;y^5SqnqdQf3CJL9N5olKnY78+1)=4&b%S#UJQt2>t18h*o4ioy_HUS|*0Ml9B|Zn~R6hhINzHfNfLLHK5y+N{je5&1nq?H_tgmjH{a0fO7LPuV-+sRz!?lxH?ga;CDwGB`-O^-&)rIfXiA_fWT6#t6k1Hw@a$jB_QJ@FWx<3V=p_R;~-1iu0dqi>2wb58*X0L0Gwe;o1s~X!H&XwAe{g;M&^#G<8TFoy;zV`@RdPrAO6Wgz51{|0&wqvcEsQWdb`L^+Yy-KNDQ0%)s%MGORLS|51Ke)cn%h&s2Y>e9TK5EFD6=ZLyhKa2mE0joLh!zKC`yYuEGxd!-74#2-Dy(c?s};T?792%ko44V9YxS@Vn262Y_F<?G58#tm!jejgeY7)J`k{S5Z4Z!)KQ&1hgX<GV82?W1JQV&<v2;3FBOQq8i(@5ZRC_LVQDIWyayoSXqW7mziit63NI!q~zjJ2q2$P-po{@D_~|Y7U-gOi8Gt0m%kc@m+-r&ned=(6D%2E1@&a@^Q*=8Eb*A94DIGA6PoO?tqZd&NB-L2Qw{l6N|_i}Zo-_atlp0WhBIhbDon&`twhD@+?b5%>@a+T&JB8&T<-@#YwJoBZFN2|l2(?&G)=u97nrX>t$g<fS8K~kY)z!CMA)|Vl8LiH+s4|w?>cqL4n3|g>&Cp?d<^R4hdj94wlOV4=Oite7#((Qn1%^3TIc*LX1p@fb4zjOdTzNIRr6tIT+PqEF+lX6S(4lm^FSPm*@ro{27HhjSMw4hYrdLMKs3HHIOv2CLF}yAhk&*Q{J3{M=$*4OLf{~Rn?v4JlxU-$DkF|KpSx)o&Tbr{!|cPVu?Aq-TMK^wG5guOIAJUs_4M&><P-a8{1e@26ckpNnTJiptieLHQ+Xz;3QNw&D#VM?Rd9h3R=>H3S%>{+P*m5P(OOtUMr<K6jN1C47?p(`b8y?TGXI60*Q&uh<spI{+z^98ml_=eZHN;1w!vXy>>AFS-u?nXVGJA2tujPzXshX<KUO>-o9QgjAJo~|JRHPE#^JQy3A^vnPU16@cz^~*vBA{N%e@D7GA||2d0CmiBV^d^ckFYH#Fwi`{L8h{|CPhv`1*~n-}w5CuiyCk|AMb`l>b*q{PAA!#^G-q{>I^N9R9}PZyf%{;cp!N#^JB$@b!8Q|K>&f1rASHpyv`rDcSE%L#m@f+TbyBG&66{S7eR~v-6lI$_b#C@<hvZd7^Svo@fnZ{Po1qnKJcW%Mx9$$`Y+1OSFb8QDs(LnNn-u${J{Ky(R^e0tb|ijCQ>u1+<0~(8_c)Uy%Z;Aq6xu=e#B-loCfT<%BL*<%E`3azbAir35}HSEPXAcqQtzkS4kWo%L**s0IqSN80OYqMQ>-d7?+^2OIUPd7=xYi5dmGm^NzkuMzi?aw(70Xdax0lrwcE?G!MsQgcfB37b2Uclt)2sS+{zvb@qnbmz+wM>BDlL<HumGD8b-kVFLJtxQlMULnLP5^;+1W@cz%Dv_8-K*}Bp4EHOsicFlMzL^@DnM!D24Hq*(^V!VMMC70_GpJva8LHd~&hu=P2x?fpFzhd1kUFYDf=Y>@3ulfR)X!g#TiPgd)Bt^AIG--(nl7AbYPel5=br9RoAJ54m3-RX$|QX=ar95;i7v0gQ+&Gg7Cv1r;M1BIpW^TSs4~!KV|<$MFs7GHJ7irYTs0NOta%BbbqSy~1<+bs0Ika$L2JnYw613^lJXottIRE;R@DGoQ-G}^E#OuL&waz!cv(bVHTX~hcBT6YK`+kdBq_k@{xdOv*LbHx7h<Zh=RKqs`q7PJF+jTpK+DE6c<*!>Qy9~(!kBgmnAT0;=`w{u?GiC8g+~mv6hrMyq;(8iYrwD+Xes-NI$e~cfNE6(s$BxA)d*|pRtzWf1Y=VPsFgy@O|ieWSW8SYbWrw$Tb=BPTivf4yHuFJ4ybA+r0V}o4D6|V0Z}SmCJ5gp5ExauH-G~S$_7@|+t2i#CLd?;<;o!Ag+U^$8^A8#79@9uSHvn69+Vjx7QQF&8W}AV1i%KD2`>xZ5Xj1iS?GQsU3!Y8Sj>o^4R0#~ZWTh@%5Sy2MkW(>X8^xu7m5HV6U;W0O`u)q{y-bSb}vX&L)fGc5l}+@{HDubH{TBkUk_-&^13pZ*MR2nnhhIL?n$C&S^LW`zBK@M4RGEV;iJQ-k_5ZLZ_0MmUoN74J<9?zzYkNQ0T_GqPk$!@7=2`Brvl+>;7x9j_*oghE5lXElEjsS%~k^U`%^PzK7hLk>twRh2=MQ(&%*OF+~cs0ae~a8U|~*>i4!E|1c`pf!@eyGKXId1o#XbuGOcjOnb8P;{XGQGit>r4eB_;d<>p#3X5m_~AM0>tDL<$rfoV9SJ71}J<16=n{0BO5=>h'''


def canonical_line(a: tuple[int,int], b: tuple[int,int]) -> tuple[int,int,int]:
    x1,y1=a; x2,y2=b
    aa=y2-y1; bb=x1-x2; cc=-(aa*x1+bb*y1)
    g=math.gcd(math.gcd(abs(aa),abs(bb)),abs(cc))
    aa//=g; bb//=g; cc//=g
    if aa<0 or (aa==0 and bb<0): aa,bb,cc=-aa,-bb,-cc
    return aa,bb,cc


def group_weight(family: str, key: int) -> int:
    if family=='row': return ROW[key]
    if family=='col': return COL[key]
    if family=='diff': return DIFF[key]
    if family=='sum': return SUM[key]
    raise AssertionError(f'bad family {family}')


def group_points(family: str, key: int) -> list[tuple[int,int]]:
    if family=='row': return [p for p in POINTS if p[1]==key]
    if family=='col': return [p for p in POINTS if p[0]==key]
    if family=='diff': return [p for p in POINTS if p[0]-p[1]==key]
    if family=='sum': return [p for p in POINTS if p[0]+p[1]==key]
    raise AssertionError(f'bad family {family}')


def transform_point(p: tuple[int,int], op: str) -> tuple[int,int]:
    x,y=p
    if op=='id': return x,y
    if op=='tr': return y,x
    if op=='rot': return N-1-x,N-1-y
    if op=='anti': return N-1-y,N-1-x
    raise AssertionError(op)


def transform_group(family: str, key: int, op: str) -> tuple[str,int]:
    if op=='id': return family,key
    if op=='tr':
        if family=='row': return 'col',key
        if family=='col': return 'row',key
        if family=='diff': return 'diff',-key
        return 'sum',key
    if op=='rot':
        if family in ('row','col'): return family,N-1-key
        if family=='diff': return 'diff',-key
        return 'sum',2*(N-1)-key
    if op=='anti':
        if family=='row': return 'col',N-1-key
        if family=='col': return 'row',N-1-key
        if family=='diff': return 'diff',key
        return 'sum',2*(N-1)-key
    raise AssertionError(op)


def transform_ref(ref: list, op: str) -> list:
    kind=ref[0]
    if kind=='L':
        aa,bb,cc=map(int,ref[1:])
        members=[p for p in POINTS if aa*p[0]+bb*p[1]+cc==0]
        assert len(members)>=3
        a,b=transform_point(members[0],op),transform_point(members[1],op)
        return ['L',*canonical_line(a,b)]
    if kind=='T': return ref[:]
    if kind in ('U','S+','S-'):
        fam,key=transform_group(ref[1],int(ref[2]),op)
        return [kind,fam,key]
    if kind in ('B+','B-'):
        x,y=transform_point((int(ref[1]),int(ref[2])),op)
        return [kind,x,y]
    raise AssertionError(ref)


def transform_pattern(pattern: set[tuple[str,int]], op: str) -> frozenset[tuple[str,int]]:
    return frozenset(transform_group(f,k,op) for f,k in pattern)


def inequality(ref: list, underfull: frozenset[tuple[str,int]]) -> tuple[dict[int,int],int]:
    kind=ref[0]
    if kind=='L':
        aa,bb,cc=map(int,ref[1:])
        members=[p for p in POINTS if aa*p[0]+bb*p[1]+cc==0]
        assert len(members)>=3
        return {PID[p]:1 for p in members},2
    if kind=='T':
        if ref[1]=='<=34': return {i:1 for i in range(len(POINTS))},34
        assert ref[1]=='>=34'
        return {i:-1 for i in range(len(POINTS))},-34
    if kind in ('U','S+','S-'):
        fam,key=ref[1],int(ref[2])
        pair=(fam,key)
        w=group_weight(fam,key)
        assert w>=35
        members=group_points(fam,key)
        if kind=='U':
            assert pair in underfull
            return {PID[p]:1 for p in members},1
        assert pair not in underfull
        if kind=='S+': return {PID[p]:1 for p in members},2
        return {PID[p]:-1 for p in members},-2
    if kind in ('B+','B-'):
        p=(int(ref[1]),int(ref[2])); assert p in PID
        return {PID[p]:(1 if kind=='B+' else -1)},(1 if kind=='B+' else 0)
    raise AssertionError(ref)


def verify_certificate(rep: dict, op: str) -> frozenset[tuple[str,int]]:
    original=frozenset((f,int(k)) for f,k,_w in rep['underfull_heavy35'])
    under=transform_pattern(set(original),op)
    coeff=[0]*len(POINTS)
    rhs=0
    for ref,mult in rep['terms']:
        assert isinstance(mult,int) and mult>=0
        tref=transform_ref(ref,op)
        row,b=inequality(tref,under)
        for i,a in row.items(): coeff[i]+=mult*a
        rhs+=mult*b
    assert all(v==0 for v in coeff)
    assert rhs==int(rep['rhs_sum'])<0
    return under


def main() -> None:
    raw=zlib.decompress(base64.b85decode(DATA_B85.encode('ascii')))
    data=json.loads(raw)
    assert data['n']==N and data['target']==TARGET
    assert len(data['representatives'])==5

    new35={('row',2),('row',19),('col',2),('col',19)}
    expected=set()
    for c in itertools.combinations(sorted(new35),3): expected.add(frozenset(c))
    for s in (8,34):
        for c in itertools.combinations(sorted(new35),2):
            expected.add(frozenset(set(c)|{('sum',s)}))
    assert len(expected)==16

    covered=set()
    for rep in data['representatives']:
        for op in ('id','tr','rot','anti'):
            pattern=verify_certificate(rep,op)
            if pattern in expected: covered.add(pattern)

    assert covered==expected
    print('PASS exact n22 Farkas certificates representatives=5 cases=16 points=242')


if __name__=='__main__':
    main()
