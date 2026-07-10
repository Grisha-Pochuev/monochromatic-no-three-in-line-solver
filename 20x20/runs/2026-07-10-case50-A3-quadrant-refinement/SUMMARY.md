# Case 50, A=3: quadrant refinement

Date: 2026-07-10

Definitions: L is the number of selected points with x<10; T with y<10; Q with x<10 and y<10; C in the central square 5<=x<15 and 5<=y<15.

Exact CP-SAT infeasibility checks closed the profiles (L,T)=(12,15) and (13,14).

The remaining A=3 profiles are:

- (13,15)
- (14,14)
- (14,15)
- (15,15)

For (13,15), Q=5 and Q=7 are infeasible. The only remaining quadrant branch is Q=6. Splitting it by C closed C=1 and C=3, while all other values except C=2 had already closed in the complete scan.

Therefore (13,15) is reduced to the single micro-profile:

A=3, L=13, T=15, Q=6, C=2.

This micro-profile remains UNKNOWN within the local time budget. UNKNOWN is not evidence of feasibility.

The board status remains 30 <= D_mono(20) <= 31.
