#!/usr/bin/env python3
import json, math, sys
from fractions import Fraction
from pathlib import Path

N=22; PARITY=0
POINTS=[(x,y) for y in range(N) for x in range(N) if (x+y)%2==PARITY]
PID={p:i for i,p in enumerate(POINTS)}

def line_members(key):
 A,B,C=key
 return [i for i,(x,y) in enumerate(POINTS) if A*x+B*y==C]

def main():
 path=Path(sys.argv[1] if len(sys.argv)>1 else 'a_bound_803_273_compact.min.json')
 d=json.loads(path.read_text())
 scale=int(d['scale'])
 coeff=[0]*len(POINTS); rhs=0
 for rec in d['line_multipliers']:
  m=int(rec['multiplier_scaled']); key=tuple(rec['line_key'])
  assert m<=0
  for i in line_members(key): coeff[i]+=m
  rhs+=2*m
 for rec in d['equality_multipliers']:
  m=int(rec['multiplier_scaled']); label=rec['label']; rr=int(rec['rhs'])
  rhs+=m*rr
  if label[0]=='total':
   for i in range(len(POINTS)): coeff[i]+=m
  elif label[0]=='main': coeff[PID[(int(label[1]),int(label[1]))]]+=m
  else: raise AssertionError(label)
 for rec in d['lower_bound_multipliers']:
  m=int(rec['multiplier_scaled']); assert m>=0
  coeff[PID[tuple(rec['point'])]]-=m
 for rec in d['upper_bound_multipliers']:
  m=int(rec['multiplier_scaled']); assert m<=0
  coeff[PID[tuple(rec['point'])]]+=m
  rhs+=m
 Apts=[]
 for dm in d['A_definition']['diag_plus']:
  for dp in d['A_definition']['diag_minus']:
   x=(dp+dm)//2;y=(dp-dm)//2
   assert x-y==dm and x+y==dp and (x,y) in PID
   Apts.append((x,y))
 target=[0]*len(POINTS)
 for p in Apts: target[PID[p]]=-scale
 assert coeff==target, next((POINTS[i],coeff[i],target[i]) for i in range(len(POINTS)) if coeff[i]!=target[i])
 assert rhs==-803
 assert Fraction(803,273)<3
 print('Certificate verified exactly.')
 print('For every feasible fractional configuration: -273*A >= -803.')
 print('Therefore A <= 803/273 < 3, so every integral configuration has A <= 2.')

if __name__=='__main__': main()
