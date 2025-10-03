# 📊 Data Science Analysis - YouTube Analytics Enhancement

**Fecha:** 2 de Octubre, 2025
**Objetivo:** Maximizar valor de datos para análisis de usuarios de YouTube
**Enfoque:** Predictive analytics + User behavior patterns

---

## 🔍 Current Schema Analysis

### ✅ What We HAVE (Excellent Foundation)

**URLs Table:**
- short_code, original_url, title
- created_at, expires_at, is_active
- click_count, last_clicked_at
- domain tracking

**Clicks Table:**
```sql
-- Geographic & Device Data
✅ ip_address, country_code, country_name, city
✅ device_type, browser_name, browser_version
✅ os_name, os_version

-- Traffic Source Data
✅ referer, referrer_domain, referrer_type
✅ utm_source, utm_medium, utm_campaign, utm_term, utm_content

-- Performance Data
✅ clicked_at, response_time_ms
```

---

## ❌ Critical GAPS for YouTube Analytics

### 1. **Video-Specific Tracking** (HIGH PRIORITY)

**Missing Columns:**
```sql
-- YouTube Video Identification
video_id VARCHAR(20)           -- ej: "dQw4w9WgXcQ"
video_title VARCHAR(500)       -- Parsed from URL or API
channel_id VARCHAR(50)         -- ej: "UCuAXFkgsw1L7xaCfnd5JJOw"
channel_name VARCHAR(200)      -- Para agrupar por channel
playlist_id VARCHAR(50)        -- Si viene de playlist
video_timestamp INTEGER        -- Segundo del video (ej: ?t=120)
```

**Business Value:**
- Saber QUÉ videos generan más clicks
- Identificar qué canales son más efectivos
- Ver en qué momento del video clickean (engagement point)

**Predictive Value:**
- Entrenar modelo: "Video features → Click probability"
- Predecir: "Este tipo de video generará X clicks"

---

### 2. **YouTube-Specific Parameters** (MEDIUM PRIORITY)

**Missing Columns:**
```sql
-- YouTube App Behavior
yt_feature VARCHAR(50)         -- "share", "embed", "related", "search"
yt_app VARCHAR(20)             -- "mobile_app", "web", "tv_app"
yt_list VARCHAR(100)           -- Playlist tracking
yt_index INTEGER               -- Position in playlist
```

**Business Value:**
- ¿Los usuarios vienen de videos relacionados?
- ¿O de shares directos?
- ¿Desde app mobile o web?

**Example URL Parsing:**
```
https://www.youtube.com/watch?v=ABC123&feature=share
                               ^video_id  ^yt_feature

https://www.youtube.com/watch?v=ABC123&list=PLxxx&index=3
                                        ^playlist ^position
```

---

### 3. **Session & User Journey Tracking** (HIGH PRIORITY)

**Missing Columns:**
```sql
-- Session Tracking
session_id UUID                     -- Para agrupar clicks de misma sesión
is_first_click BOOLEAN DEFAULT true -- ¿Primera vez este user clickea?
is_returning_visitor BOOLEAN        -- ¿Ya había clickeado antes?
previous_click_id UUID              -- Referencia al click anterior
clicks_in_session INTEGER DEFAULT 1 -- Cuántos clicks en esta sesión

-- Conversion Funnel Stage
funnel_stage VARCHAR(20)            -- 'awareness', 'interest', 'decision', 'action'
conversion_event VARCHAR(50)        -- Qué acción tomó después del click
```

**Business Value:**
- Identificar user journey completo
- Calcular conversion rate
- Optimizar funnel drop-off points

**Predictive Value:**
- Modelo: "Session features → Conversion probability"
- Churn prediction: "¿Este usuario volverá?"

---

### 4. **Time-Based Pattern Analytics** (MEDIUM PRIORITY)

**Missing Columns:**
```sql
-- Temporal Features
hour_of_day SMALLINT              -- 0-23 (para detectar peak hours)
day_of_week SMALLINT              -- 0-6 (lunes=0)
is_weekend BOOLEAN                -- Weekend vs weekday behavior
time_since_creation_seconds INT   -- Cuánto tardó en recibir 1er click

-- Click Velocity
clicks_last_hour INTEGER DEFAULT 0
clicks_last_24h INTEGER DEFAULT 0
viral_score DECIMAL(5,2)          -- Clicks per hour since creation
```

**Business Value:**
- ¿Cuándo es el mejor momento para compartir?
- ¿Qué días tienen mejor engagement?
- Detectar contenido "viral" temprano

**Predictive Value:**
- Time series forecasting: "Predecir clicks próximas 24h"
- Optimal posting time recommendation

---

### 5. **Engagement & Retention Metrics** (LOW PRIORITY - Future)

**Missing Columns:**
```sql
-- Engagement Depth
dwell_time_seconds INTEGER        -- Tiempo en página destino (requiere JS tracking)
bounce_rate_indicator BOOLEAN     -- ¿Se fue rápido? (<5 sec)
scroll_depth_percent SMALLINT     -- % de scroll en página (0-100)

-- Social Proof
shares_count INTEGER DEFAULT 0    -- Cuántas veces se compartió este link
comments_count INTEGER DEFAULT 0  -- Si tiene comments en video original
likes_count INTEGER DEFAULT 0     -- Likes del video (from YouTube API)
```

**Business Value:**
- Medir engagement real (no solo clicks)
- Identificar contenido que realmente engancha

**Requires:**
- JavaScript tracking pixel
- YouTube Data API integration

---

### 6. **Referral Chain & Viral Coefficient** (MEDIUM PRIORITY)

**Missing Columns:**
```sql
-- Viral Tracking
referral_code VARCHAR(8)           -- ¿Fue referido por otro short link?
referral_depth INTEGER DEFAULT 0   -- Nivel en la cadena de referidos
viral_coefficient DECIMAL(5,2)     -- Avg clicks generados por cada click
attribution_source VARCHAR(100)    -- First touch attribution

-- Click Source Chain
click_source_chain TEXT[]          -- Array: ['youtube', 'twitter', 'whatsapp']
influence_score DECIMAL(5,2)       -- Cuánta viralidad generó este click
```

**Business Value:**
- Entender cadenas de viralidad
- Identificar influencers naturales
- Optimizar estrategia de distribución

**Predictive Value:**
- Network analysis: "Qué nodes generan más viralidad"
- Viral coefficient optimization

---

## 🎯 Recommended Implementation Priority

### Phase 1: YouTube Essentials (Week 1) ⭐⭐⭐
```sql
ALTER TABLE clicks ADD COLUMN:
- video_id VARCHAR(20)
- channel_id VARCHAR(50)
- video_timestamp INTEGER
- yt_feature VARCHAR(50)
- hour_of_day SMALLINT
- day_of_week SMALLINT
```

**Why First:**
- Immediate value for YouTube analytics
- Easy to parse from referrer URL
- No external API dependencies

### Phase 2: Session & Journey (Week 2) ⭐⭐
```sql
ALTER TABLE clicks ADD COLUMN:
- session_id UUID
- is_first_click BOOLEAN
- is_returning_visitor BOOLEAN
- time_since_creation_seconds INTEGER
- clicks_last_hour INTEGER
```

**Why Second:**
- Requires cookie/session tracking
- Medium complexity
- High predictive value

### Phase 3: Viral & Referral (Week 3) ⭐
```sql
ALTER TABLE clicks ADD COLUMN:
- referral_code VARCHAR(8)
- referral_depth INTEGER
- click_source_chain TEXT[]
- viral_coefficient DECIMAL(5,2)
```

**Why Third:**
- Requires building referral system
- Complex calculation logic
- Great for growth hacking

### Phase 4: Engagement (Future) ⭐ (Nice-to-have)
```sql
ALTER TABLE clicks ADD COLUMN:
- dwell_time_seconds INTEGER
- scroll_depth_percent SMALLINT
```

**Why Last:**
- Requires JavaScript tracking pixel
- Privacy concerns (GDPR)
- Lower immediate ROI

---

## 📈 Data Science Use Cases Enabled

### 1. **Descriptive Analytics** (Current State)
```sql
-- Which videos drive most traffic?
SELECT video_id, COUNT(*) as clicks
FROM clicks
WHERE video_id IS NOT NULL
GROUP BY video_id
ORDER BY clicks DESC
LIMIT 10;

-- Best time to post links?
SELECT hour_of_day, day_of_week, COUNT(*) as clicks
FROM clicks
GROUP BY hour_of_day, day_of_week
ORDER BY clicks DESC;
```

### 2. **Diagnostic Analytics** (Why it happened)
```sql
-- Why did this video go viral?
SELECT
    video_id,
    AVG(viral_coefficient) as avg_viral_coef,
    COUNT(DISTINCT yt_feature) as distribution_channels,
    mode() WITHIN GROUP (ORDER BY hour_of_day) as peak_hour
FROM clicks
WHERE clicks_last_24h > 100
GROUP BY video_id;
```

### 3. **Predictive Analytics** (Future Models)

**Model 1: Click Probability**
```python
# Features: video_id, channel_id, hour_of_day, day_of_week, yt_feature
# Target: clicks_next_24h
# Algorithm: XGBoost Regression
```

**Model 2: Viral Detection**
```python
# Features: clicks_last_hour, viral_coefficient, referral_depth
# Target: will_go_viral (>1000 clicks)
# Algorithm: Random Forest Classification
```

**Model 3: Conversion Prediction**
```python
# Features: session features, user journey, time patterns
# Target: conversion_probability
# Algorithm: Neural Network (LSTM for sequence data)
```

### 4. **Prescriptive Analytics** (What to do)

**Recommendation Engine:**
- "Post your next link at 7PM on Wednesday for max engagement"
- "Videos from this channel have 80% click-through rate"
- "Add video timestamp to increase engagement by 30%"

---

## 🔄 Data Collection Strategy

### URL Parameter Parsing

**YouTube URL Patterns:**
```python
# Example URLs to parse:
1. https://www.youtube.com/watch?v=ABC123
   → video_id: "ABC123"

2. https://www.youtube.com/watch?v=ABC123&t=120
   → video_id: "ABC123", video_timestamp: 120

3. https://www.youtube.com/watch?v=ABC123&list=PLxxx&index=5
   → video_id: "ABC123", playlist_id: "PLxxx", yt_index: 5

4. https://youtu.be/ABC123?feature=share
   → video_id: "ABC123", yt_feature: "share"

5. https://m.youtube.com/watch?v=ABC123&app=desktop
   → video_id: "ABC123", yt_app: "desktop"
```

**Parser Implementation:**
```python
from urllib.parse import urlparse, parse_qs

def parse_youtube_url(url: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    # Extract video_id
    video_id = None
    if 'youtu.be' in parsed.netloc:
        video_id = parsed.path[1:]  # Remove leading /
    else:
        video_id = params.get('v', [None])[0]

    return {
        'video_id': video_id,
        'video_timestamp': int(params.get('t', [0])[0]),
        'playlist_id': params.get('list', [None])[0],
        'yt_index': int(params.get('index', [0])[0]),
        'yt_feature': params.get('feature', [None])[0],
        'yt_app': params.get('app', [None])[0]
    }
```

### Temporal Feature Extraction

```python
from datetime import datetime

def extract_temporal_features(timestamp: datetime) -> dict:
    return {
        'hour_of_day': timestamp.hour,
        'day_of_week': timestamp.weekday(),
        'is_weekend': timestamp.weekday() >= 5,
        'week_of_year': timestamp.isocalendar()[1],
        'month': timestamp.month
    }
```

### Session Tracking Strategy

```python
# Using IP + User-Agent hash for session identification
import hashlib

def generate_session_id(ip: str, user_agent: str, time_window_mins: int = 30) -> str:
    """
    Generate session ID based on IP + User-Agent + Time Window
    Same user within 30 mins = same session
    """
    time_bucket = int(datetime.now().timestamp() / (time_window_mins * 60))
    session_key = f"{ip}_{user_agent}_{time_bucket}"
    return hashlib.sha256(session_key.encode()).hexdigest()[:16]
```

---

## 📊 Analytics Dashboard Enhancements

### New Widgets for YouTube Analytics

**1. Top Performing Videos**
```sql
SELECT
    video_id,
    video_title,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT ip_address) as unique_viewers,
    ROUND(AVG(video_timestamp), 0) as avg_click_position,
    mode() WITHIN GROUP (ORDER BY yt_feature) as primary_source
FROM clicks
WHERE video_id IS NOT NULL
AND clicked_at >= NOW() - INTERVAL '7 days'
GROUP BY video_id, video_title
ORDER BY total_clicks DESC
LIMIT 10;
```

**2. Hour Heatmap**
```sql
SELECT
    day_of_week,
    hour_of_day,
    COUNT(*) as clicks,
    AVG(viral_coefficient) as avg_virality
FROM clicks
WHERE clicked_at >= NOW() - INTERVAL '30 days'
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;
```

**3. Viral Coefficient Trend**
```sql
SELECT
    DATE(clicked_at) as date,
    AVG(viral_coefficient) as daily_viral_score,
    SUM(clicks_last_24h) as total_viral_clicks
FROM clicks
WHERE clicked_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(clicked_at)
ORDER BY date;
```

---

## 🚀 Next Steps - Implementation Plan

### Step 1: Schema Migration (30 mins)
- Create migration SQL file
- Add Phase 1 columns (YouTube essentials)
- Test on local Supabase
- Deploy to production

### Step 2: Backend URL Parser (1 hour)
- Implement `parse_youtube_url()` function
- Add to click tracking pipeline
- Test with various YouTube URL formats
- Add logging for debug

### Step 3: Temporal Features (30 mins)
- Implement `extract_temporal_features()`
- Auto-populate on click insert
- Create indexes for time-based queries

### Step 4: Session Tracking (1 hour)
- Implement `generate_session_id()`
- Add session detection logic
- Track first vs returning visitors
- Add session analytics queries

### Step 5: Analytics Dashboard (2 hours)
- Add "Top Videos" widget
- Add "Hour Heatmap" visualization
- Add "Viral Trend" chart
- Update frontend to display new metrics

### Step 6: Testing & Validation (1 hour)
- Create test YouTube URLs
- Verify parsing accuracy
- Check analytics calculations
- Performance testing

---

## 📝 Success Metrics

**After Implementation:**
- ✅ Can identify top-performing YouTube videos
- ✅ Know optimal posting times
- ✅ Track viral coefficient per link
- ✅ Understand user journey (session-based)
- ✅ Detect patterns for predictive models

**Future Capabilities:**
- 🔮 Predict clicks for new videos
- 🔮 Recommend best posting times
- 🔮 Identify viral content early
- 🔮 Optimize conversion funnels
- 🔮 Build recommendation engine

---

**Analysis Time:** ~45 minutes
**Implementation Est:** ~6 hours total
**ROI:** HIGH - Enables predictive analytics + YouTube optimization

🤖 Generated with [Claude Code](https://claude.com/claude-code)
