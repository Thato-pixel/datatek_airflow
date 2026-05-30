INSERT INTO quarantine_records (source, raw_record, detected_at)
SELECT 'src_billing_transactions', row_to_json(b)::jsonb, NOW()
FROM src_billing_transactions b
WHERE b.transaction_id IN (
    SELECT transaction_id FROM src_billing_transactions
    GROUP BY transaction_id HAVING COUNT(*) > 1
);
