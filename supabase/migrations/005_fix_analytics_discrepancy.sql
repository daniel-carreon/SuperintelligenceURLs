-- ========================================
-- Migration 005: Fix Analytics Discrepancy
-- Created: 2025-10-10
-- Purpose: Fix total_clicks to count only current project links
-- ========================================

-- Drop existing materialized view
DROP MATERIALIZED VIEW IF EXISTS mv_video_project_performance CASCADE;

-- Recreate with correct total_clicks calculation
CREATE MATERIALIZED VIEW mv_video_project_performance AS
SELECT
    vp.id as project_id,
    vp.youtube_video_id,
    vp.youtube_url,
    vp.title,
    vp.thumbnail_url,
    vp.created_at,

    -- Link statistics
    COUNT(DISTINCT pl.url_id) as total_links,

    -- Click aggregations (FIXED: count only clicks from current project links)
    COUNT(DISTINCT c.id) as total_clicks,  -- Fixed: was SUM(u.click_count)
    COUNT(DISTINCT c.ip_address) as unique_visitors,
    COUNT(DISTINCT c.country_code) as countries_reached,

    -- Device breakdown aggregated
    COUNT(*) FILTER (WHERE c.device_type = 'mobile') as mobile_clicks,
    COUNT(*) FILTER (WHERE c.device_type = 'desktop') as desktop_clicks,
    COUNT(*) FILTER (WHERE c.device_type = 'tablet') as tablet_clicks,

    -- Time tracking
    MAX(c.clicked_at) as last_click_at,
    MIN(c.clicked_at) as first_click_at

FROM video_projects vp
LEFT JOIN project_links pl ON vp.id = pl.project_id
LEFT JOIN urls u ON pl.url_id = u.id
LEFT JOIN clicks c ON u.id = c.url_id
GROUP BY vp.id, vp.youtube_video_id, vp.youtube_url, vp.title, vp.thumbnail_url, vp.created_at;

-- Recreate unique index for concurrent refresh
CREATE UNIQUE INDEX mv_video_project_performance_unique_idx
    ON mv_video_project_performance(project_id);

-- Refresh the view with correct data
REFRESH MATERIALIZED VIEW mv_video_project_performance;

-- ========================================
-- Explanation of the fix:
-- ========================================
-- BEFORE: total_clicks = SUM(u.click_count)
--   This summed ALL historical clicks from urls table,
--   including clicks from links no longer in the project
--
-- AFTER: total_clicks = COUNT(DISTINCT c.id)
--   This counts only clicks from links CURRENTLY assigned
--   to the project via project_links join
-- ========================================
