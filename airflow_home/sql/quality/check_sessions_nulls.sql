INSERT INTO quarantine_records (source, raw_record, detected_at)
SELECT 'src_network_sessions', row_to_json(s)::jsonb, NOW()
FROM src_network_sessions s
WHERE s.session_id IS NULL OR s.customer_id IS NULL;
