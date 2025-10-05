"""
YouTube Metadata Client
Extracts video ID and fetches metadata from YouTube
Supports both API mode (with YouTube Data API key) and fallback mode
"""

import re
from typing import Optional, Dict
from urllib.parse import urlparse, parse_qs


class YouTubeMetadataClient:
    """
    Client for fetching YouTube video metadata
    Works in two modes:
    1. API mode: Uses YouTube Data API v3 (requires API key)
    2. Fallback mode: Extracts video ID and uses default thumbnail URLs
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube metadata client

        Args:
            api_key: YouTube Data API v3 key (optional)
        """
        self.api_key = api_key
        self.youtube_patterns = {
            'standard': r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})',
            'short': r'youtu\.be/([A-Za-z0-9_-]{11})',
            'embed': r'youtube\.com/embed/([A-Za-z0-9_-]{11})',
            'shorts': r'youtube\.com/shorts/([A-Za-z0-9_-]{11})'
        }

    def extract_video_id(self, youtube_url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats

        Args:
            youtube_url: YouTube video URL

        Returns:
            Video ID (11 characters) or None if invalid

        Examples:
            https://www.youtube.com/watch?v=dQw4w9WgXcQ -> dQw4w9WgXcQ
            https://youtu.be/dQw4w9WgXcQ -> dQw4w9WgXcQ
            https://www.youtube.com/embed/dQw4w9WgXcQ -> dQw4w9WgXcQ
            https://www.youtube.com/shorts/dQw4w9WgXcQ -> dQw4w9WgXcQ
        """
        if not youtube_url:
            return None

        try:
            # Parse URL
            parsed = urlparse(youtube_url)

            # Handle youtube.com/watch?v=VIDEO_ID
            if 'youtube.com' in parsed.netloc and parsed.path == '/watch':
                query_params = parse_qs(parsed.query)
                if 'v' in query_params:
                    return query_params['v'][0]

            # Try all YouTube patterns
            for pattern_name, pattern in self.youtube_patterns.items():
                match = re.search(pattern, youtube_url)
                if match:
                    return match.group(1)

            return None

        except Exception as e:
            print(f"Error extracting YouTube video ID: {e}")
            return None

    def get_thumbnail_url(self, video_id: str, quality: str = 'maxresdefault') -> str:
        """
        Get YouTube video thumbnail URL

        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality (maxresdefault, sddefault, hqdefault, mqdefault, default)

        Returns:
            Thumbnail URL

        Note:
            YouTube provides predictable thumbnail URLs without API:
            - maxresdefault: 1280x720 (best quality, may not exist for old videos)
            - sddefault: 640x480
            - hqdefault: 480x360
            - mqdefault: 320x180
            - default: 120x90
        """
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"

    async def get_video_metadata(self, youtube_url: str) -> Dict[str, Optional[str]]:
        """
        Get video metadata from YouTube URL

        Args:
            youtube_url: YouTube video URL

        Returns:
            Dictionary with metadata:
            - video_id: YouTube video ID
            - title: Video title (None in fallback mode, user must provide)
            - thumbnail_url: Video thumbnail URL
            - description: Video description (None in fallback mode)

        Note:
            In fallback mode (no API key), only video_id and thumbnail_url are available.
            User must manually enter the title.
        """
        # Extract video ID
        video_id = self.extract_video_id(youtube_url)

        if not video_id:
            return {
                'video_id': None,
                'title': None,
                'thumbnail_url': None,
                'description': None
            }

        # Get thumbnail URL (works without API)
        thumbnail_url = self.get_thumbnail_url(video_id, quality='maxresdefault')

        # If API key is available, fetch metadata from YouTube Data API
        if self.api_key:
            try:
                # TODO: Implement YouTube Data API v3 call
                # For now, return fallback mode
                pass
            except Exception as e:
                print(f"YouTube API call failed: {e}")

        # Fallback mode: Return video ID and thumbnail URL
        # User must manually enter title
        return {
            'video_id': video_id,
            'title': None,  # User must provide title manually
            'thumbnail_url': thumbnail_url,
            'description': None
        }

    def validate_youtube_url(self, url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL

        Args:
            url: URL to validate

        Returns:
            True if valid YouTube URL, False otherwise
        """
        video_id = self.extract_video_id(url)
        return video_id is not None


# Singleton instance (without API key by default)
youtube_metadata_client = YouTubeMetadataClient(api_key=None)


async def get_youtube_metadata(youtube_url: str) -> Dict[str, Optional[str]]:
    """
    Convenience function for getting YouTube metadata

    Args:
        youtube_url: YouTube video URL

    Returns:
        Dictionary with video metadata
    """
    return await youtube_metadata_client.get_video_metadata(youtube_url)


def extract_youtube_video_id(youtube_url: str) -> Optional[str]:
    """
    Convenience function for extracting YouTube video ID

    Args:
        youtube_url: YouTube video URL

    Returns:
        Video ID or None
    """
    return youtube_metadata_client.extract_video_id(youtube_url)


if __name__ == "__main__":
    # Test YouTube metadata client
    import asyncio

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/abc123XYZ_-",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://google.com"  # Invalid
    ]

    print("YouTube Metadata Client Test")
    print("=" * 50)

    for url in test_urls:
        print(f"\nURL: {url}")

        # Extract video ID
        video_id = extract_youtube_video_id(url)
        print(f"Video ID: {video_id}")

        # Get metadata
        metadata = asyncio.run(get_youtube_metadata(url))
        print(f"Metadata: {metadata}")

    print("\n" + "=" * 50)
    print("YouTube metadata client test completed!")
