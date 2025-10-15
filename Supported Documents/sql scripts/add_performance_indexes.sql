-- ======================================================================
-- PERFORMANCE OPTIMIZATION: Add Missing Database Indexes (MySQL 8.x)
-- ======================================================================

USE sabpaisa2;

-- Inspect existing indexes
SHOW INDEX FROM transaction_detail;

-- Helper: drop old indexes safely (only if you know names may exist)
-- (Uncomment if you want idempotent behavior)
-- DROP INDEX IF EXISTS idx_trans_date_status ON transaction_detail;
-- DROP INDEX IF EXISTS idx_client_status_date ON transaction_detail;
-- DROP INDEX IF EXISTS idx_payment_mode_date ON transaction_detail;
-- DROP INDEX IF EXISTS idx_settlement_status_date ON transaction_detail;
-- DROP INDEX IF EXISTS idx_txn_id ON transaction_detail;
-- DROP INDEX IF EXISTS idx_client_txn_id ON transaction_detail;
-- DROP INDEX IF EXISTS idx_success_trans_date ON transaction_detail;

-- ======================================================================
-- RECOMMENDED INDEXES (orders tuned to common filters)
-- ======================================================================

-- 1) Date + status filters (most frequent)
-- Use equality first, then range
CREATE INDEX idx_status_trans_date
  ON transaction_detail (status, trans_date);

-- 2) Merchant analytics: filter by status/date, group by client_code
-- Put filter columns first, then the grouping column
CREATE INDEX idx_status_date_client
  ON transaction_detail (status, trans_date, client_code);

-- 3) Payment mode + date (for filtering by payment_mode within a date range)
-- If you more often start with a date filter and then GROUP BY payment_mode,
-- consider (trans_date, payment_mode) instead. Pick ONE dominant pattern.
CREATE INDEX idx_payment_mode_trans_date
  ON transaction_detail (payment_mode, trans_date);

-- 4) Settlement flows (filter by is_settled, then settlement_date, then optional trans_date)
CREATE INDEX idx_is_settled_settlement_date_trans_date
  ON transaction_detail (is_settled, settlement_date, trans_date);

-- 5) Direct lookups
CREATE INDEX idx_txn_id
  ON transaction_detail (txn_id);

CREATE INDEX idx_client_txn_id
  ON transaction_detail (client_txn_id);

-- 6) Active merchants count: COUNT(DISTINCT client_code) by date range
-- CRITICAL for dashboard performance - speeds up merchant counting
CREATE INDEX idx_trans_date_client_code
  ON transaction_detail (trans_date, client_code);

-- NOTE: Partial index for SUCCESS-only is not supported in MySQL.
-- The general-purpose composite idx_status_trans_date covers that use case.

-- ======================================================================
-- VERIFY INDEXES
-- ======================================================================

SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'sabpaisa2'       -- match your active schema
  AND TABLE_NAME = 'transaction_detail'
  AND INDEX_NAME LIKE 'idx_%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- ======================================================================
-- STATS / OPTIMIZER HELPERS
-- ======================================================================
ANALYZE TABLE transaction_detail;

-- ======================================================================
-- EXPLAIN TESTS
-- ======================================================================

-- Test 1: should prefer idx_status_trans_date
EXPLAIN FORMAT=TREE
SELECT COUNT(*), SUM(paid_amount)
FROM transaction_detail
WHERE status = 'SUCCESS'
  AND trans_date >= '2025-10-07 00:00:00'
  AND trans_date <= '2025-10-07 23:59:59';

-- Test 2: should prefer idx_status_date_client
EXPLAIN FORMAT=TREE
SELECT client_code, COUNT(*), SUM(paid_amount)
FROM transaction_detail
WHERE status = 'SUCCESS'
  AND trans_date >= '2025-10-01'
GROUP BY client_code
ORDER BY SUM(paid_amount) DESC
LIMIT 10;

-- Test 3: distribution by payment mode within date window
-- If you mostly filter only by date and then GROUP BY payment_mode,
-- consider swapping to (trans_date, payment_mode).
EXPLAIN FORMAT=TREE
SELECT payment_mode, COUNT(*)
FROM transaction_detail
WHERE trans_date >= '2025-10-01'
GROUP BY payment_mode;
