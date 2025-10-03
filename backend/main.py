# -*- coding: utf-8 -*-
"""
SuperintelligenceURLs FastAPI Application
URL Shortener with real-time analytics
"""

import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Import domain models
from domain.models.url import URLCreate
from domain.services.url_generator import generate_short_code, validate_short_code

# Import advanced analytics services
from infrastructure.external_apis.geolocation_client import get_ip_location
from infrastructure.external_apis.user_agent_parser import parse_user_agent
from infrastructure.external_apis.video_attribution import parse_video_referrer
from infrastructure.external_apis.temporal_features import (
    extract_temporal_features,
    generate_session_id,
    track_session
)

# Import folder service
from application.services.folder_service import FolderService

# Import click tracker service
from application.services.click_tracker_service import click_tracker_service

# Import Supabase repositories
from infrastructure.persistence.url_repository import URLRepository
from infrastructure.persistence.click_repository import ClickRepository
from infrastructure.persistence.folder_repository import FolderRepository

# Initialize repositories
url_repo = URLRepository()
click_repo = ClickRepository()
folder_repo = FolderRepository()

# Initialize folder service with repository
folder_service_instance = FolderService(folder_repo)

# Legacy exports (mantener compatibilidad temporal)
urls_db = {}
clicks_db = []
urls = urls_db
clicks = clicks_db

# Initialize FastAPI app
app = FastAPI(
    title="SuperintelligenceURLs API",
    description="URL Shortener with real-time analytics and authentication",
    version="1.0.1",
    docs_url="/docs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
from api.auth_middleware import AuthMiddleware
app.add_middleware(AuthMiddleware)

# Global exception handler for CORS on errors
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Include auth router
from api.auth_router import router as auth_router
app.include_router(auth_router)

# Include folders router
from api.folders_router import router as folders_router_impl, folder_service as _folder_service_var
# Set the folder service instance
import api.folders_router as folders_router_module
folders_router_module.folder_service = folder_service_instance
app.include_router(folders_router_impl)


class URLRecord:
    """Simple URL record for MVP"""
    def __init__(self, short_code: str, original_url: str, title: str = None):
        self.id = short_code
        self.short_code = short_code
        self.original_url = original_url
        self.title = title
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.click_count = 0
        self.last_clicked_at = None
        self.domain = self._extract_domain(original_url)

    def _extract_domain(self, url: str) -> Optional[str]:
        try:
            if not url.startswith(('http://', 'https://')):
                return None
            url_without_protocol = url.split('://', 1)[1]
            domain = url_without_protocol.split('/')[0]
            domain = domain.split(':')[0]
            return domain.lower()
        except Exception:
            return None

    def can_redirect(self) -> bool:
        return self.is_active


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SuperintelligenceURLs",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "urls_count": len(urls_db),
        "clicks_count": len(clicks_db)
    }


@app.post("/shorten")
async def create_short_url(url_data: URLCreate):
    """Create a new shortened URL"""
    start_time = time.perf_counter()

    # Validate original URL format
    if not url_data.original_url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://"
        )

    # Generate unique short code
    short_code = generate_short_code(url=url_data.original_url)

    # Ensure uniqueness in Supabase
    max_attempts = 10
    attempts = 0
    existing = url_repo.get_by_short_code(short_code)
    while existing and attempts < max_attempts:
        short_code = generate_short_code()
        existing = url_repo.get_by_short_code(short_code)
        attempts += 1

    if existing:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate unique short code"
        )

    # Extract domain
    try:
        if not url_data.original_url.startswith(('http://', 'https://')):
            domain = None
        else:
            url_without_protocol = url_data.original_url.split('://', 1)[1]
            domain = url_without_protocol.split('/')[0].split(':')[0].lower()
    except Exception:
        domain = None

    # Create in Supabase
    url_record = url_repo.create(
        short_code=short_code,
        original_url=url_data.original_url,
        title=url_data.title,
        domain=domain
    )

    # Assign to folder if folder_id provided
    if url_data.folder_id:
        try:
            folder_repo.assign_link(folder_id=url_data.folder_id, url_id=url_record['id'])
            print(f"✅ Link {short_code} assigned to folder {url_data.folder_id}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to assign link to folder: {e}")
            # Continue anyway - link was created successfully

    # Performance tracking
    processing_time = (time.perf_counter() - start_time) * 1000
    print(f"✅ URL created in Supabase: {short_code} -> {url_data.original_url} ({processing_time:.2f}ms)")

    return url_record


@app.get("/urls/all")
async def get_all_urls():
    """Get all shortened URLs"""
    try:
        urls = url_repo.get_all(limit=100)
        print(f"✅ Retrieved {len(urls)} URLs from Supabase")
        return {
            "urls": urls,
            "total": len(urls)
        }
    except Exception as e:
        print(f"❌ Error getting URLs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve URLs: {str(e)}"
        )


@app.get("/{short_code}")
async def redirect_url(short_code: str, request: Request):
    """Redirect to original URL and track analytics"""
    start_time = time.perf_counter()

    # Validate short code format
    if not validate_short_code(short_code):
        raise HTTPException(
            status_code=404,
            detail="Invalid short code format"
        )

    # Lookup URL in Supabase
    url_record = url_repo.get_by_short_code(short_code)
    if not url_record:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    # Check if URL is active
    if not url_record.get('is_active', True):
        raise HTTPException(
            status_code=410,
            detail="Short URL is inactive"
        )

    # Track click with advanced analytics
    click_data = await click_tracker_service.track_click(
        url_id=url_record['id'],
        short_code=short_code,
        request=request
    )

    # Save click to Supabase with all advanced fields
    click_repo.create({
        'url_id': url_record['id'],
        'short_code': short_code,
        'ip_address': click_data.ip_address,
        'user_agent': click_data.user_agent,
        'referer': click_data.referer,
        'country_code': click_data.country_code,
        'country_name': click_data.country_name,
        'city': click_data.city,
        'device_type': click_data.device_type,
        'browser_name': click_data.browser_name,
        'os_name': click_data.os_name,
        'referrer_domain': click_data.referrer_domain,
        'referrer_type': click_data.referrer_type,
        # Advanced analytics fields
        'video_id': click_data.video_id,
        'video_platform': click_data.video_platform,
        'platform': click_data.platform,
        'is_returning_visitor': click_data.is_returning_visitor,
        'session_id': click_data.session_id
    })

    # Update click count in Supabase
    url_repo.update_click_count(url_record['id'])

    # Performance logging
    redirect_time = (time.perf_counter() - start_time) * 1000
    print(f"✅ Redirect + Analytics: {short_code} ({redirect_time:.2f}ms)")

    # Return redirect response
    return RedirectResponse(
        url=url_record['original_url'],
        status_code=301
    )


@app.get("/analytics/{short_code}")
async def get_analytics(short_code: str):
    """Get analytics for a specific short URL with advanced features"""
    # Get URL from Supabase
    url_record = url_repo.get_by_short_code(short_code)
    if not url_record:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    # Get analytics from Supabase
    analytics = click_repo.get_analytics_summary(short_code)

    return {
        "short_code": short_code,
        "original_url": url_record['original_url'],
        "created_at": url_record['created_at'],
        "total_clicks": analytics['total_clicks'],
        "unique_visitors": analytics['unique_visitors'],
        "returning_visitors": analytics['returning_visitors'],  # NEW
        "device_breakdown": analytics['device_breakdown'],
        "country_breakdown": analytics['country_breakdown'],
        "city_breakdown": analytics['city_breakdown'],  # NEW - city-level geo
        "platform_breakdown": analytics['platform_breakdown'],  # NEW - detailed platforms
        "video_sources": analytics['video_sources'],  # NEW - video attribution
        "time_patterns": analytics['time_patterns'],  # NEW - time analysis
        "referrer_breakdown": analytics['referrer_breakdown'],
        "recent_clicks": analytics.get('recent_clicks', [])  # ✅ Recent clicks table data
    }


@app.delete("/{short_code}")
async def delete_url(short_code: str):
    """Soft delete URL - sets is_active to False"""
    success = url_repo.delete(short_code)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )
    print(f"✅ URL soft-deleted: {short_code}")
    return {"message": "URL deleted successfully", "short_code": short_code}


async def track_click(short_code: str, url_id: str, request: Request, start_time: float):
    """Track click event with advanced analytics + temporal features"""
    analytics_start = time.perf_counter()

    # Extract request metadata
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('user-agent', '')
    referer = request.headers.get('referer')

    # Get URL record for temporal calculations
    url_record = url_repo.get_by_id(url_id)
    url_created_at = url_record.get('created_at') if url_record else None

    # Parse video attribution from REFERER (YouTube, TikTok, Instagram, etc.)
    video_data = parse_video_referrer(referer)
    if video_data.get('video_platform'):
        print(f"🎥 Video detected: {video_data.get('video_platform')} | ID: {video_data.get('video_id')}")

    # Generate session ID for tracking
    current_time = datetime.utcnow()
    session_id = generate_session_id(ip_address, user_agent, current_time)

    # Track session metrics
    session_metrics = track_session(session_id, current_time)

    # Extract temporal features
    temporal_features = extract_temporal_features(current_time, url_created_at)
    print(f"⏰ Temporal: {temporal_features.get('day_of_week')} (day), {temporal_features.get('hour_of_day')}h | Session: {session_metrics.get('clicks_in_session')} clicks")

    # Advanced user agent parsing
    device_info = parse_user_agent(user_agent)

    # Advanced geolocation (async with fallback)
    location_data = {}
    try:
        if ip_address and ip_address not in ['127.0.0.1', 'localhost', 'testclient']:
            location_data = await get_ip_location(ip_address)
            print(f"🌍 Location: {location_data.get('country_name', 'Unknown')}, {location_data.get('city', 'N/A')}")
        else:
            location_data = {'country_name': 'Unknown', 'city': None}
    except Exception as e:
        print(f"❌ Geolocation failed: {e}")
        location_data = {'country_name': 'Unknown', 'city': None}

    # Extract referrer source
    referrer_source = extract_referrer_source(referer)

    analytics_time = (time.perf_counter() - analytics_start) * 1000

    # Create comprehensive click record with NEW temporal + video fields
    click_data = {
        'url_id': url_id,
        'short_code': short_code,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'referer': referer,

        # Device Analytics
        'device_type': device_info.get('device_type', 'unknown'),
        'browser_name': device_info.get('browser_name', 'Unknown'),
        'browser_version': device_info.get('browser_version'),
        'os_name': device_info.get('os_name', 'Unknown'),
        'os_version': device_info.get('os_version'),

        # Geographic Analytics
        'country_name': location_data.get('country_name', 'Unknown'),
        'country_code': location_data.get('country_code'),
        'city': location_data.get('city'),

        # Referrer Analytics
        'referrer_domain': referrer_source,
        'referrer_type': referrer_source,

        # 🆕 VIDEO ATTRIBUTION (from REFERER)
        'video_platform': video_data.get('video_platform'),
        'video_id': video_data.get('video_id'),

        # 🆕 TEMPORAL FEATURES
        'hour_of_day': temporal_features.get('hour_of_day'),
        'day_of_week': temporal_features.get('day_of_week'),
        'is_weekend': temporal_features.get('is_weekend'),
        'month': temporal_features.get('month'),
        'time_since_creation_seconds': temporal_features.get('time_since_creation_seconds'),

        # 🆕 SESSION TRACKING
        'session_id': session_id,
        'is_first_click': session_metrics.get('is_first_click'),
        'is_returning_visitor': not session_metrics.get('is_first_click'),
        'clicks_in_session': session_metrics.get('clicks_in_session'),

        # Timestamps
        'clicked_at': current_time,
        'response_time_ms': int((time.perf_counter() - start_time) * 1000)
    }

    # 🆕 SAVE TO SUPABASE (instead of RAM)
    try:
        saved_click = click_repo.create(click_data)
        print(f"✅ Click saved to Supabase: {saved_click.get('id') if saved_click else 'None'}")
    except Exception as e:
        print(f"❌ Failed to save click to Supabase: {e}")
        # Fallback to RAM for backward compatibility
        clicks_db.append(click_data)

    # Performance logging
    print(f"📊 Analytics: {analytics_time:.2f}ms | Device: {device_info.get('device_type')} | Location: {location_data.get('country_name')}")

    return click_data


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('x-real-ip')
    if real_ip:
        return real_ip

    return request.client.host if request.client else None


def detect_device_type(user_agent: str) -> str:
    """Basic device type detection from user agent"""
    if not user_agent:
        return 'unknown'

    user_agent_lower = user_agent.lower()

    # Mobile patterns
    mobile_patterns = ['mobile', 'android', 'iphone', 'ipod', 'blackberry']
    if any(pattern in user_agent_lower for pattern in mobile_patterns):
        return 'mobile'

    # Tablet patterns
    tablet_patterns = ['ipad', 'tablet', 'kindle']
    if any(pattern in user_agent_lower for pattern in tablet_patterns):
        return 'tablet'

    # Bot patterns
    bot_patterns = ['bot', 'crawler', 'spider', 'scraper']
    if any(pattern in user_agent_lower for pattern in bot_patterns):
        return 'bot'

    return 'desktop'


def extract_referrer_source(referer: Optional[str]) -> str:
    """Extract traffic source from referrer URL"""
    if not referer:
        return 'direct'

    referer_lower = referer.lower()

    # Social media platforms
    social_sources = {
        'facebook.com': 'Facebook',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter',
        'linkedin.com': 'LinkedIn',
        'instagram.com': 'Instagram',
        'youtube.com': 'YouTube',
        'tiktok.com': 'TikTok',
        'reddit.com': 'Reddit',
        'pinterest.com': 'Pinterest',
        'whatsapp.com': 'WhatsApp',
        'telegram.org': 'Telegram'
    }

    # Search engines
    search_sources = {
        'google.com': 'Google',
        'bing.com': 'Bing',
        'yahoo.com': 'Yahoo',
        'duckduckgo.com': 'DuckDuckGo',
        'baidu.com': 'Baidu'
    }

    # Email platforms
    email_sources = {
        'gmail.com': 'Gmail',
        'outlook.com': 'Outlook',
        'mail.yahoo.com': 'Yahoo Mail'
    }

    # Check all source categories
    for domain, source in {**social_sources, **search_sources, **email_sources}.items():
        if domain in referer_lower:
            return source

    # Extract domain for unknown sources
    try:
        if '://' in referer:
            domain = referer.split('://')[1].split('/')[0]
            return domain.replace('www.', '')
    except Exception:
        pass

    return 'other'


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SuperintelligenceURLs",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "total_urls": len(urls_db),
            "total_clicks": len(clicks_db),
            "active_urls": sum(1 for url in urls_db.values() if url.is_active)
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting SuperintelligenceURLs API server...")
    print("Dashboard: http://localhost:8000/docs")
    print("Create URLs: POST http://localhost:8000/shorten")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )