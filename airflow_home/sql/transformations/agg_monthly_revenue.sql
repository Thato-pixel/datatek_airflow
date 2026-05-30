CREATE TABLE IF NOT EXISTS agg_monthly_revenue (
    customer_id TEXT,
    revenue_month DATE,
    monthly_revenue NUMERIC(14,2),
    PRIMARY KEY (customer_id, revenue_month)
);

INSERT INTO agg_monthly_revenue (customer_id, revenue_month, monthly_revenue)
SELECT customer_id, DATE_TRUNC('month', transaction_date)::DATE, SUM(amount)
FROM stg_billing
GROUP BY customer_id, DATE_TRUNC('month', transaction_date)
ON CONFLICT (customer_id, revenue_month) DO UPDATE
    SET monthly_revenue = EXCLUDED.monthly_revenue;
