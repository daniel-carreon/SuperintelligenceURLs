"""
Advanced User Agent Parser
Comprehensive device, browser, and OS detection from user agent strings
"""

import re
from typing import Dict, Optional
from user_agents import parse as ua_parse


class UserAgentParser:
    """
    Advanced user agent parser with comprehensive device detection
    Provides detailed browser, OS, and device information
    """

    def __init__(self):
        # Common bot patterns for enhanced bot detection
        self.bot_patterns = [
            r'bot', r'crawler', r'spider', r'scraper', r'fetcher',
            r'googlebot', r'bingbot', r'facebookexternalhit',
            r'twitterbot', r'linkedinbot', r'slackbot',
            r'whatsapp', r'telegram', r'curl', r'wget',
            r'postman', r'insomnia', r'httpie'
        ]

        # Device type detection patterns
        self.mobile_patterns = [
            r'mobile', r'android', r'iphone', r'ipod', r'blackberry',
            r'windows phone', r'symbian', r'palm', r'webos'
        ]

        self.tablet_patterns = [
            r'ipad', r'tablet', r'kindle', r'nook', r'playbook'
        ]

        self.desktop_patterns = [
            r'windows nt', r'macintosh', r'linux', r'ubuntu',
            r'debian', r'fedora', r'chrome os'
        ]

        self.tv_patterns = [
            r'smart-tv', r'smarttv', r'tv', r'roku', r'chromecast',
            r'apple tv', r'android tv', r'fire tv'
        ]

        # Compile patterns for better performance
        self.compiled_bot_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.bot_patterns]

    def parse_user_agent(self, user_agent_string: str) -> dict:
        """
        Parse user agent string into detailed device information

        Args:
            user_agent_string: Raw user agent string

        Returns:
            Dictionary with parsed device information
        """
        if not user_agent_string:
            return self._get_unknown_device()

        # Use user_agents library for initial parsing
        try:
            parsed_ua = ua_parse(user_agent_string)

            # Extract basic information
            browser_info = self._extract_browser_info(parsed_ua)
            os_info = self._extract_os_info(parsed_ua)
            device_info = self._extract_device_info(parsed_ua, user_agent_string)

            # Enhanced device type detection
            device_type = self._detect_device_type(user_agent_string, parsed_ua)

            # Bot detection
            is_bot = self._is_bot(user_agent_string)

            return {
                'user_agent': user_agent_string,
                'is_bot': is_bot,
                'device_type': 'bot' if is_bot else device_type,
                'device_brand': device_info.get('brand'),
                'device_model': device_info.get('model'),
                'browser_name': browser_info.get('name'),
                'browser_version': browser_info.get('version'),
                'browser_family': browser_info.get('family'),
                'os_name': os_info.get('name'),
                'os_version': os_info.get('version'),
                'os_family': os_info.get('family'),
                'is_mobile': device_type in ['mobile', 'tablet'],
                'is_tablet': device_type == 'tablet',
                'is_desktop': device_type == 'desktop',
                'is_tv': device_type == 'tv'
            }

        except Exception as e:
            print(f"Error parsing user agent: {e}")
            return self._get_unknown_device(user_agent_string)

    def _extract_browser_info(self, parsed_ua) -> dict:
        """Extract browser information from parsed user agent"""
        return {
            'name': parsed_ua.browser.family if parsed_ua.browser else 'Unknown',
            'version': parsed_ua.browser.version_string if parsed_ua.browser else None,
            'family': parsed_ua.browser.family if parsed_ua.browser else 'Unknown'
        }

    def _extract_os_info(self, parsed_ua) -> dict:
        """Extract operating system information from parsed user agent"""
        return {
            'name': parsed_ua.os.family if parsed_ua.os else 'Unknown',
            'version': parsed_ua.os.version_string if parsed_ua.os else None,
            'family': parsed_ua.os.family if parsed_ua.os else 'Unknown'
        }

    def _extract_device_info(self, parsed_ua, user_agent_string: str) -> dict:
        """Extract device information from parsed user agent"""
        device_brand = None
        device_model = None

        if parsed_ua.device:
            device_brand = parsed_ua.device.brand
            device_model = parsed_ua.device.model

        # Enhanced device detection for better accuracy
        if not device_brand or device_brand == 'Other':
            device_brand = self._detect_device_brand(user_agent_string)

        return {
            'brand': device_brand,
            'model': device_model
        }

    def _detect_device_type(self, user_agent_string: str, parsed_ua) -> str:
        """
        Detect device type with enhanced accuracy
        """
        user_agent_lower = user_agent_string.lower()

        # Check for TV first (most specific)
        if any(re.search(pattern, user_agent_lower) for pattern in self.tv_patterns):
            return 'tv'

        # Check parsed device type first
        if parsed_ua.device and hasattr(parsed_ua.device, 'family'):
            if parsed_ua.device.family.lower() in ['tablet', 'ipad']:
                return 'tablet'
            elif parsed_ua.device.family.lower() in ['smartphone', 'mobile']:
                return 'mobile'

        # Check for tablet patterns
        if any(re.search(pattern, user_agent_lower) for pattern in self.tablet_patterns):
            return 'tablet'

        # Check for mobile patterns
        if any(re.search(pattern, user_agent_lower) for pattern in self.mobile_patterns):
            return 'mobile'

        # Check for desktop patterns
        if any(re.search(pattern, user_agent_lower) for pattern in self.desktop_patterns):
            return 'desktop'

        # Default fallback based on OS
        if parsed_ua.os:
            os_family = parsed_ua.os.family.lower()
            if 'android' in os_family or 'ios' in os_family:
                return 'mobile'  # Default mobile for mobile OS
            elif any(desktop_os in os_family for desktop_os in ['windows', 'mac', 'linux']):
                return 'desktop'

        return 'unknown'

    def _detect_device_brand(self, user_agent_string: str) -> Optional[str]:
        """
        Enhanced device brand detection
        """
        user_agent_lower = user_agent_string.lower()

        # Brand patterns
        brand_patterns = {
            'Apple': [r'iphone', r'ipad', r'ipod', r'macintosh', r'mac os'],
            'Samsung': [r'samsung', r'galaxy', r'sm-'],
            'Google': [r'pixel', r'nexus', r'chromebook'],
            'Microsoft': [r'windows phone', r'surface', r'xbox'],
            'Amazon': [r'kindle', r'fire tv', r'echo'],
            'Sony': [r'playstation', r'xperia'],
            'LG': [r'lg-'],
            'HTC': [r'htc'],
            'Motorola': [r'motorola', r'moto'],
            'Xiaomi': [r'xiaomi', r'mi ', r'redmi'],
            'Huawei': [r'huawei'],
            'OnePlus': [r'oneplus'],
            'Nokia': [r'nokia']
        }

        for brand, patterns in brand_patterns.items():
            if any(re.search(pattern, user_agent_lower) for pattern in patterns):
                return brand

        return None

    def _is_bot(self, user_agent_string: str) -> bool:
        """
        Enhanced bot detection using multiple patterns
        """
        if not user_agent_string:
            return False

        # Check against compiled bot patterns
        return any(pattern.search(user_agent_string) for pattern in self.compiled_bot_patterns)

    def _get_unknown_device(self, user_agent_string: str = None) -> dict:
        """
        Return default data for unknown devices
        """
        return {
            'user_agent': user_agent_string,
            'is_bot': False,
            'device_type': 'unknown',
            'device_brand': None,
            'device_model': None,
            'browser_name': 'Unknown',
            'browser_version': None,
            'browser_family': 'Unknown',
            'os_name': 'Unknown',
            'os_version': None,
            'os_family': 'Unknown',
            'is_mobile': False,
            'is_tablet': False,
            'is_desktop': False,
            'is_tv': False
        }


# Singleton instance for global use
user_agent_parser = UserAgentParser()


def parse_user_agent(user_agent_string: str) -> dict:
    """
    Convenience function for user agent parsing

    Args:
        user_agent_string: User agent string to parse

    Returns:
        Parsed device information dictionary
    """
    return user_agent_parser.parse_user_agent(user_agent_string)


def get_device_summary(user_agent_string: str) -> str:
    """
    Convenience function for device summary

    Args:
        user_agent_string: User agent string to parse

    Returns:
        Human-readable device description
    """
    parsed = user_agent_parser.parse_user_agent(user_agent_string)

    if parsed['is_bot']:
        return f"Bot ({parsed['browser_name']})"

    device_parts = []

    # Device type and brand
    if parsed['device_brand']:
        device_parts.append(f"{parsed['device_brand']} {parsed['device_type']}")
    else:
        device_parts.append(parsed['device_type'].title())

    # Browser
    if parsed['browser_name'] != 'Unknown':
        browser_info = parsed['browser_name']
        if parsed['browser_version']:
            browser_info += f" {parsed['browser_version']}"
        device_parts.append(browser_info)

    # OS
    if parsed['os_name'] != 'Unknown':
        os_info = parsed['os_name']
        if parsed['os_version']:
            os_info += f" {parsed['os_version']}"
        device_parts.append(os_info)

    return " | ".join(device_parts) if device_parts else "Unknown Device"


# Analytics helper functions
def categorize_device_for_analytics(parsed_device: dict) -> str:
    """
    Categorize device for analytics dashboards
    """
    if parsed_device['is_bot']:
        return 'bot'
    elif parsed_device['is_tablet']:
        return 'tablet'
    elif parsed_device['is_mobile']:
        return 'mobile'
    elif parsed_device['is_desktop']:
        return 'desktop'
    elif parsed_device['is_tv']:
        return 'tv'
    else:
        return 'unknown'


def get_browser_category(parsed_device: dict) -> str:
    """
    Get simplified browser category for analytics
    """
    browser_name = parsed_device.get('browser_name', '').lower()

    if 'chrome' in browser_name:
        return 'Chrome'
    elif 'firefox' in browser_name:
        return 'Firefox'
    elif 'safari' in browser_name:
        return 'Safari'
    elif 'edge' in browser_name:
        return 'Edge'
    elif 'opera' in browser_name:
        return 'Opera'
    elif 'internet explorer' in browser_name or 'ie' in browser_name:
        return 'Internet Explorer'
    else:
        return 'Other'


if __name__ == "__main__":
    # Quick test
    test_user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0"
    ]

    print("User Agent Parser Test")
    print("=" * 50)

    for ua in test_user_agents:
        result = parse_user_agent(ua)
        summary = get_device_summary(ua)

        print(f"\nUser Agent: {ua[:50]}...")
        print(f"Summary: {summary}")
        print(f"Device Type: {result['device_type']}")
        print(f"Is Bot: {result['is_bot']}")
        print(f"Browser: {result['browser_name']} {result['browser_version'] or ''}")
        print(f"OS: {result['os_name']} {result['os_version'] or ''}")

    print("\nUser Agent Parser test completed!")