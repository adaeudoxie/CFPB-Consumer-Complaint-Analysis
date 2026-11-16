# Business Insights

All figures are from validated query outputs (output name in brackets), regenerated in `outputs/kpi_outputs/` by `python run_pipeline.py`. Each was produced by `sql/complaint_analysis.sql` or `sql/kpi_calculations.sql` and cross-checked in Python.
**Reading rules:** a complaint is a consumer-reported issue, not proven misconduct. A company response category is a recorded classification, not proof of a satisfactory outcome. 2017 and 2023 are partial years.

---

### Insight 1: Complaint volume grew 64.5% between 2018 and 2022 and is still rising in 2023
- Full-year volumes rose from **7,872 (2018) to 12,953 (2022)**, an increase of 64.5%. The only decline in that run was in 2019 (−10.12%). *(EV_E1_full_year_growth, K12_yoy_calendar)*
- On a like-for-like basis (1 Jan–28 Aug), 2023 recorded **9,131 complaints, 11.34% more than the same period in 2022 (8,201)**, the highest of any year. *(K12b_yoy_like_for_like)*
- **So what:** demand on complaint handling has grown every year since 2019. The 2023 partial-year total (−29.51% vs 2022) understates this, and should not be read as a decline.

### Insight 2: Two products account for two-thirds of all complaints, and "Managing an account" alone is almost a quarter
- **Checking/savings accounts (39.69%)** and **credit/prepaid cards (25.91%)** together account for **65.60%** of complaints. Adding credit reporting and mortgages brings this to 88.49%. *(EV_E2_product_concentration)*
- "Managing an account" is the single most common issue: **15,109 complaints (24.17% of all)**. Within checking/savings it makes up **60.89%** of complaints, ahead of closing (11.90%) and opening (10.98%) accounts. *(K05_by_issue, EV_E2b_checking_savings_issues)*
- **So what:** improvement effort aimed at day-to-day account servicing would affect the largest share of complaints.

### Insight 3: Timeliness dropped sharply in mid-2021, and 2021 accounts for half of all untimely responses
- Overall, **96.06%** of complaints with a recorded value were marked timely. In 2017–2019 the rate was above 99.8% each year, but in **2021 it fell to 89.02%**. *(K09_timely_response, K09b_timely_by_year)*
- The drop starts abruptly: **June 2021 had a timely rate of 58.35%** (389 untimely out of 934). It stayed below 85% for most of Jun–Oct 2021. *(EV_E3_untimely_by_month_2020_2022)*
- **2021 holds 1,224 of the 2,403 untimely responses (50.94%) across the whole period.** *(EV_E3c_untimely_share_2021)*
- In 2021 the untimely rate was highest for **debt collection (19.52%)** and **credit reporting (18.57%)**. Mortgage stayed at 0.42%. *(EV_E3b_untimely_2021_by_product)*
- Timeliness recovered only partly: 95.62% in 2022 and 93.16% in 2023 (Yes/No only), still below the pre-2020 level.
- **So what:** the data shows *when* and *where* timeliness failed, but not *why*. The cause (for example volume, staffing or a process change) needs internal investigation.

### Insight 4: Recorded relief differs sharply by product, and non-monetary relief has grown since 2022
- Monetary relief was recorded for **32.35% of checking/savings** and **29.62% of credit card** complaints, against **3.54% for credit reporting** and **4.06% for debt collection**. *(EV_E4_response_mix_by_product)*
- Across closed complaints, the monetary-relief share has stayed between 21% and 25% every year. **Non-monetary relief rose from 5.93% (2021) to 10.99% (2022)** and stayed at 10.82% in 2023. *(EV_E4b_relief_share_by_year_closed_only)*
- **So what:** the high monetary-relief share on deposit and card products suggests recurring, correctable account or charge errors. This is a pattern worth root-cause analysis, not a finding of fault.

### Insight 5: CFPB forwarding is usually same-day, but referral complaints make up nearly half of the long delays
- The median forwarding interval is **0 days** and the average is **1.22 days**. Only **435 complaints (0.70%) took more than 30 days**, with a maximum of 275. *(K11_forwarding_interval)*
- **Referral** complaints average **3.30 days** and only **24.41% are forwarded the same day**, compared with 92.22% for web complaints. Referrals are 17.22% of volume but **47.59% of all complaints taking more than 30 days**. *(EV_E5_forwarding_by_channel, EV_E5b_long_interval_share_by_channel)*
- Among the larger products, **mortgage** has the highest average interval (1.86 days) and 1.41% of mortgage complaints (93) exceed 30 days. *(K11b_forwarding_by_product)*
- **So what:** these delays happen *before* the company receives the complaint. They should not be counted against the company's response performance.

### Insight 6: July 2023 is the highest month on record, driven by checking/savings
- **July 2023 recorded 1,749 complaints, 57.45% above the Jan–Jun 2023 monthly average of 1,110.8**, and the highest of all 76 months. *(EV_E6b_july_vs_prior_avg, K03_monthly_volume)*
- Checking/savings complaints alone were **883 in July**, more than double June's 423. *(EV_E6_recent_months_by_product)*
- **So what:** this is an early-warning signal. The dataset can't explain the cause, but a spike this size warrants a targeted review.

### Insight 7: Public responses provide almost no context, and complaints are concentrated in a few states
- **96.47%** of complaints have "chose not to provide a public response". Only 30 complaints (0.05%) carry a substantive public response. *(EV_E7_public_response)*
- **California accounts for 21.93%** of complaints, followed by Florida (10.38%), Texas (7.50%) and New York (7.11%). *(EV_E8_top_states)*
- **So what:** state counts largely reflect where customers are. Without customer-base figures by state they can't be read as complaint *rates*.
