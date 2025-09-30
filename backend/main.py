# -*- coding: utf-8 -*-
"""
LinkProxy FastAPI Application
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

# Import folder service
from application.services.folder_service import FolderService

# Import click tracker service
from application.services.click_tracker_service import click_tracker_service

# Temporary in-memory storage for MVP
urls_db = {}
clicks_db = []

# Initialize folder service
folder_service_instance = FolderService()

# Export for folder router
urls = urls_db
clicks = clicks_db

# Initialize FastAPI app
app = FastAPI(
    title="LinkProxy API",
    description="URL Shortener with real-time analytics",
    version="1.0.0",
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

# Include folders router
from api import folders_router
folders_router.folder_service = folder_service_instance
app.include_router(folders_router.router)


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
        "service": "LinkProxy",
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

    # Ensure uniqueness
    max_attempts = 10
    attempts = 0
    while short_code in urls_db and attempts < max_attempts:
        short_code = generate_short_code()
        attempts += 1

    if short_code in urls_db:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate unique short code"
        )

    # Create URL record
    url_record = URLRecord(
        short_code=short_code,
        original_url=url_data.original_url,
        title=url_data.title
    )

    # Store in temporary database
    urls_db[short_code] = url_record

    # Performance tracking
    processing_time = (time.perf_counter() - start_time) * 1000
    print(f"URL created: {short_code} -> {url_data.original_url} ({processing_time:.2f}ms)")

    return {
        "id": url_record.id,
        "short_code": url_record.short_code,
        "original_url": url_record.original_url,
        "title": url_record.title,
        "is_active": url_record.is_active,
        "created_at": url_record.created_at.isoformat(),
        "click_count": url_record.click_count,
        "domain": url_record.domain
    }


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

    # Lookup URL
    if short_code not in urls_db:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    url_record = urls_db[short_code]

    # Check if URL can be redirected
    if not url_record.can_redirect():
        raise HTTPException(
            status_code=410,
            detail="Short URL is inactive"
        )

    # Track click analytics with advanced features (async)
    click_data = await click_tracker_service.track_click(
        url_id=url_record.id,
        short_code=short_code,
        request=request
    )

    # Update URL statistics
    url_record.click_count += 1
    url_record.last_clicked_at = datetime.utcnow()

    # Also store in old format for backward compatibility
    clicks_db.append({
        'short_code': short_code,
        'ip_address': click_data.ip_address,
        'device_type': click_data.device_type
    })

    # Performance logging
    redirect_time = (time.perf_counter() - start_time) * 1000
    print(f"Redirect: {short_code} -> {url_record.original_url} ({redirect_time:.2f}ms)")

    # Return redirect response (HTTP 301 for permanent redirect)
    return RedirectResponse(
        url=url_record.original_url,
        status_code=301
    )


@app.get("/analytics/{short_code}")
async def get_analytics(short_code: str):
    """Get analytics for a specific short URL with advanced features"""
    if short_code not in urls_db:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    url_record = urls_db[short_code]

    # Get advanced analytics summary from click tracker service
    analytics = click_tracker_service.get_analytics_summary(url_record.id)

    return {
        "short_code": short_code,
        "original_url": url_record.original_url,
        "created_at": url_record.created_at.isoformat(),
        "total_clicks": analytics['total_clicks'],
        "unique_visitors": analytics['unique_visitors'],
        "returning_visitors": analytics['returning_visitors'],  # NEW
        "device_breakdown": analytics['device_breakdown'],
        "country_breakdown": analytics['country_breakdown'],
        "city_breakdown": analytics['city_breakdown'],  # NEW - city-level geo
        "platform_breakdown": analytics['platform_breakdown'],  # NEW - detailed platforms
        "video_sources": analytics['video_sources'],  # NEW - video attribution
        "time_patterns": analytics['time_patterns'],  # NEW - time analysis
        "referrer_breakdown": analytics['referrer_breakdown']
    }


async def track_click(short_code: str, url_id: str, request: Request, start_time: float):
    """Track click event with advanced analytics"""
    analytics_start = time.perf_counter()

    # Extract request metadata
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('user-agent', '')
    referer = request.headers.get('referer')

    # Advanced user agent parsing
    device_info = parse_user_agent(user_agent)

    # Advanced geolocation (async with fallback)
    location_data = {}
    try:
        if ip_address and ip_address not in ['127.0.0.1', 'localhost', 'testclient']:
            location_data = await get_ip_location(ip_address)
    except Exception as e:
        print(f"Geolocation failed for {ip_address}: {e}")
        location_data = {
            'country_name': 'Unknown',
            'city': None,
            'provider': 'fallback'
        }

    # Extract referrer source
    referrer_source = extract_referrer_source(referer)

    analytics_time = (time.perf_counter() - analytics_start) * 1000

    # Create comprehensive click record
    click_data = {
        'id': f"click_{len(clicks_db)}",
        'url_id': url_id,
        'short_code': short_code,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'referer': referer,
        'referrer_source': referrer_source,

        # Device Analytics
        'device_type': device_info.get('device_type', 'unknown'),
        'device_brand': device_info.get('device_brand'),
        'device_model': device_info.get('device_model'),
        'browser_name': device_info.get('browser_name', 'Unknown'),
        'browser_version': device_info.get('browser_version'),
        'os_name': device_info.get('os_name', 'Unknown'),
        'os_version': device_info.get('os_version'),
        'is_mobile': device_info.get('is_mobile', False),
        'is_tablet': device_info.get('is_tablet', False),
        'is_desktop': device_info.get('is_desktop', False),
        'is_bot': device_info.get('is_bot', False),

        # Geographic Analytics
        'country_name': location_data.get('country_name', 'Unknown'),
        'country_code': location_data.get('country_code'),
        'region': location_data.get('region'),
        'city': location_data.get('city'),
        'timezone': location_data.get('timezone'),
        'isp': location_data.get('isp'),
        'latitude': location_data.get('latitude'),
        'longitude': location_data.get('longitude'),
        'geo_provider': location_data.get('provider', 'none'),

        # Performance Metrics
        'clicked_at': datetime.utcnow().isoformat(),
        'response_time_ms': int((time.perf_counter() - start_time) * 1000),
        'analytics_time_ms': round(analytics_time, 2)
    }

    # Store click event
    clicks_db.append(click_data)

    # Performance logging
    print(f"📊 Analytics: {analytics_time:.2f}ms | Device: {device_info.get('device_type')} | Location: {location_data.get('country_name', 'Unknown')}")

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
        "service": "LinkProxy",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "total_urls": len(urls_db),
            "total_clicks": len(clicks_db),
            "active_urls": sum(1 for url in urls_db.values() if url.is_active)
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting LinkProxy API server...")
    print("Dashboard: http://localhost:8000/docs")
    print("Create URLs: POST http://localhost:8000/shorten")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )