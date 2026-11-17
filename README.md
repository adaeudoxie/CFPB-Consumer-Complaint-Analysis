# CFPB-Consumer-Complaint-Analysis
An end-to-end analytics project on **62,516 consumer complaints** about Bank of America submitted to the US Consumer Financial Protection Bureau (CFPB) between **1 May 2017 and 28 Aug 2023**. It covers data validation, cleaning, 12 KPIs cross-checked in Python and SQL, evidence-based insights, and a four-page Power BI dashboard.
> A complaint is a consumer-reported issue. It is not proof of misconduct. A company response category is a recorded classification, not proof of a satisfactory outcome.

![Executive Overview](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Dashboard/Executive%20Overview.jpg)

## Headline Results
| KPI | Value |
|---|---|
| Total Complaints | **62,516** |
| Full-Year Growth, 2018 → 2022 | **+64.5%** |
| Jan–Aug 2023 vs Jan–Aug 2022 | **+11.34%** |
| Top Product | Checking/Savings: **39.69%** of complaints |
| Top Issue | Managing an Account: **24.17%** |
| Timely Response % | **96.06%** (1,494 pending excluded) |
| Lowest Monthly Timely Rate | **58.35%** (June 2021) |
| CFPB Forwarding Interval | Average **1.22** days, 435 complaints > 30 days |

**Key Insights** (Full detail in [Business Insights](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Reports/Business%20Insights%20%26%20Recommendations.md))
1. Volume grew 64.5% in 4 full years and is still rising in 2023.
2. Two products account for two-thirds of complaints. "Managing an account" alone is almost a quarter.
3. Timeliness collapsed in mid-2021, and 2021 holds half of all untimely responses.
5. Referral complaints are 17% of volume but 48% of 30+ day forwarding delays.
6. July 2023 is the highest month on record (+57% vs the Jan–Jun average).

Linked recommendations in [Business Insights](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Reports/Business%20Insights%20%26%20Recommendations.md)

## Dashboard
| Page | Focus |
|---|---|
| [Executive Overview](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Dashboard/Executive%20Overview.jpg) | KPIs, monthly trend, product mix, annual volume, responses, summary |
| [Product & Issue](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Dashboard/Product%20%26%20Issue%20Analysis.jpg) | Products, top sub-products, top issues, issue × product |
| [Company Response](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Dashboard/Company%20Response%20Analysis.jpg) | Response categories, timely/untimely/pending, monthly timeliness, response mix by product, public responses |
| [Complaint Timeline](https://github.com/adaeudoxie/CFPB-Consumer-Complaint-Analysis/blob/main/Dashboard/Complaint%20Timeline%20Analysis.jpg) | Monthly trend, annual YoY (partial years flagged), interval distribution, intervals by product, 30+ day cases |

## Repository structure
```
├── src/                      # reproducible Python pipeline
│   ├── config.py             # paths and constants
│   ├── data_cleaning.py      # raw Excel → cleaned CSV (no rows removed, originals preserved)
│   ├── data_inspection.py    # profiles the raw data
│   ├── validation.py         # 23 automated data checks
│   ├── analysis.py           # 12 KPIs (pandas)
│   ├── run_sql.py            # runs named SQL queries in SQLite
│   └── cross_check.py        # Python vs SQL KPI comparison
├── sql/                      # KPI, insight-evidence and validation queries
├── notebooks/                # complaint_analysis.ipynb (executed walkthrough)
├── reports/                  # data quality · KPI report · business insights · recommendations
├── documentation/            # data dictionary · methodology · dashboard guide · testing report
├── powerbi/                  # dashboard template (.pbit), DAX measures, screenshots
└── run_pipeline.py           # one command: clean → validate → KPIs → SQL → cross-check
```

## Methodology
### Design Decisions
| Decision | Rationale |
|---|---|
| Never delete rows | No duplicate keys or rows. Distinct Complaint IDs are distinct complaints (brief §4) |
| Keep originals and add new columns | Every cleaned value traces back to the source |
| Blank timely → "Pending", excluded from denominator | The blanks match *In progress* exactly |
| Forwarding interval named as CFPB-side | Avoids misreading it as company response time |
| "Unusually long" = > 30 days | About the 99.3rd percentile (435 of 62,516). Clear operational meaning |
| Partial-year flags on 2017 and 2023 | Prevents misleading YoY |
| Like-for-like YoY window (1 Jan – 28 Aug) | Fair 2023 comparison |
| Same-attribute groups flagged, not removed | 248 possible repeat submissions. Sensitivity can be tested |
| Two independent KPI implementations | Detects logic errors that a single implementation would hide |

### Validation Strategy
Data checks → negative tests → SQL cross-check → schema validation of report JSON → DAX query check in Power BI → visual inspection. See [`testing_report.md`](testing_report.md).

### Assumptions and Limitations
#### Data Limitations
- **No company response or resolution date.** Company response time cannot be measured. The only interval available is CFPB forwarding time.
- **No customer or account counts.** Volumes can't be converted to complaint *rates* by product or state. California's 21.93% share most likely reflects customer distribution.
- **No relief amounts or satisfaction/dispute field.** Response categories describe what was recorded, not whether the consumer was satisfied.
- **Partial periods:** 2017 (May–Dec), 2023 (Jan–28 Aug), Aug 2023 (to the 28th).
- **Recent complaints still open:** 1,494 in progress, and 1,550 of the blank public responses are from 2023. Recent-period response metrics may change.
- **Possible repeat submissions:** 248 rows in 120 groups share all attributes with near-consecutive IDs. They are kept since the effect on KPIs is below 0.4% of volume.

#### Analytical Assumptions
- Each Complaint ID is one complaint.
- Date submitted is the event date for all time-based analysis.
- The ">30 days" threshold for unusually long forwarding is a judgement (≈99.3rd percentile).
- Issue and product combinations are taken as recorded. Credit-reporting issues filed under card or mortgage products follow CFPB form design.

#### What the Analysis Does not Claim
- Causes for the June 2021 timeliness drop or the July 2023 spike. These need internal data.
- Misconduct or regulatory breach.

### Integration with Other Tracks
This project provides validated, reusable assets for the other tracks in the internship:

| Track | What Data Analytics Provides | Where |
|---|---|---|
| Data Science | Cleaned dataset with documented rules. Validated KPI tables for hypothesis tests | `03_Working_Files/complaints_clean.csv`, `outputs/kpi_outputs/` (via `run_pipeline.py`) |
| Machine Learning | Validated monthly series (76 months, no gaps) with partial-month flag | `outputs/kpi_outputs/PY_K03_monthly_volume.csv` |
| Generative AI | Ground-truth KPI values and definitions for grounding and evaluating the assistant's answers | `reports/kpi_report.md` |
| Project Management | Deliverables register, testing evidence, risk inputs (data quality issues DQ1–DQ10) | `04_Deliverables/Deliverables_Register.xlsx`, `reports/data_quality_report.md` |

#### Shared Definitions
See the "Shared definitions" table in `reports/kpi_report.md` (section 4): complaint volume, product/issue, company response, timely indicator (Yes/No/Pending), forwarding interval and reporting period.

## Method in Brief
1. **Inspect and clean:** label, derive and flag, never delete. 22 derived columns ([data_quality_report](reports/data_quality_report.md)).
2. **Validate:** 23 Python and 9 SQL checks, plus negative tests ([data_quality_report §6](reports/data_quality_report.md#6-validation-results)).
3. **Calculate:** 12 KPIs in Python and independently in SQL. 16/16 tables identical ([kpi_report](reports/kpi_report.md)).
4. **Visualise:** Power BI model with 19 DAX measures, validated by DAX query against the Python/SQL outputs ([testing_report](documentation/testing_report.md)).

Full methodology: [`documentation/methodology.md`](documentation/methodology.md).

## Key Interpretation Rules
- **Blank "Timely response?" is not "No".** The 1,494 blanks are all *In progress* complaints. They are labelled *Pending* and excluded from the timely % denominator.
- **Date received − Date submitted is the CFPB forwarding interval**, not the company's response or resolution time.
- **2017 (May–Dec) and 2023 (Jan–28 Aug) are partial years.** Year-on-year comparisons use full years or the same Jan–Aug window.

## Tools
- Python
- SQLite
- Jupyter
- Power BI

## AI assistance
Claude (Anthropic) was used as an AI assistant for Python checks. All outputs were run, validated and reviewed. The revision log is in [`documentation/testing_report.md`](documentation/testing_report.md#7-revision-log).

---
#AnalystLabAfrica
