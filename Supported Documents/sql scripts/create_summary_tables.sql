-- ======================================================================
-- CREATE SUMMARY TABLES FOR 240M SCALE
-- Pre-aggregate data for fast dashboard queries
-- ======================================================================

USE sabpaisa2;

-- ======================================================================
-- 1. DAILY MERCHANT SUMMARY
-- ======================================================================
CREATE TABLE IF NOT EXISTS daily_merchant_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    client_code VARCHAR(50) NOT NULL,
    client_name VARCHAR(255),
    total_transactions INT DEFAULT 0,
    successful_transactions INT DEFAULT 0,
    failed_transactions INT DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    success_amount DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_date_client (summary_date, client_code),
    INDEX idx_date (summary_date),
    INDEX idx_client (client_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================================================
-- 2. DAILY PAYMENT MODE SUMMARY
-- ======================================================================
CREATE TABLE IF NOT EXISTS daily_payment_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    payment_mode VARCHAR(50) NOT NULL,
    total_transactions INT DEFAULT 0,
    successful_transactions INT DEFAULT 0,
    failed_transactions INT DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    success_amount DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_date_payment (summary_date, payment_mode),
    INDEX idx_date (summary_date),
    INDEX idx_payment (payment_mode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================================================
-- 3. DAILY TREND SUMMARY
-- ======================================================================
CREATE TABLE IF NOT EXISTS daily_trend_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    total_transactions INT DEFAULT 0,
    successful_transactions INT DEFAULT 0,
    failed_transactions INT DEFAULT 0,
    pending_transactions INT DEFAULT 0,
    total_volume DECIMAL(15,2) DEFAULT 0,
    success_volume DECIMAL(15,2) DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_date (summary_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================================================
-- 4. HOURLY SUMMARY (for real-time today's data)
-- ======================================================================
CREATE TABLE IF NOT EXISTS hourly_transaction_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    summary_datetime DATETIME NOT NULL,
    total_transactions INT DEFAULT 0,
    successful_transactions INT DEFAULT 0,
    failed_transactions INT DEFAULT 0,
    total_volume DECIMAL(15,2) DEFAULT 0,
    success_volume DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_datetime (summary_datetime),
    INDEX idx_date (DATE(summary_datetime))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================================================
-- 5. POPULATE HISTORICAL DATA (One-time - Run after table creation)
-- ======================================================================

-- Populate daily merchant summary
INSERT INTO daily_merchant_summary
    (summary_date, client_code, client_name,
     total_transactions, successful_transactions, failed_transactions,
     total_amount, success_amount)
SELECT
    DATE(trans_date) as summary_date,
    client_code,
    MAX(client_name) as client_name,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_transactions,
    SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END) as failed_transactions,
    SUM(paid_amount) as total_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN paid_amount ELSE 0 END) as success_amount
FROM transaction_detail
WHERE trans_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)  -- Last 2 years
GROUP BY DATE(trans_date), client_code
ON DUPLICATE KEY UPDATE
    total_transactions = VALUES(total_transactions),
    successful_transactions = VALUES(successful_transactions),
    failed_transactions = VALUES(failed_transactions),
    total_amount = VALUES(total_amount),
    success_amount = VALUES(success_amount);

-- Populate daily payment summary
INSERT INTO daily_payment_summary
    (summary_date, payment_mode,
     total_transactions, successful_transactions, failed_transactions,
     success_rate, total_amount, success_amount)
SELECT
    DATE(trans_date) as summary_date,
    payment_mode,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_transactions,
    SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END) as failed_transactions,
    ROUND((SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate,
    SUM(paid_amount) as total_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN paid_amount ELSE 0 END) as success_amount
FROM transaction_detail
WHERE trans_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)  -- Last 2 years
GROUP BY DATE(trans_date), payment_mode
ON DUPLICATE KEY UPDATE
    total_transactions = VALUES(total_transactions),
    successful_transactions = VALUES(successful_transactions),
    failed_transactions = VALUES(failed_transactions),
    success_rate = VALUES(success_rate),
    total_amount = VALUES(total_amount),
    success_amount = VALUES(success_amount);

-- Populate daily trend summary
INSERT INTO daily_trend_summary
    (summary_date,
     total_transactions, successful_transactions, failed_transactions, pending_transactions,
     total_volume, success_volume, success_rate)
SELECT
    DATE(trans_date) as summary_date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_transactions,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_transactions,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_transactions,
    SUM(paid_amount) as total_volume,
    SUM(CASE WHEN status = 'SUCCESS' THEN paid_amount ELSE 0 END) as success_volume,
    ROUND((SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
FROM transaction_detail
WHERE trans_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)  -- Last 2 years
GROUP BY DATE(trans_date)
ON DUPLICATE KEY UPDATE
    total_transactions = VALUES(total_transactions),
    successful_transactions = VALUES(successful_transactions),
    failed_transactions = VALUES(failed_transactions),
    pending_transactions = VALUES(pending_transactions),
    total_volume = VALUES(total_volume),
    success_volume = VALUES(success_volume),
    success_rate = VALUES(success_rate);

-- ======================================================================
-- 6. VERIFY DATA POPULATED
-- ======================================================================
SELECT
    'daily_merchant_summary' as table_name,
    COUNT(*) as row_count,
    MIN(summary_date) as oldest_date,
    MAX(summary_date) as latest_date
FROM daily_merchant_summary
UNION ALL
SELECT
    'daily_payment_summary' as table_name,
    COUNT(*) as row_count,
    MIN(summary_date) as oldest_date,
    MAX(summary_date) as latest_date
FROM daily_payment_summary
UNION ALL
SELECT
    'daily_trend_summary' as table_name,
    COUNT(*) as row_count,
    MIN(summary_date) as oldest_date,
    MAX(summary_date) as latest_date
FROM daily_trend_summary;

-- ======================================================================
-- SUCCESS MESSAGE
-- ======================================================================
SELECT '✓ Summary tables created and populated!' AS Status,
       'Now update Python code to use summary tables' AS Next_Step;
