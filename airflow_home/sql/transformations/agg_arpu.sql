CREATE TABLE IF NOT EXISTS agg_arpu (
    customer_id TEXT PRIMARY KEY,
    arpu NUMERIC(14,2)
);

INSERT INTO agg_arpu (customer_id, arpu)
SELECT customer_id,
    COALESCE(SUM(monthly_revenue) / NULLIF(COUNT(DISTINCT revenue_month), 0), 0)
FROM agg_monthly_revenue
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE
    SET arpu = EXCLUDED.arpu;
