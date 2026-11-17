# KPI Report

**Source table:** `cleaned_dataset.csv` (62,516 rows).
**Date basis:** `Date submitted`, the date the CFPB received the complaint.
**Calculated in:** `python_flies/analysis.py` (Python) and `sql_scripts/kpi_calculations.sql` (SQL). Both results are compared automatically (section 3: 16/16 match).
**Dashboard:** the DAX measure names below are the ones used in the Power BI model.

## Contents
1. Definitions
2. Results summary
3. Python vs SQL cross-check
4. Shared definitions

## Definitions

| # | KPI | Definition | Formula | DAX measure | Result | Caveats |
|---|---|---|---|---|---|---|
| 1 | Total complaints | Number of complaint records | `COUNT(Complaint ID)` | `[Total Complaints]` | 62,516 | A complaint is a consumer-reported issue, not proof of wrongdoing |
| 2 | Annual complaint volume | Complaints per calendar year of Date submitted | `COUNT` grouped by Year | `[Total Complaints]` by Year | 2018: 7,872 · 2019: 7,075 · 2020: 8,942 · 2021: 11,149 · 2022: 12,953 | 2017 (May–Dec, 5,394) and 2023 (Jan–28 Aug, 9,131) are partial years |
| 3 | Monthly complaint volume | Complaints per calendar month | `COUNT` grouped by Year Month | `[Total Complaints]` by Year Month | 76 months. Peak Jul 2023 = 1,749 | Aug 2023 is partial (ends on the 28th) |
| 4 | Complaints by product | Complaints per Product | `COUNT` by Product | `[Total Complaints]` by Product | Checking or savings: 24,814 | 9 products |
| 5 | Complaints by issue | Complaints per Issue | `COUNT` by Issue | `[Total Complaints]` by Issue | Managing an account: 15,109 | 76 issues. Some issues appear under several products |
| 6 | Complaints by sub-product / sub-issue | Complaints per Product × Sub-product, and per Issue × Sub-issue | `COUNT` by pair | `[Total Complaints]` by Sub-product / Sub-issue | 47 and 211 pairs | Blanks shown as "Not provided" / "No sub-issue recorded" |
| 7 | Product % contribution | Product complaints ÷ total complaints | `COUNT(product) / COUNT(all)` | `[% of Total Complaints]` | Checking or savings 39.69%. Top 2 products 65.60% | Respects slicers: % of the filtered total |
| 8 | Company response distribution | Complaints per Company response to consumer, plus public-response mix | `COUNT` by category | `[Total Complaints]` by Response | Closed with explanation 65.65% · Monetary relief 23.51% · Non-monetary 8.43% · In progress 2.39% · Closed 0.01% | Recorded classification, not proof of satisfactory resolution |
| 9 | Timely response % | Share of complaints marked timely, among complaints with a Yes/No value | `Yes ÷ (Yes + No)` | `[Timely Response %]` | 96.06% (58,619 ÷ 61,022) | 1,494 Pending (blank) records are excluded from the denominator and reported separately (`[Pending Timely Response]`) |
| 10 | In-progress complaints | Complaints whose company response = In progress | `COUNT WHERE response = 'In progress'` | `[In Progress Complaints]` | 1,494 | All submitted 12 May – 28 Aug 2023 |
| 11 | Average & median forwarding interval | Days between the CFPB receiving a complaint and sending it to the company | `AVG / MEDIAN(Date received − Date submitted)` | `[Avg Forwarding Days]`, `[Median Forwarding Days]` | 1.22 days average, 0 days median. 435 complaints > 30 days. Max 275 | This is CFPB forwarding time, not company response or resolution time. "Unusually long" = > 30 days |
| 12 | Year-over-year change | (Year N − Year N−1) ÷ Year N−1 | as stated | `[YoY Change %]` | 2019 −10.12% · 2020 +26.39% · 2021 +24.68% · 2022 +16.18% | Only full-year pairs are valid. Like-for-like (1 Jan–28 Aug): 2023 vs 2022 +11.34% |

## Results Summary
| # | KPI | Value |
|---|---|---|
| 1 | Total complaints | 62,516 |
| 2 | Annual volume | Peak full year 2022: 12,953. 2017 and 2023 are partial years |
| 3 | Monthly volume | 76 months. Highest: 2023-07 (1,749) |
| 4 | Top product | Checking or savings account: 24,814 |
| 5 | Top issue | Managing an account: 15,109 (24.17%) |
| 6 | Sub-product / sub-issue combinations | 47 product–sub-product pairs. 211 issue–sub-issue pairs |
| 7 | Top product share | 39.69% of all complaints |
| 8 | Most common company response | Closed with explanation: 41,044 (65.65%) |
| 9 | Timely response % | 96.06% (58,619 Yes ÷ 61,022 Yes+No). 1,494 pending excluded |
| 10 | In progress | 1,494 |
| 11 | CFPB forwarding interval | Average 1.22 days, median 0 days. 435 over 30 days (max 275) |
| 12 | YoY change (full years) | 2019: -10.12%, 2020: +26.39%, 2021: +24.68%, 2022: +16.18% |

## Python vs SQL cross-check
Each KPI was calculated twice, in pandas (`python_files/analysis.py`) and in SQLite (`sql_scripts/kpi_calculations.sql`), using code written independently. A KPI passes only if every row and value matches (tolerance ±0.01 for rounded percentages). All KPI values matched.

| KPI Table | Result | Detail |
|---|---|---|
| K01_total_complaints | PASS | 1 row, identical |
| K02_annual_volume | PASS | 7 rows, identical |
| K03_monthly_volume | PASS | 76 rows, identical |
| K04_K07_by_product | PASS | 9 rows, identical |
| K05_by_issue | PASS | 76 rows, identical |
| K06a_by_sub_product | PASS | 47 rows, identical |
| K06b_by_sub_issue | PASS | 211 rows, identical |
| K08_response_distribution | PASS | 5 rows, identical |
| K08b_public_response_distribution | PASS | 7 rows, identical |
| K09_timely_response | PASS | 1 row, identical |
| K09b_timely_by_year | PASS | 7 rows, identical |
| K10_in_progress | PASS | 1 row, identical |
| K11_forwarding_interval | PASS | 1 row, identical |
| K11b_forwarding_by_product | PASS | 9 rows, identical |
| K12_yoy_calendar | PASS | 7 rows, identical |
| K12b_yoy_like_for_like | PASS | 6 rows, identical |

## Definitions
| Term | Definition |
|---|---|
| Complaint volume | Count of distinct Complaint IDs |
| Product / Issue | Values exactly as recorded by the CFPB (short labels for display only) |
| Company response | `Company response to consumer`, a recorded category, not a judgement of the outcome |
| Timely-response indicator | Yes / No / Pending. Pending (blank) is excluded from timely % |
| Forwarding interval | `Date received − Date submitted`, in days. CFPB-side forwarding time only |
| Reporting period | 1 May 2017 – 28 Aug 2023. 2017 and 2023 are partial years. Aug 2023 is a partial month |
