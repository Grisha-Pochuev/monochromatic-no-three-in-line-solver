# n22 final-two replicated run

Conclusion: `FOLLOWUP_RUN_INCOMPLETE`

- scheduled replica records: 20
- records found: 20
- complete replica set: yes
- child `652`: 10 `UNKNOWN`
- child `1132`: 5 `INFEASIBLE`, 5 `UNKNOWN`
- selected final status of child `652`: `UNKNOWN`
- selected final status of child `1132`: `INFEASIBLE`
- remaining child ids: `[652]`
- remaining main-diagonal pair indices: `[40]`
- cumulative exact exclusions: 2639 / 2640
- missing / duplicate / unexpected assignments: 0
- contradictory child ids: 0
- technical records: 0
- memory-guard records: 0
- solver work: 104.30 job-hours

The board is not yet closed. The next exact step is an exhaustive split of child `652` by the exact numbers of rows and columns containing two selected points. Transpose symmetry leaves 21 disjoint cases:

```text
12 <= row_twos <= column_twos <= 17
```
