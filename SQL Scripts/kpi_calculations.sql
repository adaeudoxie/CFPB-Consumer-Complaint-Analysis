-- ============================================================================
-- KPI calculations: AnalystLab Africa Week 4 (Data Analytics track)
-- Dialect: SQLite 3.  Table: complaints (loaded from complaints_clean.csv by src/run_sql.py)
-- Each query starts with "-- name: <KPI id>". run_sql.py runs them and writes
-- outputs/kpi_outputs/SQL_<KPI id>.csv. src/cross_check.py compares them with the Python results.
-- Business rules: timely % denominator = Yes + No only; forwarding interval = CFPB forwarding,
-- not company response time; 2017 and 2023 are partial years.
-- ============================================================================

-- name: K01_total_complaints
SELECT COUNT(*) AS total_complaints FROM complaints;

-- name: K02_annual_volume
SELECT "Year" AS year, COUNT(*) AS complaints, MAX("Is Partial Year") AS is_partial_year
FROM complaints GROUP BY "Year" ORDER BY "Year";

-- name: K03_monthly_volume
SELECT substr("Year Month", 1, 7) AS year_month, COUNT(*) AS complaints, MAX("Is Partial Month") AS is_partial_month
FROM complaints GROUP BY year_month ORDER BY year_month;

-- name: K04_K07_by_product
SELECT "Product" AS product, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct_of_total
FROM complaints GROUP BY "Product" ORDER BY complaints DESC;

-- name: K05_by_issue
SELECT "Issue" AS issue, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct_of_total
FROM complaints GROUP BY "Issue" ORDER BY complaints DESC, issue;

-- name: K06a_by_sub_product
SELECT "Product" AS product, "Sub-product Clean" AS sub_product, COUNT(*) AS complaints
FROM complaints GROUP BY 1, 2 ORDER BY complaints DESC, product, sub_product;

-- name: K06b_by_sub_issue
SELECT "Issue" AS issue, "Sub-issue Clean" AS sub_issue, COUNT(*) AS complaints
FROM complaints GROUP BY 1, 2 ORDER BY complaints DESC, issue, sub_issue;

-- name: K08_response_distribution
SELECT "Company response to consumer" AS company_response, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct_of_total
FROM complaints GROUP BY 1 ORDER BY complaints DESC;

-- name: K08b_public_response_distribution
SELECT "Public Response Clean" AS public_response, COUNT(*) AS complaints,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM complaints), 2) AS pct_of_total
FROM complaints GROUP BY 1 ORDER BY complaints DESC;

-- name: K09_timely_response
SELECT SUM("Timely Response Status" = 'Yes') AS timely_yes,
       SUM("Timely Response Status" = 'No')  AS timely_no,
       SUM("Timely Response Status" IN ('Yes','No')) AS valid_denominator,
       SUM("Timely Response Status" = 'Pending') AS excluded_pending,
       ROUND(100.0 * SUM("Timely Response Status" = 'Yes') / SUM("Timely Response Status" IN ('Yes','No')), 2) AS timely_pct
FROM complaints;

-- name: K09b_timely_by_year
SELECT "Year" AS year,
       SUM("Timely Response Status" = 'Yes') AS timely_yes,
       SUM("Timely Response Status" = 'No')  AS timely_no,
       ROUND(100.0 * SUM("Timely Response Status" = 'Yes') / SUM("Timely Response Status" IN ('Yes','No')), 2) AS timely_pct
FROM complaints WHERE "Timely Response Status" IN ('Yes','No') GROUP BY "Year" ORDER BY "Year";

-- name: K10_in_progress
SELECT COUNT(*) AS in_progress FROM complaints WHERE "Company response to consumer" = 'In progress';

-- name: K11_forwarding_interval
WITH ordered AS (
  SELECT "Forwarding Interval Days" AS d,
         ROW_NUMBER() OVER (ORDER BY "Forwarding Interval Days") AS rn,
         COUNT(*) OVER () AS n
  FROM complaints)
SELECT (SELECT ROUND(AVG("Forwarding Interval Days"), 2) FROM complaints) AS avg_days,
       (SELECT AVG(d) * 1.0 FROM ordered WHERE rn IN ((n + 1) / 2, (n + 2) / 2)) AS median_days,
       (SELECT MAX("Forwarding Interval Days") FROM complaints) AS max_days,
       (SELECT COUNT(*) FROM complaints WHERE "Forwarding Interval Days" > 30) AS over_30_days;

-- name: K11b_forwarding_by_product
WITH ordered AS (
  SELECT "Product" AS product, "Forwarding Interval Days" AS d,
         ROW_NUMBER() OVER (PARTITION BY "Product" ORDER BY "Forwarding Interval Days") AS rn,
         COUNT(*) OVER (PARTITION BY "Product") AS n
  FROM complaints),
med AS (SELECT product, AVG(d) * 1.0 AS median_days FROM ordered WHERE rn IN ((n + 1) / 2, (n + 2) / 2) GROUP BY product)
SELECT c."Product" AS product, COUNT(*) AS complaints, ROUND(AVG(c."Forwarding Interval Days"), 2) AS avg_days,
       m.median_days, SUM(c."Forwarding Interval Days" > 30) AS over_30_days
FROM complaints c JOIN med m ON m.product = c."Product"
GROUP BY c."Product" ORDER BY avg_days DESC;

-- name: K12_yoy_calendar
WITH y AS (SELECT "Year" AS year, COUNT(*) AS complaints, MAX("Is Partial Year") AS is_partial_year
           FROM complaints GROUP BY "Year")
SELECT year, complaints, is_partial_year,
       LAG(complaints) OVER (ORDER BY year) AS prev_year_complaints,
       complaints - LAG(complaints) OVER (ORDER BY year) AS yoy_change,
       ROUND(100.0 * (complaints - LAG(complaints) OVER (ORDER BY year)) / LAG(complaints) OVER (ORDER BY year), 2) AS yoy_pct,
       CASE WHEN is_partial_year = 0 AND LAG(is_partial_year) OVER (ORDER BY year) = 0 THEN 1 ELSE 0 END AS comparison_valid
FROM y ORDER BY year;

-- name: K12b_yoy_like_for_like
WITH y AS (SELECT "Year" AS year, COUNT(*) AS complaints_jan1_to_aug28
           FROM complaints WHERE substr("Date submitted", 6, 5) <= '08-28' AND "Year" >= 2018
           GROUP BY "Year")
SELECT year, complaints_jan1_to_aug28,
       ROUND(100.0 * (complaints_jan1_to_aug28 - LAG(complaints_jan1_to_aug28) OVER (ORDER BY year))
             / LAG(complaints_jan1_to_aug28) OVER (ORDER BY year), 2) AS yoy_pct
FROM y ORDER BY year;
