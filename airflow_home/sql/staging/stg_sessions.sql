CREATE TABLE IF NOT EXISTS stg_sessions (
    session_id TEXT PRIMARY KEY,
    customer_id TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    data_used_mb NUMERIC(12,4),
    session_date DATE,
    session_duration_sec INT
);

INSERT INTO stg_sessions (session_id, customer_id, start_time, end_time, data_used_mb, session_date, session_duration_sec)
SELECT DISTINCT ON (session_id)
    session_id, customer_id,
    CAST(start_time AS TIMESTAMP),
    CAST(end_time AS TIMESTAMP),
    COALESCE(data_used_mb, 0),
    CAST(session_date AS DATE),
    CASE WHEN CAST(end_time AS TIMESTAMP) > CAST(start_time AS TIMESTAMP)
        THEN EXTRACT(EPOCH FROM (CAST(end_time AS TIMESTAMP) - CAST(start_time AS TIMESTAMP)))::INT
        ELSE 0 END
FROM src_network_sessions
WHERE session_id IS NOT NULL AND customer_id IS NOT NULL
ORDER BY session_id, CAST(start_time AS TIMESTAMP) DESC
ON CONFLICT (session_id) DO UPDATE
    SET end_time = EXCLUDED.end_time,
        data_used_mb = EXCLUDED.data_used_mb,
        session_duration_sec = EXCLUDED.session_duration_sec;
