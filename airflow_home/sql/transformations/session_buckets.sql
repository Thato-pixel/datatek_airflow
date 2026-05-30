CREATE TABLE IF NOT EXISTS session_buckets (
    session_id TEXT PRIMARY KEY,
    customer_id TEXT,
    bucket TEXT
);

INSERT INTO session_buckets (session_id, customer_id, bucket)
SELECT session_id, customer_id,
    CASE WHEN session_duration_sec < 60 THEN 'short'
         WHEN session_duration_sec < 300 THEN 'medium'
         ELSE 'long' END
FROM stg_sessions
ON CONFLICT (session_id) DO UPDATE
    SET bucket = EXCLUDED.bucket;
