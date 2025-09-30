"""
Video Attribution Parser
Extracts video platform and video ID from referrer URLs
Supports YouTube, TikTok, Instagram, Twitter/X, LinkedIn
"""

import re
from typing import Optional, Dict
from urllib.parse import urlparse, parse_qs


class VideoAttributionParser:
    """
    Parse referrer URLs to extract video platform and video ID
    Useful for tracking which videos drive traffic to shortened links
    """

    def __init__(self):
        # YouTube patterns
        self.youtube_patterns = {
            'standard': r'youtube\.com/watch\?v=([A-Za-z0-9_-]+)',
            'short': r'youtu\.be/([A-Za-z0-9_-]+)',
            'embed': r'youtube\.com/embed/([A-Za-z0-9_-]+)',
            'shorts': r'youtube\.com/shorts/([A-Za-z0-9_-]+)'
        }

        # TikTok patterns
        self.tiktok_patterns = {
            'video': r'tiktok\.com/@[\w.-]+/video/(\d+)',
            'vm': r'vm\.tiktok\.com/([A-Za-z0-9]+)',
            'vt': r'vt\.tiktok\.com/([A-Za-z0-9]+)'
        }

        # Instagram patterns
        self.instagram_patterns = {
            'reel': r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            'p': r'instagram\.com/p/([A-Za-z0-9_-]+)',
            'tv': r'instagram\.com/tv/([A-Za-z0-9_-]+)'
        }

        # Twitter/X patterns
        self.twitter_patterns = {
            'status': r'twitter\.com/\w+/status/(\d+)',
            'x_status': r'x\.com/\w+/status/(\d+)'
        }

        # LinkedIn patterns
        self.linkedin_patterns = {
            'posts': r'linkedin\.com/posts/[\w-]+_([a-zA-Z0-9]+)',
            'feed': r'linkedin\.com/feed/update/urn:li:activity:(\d+)'
        }

    def parse_referrer(self, referrer_url: Optional[str]) -> Dict[str, Optional[str]]:
        """
        Parse referrer URL to extract video platform and ID

        Args:
            referrer_url: The HTTP referrer URL

        Returns:
            Dictionary with 'video_platform' and 'video_id'
        """
        if not referrer_url:
            return {'video_platform': None, 'video_id': None}

        try:
            # Parse URL
            parsed = urlparse(referrer_url)
            domain = parsed.netloc.lower()
            full_url = referrer_url.lower()

            # Check YouTube
            if 'youtube.com' in domain or 'youtu.be' in domain:
                video_id = self._extract_youtube_id(full_url, parsed)
                if video_id:
                    return {'video_platform': 'youtube', 'video_id': video_id}

            # Check TikTok
            if 'tiktok.com' in domain:
                video_id = self._extract_tiktok_id(full_url)
                if video_id:
                    return {'video_platform': 'tiktok', 'video_id': video_id}

            # Check Instagram
            if 'instagram.com' in domain:
                video_id = self._extract_instagram_id(full_url)
                if video_id:
                    return {'video_platform': 'instagram', 'video_id': video_id}

            # Check Twitter/X
            if 'twitter.com' in domain or 'x.com' in domain:
                video_id = self._extract_twitter_id(full_url)
                if video_id:
                    return {'video_platform': 'twitter', 'video_id': video_id}

            # Check LinkedIn
            if 'linkedin.com' in domain:
                video_id = self._extract_linkedin_id(full_url)
                if video_id:
                    return {'video_platform': 'linkedin', 'video_id': video_id}

            # Not a video platform
            return {'video_platform': None, 'video_id': None}

        except Exception as e:
            print(f"Error parsing video referrer: {e}")
            return {'video_platform': None, 'video_id': None}

    def _extract_youtube_id(self, url: str, parsed_url) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        # Try standard watch URL
        if 'youtube.com/watch' in url:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]

        # Try all YouTube patterns
        for pattern_name, pattern in self.youtube_patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _extract_tiktok_id(self, url: str) -> Optional[str]:
        """Extract TikTok video ID"""
        for pattern_name, pattern in self.tiktok_patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_instagram_id(self, url: str) -> Optional[str]:
        """Extract Instagram video/post ID"""
        for pattern_name, pattern in self.instagram_patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_twitter_id(self, url: str) -> Optional[str]:
        """Extract Twitter/X tweet ID"""
        for pattern_name, pattern in self.twitter_patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_linkedin_id(self, url: str) -> Optional[str]:
        """Extract LinkedIn post ID"""
        for pattern_name, pattern in self.linkedin_patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_url(self, platform: str, video_id: str) -> Optional[str]:
        """
        Reconstruct video URL from platform and ID

        Args:
            platform: Video platform name
            video_id: Video identifier

        Returns:
            Full video URL
        """
        url_templates = {
            'youtube': f'https://youtube.com/watch?v={video_id}',
            'tiktok': f'https://tiktok.com/video/{video_id}',
            'instagram': f'https://instagram.com/p/{video_id}',
            'twitter': f'https://twitter.com/i/status/{video_id}',
            'linkedin': f'https://linkedin.com/feed/update/urn:li:activity:{video_id}'
        }

        return url_templates.get(platform)


# Singleton instance
video_attribution_parser = VideoAttributionParser()


def parse_video_referrer(referrer_url: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Convenience function for parsing video referrers

    Args:
        referrer_url: The HTTP referrer URL

    Returns:
        Dictionary with video_platform and video_id
    """
    return video_attribution_parser.parse_referrer(referrer_url)


if __name__ == "__main__":
    # Test video attribution parser
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/abc123XYZ",
        "https://www.tiktok.com/@username/video/1234567890",
        "https://www.instagram.com/reel/CxYz123abc/",
        "https://twitter.com/user/status/1234567890123456789",
        "https://www.linkedin.com/posts/username_activity-7123456789",
        "https://google.com"  # Not a video platform
    ]

    print("Video Attribution Parser Test")
    print("=" * 50)

    for url in test_urls:
        result = parse_video_referrer(url)
        print(f"\nURL: {url}")
        print(f"Platform: {result['video_platform']}")
        print(f"Video ID: {result['video_id']}")

    print("\n" + "=" * 50)
    print("Video Attribution Parser test completed!")