"""
Geolocation Service Client
IP to geographic location mapping with fallbacks and caching
"""

import asyncio
import json
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

import httpx


class GeolocationClient:
    """
    IP geolocation service with multiple providers and caching
    Optimized for performance with <100ms response time target
    """

    def __init__(self):
        self.cache: Dict[str, Tuple[dict, datetime]] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        self.timeout = 2.0  # 2 second timeout
        self.max_retries = 2

        # Free API endpoints with rate limits
        self.providers = [
            {
                'name': 'ipapi.co',
                'url': 'http://ipapi.co/{ip}/json/',
                'parser': self._parse_ipapi_response,
                'rate_limit': 1000  # 1000 requests per day
            },
            {
                'name': 'ip-api.com',
                'url': 'http://ip-api.com/json/{ip}',
                'parser': self._parse_ipapi_com_response,
                'rate_limit': 1000  # 1000 requests per month for free
            },
            {
                'name': 'ipinfo.io',
                'url': 'http://ipinfo.io/{ip}/json',
                'parser': self._parse_ipinfo_response,
                'rate_limit': 50000  # 50k requests per month
            }
        ]

        self.current_provider_index = 0
        self.provider_failures = {}

    async def get_location(self, ip_address: str) -> dict:
        """
        Get geographic location data for an IP address

        Args:
            ip_address: IP address to lookup

        Returns:
            Dictionary with location data or fallback data
        """
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', 'testclient']:
            return self._get_fallback_data(ip_address)

        # Check cache first
        cached_data = self._get_cached_location(ip_address)
        if cached_data:
            return cached_data

        # Try geolocation lookup
        location_data = await self._fetch_location_data(ip_address)

        # Cache the result
        self._cache_location(ip_address, location_data)

        return location_data

    def _get_cached_location(self, ip_address: str) -> Optional[dict]:
        """Check if location data is cached and still valid"""
        if ip_address in self.cache:
            cached_data, cached_time = self.cache[ip_address]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return cached_data

        return None

    def _cache_location(self, ip_address: str, data: dict):
        """Cache location data with timestamp"""
        self.cache[ip_address] = (data, datetime.utcnow())

        # Simple cache cleanup - remove oldest entries if cache gets too large
        if len(self.cache) > 10000:
            # Remove entries older than cache_ttl
            cutoff_time = datetime.utcnow() - self.cache_ttl
            self.cache = {
                ip: (data, timestamp)
                for ip, (data, timestamp) in self.cache.items()
                if timestamp > cutoff_time
            }

    async def _fetch_location_data(self, ip_address: str) -> dict:
        """
        Fetch location data from available providers with fallback
        """
        for attempt in range(len(self.providers)):
            provider = self._get_next_provider()

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = provider['url'].format(ip=ip_address)

                    response = await client.get(url)
                    response.raise_for_status()

                    raw_data = response.json()
                    parsed_data = provider['parser'](raw_data)

                    # Reset failure count on success
                    self.provider_failures[provider['name']] = 0

                    return parsed_data

            except Exception as e:
                self._record_provider_failure(provider['name'], e)
                continue

        # All providers failed, return fallback data
        return self._get_fallback_data(ip_address, error="All providers failed")

    def _get_next_provider(self) -> dict:
        """
        Get next available provider, skipping failed ones
        """
        for i in range(len(self.providers)):
            provider_index = (self.current_provider_index + i) % len(self.providers)
            provider = self.providers[provider_index]

            # Skip providers with too many recent failures
            failure_count = self.provider_failures.get(provider['name'], 0)
            if failure_count < 5:  # Allow up to 5 failures before skipping
                self.current_provider_index = (provider_index + 1) % len(self.providers)
                return provider

        # If all providers are failing, use the first one anyway
        self.current_provider_index = 0
        return self.providers[0]

    def _record_provider_failure(self, provider_name: str, error: Exception):
        """Record provider failure for failover logic"""
        self.provider_failures[provider_name] = self.provider_failures.get(provider_name, 0) + 1
        print(f"Geolocation provider {provider_name} failed: {error}")

    def _parse_ipapi_response(self, data: dict) -> dict:
        """Parse response from ipapi.co"""
        return {
            'ip': data.get('ip'),
            'country_code': data.get('country_code'),
            'country_name': data.get('country_name'),
            'region': data.get('region'),
            'city': data.get('city'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'timezone': data.get('timezone'),
            'isp': data.get('org'),
            'provider': 'ipapi.co'
        }

    def _parse_ipapi_com_response(self, data: dict) -> dict:
        """Parse response from ip-api.com"""
        if data.get('status') == 'fail':
            raise Exception(f"API Error: {data.get('message', 'Unknown error')}")

        return {
            'ip': data.get('query'),
            'country_code': data.get('countryCode'),
            'country_name': data.get('country'),
            'region': data.get('regionName'),
            'city': data.get('city'),
            'latitude': data.get('lat'),
            'longitude': data.get('lon'),
            'timezone': data.get('timezone'),
            'isp': data.get('isp'),
            'provider': 'ip-api.com'
        }

    def _parse_ipinfo_response(self, data: dict) -> dict:
        """Parse response from ipinfo.io"""
        # Parse location coordinates if available
        loc_parts = data.get('loc', '').split(',')
        latitude = float(loc_parts[0]) if len(loc_parts) > 0 and loc_parts[0] else None
        longitude = float(loc_parts[1]) if len(loc_parts) > 1 and loc_parts[1] else None

        return {
            'ip': data.get('ip'),
            'country_code': data.get('country'),
            'country_name': self._get_country_name_from_code(data.get('country')),
            'region': data.get('region'),
            'city': data.get('city'),
            'latitude': latitude,
            'longitude': longitude,
            'timezone': data.get('timezone'),
            'isp': data.get('org'),
            'provider': 'ipinfo.io'
        }

    def _get_country_name_from_code(self, country_code: str) -> Optional[str]:
        """Convert country code to country name (basic mapping)"""
        if not country_code:
            return None

        # Basic country code to name mapping
        country_mapping = {
            'US': 'United States',
            'GB': 'United Kingdom',
            'CA': 'Canada',
            'AU': 'Australia',
            'DE': 'Germany',
            'FR': 'France',
            'IT': 'Italy',
            'ES': 'Spain',
            'NL': 'Netherlands',
            'JP': 'Japan',
            'CN': 'China',
            'IN': 'India',
            'BR': 'Brazil',
            'MX': 'Mexico',
            'RU': 'Russia'
        }

        return country_mapping.get(country_code, country_code)

    def _get_fallback_data(self, ip_address: str, error: str = None) -> dict:
        """
        Return fallback data when geolocation fails
        """
        return {
            'ip': ip_address,
            'country_code': None,
            'country_name': 'Unknown',
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': None,
            'provider': 'fallback',
            'error': error
        }

    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring"""
        return {
            'cache_size': len(self.cache),
            'provider_failures': self.provider_failures.copy(),
            'current_provider': self.providers[self.current_provider_index]['name']
        }


# Singleton instance for global use
geolocation_client = GeolocationClient()


async def get_ip_location(ip_address: str) -> dict:
    """
    Convenience function for IP geolocation

    Args:
        ip_address: IP address to lookup

    Returns:
        Location data dictionary
    """
    return await geolocation_client.get_location(ip_address)


# Performance testing utility
async def benchmark_geolocation(test_ips: list = None, iterations: int = 100) -> dict:
    """
    Benchmark geolocation service performance

    Args:
        test_ips: List of IPs to test (uses defaults if None)
        iterations: Number of iterations per IP

    Returns:
        Performance metrics
    """
    if test_ips is None:
        test_ips = ['8.8.8.8', '1.1.1.1', '208.67.222.222']

    start_time = time.perf_counter()
    results = []

    for ip in test_ips:
        for _ in range(iterations):
            ip_start = time.perf_counter()
            await get_ip_location(ip)
            ip_time = (time.perf_counter() - ip_start) * 1000
            results.append(ip_time)

    end_time = time.perf_counter()

    return {
        'total_requests': len(results),
        'total_time_ms': (end_time - start_time) * 1000,
        'avg_time_ms': sum(results) / len(results),
        'min_time_ms': min(results),
        'max_time_ms': max(results),
        'cache_stats': geolocation_client.get_cache_stats()
    }


if __name__ == "__main__":
    # Quick test
    import asyncio

    async def test_geolocation():
        print("< Testing Geolocation Service")
        print("=" * 40)

        test_ips = ['8.8.8.8', '1.1.1.1', 'invalid-ip']

        for ip in test_ips:
            start_time = time.perf_counter()
            result = await get_ip_location(ip)
            elapsed = (time.perf_counter() - start_time) * 1000

            print(f"\n= IP: {ip}")
            print(f"   Country: {result.get('country_name', 'Unknown')}")
            print(f"   City: {result.get('city', 'Unknown')}")
            print(f"   Provider: {result.get('provider', 'Unknown')}")
            print(f"   Time: {elapsed:.2f}ms")

        # Performance benchmark
