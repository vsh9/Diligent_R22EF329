-- View: top content performance with total hours, unique viewers, avg completion
CREATE VIEW IF NOT EXISTS top_content_view AS
SELECT
    c.content_id,
    c.title,
    c.genre,
    ROUND(SUM(ul.duration_watched) / 60.0, 2) AS total_watch_hours,
    COUNT(DISTINCT ul.customer_id) AS unique_viewers,
    ROUND(AVG(ul.completion_rate), 3) AS avg_completion_rate
FROM usage_logs AS ul
JOIN content AS c ON c.content_id = ul.content_id
GROUP BY
    c.content_id,
    c.title,
    c.genre
ORDER BY
    total_watch_hours DESC,
    unique_viewers DESC;

