"""
Click Tracker Service
Comprehensive click tracking with advanced analytics:
- Video attribution (YouTube, TikTok, Instagram)
- Returning visitor detection
- City-level geolocation
- Enhanced platform detection
- Time pattern analysis
"""

import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict
from fastapi import Request

from domain.models.url import Click
from infrastructure.external_apis.geolocation_client import get_ip_location
from infrastructure.external_apis.user_agent_parser import parse_user_agent
from infrastructure.external_apis.video_attribution import parse_video_referrer


class ClickTrackerService:
    """
    Advanced click tracking service with comprehensive analytics
    """

    def __init__(self):
        # In-memory storage for returning visitor detection
        # Key: (ip_address, url_id) -> first_click_timestamp
        self.visitor_sessions = {}

        # In-memory click storage (MVP - replace with database later)
        self.clicks_storage = []

    async def track_click(
        self,
        url_id: str,
        short_code: str,
        request: Request
    ) -> Click:
        """
        Track a click event with comprehensive analytics

        Args:
            url_id: URL identifier
            short_code: Short code of the URL
            request: FastAPI request object

        Returns:
            Click object with all analytics data
        """
        # Extract request metadata
        ip_address = self._extract_ip_address(request)
        user_agent = request.headers.get('user-agent', '')
        referer = request.headers.get('referer', request.headers.get('referrer', ''))

        # Generate session ID for visitor tracking
        session_id = self._generate_session_id(ip_address, user_agent)

        # Check if returning visitor
        is_returning = self._check_returning_visitor(ip_address, url_id, session_id)

        # Parse user agent for device/platform info
        device_info = parse_user_agent(user_agent)

        # Get geolocation (with city-level detail)
        location_data = await get_ip_location(ip_address)

        # Parse video attribution from referrer
        video_data = parse_video_referrer(referer)

        # Extract referrer domain and type
        referrer_domain, referrer_type = self._parse_referrer(referer)

        # Create click record
        click = Click(
            id=f"click_{uuid.uuid4().hex[:12]}",
            url_id=url_id,
            short_code=short_code,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            # Geolocation data (with city)
            country_code=location_data.get('country_code'),
            country_name=location_data.get('country_name'),
            city=location_data.get('city'),  # City-level detail
            # Device detection
            device_type=device_info.get('device_type'),
            browser_name=device_info.get('browser_name'),
            os_name=device_info.get('os_name'),
            # Advanced: Platform detection
            platform=device_info.get('platform'),  # e.g., "iOS 17.5", "Windows 11"
            # Traffic source
            referrer_domain=referrer_domain,
            referrer_type=referrer_type,
            # Advanced: Video attribution
            video_id=video_data.get('video_id'),
            video_platform=video_data.get('video_platform'),
            # Advanced: Returning visitor tracking
            is_returning_visitor=is_returning,
            session_id=session_id,
            # Timestamp
            clicked_at=datetime.utcnow()
        )

        # Store click (in-memory for MVP)
        self.clicks_storage.append(click)

        # Update visitor session tracking
        self._record_visitor_session(ip_address, url_id, session_id)

        return click

    def _extract_ip_address(self, request: Request) -> str:
        """
        Extract real IP address from request, handling proxies
        """
        # Check common proxy headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # Fallback to client IP
        if request.client:
            return request.client.host

        return '0.0.0.0'

    def _generate_session_id(self, ip_address: str, user_agent: str) -> str:
        """
        Generate consistent session ID for visitor tracking
        Uses IP + user agent hash for privacy-friendly tracking
        """
        session_string = f"{ip_address}:{user_agent}"
        return hashlib.sha256(session_string.encode()).hexdigest()[:16]

    def _check_returning_visitor(
        self,
        ip_address: str,
        url_id: str,
        session_id: str
    ) -> bool:
        """
        Check if this visitor has clicked this link before
        """
        visitor_key = f"{session_id}:{url_id}"
        return visitor_key in self.visitor_sessions

    def _record_visitor_session(
        self,
        ip_address: str,
        url_id: str,
        session_id: str
    ):
        """
        Record visitor session for returning visitor detection
        """
        visitor_key = f"{session_id}:{url_id}"
        if visitor_key not in self.visitor_sessions:
            self.visitor_sessions[visitor_key] = datetime.utcnow()

    def _parse_referrer(self, referer: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Parse referrer URL to extract domain and type

        Returns:
            Tuple of (referrer_domain, referrer_type)
        """
        if not referer:
            return None, 'direct'

        try:
            from urllib.parse import urlparse
            parsed = urlparse(referer)
            domain = parsed.netloc.lower()

            # Categorize referrer type
            referrer_type = self._categorize_referrer(domain)

            return domain, referrer_type

        except Exception:
            return None, 'unknown'

    def _categorize_referrer(self, domain: str) -> str:
        """
        Categorize referrer domain into types
        """
        if not domain:
            return 'direct'

        # Social media platforms
        social_platforms = {
            'facebook.com': 'facebook',
            'fb.com': 'facebook',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            't.co': 'twitter',
            'linkedin.com': 'linkedin',
            'instagram.com': 'instagram',
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'tiktok.com': 'tiktok',
            'reddit.com': 'reddit',
            'pinterest.com': 'pinterest',
            'whatsapp.com': 'whatsapp',
            'telegram.org': 'telegram',
            'discord.com': 'discord'
        }

        for platform_domain, platform_name in social_platforms.items():
            if platform_domain in domain:
                return platform_name

        # Search engines
        search_engines = ['google', 'bing', 'yahoo', 'duckduckgo', 'baidu', 'yandex']
        if any(engine in domain for engine in search_engines):
            return 'search'

        # Email clients
        email_clients = ['mail.', 'outlook', 'gmail', 'yahoo.com', 'protonmail']
        if any(client in domain for client in email_clients):
            return 'email'

        # Default to domain or unknown
        return domain if domain else 'unknown'

    def get_clicks_by_url(self, url_id: str) -> list[Click]:
        """
        Get all clicks for a specific URL

        Args:
            url_id: URL identifier

        Returns:
            List of Click objects
        """
        return [click for click in self.clicks_storage if click.url_id == url_id]

    def get_analytics_summary(self, url_id: str) -> dict:
        """
        Get analytics summary for a URL with advanced metrics

        Args:
            url_id: URL identifier

        Returns:
            Analytics summary dictionary
        """
        clicks = self.get_clicks_by_url(url_id)

        if not clicks:
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'returning_visitors': 0,
                'device_breakdown': {},
                'country_breakdown': {},
                'city_breakdown': {},
                'platform_breakdown': {},
                'video_sources': {},
                'time_patterns': {},
                'referrer_breakdown': {}
            }

        # Calculate metrics
        total_clicks = len(clicks)
        unique_sessions = len(set(click.session_id for click in clicks if click.session_id))
        returning_count = sum(1 for click in clicks if click.is_returning_visitor)

        # Device breakdown
        device_breakdown = {}
        for click in clicks:
            device = click.device_type or 'unknown'
            device_breakdown[device] = device_breakdown.get(device, 0) + 1

        # Country breakdown
        country_breakdown = {}
        for click in clicks:
            country = click.country_name or 'Unknown'
            country_breakdown[country] = country_breakdown.get(country, 0) + 1

        # City breakdown (NEW)
        city_breakdown = {}
        for click in clicks:
            if click.city:
                city_key = f"{click.city}, {click.country_code or 'XX'}"
                city_breakdown[city_key] = city_breakdown.get(city_key, 0) + 1

        # Platform breakdown (NEW - detailed OS versions)
        platform_breakdown = {}
        for click in clicks:
            platform = click.platform or 'Unknown'
            platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1

        # Video sources (NEW)
        video_sources = {}
        for click in clicks:
            if click.video_platform and click.video_id:
                video_key = f"{click.video_platform}:{click.video_id}"
                video_sources[video_key] = video_sources.get(video_key, 0) + 1

        # Time patterns (NEW - hour/day analysis)
        time_patterns = self._analyze_time_patterns(clicks)

        # Referrer breakdown
        referrer_breakdown = {}
        for click in clicks:
            ref_type = click.referrer_type or 'direct'
            referrer_breakdown[ref_type] = referrer_breakdown.get(ref_type, 0) + 1

        return {
            'total_clicks': total_clicks,
            'unique_visitors': unique_sessions,
            'returning_visitors': returning_count,
            'device_breakdown': device_breakdown,
            'country_breakdown': country_breakdown,
            'city_breakdown': city_breakdown,  # NEW
            'platform_breakdown': platform_breakdown,  # NEW
            'video_sources': video_sources,  # NEW
            'time_patterns': time_patterns,  # NEW
            'referrer_breakdown': referrer_breakdown
        }

    def _analyze_time_patterns(self, clicks: list[Click]) -> dict:
        """
        Analyze click patterns by time (hour of day, day of week)

        Returns:
            Dictionary with time pattern analytics
        """
        hour_distribution = {}
        day_distribution = {}

        for click in clicks:
            if click.clicked_at:
                # Hour of day (0-23)
                hour = click.clicked_at.hour
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1

                # Day of week (0=Monday, 6=Sunday)
                day = click.clicked_at.weekday()
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_name = day_names[day]
                day_distribution[day_name] = day_distribution.get(day_name, 0) + 1

        # Find peak hour and day
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None
        peak_day = max(day_distribution.items(), key=lambda x: x[1])[0] if day_distribution else None

        return {
            'hour_distribution': hour_distribution,
            'day_distribution': day_distribution,
            'peak_hour': peak_hour,
            'peak_day': peak_day
        }


# Singleton instance
click_tracker_service = ClickTrackerService()