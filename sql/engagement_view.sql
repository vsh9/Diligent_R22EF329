-- View: customer engagement metrics (avg watch time, completion, sessions)
CREATE VIEW IF NOT EXISTS engagement_view AS
WITH session_stats AS (
    SELECT
        customer_id,
        SUM(duration_watched) AS total_watch_minutes,
        AVG(completion_rate) AS avg_completion_rate,
        COUNT(*) AS sessions
    FROM usage_logs
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.name,
    ROUND(ss.total_watch_minutes / NULLIF(ss.sessions, 0), 2) AS avg_watch_minutes_per_session,
    ROUND(ss.avg_completion_rate, 3) AS avg_completion_rate,
    ss.sessions AS total_sessions
FROM session_stats AS ss
JOIN customers AS c ON c.customer_id = ss.customer_id;

