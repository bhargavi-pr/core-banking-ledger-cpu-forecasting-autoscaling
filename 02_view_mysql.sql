-- Step 1 (Data Layer): joins Customers -> Accounts -> Transactions and counts load per minute.
USE bank_db;

CREATE OR REPLACE VIEW v_live_bank_telemetry AS
SELECT
    DATE_FORMAT(t.live_ts, '%Y-%m-%d %H:%i:00') AS minute_ts,
    COUNT(*)                                     AS txn_count,
    ROUND(SUM(t.amount_usd), 2)                  AS total_amount_usd,
    COUNT(DISTINCT a.account_id)                 AS active_accounts,
    COUNT(DISTINCT c.customer_id)                AS active_customers
FROM transactions t
JOIN accounts  a ON a.account_id  = t.account_id
JOIN customers c ON c.customer_id = a.customer_id
GROUP BY DATE_FORMAT(t.live_ts, '%Y-%m-%d %H:%i:00');
