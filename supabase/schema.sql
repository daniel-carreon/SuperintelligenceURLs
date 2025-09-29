-- LinkProxy Database Schema
-- Optimizado para analytics en tiempo real y performance

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- URLs table: Core shortening functionality
CREATE TABLE urls (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    short_code VARCHAR(8) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    title VARCHAR(500),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true NOT NULL,

    -- Performance tracking
    click_count INTEGER DEFAULT 0 NOT NULL,
    last_clicked_at TIMESTAMPTZ,

    -- User tracking (for future auth)
    user_id UUID,

    -- Analytics optimization
    domain VARCHAR(255),

    -- Indexes for performance
    CONSTRAINT valid_url CHECK (original_url ~ '^https?://'),
    CONSTRAINT valid_short_code CHECK (short_code ~ '^[A-Za-z0-9]{4,8}$')
);

-- Clicks table: Real-time analytics data
CREATE TABLE clicks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    url_id UUID REFERENCES urls(id) ON DELETE CASCADE NOT NULL,
    short_code VARCHAR(8) NOT NULL, -- Denormalized for query performance

    -- Request metadata
    ip_address INET,
    user_agent TEXT,
    referer TEXT,

    -- Parsed analytics data
    country_code VARCHAR(2),
    country_name VARCHAR(100),
    city VARCHAR(100),

    -- Device detection
    device_type VARCHAR(20), -- 'mobile', 'tablet', 'desktop', 'bot', 'unknown'
    browser_name VARCHAR(50),
    browser_version VARCHAR(20),
    os_name VARCHAR(50),
    os_version VARCHAR(20),

    -- Traffic source analysis
    referrer_domain VARCHAR(255),
    referrer_type VARCHAR(20), -- 'social', 'search', 'direct', 'email', 'other'

    -- UTM parameters
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    utm_term VARCHAR(100),
    utm_content VARCHAR(100),

    -- Timing
    clicked_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Performance tracking
    response_time_ms INTEGER
);

-- Indexes for high-performance analytics queries
-- URLs table indexes
CREATE INDEX idx_urls_short_code ON urls(short_code) WHERE is_active = true;
CREATE INDEX idx_urls_created_at ON urls(created_at DESC);
CREATE INDEX idx_urls_click_count ON urls(click_count DESC);
CREATE INDEX idx_urls_domain ON urls(domain);

-- Clicks table indexes (optimized for analytics aggregations)
CREATE INDEX idx_clicks_url_id ON clicks(url_id);
CREATE INDEX idx_clicks_short_code ON clicks(short_code);
CREATE INDEX idx_clicks_clicked_at ON clicks(clicked_at DESC);
CREATE INDEX idx_clicks_country_code ON clicks(country_code);
CREATE INDEX idx_clicks_device_type ON clicks(device_type);
CREATE INDEX idx_clicks_referrer_domain ON clicks(referrer_domain);
CREATE INDEX idx_clicks_referrer_type ON clicks(referrer_type);

-- Composite indexes for common analytics queries
CREATE INDEX idx_clicks_analytics ON clicks(short_code, clicked_at DESC, country_code, device_type);
CREATE INDEX idx_clicks_time_series ON clicks(clicked_at DESC, url_id);

-- Functions for real-time analytics

-- Function to increment click count atomically
CREATE OR REPLACE FUNCTION increment_click_count(p_url_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE urls
    SET click_count = click_count + 1,
        last_clicked_at = NOW()
    WHERE id = p_url_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get analytics summary
CREATE OR REPLACE FUNCTION get_analytics_summary(p_short_code VARCHAR)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_clicks', COUNT(*),
        'unique_ips', COUNT(DISTINCT ip_address),
        'countries', COUNT(DISTINCT country_code),
        'devices', json_build_object(
            'mobile', COUNT(*) FILTER (WHERE device_type = 'mobile'),
            'desktop', COUNT(*) FILTER (WHERE device_type = 'desktop'),
            'tablet', COUNT(*) FILTER (WHERE device_type = 'tablet'),
            'unknown', COUNT(*) FILTER (WHERE device_type = 'unknown')
        ),
        'top_countries', (
            SELECT json_agg(json_build_object('country', country_name, 'count', count))
            FROM (
                SELECT country_name, COUNT(*) as count
                FROM clicks
                WHERE short_code = p_short_code AND country_name IS NOT NULL
                GROUP BY country_name
                ORDER BY count DESC
                LIMIT 5
            ) t
        ),
        'referrer_types', (
            SELECT json_build_object(
                'social', COUNT(*) FILTER (WHERE referrer_type = 'social'),
                'search', COUNT(*) FILTER (WHERE referrer_type = 'search'),
                'direct', COUNT(*) FILTER (WHERE referrer_type = 'direct'),
                'email', COUNT(*) FILTER (WHERE referrer_type = 'email'),
                'other', COUNT(*) FILTER (WHERE referrer_type = 'other')
            )
            FROM clicks WHERE short_code = p_short_code
        ),
        'clicks_over_time', (
            SELECT json_agg(json_build_object('date', date, 'clicks', clicks))
            FROM (
                SELECT DATE(clicked_at) as date, COUNT(*) as clicks
                FROM clicks
                WHERE short_code = p_short_code
                AND clicked_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(clicked_at)
                ORDER BY date
            ) t
        )
    ) INTO result
    FROM clicks
    WHERE short_code = p_short_code;

    RETURN COALESCE(result, '{}'::json);
END;
$$ LANGUAGE plpgsql;

-- Real-time notifications for dashboard updates
CREATE OR REPLACE FUNCTION notify_click_event()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('click_event', json_build_object(
        'short_code', NEW.short_code,
        'country', NEW.country_name,
        'device', NEW.device_type,
        'timestamp', NEW.clicked_at
    )::text);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for real-time notifications
CREATE TRIGGER trigger_click_notification
    AFTER INSERT ON clicks
    FOR EACH ROW
    EXECUTE FUNCTION notify_click_event();

-- Row Level Security (RLS) - Ready for future auth
ALTER TABLE urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE clicks ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for MVP, will restrict later)
CREATE POLICY "urls_policy" ON urls FOR ALL USING (true);
CREATE POLICY "clicks_policy" ON clicks FOR ALL USING (true);

-- Views for common analytics queries
CREATE VIEW analytics_summary AS
SELECT
    u.short_code,
    u.original_url,
    u.title,
    u.created_at,
    u.click_count,
    u.last_clicked_at,
    COUNT(c.id) as actual_clicks,
    COUNT(DISTINCT c.ip_address) as unique_visitors,
    COUNT(DISTINCT c.country_code) as countries_reached
FROM urls u
LEFT JOIN clicks c ON u.id = c.url_id
WHERE u.is_active = true
GROUP BY u.id, u.short_code, u.original_url, u.title, u.created_at, u.click_count, u.last_clicked_at;

-- Device analytics view
CREATE VIEW device_analytics AS
SELECT
    short_code,
    device_type,
    COUNT(*) as clicks,
    COUNT(DISTINCT ip_address) as unique_users,
    ROUND(COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER (PARTITION BY short_code) * 100, 2) as percentage
FROM clicks
GROUP BY short_code, device_type;

-- Geographic analytics view
CREATE VIEW geographic_analytics AS
SELECT
    short_code,
    country_name,
    country_code,
    city,
    COUNT(*) as clicks,
    COUNT(DISTINCT ip_address) as unique_users,
    ROUND(COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER (PARTITION BY short_code) * 100, 2) as percentage
FROM clicks
WHERE country_name IS NOT NULL
GROUP BY short_code, country_name, country_code, city;

-- Traffic source analytics view
CREATE VIEW traffic_source_analytics AS
SELECT
    short_code,
    referrer_type,
    referrer_domain,
    COUNT(*) as clicks,
    COUNT(DISTINCT ip_address) as unique_users,
    ROUND(COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER (PARTITION BY short_code) * 100, 2) as percentage
FROM clicks
GROUP BY short_code, referrer_type, referrer_domain;