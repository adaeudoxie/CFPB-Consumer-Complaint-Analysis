# Testing and Validation Report

**Scope:** data pipeline, KPI calculations and the Power BI dashboard (Data Analytics track).
**Date:** 13 Nov 2026 · **Tested by:** Ada Eudoxie, with Claude as an AI assistant · **Environment:** Python 3 + pandas, SQLite, Power BI Desktop

## 1. Summary
| Test layer | Tests | Result | Evidence |
|---|---|---|---|
| Data validation (Python) | 23 automated checks | ✅ 23/23 pass | `reports/data_quality_report.md` §6 |
| Data validation (SQL) | 9 checks | ✅ 9/9 pass | `sql/data_validation.sql` |
| Negative test: validation catches bad data | Corrupted clean file (row removed, Pending→No) | ✅ 6 checks fail as expected | Section 3 |
| KPI cross-check (Python vs SQL) | 16 KPI tables, independently coded | ✅ 16/16 identical | `reports/kpi_report.md` §3 |
| Negative test: cross-check catches bad values | One altered SQL value (96.06→95.06) | ✅ Detected | Section 3 |
| Report definition (PBIR JSON schema) | 78 report files vs Microsoft schemas | ✅ 0 schema errors | Checked during development |
| Power BI model (DAX query view) | 18 measure values vs Python/SQL | ✅ 18/18 match | Section 4 |
| Power BI visuals (visual inspection) | 4 pages, 71 visuals | ✅ Render with correct values | `powerbi/screenshots/` |
| End-to-end reproducibility | `python run_pipeline.py` from raw Excel | ✅ Completes, all checks pass | Console log |

## 2. Data validation checks (Python)
Row and column counts. Complaint ID uniqueness and identical ID sets (raw vs clean). No duplicate rows. Date range 2017-05-01..2023-08-28. No date parse failures. No negative intervals. Forwarding interval recomputed row by row (0 mismatches). Year, quarter and month derivation. No missing months. Timely blanks match In-progress exactly. Blanks became Pending, never No. Timely denominator = Yes + No (61,022). Original categorical values unchanged. Product counts reconcile. All products mapped. No blanks in labelled columns. Label counts reconcile to raw blanks. Same-attribute groups flagged, not removed. Partial-year flag only on 2017 and 2023. Partial-month flag only on Aug 2023.

## 3. Negative tests
These confirm that the tests can fail, not just pass:
- **Validation:** removing one row and relabelling Pending as "No" made 6 checks FAIL (row count, ID set, Pending rule, denominator, category reconciliation, label reconciliation).
- **Cross-check:** changing the SQL timely % to 95.06 made K09 FAIL.

## 4. Power BI model vs independent calculations
DAX query run in Power BI Desktop (DAX query view) against the refreshed model. The query is at the end of [`powerbi/measures.dax`](../powerbi/measures.dax):

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

## 5. Defects found and fixed during testing
| # | Defect | Cause | Fix | Retest |
|---|---|---|---|---|
| T1 | Report would not open: path too long | Windows 260-character path limit with the long repo folder name | Shortened the project name to `CCI_Dashboard` and the page and visual folder names (max path now 243) | ✅ Opens |
| T2 | "Circular dependency" on load | Sort-by column was calculated from the column it sorts | Moved `Interval Band Order` into Power Query | ✅ |
| T3 | Sub-issues showed 159 instead of 158 | Power Query loads blank CSV cells as empty text, which counts as a value | Measure now counts `Sub-issue Clean` excluding the "No sub-issue recorded" label | ✅ 158 |
| T4 | Total showed "63K" | Card auto display units | Display units set to none | ✅ 62,516 |
| T5 | Navigation buttons had no text, then truncated text | Button text formatting needed an unscoped `show` entry. Labels were too long | Fixed formatting. Shorter labels | ✅ |
| T6 | Grey auto-subtitles on every chart | Default subtitle in the stylable header | Subtitle hidden | ✅ |
| T7 | Validation flagged only 2023 as a partial year | 2017 starts in May | Partial-year flag covers 2017 and 2023 | ✅ |
| T8 | Mortgage >30-day share typed as 1.38% in the insights report | Manual typo | Corrected to 1.41% (93/6,601) after cross-checking against query output | ✅ |

## 6. Known limitations of the tests
- `% of Total Complaints` is relative to the current selection (`ALLSELECTED`). In an isolated DAX query that filters to one product it returns 100% by design. In visuals it gives the correct share (verified: 39.69%).
- Slicer and cross-filter interactions were checked visually, not by automated tests.
- The pipeline was executed in a Linux environment on a copy of the data. Power BI was tested on Ada's Windows PC.

## 7. Revision log
Meaningful revisions made during development and after feedback (brief §7.6).

| Date | Area | Revision | Reason |
|---|---|---|---|
| 13 Nov 2026 | Cleaning | Same-attribute groups flagged (248 possible repeat submissions) | Profiling found 1,494 rows identical apart from the ID. Investigated rather than deleted |
| 13 Nov 2026 | Cleaning | Partial-year flag extended to 2017 | 2017 covers May–Dec only. The original flag marked 2023 alone |
| 13 Nov 2026 | Analysis | Cross-check made sort-insensitive | First run flagged tied issue counts in a different order (not a value error) |
| 13 Nov 2026 | Reports | Mortgage >30-day share corrected 1.38% → 1.41% | Manual check against query output |
| 13 Nov 2026 | Dashboard | Project and visual names shortened | Windows 260-character path limit |
| 13 Nov 2026 | Dashboard | Interval band sort moved to Power Query | Circular dependency in a calculated sort column |
| 13 Nov 2026 | Dashboard | Sub-issues measure uses labelled column (159 → 158) | Blank text counted as a value in Power BI |
| 13 Nov 2026 | Dashboard | Full numbers on KPI cards, nav labels, subtitles removed | Visual QA |
| 13 Nov 2026 | Dashboard | Executive summary: June 2021 timely rate 58.3% → 58.4% | Rounding check against 58.35% |
| 13 Nov 2026 | Repository | Generated outputs moved to `outputs/` (not committed). Reports and docs consolidated. Power BI delivered as a template (.pbit) plus readable DAX | Leaner, more readable repository (134 → 30 files) |
| 14 Nov 2026 | Dashboard | Colour theme changed from plum to "Lavender Bloom" (lavender, violet, pink). Timeline KPI titles shortened. Screenshots retaken | Distinguish from a previous dashboard; titles were wrapping |
| _date_ | _area_ | _Mentor feedback and resulting change_ | _to be added after review_ |
