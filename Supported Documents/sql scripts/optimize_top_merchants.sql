-- ======================================================================
-- OPTIMIZE TOP MERCHANTS QUERY
-- Fix 18-second query time → Target under 1 second
-- ======================================================================

USE sabpaisa2;

-- SOLUTION 1: Add optimized index with status first (better for WHERE clause)
-- This index order prioritizes the equality filter (status='SUCCESS')
-- before the range filter (trans_date), which is more efficient

CREATE INDEX IF NOT EXISTS idx_status_date_client_amount
    ON transaction_detail (status, trans_date, client_code, client_name, paid_amount);

-- SOLUTION 2: Create specialized index for GROUP BY optimization
-- This helps MySQL avoid filesort by having client columns early
CREATE INDEX IF NOT EXISTS idx_status_client_date_amount
    ON transaction_detail (status, client_code, client_name, trans_date, paid_amount);

-- SOLUTION 3: Ensure we have an index optimized for the exact query pattern
-- Column order: WHERE filters (status, trans_date) → GROUP BY (client_code) → SELECT (paid_amount)
CREATE INDEX IF NOT EXISTS idx_status_date_client_paid
    ON transaction_detail (status, trans_date, client_code, paid_amount);

-- Update table statistics to help query optimizer choose best index
ANALYZE TABLE transaction_detail;

-- ======================================================================
-- TEST THE OPTIMIZATIONS
-- ======================================================================

-- Test 1: Force use of status-first index
SET @start1 = NOW(6);
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail USE INDEX (idx_status_date_client_amount)
WHERE status = 'SUCCESS'
  AND trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;
SET @end1 = NOW(6);
SELECT CONCAT('Test 1 (status-first index): ',
    ROUND(TIMESTAMPDIFF(MICROSECOND, @start1, @end1) / 1000, 2), ' ms') AS Performance;

-- Test 2: Force use of client-optimized index
SET @start2 = NOW(6);
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail USE INDEX (idx_status_client_date_amount)
WHERE status = 'SUCCESS'
  AND trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;
SET @end2 = NOW(6);
SELECT CONCAT('Test 2 (client-optimized index): ',
    ROUND(TIMESTAMPDIFF(MICROSECOND, @start2, @end2) / 1000, 2), ' ms') AS Performance;

-- Test 3: Let MySQL choose automatically
SET @start3 = NOW(6);
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail
WHERE status = 'SUCCESS'
  AND trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;
SET @end3 = NOW(6);
SELECT CONCAT('Test 3 (auto-select index): ',
    ROUND(TIMESTAMPDIFF(MICROSECOND, @start3, @end3) / 1000, 2), ' ms') AS Performance;

-- ======================================================================
-- VERIFY INDEX USAGE
-- ======================================================================
EXPLAIN
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail
WHERE status = 'SUCCESS'
  AND trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;

-- ======================================================================
-- SUMMARY
-- ======================================================================
SELECT '✓ Optimized indexes created!' AS Status,
       'Run the tests above to find fastest index' AS Next_Step,
       'Update Python code with best-performing index hint' AS Final_Step;
