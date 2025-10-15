-- ======================================================================
-- DIAGNOSE TOP MERCHANTS QUERY PERFORMANCE
-- ======================================================================

USE sabpaisa2;

-- 1. Check current indexes on transaction_detail
SELECT
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    CARDINALITY,
    INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'sabpaisa2'
  AND TABLE_NAME = 'transaction_detail'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- 2. EXPLAIN the current slow query
EXPLAIN
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail
WHERE trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
  AND status = 'SUCCESS'
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;

-- 3. Check if index statistics are up to date
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    AVG_ROW_LENGTH,
    DATA_LENGTH,
    INDEX_LENGTH,
    UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'sabpaisa2'
  AND TABLE_NAME = 'transaction_detail';

-- 4. Test with INDEX HINT to force covering index usage
EXPLAIN
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail USE INDEX (idx_date_status_client_amount)
WHERE trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
  AND status = 'SUCCESS'
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;

-- 5. Alternative approach: Pre-filtered subquery with index
EXPLAIN
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM (
    SELECT client_code, client_name, paid_amount
    FROM transaction_detail
    WHERE trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
      AND trans_date <= NOW()
      AND status = 'SUCCESS'
) AS filtered
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;

-- 6. Check distinct client counts (impacts GROUP BY performance)
SELECT
    COUNT(DISTINCT client_code) as distinct_clients,
    COUNT(DISTINCT client_name) as distinct_names,
    COUNT(*) as total_success_records
FROM transaction_detail
WHERE trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
  AND status = 'SUCCESS';

-- 7. Test optimized index order (status first, then date)
-- This might be better for WHERE status = 'SUCCESS' filter
SELECT 'Creating optimized index for Top Merchants query...' AS Step;

CREATE INDEX IF NOT EXISTS idx_status_date_client_amount
    ON transaction_detail (status, trans_date, client_code, client_name, paid_amount);

-- 8. Test with new optimized index
EXPLAIN
SELECT
    client_code,
    client_name,
    SUM(paid_amount) as volume,
    COUNT(*) as count
FROM transaction_detail USE INDEX (idx_status_date_client_amount)
WHERE trans_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  AND trans_date <= NOW()
  AND status = 'SUCCESS'
GROUP BY client_code, client_name
ORDER BY volume DESC
LIMIT 10;

-- 9. Update statistics
ANALYZE TABLE transaction_detail;

-- 10. Show summary
SELECT
    'Diagnosis complete!' AS Status,
    'Check EXPLAIN output to see which index is being used' AS Action,
    'If "Using filesort" appears, GROUP BY is not optimized' AS Note;
