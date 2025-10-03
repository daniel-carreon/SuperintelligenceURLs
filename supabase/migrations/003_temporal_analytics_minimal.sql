-- ========================================
-- Migration 003: Temporal Analytics (Minimal)
-- Purpose: Track WHEN users click to optimize video posting times
-- Created: 2025-10-02
-- ========================================

-- Temporal Pattern Columns (for "Best Time to Post" analytics)
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS hour_of_day SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS day_of_week SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS is_weekend BOOLEAN DEFAULT false;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS month SMALLINT;

-- Session Journey Columns (for user behavior analysis)
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS is_first_click BOOLEAN DEFAULT true;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS clicks_in_session INTEGER DEFAULT 1;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS time_since_creation_seconds INTEGER;

-- Add comments for clarity
COMMENT ON COLUMN clicks.hour_of_day IS 'Hour of day when clicked (0-23) for temporal analysis';
COMMENT ON COLUMN clicks.day_of_week IS 'Day of week when clicked (0=Monday, 6=Sunday)';
COMMENT ON COLUMN clicks.is_weekend IS 'True if clicked on Saturday or Sunday';
COMMENT ON COLUMN clicks.month IS 'Month when clicked (1-12)';
COMMENT ON COLUMN clicks.is_first_click IS 'True if this is the first click in the session';
COMMENT ON COLUMN clicks.clicks_in_session IS 'Number of clicks within the same session';
COMMENT ON COLUMN clicks.time_since_creation_seconds IS 'Seconds between URL creation and click (for viral tracking)';

-- Performance Indexes (focused on temporal queries)
CREATE INDEX IF NOT EXISTS idx_clicks_temporal_pattern
ON clicks(day_of_week, hour_of_day)
WHERE clicked_at > NOW() - INTERVAL '90 days';

CREATE INDEX IF NOT EXISTS idx_clicks_hour_of_day
ON clicks(hour_of_day)
WHERE hour_of_day IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_clicks_video_tracking
ON clicks(video_platform, video_id)
WHERE video_id IS NOT NULL;

-- ========================================
-- Materialized View: Hour Heatmap
-- Purpose: See best times to post videos
-- ========================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hour_heatmap AS
SELECT
    day_of_week,
    hour_of_day,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_visitors,
    COUNT(*) FILTER (WHERE is_first_click = true) as new_visitors,
    COUNT(*) FILTER (WHERE is_returning_visitor = true) as returning_visitors,
    -- Day name for readability
    CASE day_of_week
        WHEN 0 THEN 'Monday'
        WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'
        WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END as day_name
FROM clicks
WHERE hour_of_day IS NOT NULL
  AND day_of_week IS NOT NULL
  AND clicked_at > NOW() - INTERVAL '90 days'  -- Last 90 days only
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX IF NOT EXISTS mv_hour_heatmap_unique_idx
ON mv_hour_heatmap(day_of_week, hour_of_day);

-- ========================================
-- Materialized View: Video Sources
-- Purpose: See which YouTube videos drive most traffic
-- ========================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_video_sources AS
SELECT
    video_platform,
    video_id,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_viewers,
    COUNT(DISTINCT ip_address) as unique_ips,
    COUNT(*) FILTER (WHERE is_first_click = true) as new_visitor_clicks,
    COUNT(*) FILTER (WHERE is_returning_visitor = true) as returning_visitor_clicks,
    MAX(clicked_at) as last_clicked_at,
    MIN(clicked_at) as first_clicked_at
FROM clicks
WHERE video_id IS NOT NULL
  AND video_platform IS NOT NULL
  AND clicked_at > NOW() - INTERVAL '90 days'
GROUP BY video_platform, video_id
ORDER BY total_clicks DESC;

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX IF NOT EXISTS mv_video_sources_unique_idx
ON mv_video_sources(video_platform, video_id);

-- ========================================
-- Function: Refresh Materialized Views
-- Purpose: Call this to update analytics data
-- ========================================
CREATE OR REPLACE FUNCTION refresh_temporal_analytics()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hour_heatmap;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_video_sources;
END;
$$;

COMMENT ON FUNCTION refresh_temporal_analytics IS 'Refresh temporal analytics materialized views';

-- ========================================
-- Success Message
-- ========================================
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully!';
    RAISE NOTICE '📊 Added temporal analytics columns: hour_of_day, day_of_week, is_weekend, month';
    RAISE NOTICE '📊 Added session tracking columns: is_first_click, clicks_in_session';
    RAISE NOTICE '📈 Created materialized views: mv_hour_heatmap, mv_video_sources';
    RAISE NOTICE '🔧 To refresh analytics: SELECT refresh_temporal_analytics();';
END $$;
