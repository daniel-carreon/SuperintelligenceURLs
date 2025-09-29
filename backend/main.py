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

# Temporary in-memory storage for MVP
urls_db = {}
clicks_db = []

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

    # Track click analytics
    track_click(short_code, url_record.id, request, start_time)

    # Update URL statistics
    url_record.click_count += 1
    url_record.last_clicked_at = datetime.utcnow()

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
    """Get analytics for a specific short URL"""
    if short_code not in urls_db:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    url_record = urls_db[short_code]

    # Filter clicks for this URL
    url_clicks = [click for click in clicks_db if click['short_code'] == short_code]

    # Calculate analytics
    total_clicks = len(url_clicks)
    unique_ips = len(set(click['ip_address'] for click in url_clicks if click['ip_address']))

    # Device breakdown
    device_stats = {}
    for click in url_clicks:
        device = click.get('device_type', 'unknown')
        device_stats[device] = device_stats.get(device, 0) + 1

    return {
        "short_code": short_code,
        "original_url": url_record.original_url,
        "created_at": url_record.created_at.isoformat(),
        "total_clicks": total_clicks,
        "unique_visitors": unique_ips,
        "device_breakdown": device_stats,
        "recent_clicks": url_clicks[-10:] if url_clicks else []
    }


def track_click(short_code: str, url_id: str, request: Request, start_time: float):
    """Track click event for analytics"""
    # Extract request metadata
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('user-agent', '')
    referer = request.headers.get('referer')

    # Basic device detection
    device_type = detect_device_type(user_agent)

    # Create click record
    click_data = {
        'id': f"click_{len(clicks_db)}",
        'url_id': url_id,
        'short_code': short_code,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'referer': referer,
        'device_type': device_type,
        'country_name': 'Unknown',
        'clicked_at': datetime.utcnow().isoformat(),
        'response_time_ms': int((time.perf_counter() - start_time) * 1000)
    }

    # Store click event
    clicks_db.append(click_data)

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