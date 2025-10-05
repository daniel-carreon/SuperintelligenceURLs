-- ========================================
-- Migration 004: Video Projects Transformation
-- Created: 2025-10-04
-- Purpose: Transform folders into video-centric projects
-- ========================================

-- This migration transforms the folder-based organization into
-- a video-centric structure where each project represents a YouTube video
-- with associated business links for analytics tracking

-- ========================================
-- PHASE 1: Create New Tables
-- ========================================

-- Video Projects Table
-- Represents a YouTube video with cached metadata
CREATE TABLE IF NOT EXISTS video_projects (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- YouTube video information
    youtube_video_id VARCHAR(20), -- e.g., "dQw4w9WgXcQ"
    youtube_url TEXT,              -- Full YouTube URL

    -- Cached metadata (from YouTube Data API or manual entry)
    title VARCHAR(500) NOT NULL,
    thumbnail_url TEXT,
    description TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Future: user ownership
    user_id UUID,

    -- Constraints
    CONSTRAINT video_projects_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

-- Project Links Junction Table
-- Many-to-many relationship between video projects and URLs
CREATE TABLE IF NOT EXISTS project_links (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES video_projects(id) ON DELETE CASCADE,
    url_id UUID NOT NULL REFERENCES urls(id) ON DELETE CASCADE,

    -- Metadata
    added_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Prevent duplicate link assignments
    UNIQUE(project_id, url_id)
);

-- ========================================
-- PHASE 2: Indexes for Performance
-- ========================================

-- Video projects indexes
CREATE INDEX IF NOT EXISTS idx_video_projects_youtube_id
    ON video_projects(youtube_video_id)
    WHERE youtube_video_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_video_projects_created_at
    ON video_projects(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_video_projects_user_id
    ON video_projects(user_id)
    WHERE user_id IS NOT NULL;

-- Project links indexes
CREATE INDEX IF NOT EXISTS idx_project_links_project_id
    ON project_links(project_id);

CREATE INDEX IF NOT EXISTS idx_project_links_url_id
    ON project_links(url_id);

CREATE INDEX IF NOT EXISTS idx_project_links_added_at
    ON project_links(added_at DESC);

-- ========================================
-- PHASE 3: Data Migration
-- Migrate existing folders → video_projects
-- ========================================

-- Migrate folders to video_projects
-- Preserve IDs to maintain referential integrity
INSERT INTO video_projects (
    id,
    title,
    youtube_url,
    youtube_video_id,
    thumbnail_url,
    description,
    created_at,
    updated_at
)
SELECT
    f.id,
    f.name as title,
    NULL as youtube_url,  -- Will be filled when user adds YouTube URL
    NULL as youtube_video_id,
    NULL as thumbnail_url,
    NULL as description,
    f.created_at,
    f.updated_at
FROM folders f
ON CONFLICT (id) DO NOTHING;  -- Skip if already migrated

-- Migrate folder_links to project_links
INSERT INTO project_links (
    project_id,
    url_id,
    added_at
)
SELECT
    fl.folder_id as project_id,
    fl.url_id,
    fl.assigned_at as added_at
FROM folder_links fl
ON CONFLICT (project_id, url_id) DO NOTHING;  -- Skip duplicates

-- ========================================
-- PHASE 4: Materialized View for Analytics
-- ========================================

-- Video Project Performance View
-- Aggregates clicks across all links in a project
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_video_project_performance AS
SELECT
    vp.id as project_id,
    vp.youtube_video_id,
    vp.youtube_url,
    vp.title,
    vp.thumbnail_url,
    vp.created_at,

    -- Link statistics
    COUNT(DISTINCT pl.url_id) as total_links,

    -- Click aggregations
    COALESCE(SUM(u.click_count), 0) as total_clicks,
    COUNT(DISTINCT c.id) as actual_clicks,
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

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX IF NOT EXISTS mv_video_project_performance_unique_idx
    ON mv_video_project_performance(project_id);

-- ========================================
-- PHASE 5: Helper Functions
-- ========================================

-- Function to refresh video project analytics
CREATE OR REPLACE FUNCTION refresh_video_project_analytics()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_video_project_performance;
END;
$$;

-- Function to extract YouTube video ID from URL
CREATE OR REPLACE FUNCTION extract_youtube_video_id(url TEXT)
RETURNS VARCHAR(20)
LANGUAGE plpgsql
AS $$
DECLARE
    video_id VARCHAR(20);
BEGIN
    -- Handle youtube.com/watch?v=VIDEO_ID
    IF url ~ 'youtube\.com/watch\?.*v=' THEN
        video_id := substring(url from 'v=([A-Za-z0-9_-]{11})');
        RETURN video_id;
    END IF;

    -- Handle youtu.be/VIDEO_ID
    IF url ~ 'youtu\.be/' THEN
        video_id := substring(url from 'youtu\.be/([A-Za-z0-9_-]{11})');
        RETURN video_id;
    END IF;

    -- Handle youtube.com/embed/VIDEO_ID
    IF url ~ 'youtube\.com/embed/' THEN
        video_id := substring(url from 'embed/([A-Za-z0-9_-]{11})');
        RETURN video_id;
    END IF;

    -- Handle youtube.com/shorts/VIDEO_ID
    IF url ~ 'youtube\.com/shorts/' THEN
        video_id := substring(url from 'shorts/([A-Za-z0-9_-]{11})');
        RETURN video_id;
    END IF;

    RETURN NULL;
END;
$$;

-- Trigger to auto-update youtube_video_id when youtube_url changes
CREATE OR REPLACE FUNCTION auto_extract_youtube_video_id()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.youtube_url IS NOT NULL AND NEW.youtube_url != OLD.youtube_url THEN
        NEW.youtube_video_id := extract_youtube_video_id(NEW.youtube_url);
    END IF;

    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_auto_extract_youtube_id
    BEFORE UPDATE ON video_projects
    FOR EACH ROW
    EXECUTE FUNCTION auto_extract_youtube_video_id();

-- ========================================
-- PHASE 6: Row Level Security (RLS)
-- ========================================

ALTER TABLE video_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_links ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for MVP, will restrict later with auth)
CREATE POLICY "video_projects_policy" ON video_projects FOR ALL USING (true);
CREATE POLICY "project_links_policy" ON project_links FOR ALL USING (true);

-- ========================================
-- PHASE 7: Comments for Documentation
-- ========================================

COMMENT ON TABLE video_projects IS 'Video-centric projects representing YouTube videos with associated business links';
COMMENT ON COLUMN video_projects.youtube_video_id IS 'YouTube video ID extracted from URL (e.g., dQw4w9WgXcQ)';
COMMENT ON COLUMN video_projects.youtube_url IS 'Full YouTube video URL provided by user';
COMMENT ON COLUMN video_projects.title IS 'Video title - cached from YouTube API or manually entered';
COMMENT ON COLUMN video_projects.thumbnail_url IS 'YouTube video thumbnail URL for display in UI';

COMMENT ON TABLE project_links IS 'Junction table linking video projects to shortened URLs';
COMMENT ON COLUMN project_links.project_id IS 'Reference to video project';
COMMENT ON COLUMN project_links.url_id IS 'Reference to shortened URL';

COMMENT ON MATERIALIZED VIEW mv_video_project_performance IS 'Aggregated analytics per video project for dashboard';

COMMENT ON FUNCTION refresh_video_project_analytics IS 'Refresh video project performance materialized view';
COMMENT ON FUNCTION extract_youtube_video_id IS 'Extract YouTube video ID from various URL formats';

-- ========================================
-- SUCCESS MESSAGE
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 004 completed successfully!';
    RAISE NOTICE '📊 Created video_projects table';
    RAISE NOTICE '📊 Created project_links junction table';
    RAISE NOTICE '📊 Migrated % folders to video_projects', (SELECT COUNT(*) FROM video_projects);
    RAISE NOTICE '📊 Migrated % folder_links to project_links', (SELECT COUNT(*) FROM project_links);
    RAISE NOTICE '📈 Created mv_video_project_performance materialized view';
    RAISE NOTICE '🔧 Added helper functions for YouTube ID extraction';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT: Old folders and folder_links tables preserved for rollback';
    RAISE NOTICE '⚠️  Run refresh_video_project_analytics() to update analytics';
END $$;
