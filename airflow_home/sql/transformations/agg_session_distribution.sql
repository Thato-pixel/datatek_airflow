CREATE TABLE IF NOT EXISTS agg_session_distribution (
    customer_id TEXT PRIMARY KEY,
    short_sessions INT,
    medium_sessions INT,
    long_sessions INT
);

INSERT INTO agg_session_distribution (customer_id, short_sessions, medium_sessions, long_sessions)
SELECT customer_id,
    COUNT(*) FILTER (WHERE bucket = 'short'),
    COUNT(*) FILTER (WHERE bucket = 'medium'),
    COUNT(*) FILTER (WHERE bucket = 'long')
FROM session_buckets
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE
    SET short_sessions = EXCLUDED.short_sessions,
        medium_sessions = EXCLUDED.medium_sessions,
        long_sessions = EXCLUDED.long_sessions;
