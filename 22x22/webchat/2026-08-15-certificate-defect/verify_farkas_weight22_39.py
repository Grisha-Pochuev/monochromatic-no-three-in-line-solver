#!/usr/bin/env python3
"""Exact integer Farkas verification for 39 weight-22 count cases.

The 39 count cases listed in CLOSED_CASES are disjunctions over the identities
of the six weight-24 lines and two weight-22 lines that are underfull.  There
are 84 identity subcases in total.  A numerical LP search was used only to
find candidate rays.  The data below stores exact nonnegative INTEGER
multipliers.  This verifier uses no LP/SAT solver and no floating point.

For every covered identity subcase it combines valid inequalities A_j x<=b_j
and checks exactly that all 242 point coefficients cancel while the right-hand
side is negative.  Thus each identity gives 0 <= negative, a contradiction.
The four parity-preserving square symmetries are used only to transport an
already exact Farkas certificate; they do not identify/prune SAT branches.

This is deliberately unrelated to the old invalid transpose lex-leader rule.
"""
from __future__ import annotations

import base64
import itertools
import json
import zlib

import generate_refined_22_count as model
import verify_farkas_16 as sym

N=22
TARGET=34
CLOSED_CASES=[
  68,82,91,103,106,113,122,139,142,154,163,167,179,230,246,249,266,
  271,273,275,277,280,298,306,311,313,315,317,320,323,343,345,351,
  353,358,360,364,366,391,
]
assert len(CLOSED_CASES)==39

# 24 symmetry representatives cover 84 exact identity subcases.
DATA_B85=r'''c-rlK$*yh5aoxYXDenU^n(PSJ1CKqkH6jRskV=*SH3mu91A+hU$Y!6Dv0|Th?<-bGMe725VBNjX?lL1IV@0##-@g3wmtQl#efi_>e*eFI_~Vyfi@tsNn}7V5Km72wfBiSV`@;`^`10%Dl=jy6t<xJNv47=_$o}6hBI$3W_WxPmsMxVm->CLCmh{G2?4SL2vH!1R|HS@f`&Zw%+4<hy#O@_T_D}3zwtw|aIN3k@TgN{;mhF7D|IYUNV&{t5KfA8eZ{NQB{)hkl`yc-B!$1G=cYpkc|1)3q-@g3oKmY9yzqkMT&6nT*%m4lImfni|_U$)c{_wB=^ySUog&%*&{LAk0#~*(GPvcs<<iCG;qqnd0mVWytwH9jjp5uz^jEpm61EEdJ^LUyUG~%90r+Qpq|Fi2Qs}!l3(|OG}!^F8$@5=rnwTseth-h*T8fRJ+8w1hDgYvj)+?+TSN=*J{b_2E#X)PrpcQZRfId!(vkDJN7s{Qs&t0t}Od4V0bzqr_IaWD9kHtr=g*>vW|MLbX1V|wD$i@O(%K`Tl%b?w>TY@BQMUX@DnZ$LIuD!H4aXosO5=W=dr(gPRSsM&YcOhOE&?4|6IY~xc)ccU{-*{8OmnzFyh?on(`drD2Rzi5nuvdO`iyyq#|Go)F1QU4C(L}{r?G8qCHu|K)>B&{huZkOgu3?a?E+ce4X;$QQd{f;D2Y4B=xtDbVTHzRRpWWKYBVXeYXsrtHy&Q@Ehs_qiIwdPvwLwoX~GsLZT)_i>ASDsg7lT9Z7g=EL6YGx6k=bh#%ut#>2_FCW)oA=hFHs;L!Odo5CS}DbZ-H-lQIn0T>AA7q&F=-+)-Q{mKB-~bYF_|_&bc>C~s-#+SX_DNmj78lt+fqneoOljJP>YxrsEQvt?$%UIjUE%j>+Ndqt(WYcV!yK6bQ}H5^|{!lzNte+m0ZsSO6&Ve?WQ)=MBUwO$cvg<7dt8LoyX+oWJ{;yr}W7_L*2%vSAQ>i&z76%?ppkEAEQw;kqKa~-HA*YYo=Bc@#o{`&E^6$6<JgDV>xB4+PzAm>fURdkuJsL!`*6(%J}?JviSG1hnpa)trmL9M%vo0H!|hy^~_L$Y+`I`!6`vgcJ_2z5{aJ==Y54OY?IdJpFLzJC);YWw&GPFO=V#NS!{&;Ov+S&_5$|Csr##V48L8_Rp6pIm5oegm;^je*(x7;nb%}`1v6#b)NoQ3w+jya#WePzb2W_<;}Wv@>ZSR6*$`^$_Vk*PyClyoHFs|6)n!d{QP_7T7_~8+b|+g&?Kw2*Qp~n(m<hqB`WdQh45&Td^siq^LuHWdbGB_IH_>${Q5!UAUDZEkYGr#jyF!`$si|dcwT$g{J?VdbdHeET|BL9Cv2|<9wz0Q$zyJ32%QhZNVVMH#^?979tx+Z0DU;^M@%A>igjT8<TF;-;ypL(UWShmFm3e&LM{Q%tLgo0q&imW;TZTFDJYL4}#?@AReIA`pl|B`F*}L_8%lTN7xUu9lJzvviYOJ`f_VU+uJdXEy+{^)bSR?c2^Y>iLC?qcOJTB`#+Dvb-K9A4)$e2)D3ibKDJa05!$aHOL=@@4oH?mo&xg|Nqc~}i*8l=*XK^|+&#NJdqony&Ei0p~y4D!6S4Ne&g_V~Tot>clbrdXdNkjGIbwV}+<fvodr>T`XrqraNNGHxNwGz#Z)RP3<YD4GPyIVkpr3=zv(&LJ6xyPBb8#<w1yK9qt<MLmbSjiaVoY!g#C<!cyGwzy0t-H_-smQ&7MkFOcKy3LE3E_}?r9c2?}dzWKC>?6l<+k8xI6!(>5H?f;bs_p#BdGk__;p3tB&4dx#6w~o3WoSLImuUW5hSg_#XR<vnpC2>sV&f-feY>?Xes8a5I#Q00tYfX4NoiZx`IUCq)Mhd<D^9}eu!FUB+q9g7+wp9}VmRQCOG89<++^4wNPZqJbNjL7TzaYX_)<IE%;Ie2vgP-e&b>#;Y?7Ybyp0oP^rTi&<?~yI?cYtg*xmZ67sf_8x5<8}i?=>DBQu0aPQf2awU|hp!=A@cLwwDU-myyRIBeE!N&{CM!#EXlF-yYsjdG6Tyt%1fwWZw8fgC4H^{0VC>N%2jBHMGTTZlBDyueg)@-^PG+Su4udak1RTr*UP8H|TsnOk-1V{<)(UFUI5rdCormPVP!?WwkO&3Ha$aBcZ{?8K*vrRxbc9X7k{CUKsrY^qUJoW#yEX(%gE;&UFy86Eb%eWIRPY`&O1-ZqhP%-T@XrXI(KOFyP<94E3Tj6K0=_;I4mZMYvAc<A`4{ByS{ZQX16aVEDRjG4<hcjHX6wQfq|T&wH(W&)UrkdK{&*HdhX<ZN$U&xxAGIoWP*5bT_&u`^VgLc3ErCu&$zhW4xBxpM=azc(CZLYPj;Tu(6DtC~tEncYP3922v21{8M_#d8?T+!ULesIfEIhG5&+Dd*P<m;rh&82fISrj!mFzaNWn9v^}z<=lqGVJUS;TRAtP^>ceo)Aq-B^mW2)5nEn*?ne8`Ej8Pcs#Z6z3tP5f$egmU9zS+(TlvQ_p!Iwn8)PoZZeHh84BBO8KIc{E!t9i(oV(jNUTA29Ll5gbJn$x;data*w$s?!%co+UcehbB3$1f=vpvq_Y$IFpvFp%!vVFDfE>hVk*KwxVrd@1tBsbYQ4M)?AJ^9HVUy%)<RCPATeBZgrIAuEUw3;e4&?e`mG;wwsdb2p2fz}z5=VA-_)D$w$*ito<-IlAHySZU^o1t^JSpdjPwaTrYBU{Ecp6IYi+WM)gsSnM`jcS=AWb1?uyOB1!vQIF*)v_DY3Hr>~G=0|G5RF@zX(H@Ks7_pCQ+jNmeIAzaJ+@nRH$D@)m_08=)eX<s|J#^h>TdrSC-ML_S)H7Yt=rbZu=bN1wzgD2l|#UE9oELff;>lVc%S;sF43mNZJ%{H1+IZ>Q}+z{1wAtTSj~o%Pc<@}C^j_)$Z~di-A<UQurGE-+BmG^9$dYC?&I#=wz}q4@wkf_1_Rli*7?|#QZeKq`OpVEPq3QxYOjAhK<5dA&So>}X}C{k+JNS#xl`ux;r}B#mIbZf+m<Bt5LsTYV@lAJmf4iY;0#H!<z*__%*Rv7PT*%7g)PZ?Ojn;L>~rlXyS;E6uUQO`IHBT&n`|13v+T!lv%QMh0M4|ZzprL}n0nvx{8t7zm-l-jKQ&x(ZG_|0@`X>-JKRCncJw$kwzMHErhaM9#Q(5oefise_`ARRvfTpq^{Lu=BRoAd-`L1ZFYev!JUdsasnSkk{~td5zyHHukEj0nD-Gx4z!!gdJKgwy^DqB6#(ggA^#{LAJK*r?2QU7B;$s56*9eYG=z98Fx4Ry$n(ncTPWTdh?BG)!Uy8nSy78H(;1s7DXLt=xaB9){t-<RJPQW?-8ob;byxUxYSGxqC_3182R|Eom)Wqm&?!l4l4h-!aJ;cEQtikac9lQ8~bWZN&uI=chrQmBV!IR1bJ*bL~QxbHHa&U;UqQ8^S&j|v;%}?s`F4o{y1o4<QfAAtw4n9HxhngO*w2p)i8Tz6G&!GnYUx}`|=!xUtXu}z!$D%zPYf`;Kjk0&7RdAFMILHWGT}0sGB5-Y0a76(EaTiSgPz8UHzd+o9<!nJO3wcKhp#udRC*<8A1nv(3w}*hcgS?-EynjQ$uc6@2KtIOm?`-Fv#s4||7y|x_3~q}I-U<OP1$p-bc@G459>jYbGB_Fv_!ly`6$IP~gbo966figf7#skKxW6FWFNpFL!M!u)$Pa-3dx2;H?4A*_7ewkA0lFYC4}hEih!X&90)Q=ut24ssj3`<VJQJc?0JDM^RuQ@iB343Vh=5QK2MWSJLR5xeEMPD~d_;(g2w;X+SKS@hHaHsJhu38p-Q>V7qt^5Xw#kg9@^RB`+BPta32kBy)-amEHQ2xTVZknQ@v&<>4)J4eIZfblZ{1Qnte3ojHJiN=%iegMR`_tsPlI*-WdpTr+4s#?ZD_vM4CZT#=4-8(Wdi92>dm`t;?`i|vIZL$G9(7PMjN-3VB_W<Y+QWrsmF3Ka=Sz$S2$R?7rJ@=PQ3+mMKh@e+qVVVmso=F%Nnd-;vCFhZ6QS?<Y1JLdjY@60dG7u)YBxEU=qVsW06Y^MlpUKyLWmdF({hFrK4F4<|C^c;ma^?Xc*^?hOq?07-zHu@fe0Mh(`;;AyL#Q1<@E66|hbP-)b1gIKAiBJ&a>Cs!Ko%6fOVhe9FN<h6hepLPy(|sz5Y3fi-)$AeS|(7?8z)D_FP8VBM<U8(`aWe=l>FPhX_pX{YtuFt`cUF|!X)Vq}tnwd|rH?ur?m6tJcl%xNlUPxEODxH}YYKree64Q}dSai0eiFM(T<H=@P=nY{_V40eb}GKM03JQ;qG;TBZE%J2RSm~O26(^=R2cs2L6)9OEmV_xo^m~cSx61*oNlo-}HdnnL66rkd<03#S+j5adDfm3R#e+0uDEb~4?z)%1mxKWx1IwAyc_9h%Cyeiz78ax^;cDaQSim^Zj9N|T79?6I#ywJgIHkR;dAKwNS1(3iFmQjq-h3H(5Q8@$@0)Rp=I>sR?Rzft45mN|Y3JF0b3c)2pR3U&W6j4P(RH29}1W|=Rc!V(efv}?@?5G$&@FLL>>>z@kHcSGfLdOs;98v>R$p}?4LX~ruTqxqW?Lr<E!Ae1}LJ84IL9}u_XTy~puXwoWXP`v<F@9PuCt%Tbi&*Xs>u)!<I9=>F@Z@r*FPP-eiF^~Dfb0CuyN<4O4n}Hlz<$->N>}t<mRtXO3c2kc@W0m&x!?7h?)MvCdji+#x4iHA5$}8dhWGv9YA=X2qVv5V)ZhRtH~@<ha0T&4ob4bX9GtllKJ3=FUV?8uBZSZo_|`f2)?<$F2b}HTk$>TBuix~x?_6Dd*Z-b_|NZ=sXKrnP4kh^3dvvYG+|@lnKgzY<z>~fLZ0~v68(@<&`^S6Q5vtG~Q~^hqyWhPdzM&(&ecRFgj$@tC%>OP&Iwl5wpQl{GViq)*{~T9%2IE)I_I=0oO<?L0n7RU%ZhqGlp3%&eVC7<d8yc|;My!GjTi*4BD;lsIa?xJ8zV+4>j@D~N<F))bu5iYeK*#pIX&dsr@^|>kujDOAx1#q9U;PeedIeYcGJ`{=le~7WH}tJ9vzT8y+k;t5w`TEatuGsw-t)$vT4@`-@A=w~OSa>j-t)D8mur1li_VX}ZARyAf8>zdJJ<7F#>lN}-CqA)-}=K|{mcycOV1362JC09$Y-v|cjStECWd?_hI}T5d?to`CWd?_hP<*~(=RGBMAoMMyw%$*F!(rI$+l)&^u+Q9GDSirKu9_HsxfKeJ~PAx>|dmY;LRa|zYSVUAi;EzZPA7d684vFgCt~-Xvl}5a+g6;qN#hIErK~Eud+qt1KA>w8}f_D7RevT7J->X*}9TLSkMyYXbMvxl)yZb5`R@N&&1E^<=&0d4><8rCM5+ax)Di<B6%Z`!)nG%lXG$&7BN`lH#sCVn&d71s>Mu`9x_dCWbv5h!<ascPZ!^SdTUw|n9~`|X=Dy?K{y{QyY=?+%S08%>sMMz@@XdoX(nh|3s$y!(^|o_ZeUs~l%8V>2%&Eni_D?AT)c7Z!^;(;%N2vmH6&dK<XjMzigzp#@907%FskL1Q7tz%wnD}QL&gPR#sxZ^eZD})bb$`p0v|BEf590T4EA}$jEjO97r{dJDJ%G!jJMfFdV9}>oxz1IXtbl%4ui&F&^Qblhe6{oXbgiUkhUVx(XD9vGZ_Dnwjv>IMMBz&gtQgGw3Uze!zGj*hfI(jGC_KP5rlQc0#0(w6@j#sko`s>{mtK{VfsjVqoD36=)1cV6GdNo!<-YvnpeSES9zUtf+;31QbF9d@x5S#-8~-I<7vA6l}8WS0{Y+^ce?$|0SdXPll%k}pMc`~0L3pKK3tA<$)AAY6Ht5ticdiC2`D}R#V4Tn1Qh>y0mU-*e_lZG2z&fQm_jpRilzW5;3va0Y#cb#bF5vhj#BokViJh@+=!RetRXLldq5Z^=H*C_2qSakEx+L_SBXsJB_a$gdL3_{BfvN_IntSLbpnh^k+Hl6d{H&P3yB2eitqxCh`;v&9Qgw&=g1P?{lss0fiFp?3_VI&Gop*9P#yf+p}MsOya8;(QL3CQK6tVbenj*E^xk*5>ZM28>Vin4#ME>Ux*O3H4ibDLnWE=vi0M5Kq>&>dbOahHpbEfWe!?H90z~kb@UtLRpdeO}R=IyWXI%hfVEHTq$ROk&X5=02o^SZf0Cs;4Z3{_9>@5(1t-}8em;};;+M7m%!hld1SbRNT$pBceN>-4k*B8mM$20XkJkwvo8OR=*=%xa?QA9Ub@=EC?x`A{gy~$1j`dunmz?u;IG{ipXHTIeJgo4!!Xh#9<FrpnndfWzRrvupGcj{FI32xs5H=F{v$pPF*05=)I4KmUegf1DOi+rH^GzI8FfnpY+iy);eKo<t+(h<3|fLtUX7Y@ip12rt*5=L&<!0C$Bsx9D>6slEA;A}-$^8F|zMHbb_o{A`>A_$>(KuC`yr-9rwkeULSDZK|t3L=ugOp4V4jDUn+SJe_07;G|6U;||&^*jq%37jSXU@9Ky_f@#Z7PiyEQsB$%nB;}1hY|J2yE$EcZ=D-H1<>;}eE|wd%<Q5Xp^zQ>R<agCpDW30Bco3w^vgj)pQz^(_54Spo)uqlRTZB==o1Ki0-;YJ^a+GMfzT%q`UFBh7ZCE0=cuJ_KLrlD0XhbW(g$G=agJ$a>N|Me{cL8IDYUK~sW7c0uW1&E>1KS|%NHmLU3K}{V)EHf_a-Y%y?+}Lg%)_y8tS`6Q{*1HNmipmH|c5_npQ6DsW*k*lJ1C!&Yp|13|5Kd-;yN&DGI$x+g;KcXGsBHX|ApZBMj+PD_&9$psQ;~)O8%XU>6<|c;?P;J3oQK*KaVUHJ~xBk@yIOZkCRRFCZ_*N6%P<Y3_bI_wA7N1E~e(B=@OTt$Buiv<jcG!P&7U9)PWcG&!YMg?<Rhqj_uW+FE1o+;ibvjau7HwR%dSUi~J0F3A4fBAHd|xSU{(JP@7M*!%SS{N45R2GbR{wBm3CNy;b-k7T<;eLX2)bHsy(&^!Pkt{5kSXF<H=1UYw!Jqi@TwxZZi^k@sV%Ho^vp0hN2KR4UQhVx9tE0}wipmx6XipBHiT^E8B4<We#hCItxCk8$5x?6N2j_go^?>_HM-AyN!^nAEar^ypd`W}nwtg?v@tB0F8K~;Z2#7V7VWj`sPPA(pHDkKzgYFPfy3ec1NtCt4{@dJGx@4A{|CLo{HfIu||W`LxCL48}edJfryl_DOM9+R-zWTxhUspgCf0v&r|W<k;{_hOr7RuP`|Q^)|&0x|3+iUkO(h+&H$h%GfC>3|>!mz%8B;1ZE+E&yeZ<*mC3BvNy+A~{zlgtL`GYfAUVo0K32T7pxMH~4JWX!5*lGjr9@TCxJLA$ZSCNpMPd-4`OZEgcgS3!vMI@b(<~P244ctiZkXg1By?*S$4@+*4pK3a^5hiV2Z$N0u+bY{gT$H`A8{`U5wL>(*{9<qeu!NLg%%iQS?lrw13B^*vD)*5Bp@%Yhk8BTzoo(1yxRQ%!8#0W7-(v?;?_5ih$>U5Hr~ATwjTL#H-&Mq}$CrLhF$oD+66bh`yP)wqyy4d}WC_FfH53msSDus+U>ZzJl^LC}j~_Z#ej*<283a|u9OkOB?%`sDAtTlb|vJyEdj9|fkg^Ue!ypC7vLb`E5}r6Wi`g!$t3O*aw8lz_>1vL{`T&?E5cw}Ij}-Lg!K!w#~yZ<K{a{NBC;zW>>jX=xXUA!@HbJ*(Pl4mIYFaHwHu^#zAotosuB0Ee2$2RPJ3e+mw@pOZ38^yi{X6ZuIf(}aE$Wm<cmG7aS8o-&O&Ql_=<p-lS-LD~a6)}OJx-m$l>+RvYoHSJxRv`=2NPhPZ7UbIhMwErkxw4Z_o?dM=U+a_lVWkEffpyCg;7!s1_&wfJMv%8KHBbVdT9{ta0kN&%I`hFUyzhDFP(;WRYM?cNcPjmFs9R2^*9Nos=FWDY_x02&K4AP&YtYe#>{okd~<8@g_ZXYV^2uxe|WgRttsH~&u2g*8n`bb$vm%o6rjxPVMWgR{JOl2KSe@s~i2*rI_2ME}UvJQ~e7iAroLF9z+=dAR27{t_n*5Z%M-b!Zv$%;KfamQyd$7eCeXEDcTF~?^y$7eCeUqmrSDBbu83N<zW;tv*JNC_B7Z!nPk^G%%FyG0rNmi41eoQXnF2CMjriG(IBTqu_VKKk2PN&q-Sr6I&=jRMADa^)Ng<wzh8)~A*FsNCS_p0BQ~WL0iJQOVf5dnkMl^(eERLrQez*E?r^hb;P)f!=SRQl>~ZESVG7_v{CH*K@>ne$sQ~8)oHL&p{M$m9j=;RZmEk!$@DuuTokJ6_g~gUv-igE=Zx{Nd+XB;WH?Vz(!)V$FM=Iv6(f>BlF!?kQe%AQ3oSP^EX^D?OX^?pe7ZOn)}!d)y~Oy#2acww05qS3$IBaKR$-;8HYGT<x$lUViUE8;KZ@0uBr}-J+x0Dess~s6(s3qU4#X+@f<FdS*Opi!u?8lK)TvvL+x`+cBuzZKy|0?k-I?(5|&X!9^mg#cn|bfTclP#W$B2Lz-n^Bd4RxN6skQaiFzEE3x-bwp<rW-plDZwhpOTWKDhgW4`Gb5Xb*$|=Uo^AEfZGe3b;~32gUQY6H8_Umo+r~b{{lWPOctdmV)t}R58LM9f~}hA2+)pnK-mSl?P{pqLPpknrZ_$dW^uT@@POC%@{q(+yIj*BPt~YTw0*aLmW~YKd23`X%%c}uC-xoNd@XWoU^+@?tODpvG65B1gho)sI?ac*xCvKZgsD=B2nj&b?4@TQvz7_oWQz@HkyaCZUHVpOQ~aJhkLulbj^rrPjOqgwjr=3L1=qQZP^~Q2I$re*1i$>0bIB0p}fOQ_%0qfBzQ-g5)x0Jmo1>{Z@yzt?j;u3b?>@v?}U5f=u|^MOAzul#JuMKFLZiN!ot07qIPJ^y*lq>q6mJAm$#MY5vn|d0TI`RMIE&PC{`zQ<A{6B1!y}Arog({c$*2K@v;0iHul9aUhi#KtB9A~YFmK0N{GI>F<SQ)a2hCRrU{A_akE=K3pqPEkzMLRp{}C=de(|{9q=UuwDv9s$pJ){P}kx12dWT}n+K$acJt>(w7_;Lh_-XZ5aYSyEr9K{-8hmN<B;l#|HdJ$h`VzQz&jvs*yj`6dPgjUv6zDcx59a+4av_>TR6T2AWssYd@iAZ=(TKJ@UnEQ+~5QK`3UCqTa00rmhQrp<FJGKwoGm+I%22$>kkt^1OKn!zHrEzla5hJDG|p@t05|hlm-*7c7*3W_Vy77h?UUcW`c$qU^n9<7iB`sm&@s<n@^7!bGZTnRi8C@G0fd{?umJHCAS!jY%!Itl*o7>5|ZgShip2o0UZ+n^`WwQq&J8ebi^@-jx}b{l^od(H0IG!4ViS(QV2wHOr|T`5Z%_0PA3oxohm&5*<4G=s0%4|+-_Lqk|085io^pdDd1BAx{t{$mo>KTf!JP1ESw+~%l(}|J}_*CWWMs;7+lw%9^;Uzv7=8)G3*E<Ib}4<P2e$r&h9937O9DcoC=7uy_2xV88h}YH4iQ;U`uz&gqG^c!TEfPg&WUHR>-lQn}%QrRQx3?4yo7xs9_|MAQTA@Fd)E;W&RA|$KwudfjdBZwF1~H39ud$gdhRxY4b?0V-T`8z<C9Okc>Hmr~lta4He>y6N_ai=BE^T4ROKHWWsJkHN++f5FVxXO8KE7QG$*{%>zJJSlYqvST~dk=<hUy=1tGhtkAY-hcrW`B4ZyS1b($(Bcj-eh*SgYi@k_iL(r!kdlC6@g(H|_xUgLX+^88~V?$B^k_Z|_BW4Vcu?EB#S{6C4#Dsn)FyQlbLvVA)HjyBp=YSpg4mt+ps1Z0~8>5OqvI1<Z2pThB#vUPK=v$O)$go7{R}uL2fcru<f36|xvH`@a0Pu3C+t0D*Pzxpb0lDRnn;9Tj=qW@9uGq5}w8v)itGg~kt0LZ05p*|$8+?@nFiH!eDF0-}&6X49qxi(oi@~m7Wb}N}LQDRI=aCkorTjjxT}h$S(ZOuD;Lg|%O6+QsA+vO9p1s~f(&!ck%o>e9UxERNquTB&nfgl{wt}#)a99z9VLmPue=<z$nlY3rAy*Ut-mFy$n2d73WI1Gp3L-L0?`%Gy^`^Dz1<@qtiiSR_>=Ws(;uB~C`^>y>-Bz(@Y6;COCl=#a=!9)W(@oRT6q=Tj&mT;8N5rGr1<hJOW-ap0MO>!srnPF!7X`cp0<u6^4dqQ7BaYY(HOh>Ws|%5}*jF`$zN&(FEJrxj0~!NKlPGB@Xd8BcQ2Er)2gZ^Bv06Y_*bB9US}{L+4}5jg9<@Xy)dG;B3jE!YzMaC!@8BqH0HZ1vJ^^8m`vqie5+r>t5ao~p)@ZoD7lLxJDuvxj0UE0BwwOadRl=$&pB<HbW69#PxQcH|xN<iOc39<aCvQT-Rf57R>X^ORF?*9fn!U+4$(#z6S?oa*BW7YO&SH#;5d&gE?lVHX<nfU}`4-e~QHN~LirJnBjtIe#&u;7>V=loIi?}v?!E{dqMw~;sXAkL~Ii!0QL`4lD5Ch^7EcL=#FE?B>k+X(`(297+kJx=es36?QFAKgH{@$ErSP+I_heM!@Lrs{MKDf<>I*Le#0x{ZqIipxe=2s;i5xj`-wl6Y5Ib?*EkP*ruy!BphReC=I6g#N~-mws!QouNZ5Jv#vIKA!DHwp7O7kYuMrDJn#za1@L;-12|<1ub|w^$}LV?Ca-Fo|N>TSgp{5w%DFEk&X5t>1QH4Jn?_x+z2~+k*qhWF>RHB>Z|0mwY=u)LH;0l$ZdT^vaP~A*DdAkikto^U)%^LYF|Vz{qVqWHtq&?Hr;;9bwbJErC5@NS11()E2&JOyttaE?AP8A};9>n3NJZwK++ICKZD=Ga;o%a8hdw9yN?DjA%m$9=QzI1yH25K$k5Mqfm+{MYu(FY^d3qIHl$YREUxyRMAd|ReB5{VcOtCD<$?QVu<^w6YdAaHN_YbAq{i!^<xXPREfk4B+yZ4^2utXucjQ+90ih4W%>tW>LVd~i3m<6I7<QK)W~~HIpQ3t5;G(r3vp&TrU-R%O_7?q=?yjYhH3}gagqEL<q`3Khmq<b7lb?&Fi$B6dQ6&&4;}#<C0w)!AkK>>67nf@o{D;5q4O>i40#8cJXFRL4xN`wJR}JKQOB&qTs$OVfJ7XKqcs62Qu$^<oAdZDSky6pki5&bxSOs3kVi(&dpJ&W0cgZZh>a9Eq7~4QD~oSH58hl&&Zcrkgro?OgfMlGYXC_;E43j-dPC{(2X+|911HEV?A-&WD`@*bP7<J#C<At4MFI>rq>G6f;ZvzE2%~>Bv4CHe3;N`Okjkagu4@W{D#;a5l~CZzKw97AV}Td4QV1?FK&ys1h$k2C!dC9#yG%|3#WafscqM^Q<MM?6YN?pJ5<E}L?U2rk8oU%BRu32}<|4B8fU+bb%sRd*LnYoqQ5`Gq*vHG~AqhE#?ok^^DIh6EBt;=t5Sf$pxig+%N&!uAKvN~aDT#PWv0^R-L=_=b#TvO5KvhD%<p8VvE<>m{Cf~BdFUYREe$x?qo%xVE=EI$lZ#m#E4lE-jBLaht3ki}hSJdZx*rs3(Fsw^R+Vk1)D~}JcnQ~~A)aeGD)e^ayOK&lxL{#~nl)0qam=f(_0_Y|QYWalj&>R2Apc1Ed8S${W5C?9%z=-x$1GinEJNsG!$weqhYatcuYhW%riljYQyXk&()8;53vRD+ykyJ!uH=`1uSOj8RZ;ISviCZXeW5i&Au$ezVDH1yqA(G+viWFpo?-~pB*jA_@yoxP_VtQU|9`rsl2(aeW&@rm{iQdIz>83?cKv*@>f<*qi$aY5oAjLQkM{pFNQ3*MAv5OBf;yp#^Y~fQOy)OH%uJz9g5)tAhF22hv_VICh4OU%;Od9AifSD?c7YJlv+)(GeLzTw}RlbWF4-1&SkNZvmI$(2|Ka1QhgLRM1VBRCMBdiU=wlCQ9<y~^S5CaL-K*3N)c00z-FWC3xU3R-*jt5JdU&c1{mfTLTu}f&{^5>A-y@*;M`<-B)me8f;JJ|1DkXj%;o`lXT-$9R8f&8vRY~pIK@|rHMAzR+Al6g&^htv{Rf)*CPU~qy$pU;ZsF~%k+L>fY$5eziAz|$?iUPzCsp(G`HOZFKfb9QWuGEly?VIynaD=IyEd(TAiE)hjqzJm|ZIg?Urk<(c!AHL!T9fd2f&(jkaja`4s2TR5C+Pn|tJG<DReuJ)%W2GD1Z-ikDZH*w+X7wITrMZ&!MPgAhP|MAbN8u-b#DmGAW{qt~dlwggxace-X$fgutxHJdBIa5p=5tliEH_<AwI!w-a*LdD(O7<Cc!^2%CYI8vr&xwVJ?Dgk6O+)o1)>WZryR|CYLqo{UE6mG$qnO$klfh)<Li5@;n7rG3@P7D%>@fo62qIU5KX5{h!5<jav;IDIV$Td;KtLv%lZr*$rI<4$V@1$rhb!dRx;hha#&oj?!pxIeF9KxsWzqFZ`d&^^%}aK!Xny8#ILv~OGZh|q5CO}#)VXD3N^<bsBUpR+n~DTd2wc(tMd^ka>M*YG$walVn<Z!9OyG(Auhb*SMq~H!!P73yfjt`M2>FO>_v<im!_=nQPLKxlWtb##6!%Du{6!E%m+|%;`L0Cb4&0^ui;nVX4p7q`pL0@gLx;l`9|CxWE-ZQbB}x*eqBG?t2)VlV6&SQjDmlHwA5|q0;2L<Qo<a*(lszKrYy)|o?AUj1Lmc**U~dax5Rd{ls#m#ZBz=hV^t{v9ax!4ph9n)8;3ru_K-@|Gj;UdDo{Ww6$RQyBvQBgSLqNZD_jy#b||SMK$x}ZSdV2R(hBry^)E4lYIUrE5Le5-&+XI%oD)!b$T?jroOTZ648hfYMza=XZ8lzk^F1Z*75P1qO<)0vkKCb?Yt^2h?#q^HNd<Z0B~ivCMsBG{L%xqxYJ)m3{~@cnE1S+r*x$8KjV)etY6*$uxnvCtAoezj&0aM@!I)bptC-78<Lde9$6&X8Eh-q*%gvTzZ2sCihyJf@3%?*UNV1P(2=Un~V~~$ib10yra4(?lg=05_bz{1E!gAu)km9~*tBO4Lno<hQVQsuhfpA~RwI+=CrRI7pP*6$>-TO7Ood#auw&wswdv}aANtf6(wrI~9`^IMF6sYo3y4rr9E`_Q{IRY!~YAWj_bo&=zICpE=l=-H+tbJCKK&C$|q|js5G*b(#`nF4?ik)Virr!l$P7&>rFTaSdma|@hw|fGHbT^*mB${IH+0t@sKikG+Vdka1LNDmYXbsxZ`dwwWk3F^dc20P`x1AndUu@3@2={h>z+_x~YD?qb2r)GwJ#?#WNs8;By|_X{58H>~|0Fy)cZKar@#=K@Q$Uwo?QFelUmb1zMC_)vwhlS;wKeqFu|N*A>TYifDqy={Kw@{3TNtFphhk>8?=igsq!=MZ1-U&pe!V^_?7VO-b`<|jSL0jme70|2nP>@EQ_j6(d4#-{+g>5RBsX;m2ti(tP!05@Dy@NA2@SFp)5S`_bC=jLUB8faSl1g~i)`hz18CErmKKOl-Md{JEQuwfQwxm69rpDm*^d0Wo$M+lJT>hO|N3I!E3#ZeiJ?$ubeMrzxx8jz)b-tH_uQhcazm$1cYxTf*6l>gxwV>t*Q}@B7!!2oXY#{{bo4Icf^tvrVp4RaUSSw`opHXjoX8~Lj_D<>l;Nv!@OLywyT<o$r}dW6NtPrg^I}Hs*jSLqMW>tuFIM%qwLoIy)rTVIz`WW*y<xp6I4m(@+*zY%ih*}!ZekRCSWs1Y`J)&><f`>bdgEY<ZX_z1Vx1v!j83tVh902~F2|X#-h(fQq9X{>Y-<SZFN_}jKg_}TlaZ!nI`zP%G!rXwC^@X8A&)l}9cGSUW*ZMi&yC~|YVIk-npr63@fKi2DbGZrGm#hGZE$5t^u1^cj+fkGO(IE(Rf(EnlL{hmzb?vjimlb!w>VrLE)J<Tye^r8b3;?46GhgXrF3I{E_cY!J#CrkrBKHum>wKG2f1kKNG@8yt<ggS+QzDThsOD!Rk)ZT4DC5T?~;6bh)lcZta8SX<%_H_onBWwu0|FGoD`kV_u!f0ecoCJp3vnv2wnpRxr%2{SSh<602D}cTeXZp`;xKuM91<)mV)u|jLqW&nOv~NL=QbCx`dS56zUQ&<yL^GC41bRJ?1Wq`LqQ2w2DM6(vYUpd2be!7shHtS3KligposZht)IY*J65Y#`Idx<u_rtAlz0-h_y8ZE*CDLAsqp`h|dG$*Z^a5ZelT`bO7M&c`E0+4g@ZmLqVg|7~@YJ5w~}1%p?6h%Fl{9woIY3ohO%_m{}`=YvsWA$&CW6Rz^%M2?4b-0&2x38JMfv5l5e<|8AaFL$<C`Y@jEh?2)_+X#sLX&Bq&U&|F-0vp)JCY@p;1C?2>lbpt@nT0;jvjY$enSE@kTxmiTrMue{zUV78eU`8<mJxum2VONer3BcL~2FAu(1AHd$p`M4dAaHix*<ml#9P%M3^yl!|=fnK=dpCiGUBFcoQ0sZs!kvPE)#rarn;;{N&Eqz|dScCxXsiey&-=)(%47hJo*`-;36PNk5vU$Kpc|Ks$Qv?#PQJ?<8qm_(eTiqMyY!1|N5o!+w&nQ@43QhiNGD?ajs}LMnxLk_Py{(Qq!IJ&r65U7Gc236=O?Uq_5$IOFm+*4SG8j3LUU*fqP@3PY?Fu;q9x@<sY>RMN>Td=sfFH$oKq%l9auUS4{vRwqeAQvl1(XOgUBag&ZAREZz`mSTAPiQnesO+LZlh8kR(03=<vijDb><??6X*eTF)evZUAi={yftgJ>c3}Ms|iuryEWk8-~PLbL_*|nwqfIN|ErCl9_S#{{0L?>vn7;8&)g`ovf~!ZKBS^1=-lwpfl-R)hkgoY}gC3{7e*`v{1W9fv;?xuYK`BR^>>nYVgi5Pg3qT1gkc;)NLR_l6FouRkhR>QnRI|uI=Fydc4E(5vbZYq=>`2y<QPWA|H0Jm<ZKYQq1qRd2jW^uz6!{yQD}=|L$p&)wbkw7ry2>HqG$dO`8)FpsdU&cZ*BN?#BjQTL}n1kNCC?TMvw{QoBvKP{jMi<Y&mFg6vOP!lE`rkNM%pJD6N)DRh(mA*OnuG5O@)ES;OyCu3?|lQW50O>}Fe8)Bnouhp7pNNKk@D>*Z_;BYW~Ra^44++XXoflbY6;^&msp)i(Zmr|D$+OM?Sy3J~jxg@q2vH_pc)MtUwioTh^w;T$S#S|lrOb>KxNH^U)-t4&9c(t*yOF5Wad0a4?NVL>@%(l0wG=0T-_;BWA*4c<Mnbb(g$LG>B=bCD)eQqYSz4V@YB+@nAYgZPE-jZ5mxP}wm)I*!)U!((T^DKe3H8@<)*k^MrxT>l-JDMq;^%AD4YC4^IHa@zVE!aMnBgL+10n;fZc8jr<HZ(yB`79$uZTdAuzfLv@G`Tsy<;rW(F$I`{B-6=b>!#L(dTpK>O4Nj{Ik_cXsTpd@H9Cl-)IO@SHC88>6;O()9Uuprc9w}X+xEF_2j7RZ7dGK7(2ukjc(%)mBZ8gOI);jD*CJ#ImTa2C47!Y|F$Qc6c6+YZS)tSHUa4ke!7|Wb3qw*uHZ0q%*|d#o3r9OQs@W!Az@;?4tyLFwT+S%w5%fHLUCY5_>mpTZC9!ui*%0MyHil$qexpif6{;?ZEmI<?otY1_5rx=Z>A6CAIit(NBmGRn;nupGl*pUD%ZAc6%G%X;&{46)Qu|p%E7LhkLj`yTSTlWDIJc0%lWc(tApsbh4cWBGnLD&FTdT_AGj~h`s8r-wF3r?KO@dyuYM-8K$=H==>_O>_vh%!;7Q07o3i&<5T1|Y?S`9tkstrg1{xLP(kxKGzvhi!1chfiCCpr9j)J@+daRg1X$B(95&wd0uEzp)r2F@}a{YFND06P4*N;UnH68inrEJB-~iWxw)+C*^4knv-h&kjq?;0!dNZ8Mss1WGeAQ*B%HKFUdxYKzfyUn<}sET%fly3Gl4fJ9{6ru#%7wNdUu=klFyMKfV?YEbWQhUc(k#k(L)VVdzKt|`e(N;FH<P*x5!X=VwUCM8e4FjcIr|I%thqG>ba`>@2ifS0mT6_fac$wSqE&#(@WC1C8nlFpF-F74-$4hkdzHcj@($`we~Ox5N(40j+~lUC{sN1~_G_9wNkY8@S()c}`mc(tJ4(;jLdu{NX=uxahJQ6unz8V)mauVZUoDmJ_I^lB{kqQNqom~xPz@4O)Dc8OreURzbRT587DMh4?d&$iY>1K*j}+#bX<CkFxBjZ8FZq$0>e@o<yC^k$30o@8&p!E<V+&k)`U?ozvr8pti^HB}wfbR(>bvh91MUvWVfs_kHA4459{KwiMM508}RkjP~7O=d243C!3u)V^Wt5*Q7dEpt-=Ef8hfOx2{K;A=IrV%SivB9WY#6*QI#<~((i`c$zN%U-{U*^m_*5Z7)q<kZ4NfzXDw>jKWR>1(w?x4kh3+Br7eU{6;G^m8UXMW?SKWJ7iPK2v=e-L>5ev{qULudV&ktkWEvw^VJtCh~0Ob6>TOqvm;{Cs$n?OSQE~zc9o@YvI6VXL`bneJL9GyT!iUR7ekAUR#*CHP^>zzd+6gV2dZSS&34nr4ncG{MxQ;R$T1~+`DS(ptpiaQzlG#fbftvWm7ImD}ncY6_l9mR|rTMXDPdFHN(b9=>9bz+svA&jFb^(4%eEoj;%HsXsyPE%m%$|X+UIbkxh)x7#b+}ehvHC;&0e%s-D>}%PVXMK^qc%Oc$d`k}dF%U1cV%$(c$;Ke1_X9%;l9lB`BegWV}ZqLt0D&4Q;%smqT<sRmYb+r7J)+LF=LJp4gp&rFz8HInA#^vrKh^eFY1N)R2=W5c&?EeDQ_Bz5dN?vq#3E7NkV_{m?TKeormmea#0&{{$#x6Qrbr!#X(Hmin>X`+TLvdow(>Wsx%|4oDTt!hZ$8ggRDEfT=niX{zMTxMy^WYA9NMYj#YYy_2<xTWJv_8l|kC7s%%7VCl$X=(55ID2+KuF<xu9pbpty9{3##&YcvXTFH(!r|mi9Ub+J#cWBEKq}8>iezVb?Hn$XEwhGOU<8qokxwT8xjJ)q!>)#Tj}))vFdwlW8zt^n>l)XT+h%(>W^#&tebZRYu;kUHF7SgSLln0CY=9VOLTq}5^xk{>4RhMHeMB&v)8BTV;X~?jM;(%Wr0<`~yWAlhyMj@me8dDR4OvKvZI24FNqjAVaU@Vhe2uIRugF8{H_1aTKe>LBPvkXw2!Dh<q<n}yBs2gcj_tA0McqU5uaE^6=^SHQ?BFf#A7K-TUBE&QFbbJp<pcC0q5T&H>PG$my+~;NMd<@<BK0F=A{sNg^1Eyz8X89Dz#UQocSsG~Aq}}hJORwJC3O1n+#x$%>pij%Y|Q049^drkB5cd$+Une~fuO_4_iRykNA+v~H*6v3gL#KNM8JC@ST^-tY$A&FP*@7}itPO(WFyGsp0Sb%i<n+Dw)zoVBn1nQz&{|^y!ah%5(M-NKwjVFA_-_c<Tdfj{!<zLMvn9j6zQ+1NOGtR3Vo(Ro2i%FB*+`mkXR%k^~m>gkyM}s=}089Gljl`YNP=z$d#t^9ZVt}ctNhbn%B%BSHjF|rjShp(vS$Gy+;J%C`N%9<g%{cB_&6ykmII;+#xThLf&t!^gegU)6P3BUZR@}miwkkbZgk&mObQevWMK5uZ~M(+OjXLSK!`A&n&g0(gB)^E(11Lu)QF;N2xb9Z7^!FHEns)fF4$Cxv^rS8O!O0YvZQPEpv~SEYgrq1B;_A+fy`VqctlxsTn2OvjPVDs_+RGZI66-P--#^#K1|86dBob30_9*jTIZsSb@})xh`rjWT9w<-JCy3D55RfLkR;*v}S`jTcSBzax`CW?AI86FE<u!k0vY#imYhi4F$xF6?<dGa^%U2M0t8++uj(rH`cA(n723fZ3hFlLP0_S1Gj>KTY`ZbEnK-J!28vs@*tSJ(dHG;C0>Hj3$17~5Qpbr6k{V=<PGOwCIfFclpJ^t*^IsXvb({gBv5Zi3tG~OoZ%X5>9Yp1p2H&k&)X)o0=9R?Vug~y`qqw3Y8fJsu4csj%>?g|pj*;idnRBXXJ9JG9W45a9c=^ixGEa;^_~7q*<1b9Tm6hQ1kKz1wSeK@kYl`HXiz%Z{xRr>%!CapATm}!AnO3)gA&LJ8zVxfq4*(3h5-SPP!J>(WEDV|;AubRkx<c4C?JKvAV3i-AXq2}77CyR?U5TG@B)Nrm_$B+02vBk249^!s{~R&4H{qr;sy>)lq3*;OQ@2kfE{W850Q5ei3dx76OnoFHTB>HFa+wqOF$eL7svsEL<|x^h+wOv6ktj4_TO+AMr0D9$w_y^z|lFciC`t<*i(cn5wDaxz*1u;*sB?)Loubjz$`C7OS(lZ3B2!e!+Pi)?cY<Q-9`{2_}-aPu7b(-cR&6*TjMHG)8L9vDUk%K!djEudFh+xUVF%|A4!*y{X0oISrj)2(5`~6eNv{<V+A;6PE|D~+K=dds0}auB(D3)D<a?-#4e8UoK+)*;UI?NR3fYz96~8aXjN)SbVFe{$T~`l7DyVIdO6S)=3HaHT2V?0xz>vwgO6<0Ctaa7KpLx}JQtT?`#@(SlPItihRNAU@lEI^79lNBjR6T6xqUGzadUW9e02fjHaV~AQDE^PEcD~FL0-v%D0Q-XNO@L#tc?6Np_j(2_gQOkQ_XH)&ZIX`u#HS6iadrT0lD4X5?e?S7NlJ0N)OR~rneI-bke;UyNxbw&U+&b;S#qVA1Ko=>5JYFR<y)-dxTirR6T&{$of7q#UG@H%ppA;7w$r_e(66*56_j)`yeAvCr_Wm;9E_B1^#B~%iJs*31rB>Sotzje{$|A7U%ng|G>RYMxTW6ZY4ih5B);kiQ-NGo>}5Bno;s6^KBITd?T=rZ1LJgf@9>ScRJ$<y8YsL($wFm2V6V{C^uDCQX>z{TkF&SoaahDF>iP4>e%J0Cpr_-7E<Th>VX3`c|8deRiHym<axh_Rardc;51{hU~2bJ@&whb<CivvXSVkQ@uN7x<x7mAAcjork)Mk2pL>yt42UuW@O+(VFEe3FW#X33W>96qf7iZjm^-bv&|9o0E$Ak&#ZJyEqAQcadk=Ce4JZ#;r1;FzS$Sas($JHTC8Z3Mhnzj(U-2JNR=XB;GBo{~BB5WImI|B#laO^J<)8~<Jhgd8ga5Y0g4j~8=x=B_x8QTo)DolLLD>!da%V_6DIJ&pfzO1P1>fBoSzZM<m1Q$1oTD%u0b}n-3?2sC{;6VCb1k+xV)RhO^eCaXA(Qls9*1_e``UTT&1LE=zd%7EL=c(jEr4O2UWnFn^@Y5B_WpGA0kZrR>|}a*Bx*kyrIuHs=aVCEIVM_5E<R0BA#El^w{n*20EBM&C2+j2dvfhn&_Q8e$&i~mt3*xoLJu@sF0D$)Ha^oxFQ$f&V+@OOxf?)omoEdy_@a7XQ>cngjV9WuqGMyEFV;ZTK&hT7gbxRY2|GGDyz<{28@!g<Z5#XoUmg&Y?R`%e>E#J&-FDW%keElMT=0mPt_PO0E5kSiKE!id*`5%m+qW;oYsH;}>s80{wV;r%=iu<KCl%$JtY2<jl3>Q~DAtyc?c1nl%=FD>u6AT=@TzqAb5M&cpAL%j^6TJ0ZwAEH9EIU}80zSiiR(1#?mq!*e|dvYC^rKljLJ&Z&D4@lU7h?plpuN6?e&`#5!B^oMTDihE(d|yNxS|#cfu~);Ah}KWS>eotA?G1yQm=i!rLjjapvc?MFm+Rg4MM+4znxgq6Q|zZW-?Oi7Tb|)L2&<ZgwfG%WVdR*d{}C_Rz|{^@ha7n&_mMHoM|Ei8~qBfAr>3lzeVo+b0K>CSTl#&Xn7}IlmiTPQ8TwIZz)v<<`yi_OF2fx_xY52`)dI-_)+gBVN;PC!Jr`+bd_+r_Rye*40qx4I_pPG+#TW%PFv#u2=0$XiL&;mC3C~Zk_S;iPVegpMLwN{|5+|^Og'''

base=model.base
POINTS=base.POINTS
PID={p:i for i,p in enumerate(POINTS)}
PAIR_TO_INDEX={(f,k):i for i,(f,k,_w,_v) in enumerate(base.GROUPS)}
FIXED_LEVEL=set(i for i,(_f,_k,w,_v) in enumerate(base.GROUPS) if w>=35)
FIXED_LEVEL.update(model.refined24.NEW24)
FIXED_LEVEL.update(model.NEW22)


def group_points(family: str,key: int):
    if family=='row': return [p for p in POINTS if p[1]==key]
    if family=='col': return [p for p in POINTS if p[0]==key]
    if family=='diff': return [p for p in POINTS if p[0]-p[1]==key]
    if family=='sum': return [p for p in POINTS if p[0]+p[1]==key]
    raise AssertionError(family)


def inequality(ref,under):
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
    if kind in ('U','S-'):
        family,key=ref[1],int(ref[2])
        idx=PAIR_TO_INDEX[(family,key)]
        assert idx in FIXED_LEVEL
        members=group_points(family,key)
        if kind=='U':
            assert idx in under
            return {PID[p]:1 for p in members},1
        assert idx not in under
        return {PID[p]:-1 for p in members},-2
    if kind in ('B+','B-'):
        p=(int(ref[1]),int(ref[2])); assert p in PID
        return {PID[p]:(1 if kind=='B+' else -1)},(1 if kind=='B+' else 0)
    raise AssertionError(ref)


def expected_patterns():
    out=set()
    for case_index in CLOSED_CASES:
        count24_index,k22=model.CASES[case_index]
        refined_index,k24=model.refined24.CASES[count24_index]
        parent,extra35=model.refined24.refined35.CASES[refined_index]
        heavy=set(base.BRANCHES[parent])|set(extra35)
        for u24 in itertools.combinations(model.refined24.NEW24,k24):
            for u22 in itertools.combinations(model.NEW22,k22):
                out.add(frozenset(heavy|set(u24)|set(u22)))
    assert len(out)==84
    return out


def transform_under(raw_under,op):
    pairs=set()
    for f,k,_w in raw_under:
        tf,tk=sym.transform_group(f,int(k),op)
        pairs.add((tf,tk))
    return frozenset(PAIR_TO_INDEX[p] for p in pairs)


def verify_rep(rep,op,under):
    coeff=[0]*len(POINTS)
    rhs=0
    for ref,mult in rep['terms']:
        assert isinstance(mult,int) and mult>=0
        tref=sym.transform_ref(ref,op)
        row,b=inequality(tref,under)
        for i,a in row.items(): coeff[i]+=mult*a
        rhs+=mult*b
    assert all(v==0 for v in coeff)
    assert rhs==int(rep['rhs_sum'])<0


def main():
    raw=zlib.decompress(base64.b85decode(DATA_B85.encode('ascii')))
    data=json.loads(raw)
    assert data['n']==N and data['target']==TARGET
    assert data['closed_cases']==CLOSED_CASES
    assert len(data['representatives'])==24

    expected=expected_patterns()
    covered=set()
    for rep in data['representatives']:
        for op in ('id','tr','rot','anti'):
            under=transform_under(rep['under'],op)
            if under in expected and under not in covered:
                verify_rep(rep,op,under)
                covered.add(under)
    assert covered==expected
    print('PASS exact n22 weight22 Farkas cases=39 identity_subcases=84 representatives=24 points=242')

if __name__=='__main__':
    main()
