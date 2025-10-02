"""
YouTube URL Parser
Extracts video metadata from YouTube URLs for analytics
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import re


class YouTubeParser:
    """
    Parse YouTube URLs to extract video metadata for analytics

    Supported URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - With params: ?t=120, &list=PLAYLIST, &index=3, &feature=share
    """

    # YouTube URL patterns
    YOUTUBE_DOMAINS = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']

    # Video ID regex patterns
    VIDEO_ID_PATTERNS = [
        r'(?:v=|/)([A-Za-z0-9_-]{11})(?:[&?]|$)',  # Standard format
        r'(?:embed/)([A-Za-z0-9_-]{11})',           # Embed format
        r'^([A-Za-z0-9_-]{11})$'                     # Direct ID
    ]

    def __init__(self):
        self.cache = {}  # Simple cache for repeated URLs

    def is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube URL"""
        if not url:
            return False

        try:
            parsed = urlparse(url)
            return any(domain in parsed.netloc for domain in self.YOUTUBE_DOMAINS)
        except Exception:
            return False

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL

        Examples:
            https://www.youtube.com/watch?v=dQw4w9WgXcQ → "dQw4w9WgXcQ"
            https://youtu.be/dQw4w9WgXcQ → "dQw4w9WgXcQ"
            https://www.youtube.com/embed/dQw4w9WgXcQ → "dQw4w9WgXcQ"
        """
        if not url:
            return None

        try:
            parsed = urlparse(url)

            # youtu.be short URLs
            if 'youtu.be' in parsed.netloc:
                video_id = parsed.path.lstrip('/')
                if video_id and len(video_id) == 11:
                    return video_id

            # Query parameter format
            params = parse_qs(parsed.query)
            if 'v' in params:
                video_id = params['v'][0]
                if video_id and len(video_id) == 11:
                    return video_id

            # Embed format or path-based
            for pattern in self.VIDEO_ID_PATTERNS:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    if len(video_id) == 11:
                        return video_id

            return None

        except Exception as e:
            print(f"Error extracting video ID from {url}: {e}")
            return None

    def parse_url(self, url: str) -> Dict[str, Any]:
        """
        Parse YouTube URL and extract all metadata

        Returns:
            dict: {
                'video_id': str,
                'video_timestamp': int,
                'playlist_id': str,
                'yt_index': int,
                'yt_feature': str,
                'yt_app': str,
                'yt_list': str,
                'is_youtube': bool
            }
        """
        # Check cache first
        if url in self.cache:
            return self.cache[url]

        result = {
            'video_id': None,
            'video_timestamp': 0,
            'playlist_id': None,
            'yt_index': None,
            'yt_feature': None,
            'yt_app': None,
            'yt_list': None,
            'is_youtube': False
        }

        if not self.is_youtube_url(url):
            self.cache[url] = result
            return result

        result['is_youtube'] = True

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # Extract video ID
            result['video_id'] = self.extract_video_id(url)

            # Extract timestamp (t parameter in seconds)
            if 't' in params:
                try:
                    time_value = params['t'][0]
                    # Handle formats: "120", "2m", "1h30m"
                    result['video_timestamp'] = self._parse_timestamp(time_value)
                except Exception:
                    result['video_timestamp'] = 0

            # Extract playlist info
            if 'list' in params:
                result['playlist_id'] = params['list'][0]
                result['yt_list'] = params['list'][0]

            # Extract playlist index
            if 'index' in params:
                try:
                    result['yt_index'] = int(params['index'][0])
                except Exception:
                    result['yt_index'] = None

            # Extract YouTube feature
            if 'feature' in params:
                result['yt_feature'] = params['feature'][0]

            # Extract app type
            if 'app' in params:
                result['yt_app'] = params['app'][0]
            elif 'm.youtube.com' in parsed.netloc:
                result['yt_app'] = 'mobile_web'
            elif 'youtube.com' in parsed.netloc:
                result['yt_app'] = 'web'

            # Cache result
            self.cache[url] = result

        except Exception as e:
            print(f"Error parsing YouTube URL {url}: {e}")

        return result

    def _parse_timestamp(self, time_str: str) -> int:
        """
        Parse YouTube timestamp to seconds

        Formats:
            "120" → 120 seconds
            "2m" → 120 seconds
            "1h30m" → 5400 seconds
            "1h30m45s" → 5445 seconds
        """
        try:
            # If it's just a number, return it
            if time_str.isdigit():
                return int(time_str)

            # Parse complex format (1h30m45s)
            hours = 0
            minutes = 0
            seconds = 0

            # Extract hours
            h_match = re.search(r'(\d+)h', time_str)
            if h_match:
                hours = int(h_match.group(1))

            # Extract minutes
            m_match = re.search(r'(\d+)m', time_str)
            if m_match:
                minutes = int(m_match.group(1))

            # Extract seconds
            s_match = re.search(r'(\d+)s', time_str)
            if s_match:
                seconds = int(s_match.group(1))

            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds

        except Exception:
            return 0

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_hits': getattr(self, '_cache_hits', 0)
        }

    def clear_cache(self):
        """Clear the parser cache"""
        self.cache.clear()


# Singleton instance
youtube_parser = YouTubeParser()


def parse_youtube_url(url: str) -> Dict[str, Any]:
    """
    Convenience function to parse YouTube URL

    Args:
        url: YouTube URL to parse

    Returns:
        dict: Parsed metadata including video_id, timestamp, playlist, etc.

    Example:
        >>> parse_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120")
        {
            'video_id': 'dQw4w9WgXcQ',
            'video_timestamp': 120,
            'is_youtube': True,
            ...
        }
    """
    return youtube_parser.parse_url(url)


# ========================================
# Testing & Examples
# ========================================

if __name__ == "__main__":
    # Test cases
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxx&index=5",
        "https://youtu.be/dQw4w9WgXcQ?feature=share",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ&app=m",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.google.com",  # Non-YouTube URL
    ]

    print("🎥 Testing YouTube URL Parser\n")

    for url in test_urls:
        result = parse_youtube_url(url)
        print(f"URL: {url}")
        print(f"   Is YouTube: {result['is_youtube']}")
        if result['is_youtube']:
            print(f"   Video ID: {result['video_id']}")
            print(f"   Timestamp: {result['video_timestamp']}s")
            print(f"   Playlist: {result['playlist_id']}")
            print(f"   Feature: {result['yt_feature']}")
            print(f"   App: {result['yt_app']}")
        print()

    print(f"\n✅ Cache stats: {youtube_parser.get_cache_stats()}")
