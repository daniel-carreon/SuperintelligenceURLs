"""
Temporal Features Extractor
Extracts time-based features for analytics and predictive models
"""

from datetime import datetime, timezone
from typing import Dict, Any
import hashlib


class TemporalFeaturesExtractor:
    """
    Extract temporal features from timestamps for pattern analysis

    Features extracted:
    - hour_of_day (0-23)
    - day_of_week (0=Monday, 6=Sunday)
    - is_weekend (Saturday/Sunday)
    - week_of_year
    - month (1-12)
    - time_since_creation_seconds
    """

    def __init__(self):
        pass

    def extract_features(
        self,
        timestamp: datetime,
        creation_timestamp: datetime = None
    ) -> Dict[str, Any]:
        """
        Extract all temporal features from a timestamp

        Args:
            timestamp: The click timestamp
            creation_timestamp: When the URL was created (optional)

        Returns:
            dict: {
                'hour_of_day': int (0-23),
                'day_of_week': int (0-6, Monday=0),
                'is_weekend': bool,
                'week_of_year': int,
                'month': int (1-12),
                'time_since_creation_seconds': int
            }
        """
        # Ensure timestamp is timezone-aware (UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        features = {
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.weekday(),  # 0=Monday, 6=Sunday
            'is_weekend': timestamp.weekday() >= 5,  # Saturday=5, Sunday=6
            'week_of_year': timestamp.isocalendar()[1],
            'month': timestamp.month,
            'time_since_creation_seconds': None
        }

        # Calculate time since creation if provided
        if creation_timestamp:
            if creation_timestamp.tzinfo is None:
                creation_timestamp = creation_timestamp.replace(tzinfo=timezone.utc)

            time_diff = timestamp - creation_timestamp
            features['time_since_creation_seconds'] = int(time_diff.total_seconds())

        return features

    def get_time_bucket(
        self,
        timestamp: datetime,
        bucket_size_minutes: int = 30
    ) -> str:
        """
        Get time bucket for grouping similar timestamps

        Used for session tracking (same user within 30 mins = same session)

        Args:
            timestamp: The timestamp to bucket
            bucket_size_minutes: Size of time bucket in minutes

        Returns:
            str: Time bucket identifier (e.g., "2025-10-02_14:00")
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Round down to nearest bucket
        bucket_start = timestamp.replace(
            minute=(timestamp.minute // bucket_size_minutes) * bucket_size_minutes,
            second=0,
            microsecond=0
        )

        return bucket_start.strftime("%Y-%m-%d_%H:%M")

    def is_peak_hour(self, hour: int) -> bool:
        """
        Check if hour is a peak engagement hour

        Peak hours (based on typical YouTube engagement):
        - Morning: 6-9 AM
        - Lunch: 12-2 PM
        - Evening: 6-11 PM
        """
        return hour in [6, 7, 8, 9, 12, 13, 18, 19, 20, 21, 22, 23]

    def get_day_part(self, hour: int) -> str:
        """
        Get part of day category

        Categories:
        - night: 0-5 AM
        - morning: 6-11 AM
        - afternoon: 12-5 PM
        - evening: 6-11 PM
        """
        if 0 <= hour < 6:
            return 'night'
        elif 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'

    def get_week_type(self, day_of_week: int) -> str:
        """
        Get week type (weekday vs weekend)

        Args:
            day_of_week: 0=Monday, 6=Sunday

        Returns:
            str: "weekend" or "weekday"
        """
        return 'weekend' if day_of_week >= 5 else 'weekday'


class SessionTracker:
    """
    Track user sessions for journey analytics

    Session = unique combination of IP + User-Agent + Time Window
    """

    def __init__(self, time_window_minutes: int = 30):
        self.time_window_minutes = time_window_minutes
        self.sessions_cache = {}  # {session_id: {'first_seen': datetime, 'click_count': int}}

    def generate_session_id(
        self,
        ip_address: str,
        user_agent: str,
        timestamp: datetime
    ) -> str:
        """
        Generate session ID based on IP + User-Agent + Time Window

        Same user within time window = same session

        Args:
            ip_address: User IP address
            user_agent: User agent string
            timestamp: Current timestamp

        Returns:
            str: Session ID (16-char hex)
        """
        if not ip_address or not user_agent:
            return None

        # Get time bucket
        time_bucket = self._get_time_bucket(timestamp)

        # Create session key
        session_key = f"{ip_address}_{user_agent}_{time_bucket}"

        # Generate hash
        session_hash = hashlib.sha256(session_key.encode()).hexdigest()[:16]

        return session_hash

    def _get_time_bucket(self, timestamp: datetime) -> str:
        """Get time bucket for session grouping"""
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Round down to nearest window
        bucket_minutes = (timestamp.minute // self.time_window_minutes) * self.time_window_minutes
        bucket_start = timestamp.replace(minute=bucket_minutes, second=0, microsecond=0)

        return bucket_start.strftime("%Y%m%d%H%M")

    def is_new_session(self, session_id: str) -> bool:
        """
        Check if this is a new session (first click)

        Args:
            session_id: Session identifier

        Returns:
            bool: True if new session, False if existing
        """
        return session_id not in self.sessions_cache

    def track_session_click(
        self,
        session_id: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Track a click in a session

        Args:
            session_id: Session identifier
            timestamp: Click timestamp

        Returns:
            dict: {
                'is_first_click': bool,
                'clicks_in_session': int,
                'session_duration_seconds': int
            }
        """
        if session_id not in self.sessions_cache:
            # New session
            self.sessions_cache[session_id] = {
                'first_seen': timestamp,
                'click_count': 1,
                'last_seen': timestamp
            }

            return {
                'is_first_click': True,
                'clicks_in_session': 1,
                'session_duration_seconds': 0
            }
        else:
            # Existing session
            session = self.sessions_cache[session_id]
            session['click_count'] += 1
            session['last_seen'] = timestamp

            duration = (timestamp - session['first_seen']).total_seconds()

            return {
                'is_first_click': False,
                'clicks_in_session': session['click_count'],
                'session_duration_seconds': int(duration)
            }

    def cleanup_old_sessions(self, hours: int = 24):
        """
        Remove sessions older than X hours to prevent memory bloat

        Args:
            hours: Age threshold in hours
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        sessions_to_remove = [
            session_id
            for session_id, data in self.sessions_cache.items()
            if data['last_seen'] < cutoff_time
        ]

        for session_id in sessions_to_remove:
            del self.sessions_cache[session_id]

        return len(sessions_to_remove)


# Singleton instances
temporal_extractor = TemporalFeaturesExtractor()
session_tracker = SessionTracker(time_window_minutes=30)


# Convenience functions
def extract_temporal_features(
    timestamp: datetime,
    creation_timestamp: datetime = None
) -> Dict[str, Any]:
    """
    Extract temporal features from timestamp

    Args:
        timestamp: Click timestamp
        creation_timestamp: URL creation timestamp (optional)

    Returns:
        dict: Temporal features for analytics
    """
    return temporal_extractor.extract_features(timestamp, creation_timestamp)


def generate_session_id(
    ip_address: str,
    user_agent: str,
    timestamp: datetime
) -> str:
    """
    Generate session ID for click tracking

    Args:
        ip_address: User IP
        user_agent: User agent string
        timestamp: Click timestamp

    Returns:
        str: Session ID
    """
    return session_tracker.generate_session_id(ip_address, user_agent, timestamp)


def track_session(
    session_id: str,
    timestamp: datetime
) -> Dict[str, Any]:
    """
    Track session click and return session metrics

    Args:
        session_id: Session identifier
        timestamp: Click timestamp

    Returns:
        dict: Session metrics
    """
    return session_tracker.track_session_click(session_id, timestamp)


# ========================================
# Testing & Examples
# ========================================

if __name__ == "__main__":
    from datetime import timedelta

    print("⏰ Testing Temporal Features Extractor\n")

    # Test 1: Extract features
    now = datetime.now(timezone.utc)
    created = now - timedelta(hours=2)

    features = extract_temporal_features(now, created)
    print("Temporal Features:")
    for key, value in features.items():
        print(f"   {key}: {value}")
    print()

    # Test 2: Peak hour detection
    print("Peak Hour Detection:")
    for hour in [8, 12, 15, 19, 23, 2]:
        is_peak = temporal_extractor.is_peak_hour(hour)
        day_part = temporal_extractor.get_day_part(hour)
        print(f"   {hour:02d}:00 → Peak: {is_peak}, Part: {day_part}")
    print()

    # Test 3: Session tracking
    print("Session Tracking:")
    ip = "192.168.1.1"
    ua = "Mozilla/5.0 (iPhone)"

    session_id = generate_session_id(ip, ua, now)
    print(f"   Session ID: {session_id}")

    # Simulate clicks in same session
    for i in range(3):
        click_time = now + timedelta(minutes=i*5)
        metrics = track_session(session_id, click_time)
        print(f"   Click {i+1}: {metrics}")
    print()

    # Test 4: New session (different time window)
    later = now + timedelta(hours=1)
    new_session_id = generate_session_id(ip, ua, later)
    print(f"   New Session ID: {new_session_id}")
    print(f"   Different from first: {new_session_id != session_id}")
