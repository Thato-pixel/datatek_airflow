CREATE TABLE IF NOT EXISTS stg_billing (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT,
    amount NUMERIC(12,2),
    transaction_date TIMESTAMP
);

INSERT INTO stg_billing (transaction_id, customer_id, amount, transaction_date)
SELECT DISTINCT ON (transaction_id)
    transaction_id,
    customer_id,
    COALESCE(amount, 0) AS amount,
    CAST(transaction_date AS TIMESTAMP) AS transaction_date
FROM src_billing_transactions
WHERE transaction_id IS NOT NULL
  AND customer_id IS NOT NULL
ORDER BY transaction_id, CAST(transaction_date AS TIMESTAMP) DESC
ON CONFLICT (transaction_id) DO UPDATE
    SET amount = EXCLUDED.amount,
        transaction_date = EXCLUDED.transaction_date;
