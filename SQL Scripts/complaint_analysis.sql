-- ============================================================================
-- Evidence queries behind the business insights (reports/business_insights.md)
-- Dialect: SQLite 3. Run: python src/run_sql.py --sql sql/complaint_analysis.sql --prefix EV_
-- ============================================================================

-- name: E1_full_year_growth
SELECT "Year" AS year, COUNT(*) AS complaints FROM complaints
WHERE "Is Partial Year" = 0 GROUP BY "Year" ORDER BY "Year";

-- name: E2_product_concentration
SELECT "Product Short" AS product, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct_of_total,
       ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) / (SELECT COUNT(*) FROM complaints), 2) AS cumulative_pct
FROM complaints GROUP BY 1 ORDER BY complaints DESC;

-- name: E2b_checking_savings_issues
SELECT "Issue" AS issue, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_product
FROM complaints WHERE "Product" = 'Checking or savings account'
GROUP BY 1 ORDER BY complaints DESC LIMIT 5;

-- name: E3_untimely_by_month_2020_2022
SELECT substr("Year Month", 1, 7) AS year_month,
       SUM("Timely Response Status" = 'No') AS untimely,
       SUM("Timely Response Status" IN ('Yes','No')) AS valid,
       ROUND(100.0 * SUM("Timely Response Status" = 'Yes') / SUM("Timely Response Status" IN ('Yes','No')), 2) AS timely_pct
FROM complaints WHERE "Year" BETWEEN 2020 AND 2022 GROUP BY 1 ORDER BY 1;

-- name: E3b_untimely_2021_by_product
SELECT "Product Short" AS product,
       SUM("Timely Response Status" = 'No') AS untimely,
       SUM("Timely Response Status" IN ('Yes','No')) AS valid,
       ROUND(100.0 * SUM("Timely Response Status" = 'No') / SUM("Timely Response Status" IN ('Yes','No')), 2) AS untimely_pct
FROM complaints WHERE "Year" = 2021 GROUP BY 1 ORDER BY untimely DESC;

-- name: E3c_untimely_share_2021
SELECT SUM("Timely Response Status" = 'No' AND "Year" = 2021) AS untimely_2021,
       SUM("Timely Response Status" = 'No') AS untimely_all_years,
       ROUND(100.0 * SUM("Timely Response Status" = 'No' AND "Year" = 2021) / SUM("Timely Response Status" = 'No'), 2) AS pct_in_2021,
       SUM("Timely Response Status" = 'No' AND "Year Month" LIKE '2021-06%') AS untimely_jun_2021
FROM complaints;

-- name: E4_response_mix_by_product
SELECT "Product Short" AS product, COUNT(*) AS complaints,
       ROUND(100.0 * SUM("Company response to consumer" = 'Closed with monetary relief') / COUNT(*), 2) AS monetary_relief_pct,
       ROUND(100.0 * SUM("Company response to consumer" = 'Closed with non-monetary relief') / COUNT(*), 2) AS non_monetary_relief_pct,
       ROUND(100.0 * SUM("Company response to consumer" = 'Closed with explanation') / COUNT(*), 2) AS explanation_pct
FROM complaints GROUP BY 1 ORDER BY monetary_relief_pct DESC;

-- name: E4b_relief_share_by_year_closed_only
SELECT "Year" AS year,
       ROUND(100.0 * SUM("Company response to consumer" = 'Closed with monetary relief') / COUNT(*), 2) AS monetary_relief_pct,
       ROUND(100.0 * SUM("Company response to consumer" = 'Closed with non-monetary relief') / COUNT(*), 2) AS non_monetary_relief_pct
FROM complaints WHERE "Is In Progress" = 0 GROUP BY 1 ORDER BY 1;

-- name: E5_forwarding_by_channel
SELECT "Submitted via" AS channel, COUNT(*) AS complaints,
       ROUND(AVG("Forwarding Interval Days"), 2) AS avg_days,
       ROUND(100.0 * SUM("Forwarding Interval Days" = 0) / COUNT(*), 2) AS same_day_pct,
       SUM("Forwarding Interval Days" > 30) AS over_30_days,
       ROUND(100.0 * SUM("Forwarding Interval Days" > 30) / COUNT(*), 2) AS over_30_pct
FROM complaints GROUP BY 1 ORDER BY avg_days DESC;

-- name: E5b_long_interval_share_by_channel
SELECT "Submitted via" AS channel, SUM("Forwarding Interval Days" > 30) AS over_30_days,
       ROUND(100.0 * SUM("Forwarding Interval Days" > 30) / (SELECT SUM("Forwarding Interval Days" > 30) FROM complaints), 2) AS pct_of_long_intervals
FROM complaints GROUP BY 1 ORDER BY over_30_days DESC;

-- name: E6_recent_months_by_product
SELECT substr("Year Month", 1, 7) AS year_month, "Product Short" AS product, COUNT(*) AS complaints
FROM complaints WHERE "Year Month" >= '2023-01' GROUP BY 1, 2 ORDER BY 1, complaints DESC;

-- name: E6b_july_vs_prior_avg
WITH m AS (SELECT substr("Year Month",1,7) AS ym, COUNT(*) AS c FROM complaints
           WHERE "Year Month" >= '2023-01' AND "Year Month" < '2023-07' GROUP BY 1)
SELECT (SELECT COUNT(*) FROM complaints WHERE "Year Month" LIKE '2023-07%') AS jul_2023,
       ROUND((SELECT AVG(c) FROM m), 1) AS avg_jan_jun_2023,
       ROUND(100.0 * ((SELECT COUNT(*) FROM complaints WHERE "Year Month" LIKE '2023-07%') - (SELECT AVG(c) FROM m)) / (SELECT AVG(c) FROM m), 2) AS pct_above_avg,
       (SELECT COUNT(*) FROM complaints WHERE "Year Month" LIKE '2023-07%' AND "Product" = 'Checking or savings account') AS jul_checking_savings;

-- name: E7_public_response
SELECT "Public Response Clean" AS public_response, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct
FROM complaints GROUP BY 1 ORDER BY complaints DESC;

-- name: E8_top_states
SELECT "State" AS state, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct
FROM complaints GROUP BY 1 ORDER BY complaints DESC LIMIT 10;

-- name: E9_channel_mix
SELECT "Submitted via" AS channel, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct
FROM complaints GROUP BY 1 ORDER BY complaints DESC;
