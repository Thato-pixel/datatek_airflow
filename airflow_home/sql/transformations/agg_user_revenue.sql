CREATE TABLE IF NOT EXISTS agg_user_revenue (
    customer_id TEXT PRIMARY KEY,
    total_revenue NUMERIC(14,2),
    total_transactions INT
);

INSERT INTO agg_user_revenue (customer_id, total_revenue, total_transactions)
SELECT customer_id, SUM(amount), COUNT(*)
FROM stg_billing
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE
    SET total_revenue = EXCLUDED.total_revenue,
        total_transactions = EXCLUDED.total_transactions;
