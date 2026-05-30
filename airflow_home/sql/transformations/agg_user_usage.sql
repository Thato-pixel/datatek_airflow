CREATE TABLE IF NOT EXISTS agg_user_usage (
    customer_id TEXT PRIMARY KEY,
    total_data_used_mb NUMERIC(16,4),
    avg_session_duration_sec NUMERIC(10,2),
    total_sessions INT
);

INSERT INTO agg_user_usage (customer_id, total_data_used_mb, avg_session_duration_sec, total_sessions)
SELECT customer_id, SUM(data_used_mb), AVG(session_duration_sec), COUNT(*)
FROM stg_sessions
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE
    SET total_data_used_mb = EXCLUDED.total_data_used_mb,
        avg_session_duration_sec = EXCLUDED.avg_session_duration_sec,
        total_sessions = EXCLUDED.total_sessions;
