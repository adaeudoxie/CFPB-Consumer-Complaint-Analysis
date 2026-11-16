-- ============================================================================
-- SQL data-validation checks (complement src/validation.py). Every row should return passed = 1.
-- Run: python src/run_sql.py --sql sql/data_validation.sql --prefix DV_
-- ============================================================================

-- name: data_validation_checks
SELECT 'Row count = 62,516' AS check_name, (SELECT COUNT(*) FROM complaints) = 62516 AS passed
UNION ALL SELECT 'Complaint ID unique', (SELECT COUNT(*) - COUNT(DISTINCT "Complaint ID") FROM complaints) = 0
UNION ALL SELECT 'Date range 2017-05-01..2023-08-28',
       (SELECT MIN("Date submitted") = '2017-05-01' AND MAX("Date submitted") = '2023-08-28' FROM complaints)
UNION ALL SELECT 'No negative forwarding interval', (SELECT COUNT(*) FROM complaints WHERE "Forwarding Interval Days" < 0) = 0
UNION ALL SELECT 'Interval = julianday difference',
       (SELECT COUNT(*) FROM complaints
        WHERE CAST(julianday("Date received") - julianday("Date submitted") AS INTEGER) <> "Forwarding Interval Days") = 0
UNION ALL SELECT 'Pending only on In progress',
       (SELECT COUNT(*) FROM complaints
        WHERE ("Timely Response Status" = 'Pending') <> ("Company response to consumer" = 'In progress')) = 0
UNION ALL SELECT 'No blank Timely Response Status', (SELECT COUNT(*) FROM complaints WHERE "Timely Response Status" IS NULL) = 0
UNION ALL SELECT '76 distinct months', (SELECT COUNT(DISTINCT substr("Year Month",1,7)) FROM complaints) = 76
UNION ALL SELECT 'Product values = 9', (SELECT COUNT(DISTINCT "Product") FROM complaints) = 9;
