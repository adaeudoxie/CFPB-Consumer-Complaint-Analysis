# Testing and Validation Report

**Scope:** data pipeline, KPI calculations and the Power BI dashboard (Data Analytics track).
**Date:** 13 Nov 2026 · **Tested by:** Ada Eudoxie, with Claude as an AI assistant · **Environment:** Python 3 + pandas, SQLite, Power BI Desktop

## Summary
| Test Layer | Tests | Result | Evidence |
|---|---|---|---|
| Data validation (Python) | 23 automated checks | 23/23 pass | [Data quality report](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Reports/Data%20Quality%20Report.md) |
| Data validation (SQL) | 9 checks | 9/9 pass | [Data validation](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/SQL%20Scripts/data_validation.sql) |
| Negative test: validation catches bad data | Corrupted clean file (row removed, Pending→No) | 6 checks fail as expected | Section 3 |
| KPI cross-check (Python vs SQL) | 16 KPI tables, independently coded | 16/16 identical | [KPI report](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Reports/KPI%20Report.md) |
| Negative test: cross-check catches bad values | One altered SQL value (96.06→95.06) | Detected | Section 3 |
| Report definition (PBIR JSON schema) | 78 report files vs Microsoft schemas | 0 schema errors | Checked during development |
| Power BI model (DAX query view) | 18 measure values vs Python/SQL | 18/18 match | Section 4 |
| Power BI visuals (visual inspection) | 4 pages, 71 visuals | Render with correct values | [Dashboard](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/tree/main/Dashboard) |

## Data Validation Checks (Python)
Row and column counts. Complaint ID uniqueness and identical ID sets (raw vs clean). No duplicate rows. Date range 2017-05-01..2023-08-28. No date parse failures. No negative intervals. Forwarding interval recomputed row by row (0 mismatches). Year, quarter and month derivation. No missing months. Timely blanks match In-progress exactly. Blanks became Pending, never No. Timely denominator = Yes + No (61,022). Original categorical values unchanged. Product counts reconcile. All products mapped. No blanks in labelled columns. Label counts reconcile to raw blanks. Same-attribute groups flagged, not removed. Partial-year flag only on 2017 and 2023. Partial-month flag only on Aug 2023.

## Negative Tests
These confirm that the tests can fail, not just pass:
- Validation: removing one row and relabelling Pending as "No" made 6 checks FAIL (row count, ID set, Pending rule, denominator, category reconciliation, label reconciliation).
- Cross-check: changing the SQL timely % to 95.06 made K09 FAIL.

## Power BI Model vs Independent Calculations
DAX query run in Power BI Desktop (DAX query view) against the refreshed model. The query is at the end of [DAX measures](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Power%20BI/DAX%20Measures.dax):

| Measure | Power BI (DAX) | Python / SQL | Match |
|---|---|---|---|
| Total Complaints | 62,516 | 62,516 | ✅ |
| Timely Response % | 96.06 | 96.06 | ✅ |
| Untimely Responses | 2,403 | 2,403 | ✅ |
| Pending Timely Response | 1,494 | 1,494 | ✅ |
| In Progress Complaints | 1,494 | 1,494 | ✅ |
| Avg Forwarding Days | 1.22 | 1.22 | ✅ |
| Median Forwarding Days | 0 | 0 | ✅ |
| Max Forwarding Days | 275 | 275 | ✅ |
| Long Forwarding Complaints (>30) | 435 | 435 | ✅ |
| Monetary Relief % | 23.51 | 23.51 | ✅ |
| Products / Issues / Sub-issues | 9 / 76 / 158 | 9 / 76 / 158 | ✅ |
| YoY Change % (2022) | +16.18 | +16.18 | ✅ |
| Timely Response % (2021) | 89.02 | 89.02 | ✅ |
| Interval bands (sum) | 49,634 + 5,575 + 4,864 + 2,008 + 435 = 62,516 | 62,516 | ✅ |
| Annual volumes 2017–2023 | 5,394 · 7,872 · 7,075 · 8,942 · 11,149 · 12,953 · 9,131 | same | ✅ |
| Checking/Savings share (donut) | 39.69% | 39.69% | ✅ |
