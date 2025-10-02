-- Migration 002: YouTube Analytics Enhancement
-- Adds critical columns for YouTube video tracking and data science analysis
-- Created: 2025-10-02

-- ========================================
-- PHASE 1: YouTube Video Tracking
-- ========================================

ALTER TABLE clicks ADD COLUMN IF NOT EXISTS video_id VARCHAR(20);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS video_title VARCHAR(500);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS channel_id VARCHAR(50);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS channel_name VARCHAR(200);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS playlist_id VARCHAR(50);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS video_timestamp INTEGER DEFAULT 0;

-- YouTube-specific behavior parameters
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS yt_feature VARCHAR(50);  -- 'share', 'embed', 'related', 'search'
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS yt_app VARCHAR(20);      -- 'mobile_app', 'web', 'tv_app'
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS yt_list VARCHAR(100);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS yt_index INTEGER;

-- ========================================
-- PHASE 2: Temporal Pattern Analytics
-- ========================================

ALTER TABLE clicks ADD COLUMN IF NOT EXISTS hour_of_day SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS day_of_week SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS is_weekend BOOLEAN DEFAULT false;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS week_of_year SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS month SMALLINT;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS time_since_creation_seconds INTEGER;

-- ========================================
-- PHASE 3: Session & User Journey
-- ========================================

ALTER TABLE clicks ADD COLUMN IF NOT EXISTS session_id UUID;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS is_first_click BOOLEAN DEFAULT true;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS is_returning_visitor BOOLEAN DEFAULT false;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS previous_click_id UUID REFERENCES clicks(id);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS clicks_in_session INTEGER DEFAULT 1;

-- ========================================
-- PHASE 4: Viral & Growth Metrics
-- ========================================

ALTER TABLE clicks ADD COLUMN IF NOT EXISTS clicks_last_hour INTEGER DEFAULT 0;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS clicks_last_24h INTEGER DEFAULT 0;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS viral_coefficient DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS referral_code VARCHAR(8);
ALTER TABLE clicks ADD COLUMN IF NOT EXISTS referral_depth INTEGER DEFAULT 0;

-- ========================================
-- Indexes for YouTube Analytics Performance
-- ========================================

CREATE INDEX IF NOT EXISTS idx_clicks_video_id ON clicks(video_id) WHERE video_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clicks_channel_id ON clicks(channel_id) WHERE channel_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clicks_playlist_id ON clicks(playlist_id) WHERE playlist_id IS NOT NULL;

-- Temporal indexes for time-based queries
CREATE INDEX IF NOT EXISTS idx_clicks_hour_day ON clicks(hour_of_day, day_of_week);
CREATE INDEX IF NOT EXISTS idx_clicks_temporal ON clicks(clicked_at DESC, hour_of_day, day_of_week);

-- Session tracking indexes
CREATE INDEX IF NOT EXISTS idx_clicks_session_id ON clicks(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clicks_returning ON clicks(is_returning_visitor, clicked_at DESC);

-- Viral tracking indexes
CREATE INDEX IF NOT EXISTS idx_clicks_viral_coefficient ON clicks(viral_coefficient DESC) WHERE viral_coefficient > 0;
CREATE INDEX IF NOT EXISTS idx_clicks_referral ON clicks(referral_code) WHERE referral_code IS NOT NULL;

-- ========================================
-- Materialized Views for Performance
-- ========================================

-- Top YouTube Videos Performance
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_youtube_videos AS
SELECT
    video_id,
    MAX(video_title) as video_title,
    MAX(channel_id) as channel_id,
    MAX(channel_name) as channel_name,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT ip_address) as unique_viewers,
    COUNT(DISTINCT session_id) as unique_sessions,
    ROUND(AVG(video_timestamp), 0) as avg_timestamp_clicked,
    mode() WITHIN GROUP (ORDER BY yt_feature) as primary_feature,
    mode() WITHIN GROUP (ORDER BY device_type) as primary_device,
    AVG(viral_coefficient) as avg_viral_score,
    MAX(clicked_at) as last_clicked_at,
    MIN(clicked_at) as first_clicked_at
FROM clicks
WHERE video_id IS NOT NULL
GROUP BY video_id;

-- Hour Heatmap for Optimal Posting Times
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hour_heatmap AS
SELECT
    day_of_week,
    hour_of_day,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT ip_address) as unique_users,
    AVG(viral_coefficient) as avg_virality,
    COUNT(*) FILTER (WHERE is_returning_visitor = true) as returning_clicks,
    COUNT(*) FILTER (WHERE is_first_click = true) as first_time_clicks
FROM clicks
WHERE clicked_at >= NOW() - INTERVAL '90 days'
GROUP BY day_of_week, hour_of_day;

-- Channel Performance Summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_channel_performance AS
SELECT
    channel_id,
    MAX(channel_name) as channel_name,
    COUNT(DISTINCT video_id) as videos_shared,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT ip_address) as unique_viewers,
    AVG(viral_coefficient) as avg_viral_score,
    COUNT(*) FILTER (WHERE yt_feature = 'share') as share_clicks,
    COUNT(*) FILTER (WHERE yt_feature = 'related') as related_clicks,
    COUNT(*) FILTER (WHERE yt_app = 'mobile_app') as mobile_clicks,
    MAX(clicked_at) as last_active_at
FROM clicks
WHERE channel_id IS NOT NULL
GROUP BY channel_id;

-- ========================================
-- Functions for Real-Time Calculations
-- ========================================

-- Function to calculate viral coefficient
CREATE OR REPLACE FUNCTION calculate_viral_coefficient(p_short_code VARCHAR)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_clicks INTEGER;
    hours_since_creation DECIMAL;
    result DECIMAL(5,2);
BEGIN
    SELECT
        COUNT(*),
        EXTRACT(EPOCH FROM (NOW() - MIN(clicked_at))) / 3600
    INTO total_clicks, hours_since_creation
    FROM clicks
    WHERE short_code = p_short_code;

    IF hours_since_creation > 0 THEN
        result := total_clicks / hours_since_creation;
    ELSE
        result := 0.0;
    END IF;

    RETURN ROUND(result, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to update materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_youtube_videos;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hour_heatmap;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_channel_performance;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Scheduled Job to Refresh Views (Optional)
-- ========================================

-- Note: Requires pg_cron extension
-- Run this manually or set up cron job:
-- SELECT cron.schedule('refresh-analytics', '*/15 * * * *', 'SELECT refresh_analytics_views();');

-- ========================================
-- Comments for Documentation
-- ========================================

COMMENT ON COLUMN clicks.video_id IS 'YouTube video ID extracted from URL (e.g., dQw4w9WgXcQ)';
COMMENT ON COLUMN clicks.channel_id IS 'YouTube channel ID for grouping by creator';
COMMENT ON COLUMN clicks.video_timestamp IS 'Video position in seconds when link was clicked';
COMMENT ON COLUMN clicks.yt_feature IS 'YouTube feature used: share, embed, related, search';
COMMENT ON COLUMN clicks.hour_of_day IS 'Hour when click occurred (0-23) for pattern analysis';
COMMENT ON COLUMN clicks.day_of_week IS 'Day of week (0=Monday, 6=Sunday) for temporal patterns';
COMMENT ON COLUMN clicks.session_id IS 'Session identifier for tracking user journey';
COMMENT ON COLUMN clicks.is_returning_visitor IS 'True if user has clicked any link before';
COMMENT ON COLUMN clicks.viral_coefficient IS 'Clicks per hour - indicates viral potential';

COMMENT ON MATERIALIZED VIEW mv_top_youtube_videos IS 'Performance metrics per YouTube video for analytics dashboard';
COMMENT ON MATERIALIZED VIEW mv_hour_heatmap IS 'Click patterns by hour and day for optimal posting recommendations';
COMMENT ON MATERIALIZED VIEW mv_channel_performance IS 'Aggregated metrics per YouTube channel';

-- ========================================
-- Migration Complete
-- ========================================

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Migration 002 completed successfully';
    RAISE NOTICE 'Added % YouTube analytics columns', (
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_name = 'clicks'
        AND column_name IN ('video_id', 'channel_id', 'yt_feature', 'hour_of_day', 'session_id', 'viral_coefficient')
    );
END $$;
