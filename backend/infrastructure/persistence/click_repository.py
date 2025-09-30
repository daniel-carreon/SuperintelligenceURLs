"""
Click Repository - Supabase implementation
"""
from typing import Optional, List, Dict
from infrastructure.persistence.supabase_client import get_supabase


class ClickRepository:
    """Repository para operaciones de clicks en Supabase"""

    def __init__(self):
        self.client = get_supabase()
        self.table = self.client.table('clicks')

    def create(self, click_data: dict) -> dict:
        """Crear nuevo click con todos los campos avanzados"""
        response = self.table.insert(click_data).execute()
        return response.data[0] if response.data else None

    def get_by_url_id(self, url_id: str, limit: int = 1000) -> List[dict]:
        """Obtener clicks por URL"""
        response = self.table.select('*').eq('url_id', url_id).order('clicked_at', desc=True).limit(limit).execute()
        return response.data

    def get_analytics_summary(self, short_code: str) -> Dict:
        """Obtener resumen de analytics desde Supabase"""
        clicks = self.table.select('*').eq('short_code', short_code).execute().data

        if not clicks:
            return self._empty_analytics()

        # Process analytics (igual que click_tracker_service pero desde DB)
        total_clicks = len(clicks)
        unique_sessions = len(set(c['session_id'] for c in clicks if c.get('session_id')))
        returning = sum(1 for c in clicks if c.get('is_returning_visitor'))

        return {
            'total_clicks': total_clicks,
            'unique_visitors': unique_sessions,
            'returning_visitors': returning,
            'device_breakdown': self._count_field(clicks, 'device_type'),
            'country_breakdown': self._count_field(clicks, 'country_name'),
            'city_breakdown': self._count_cities(clicks),
            'platform_breakdown': self._count_field(clicks, 'platform'),
            'video_sources': self._count_videos(clicks),
            'time_patterns': self._analyze_time(clicks),
            'referrer_breakdown': self._count_field(clicks, 'referrer_type'),
            'recent_clicks': clicks[:50]  # ✅ Return last 50 clicks for table
        }

    def _count_field(self, clicks, field):
        result = {}
        for c in clicks:
            val = c.get(field) or 'Unknown'
            result[val] = result.get(val, 0) + 1
        return result

    def _count_cities(self, clicks):
        result = {}
        for c in clicks:
            if c.get('city'):
                key = f"{c['city']}, {c.get('country_code', 'XX')}"
                result[key] = result.get(key, 0) + 1
        return result

    def _count_videos(self, clicks):
        result = {}
        for c in clicks:
            if c.get('video_platform') and c.get('video_id'):
                key = f"{c['video_platform']}:{c['video_id']}"
                result[key] = result.get(key, 0) + 1
        return result

    def _analyze_time(self, clicks):
        from datetime import datetime as dt
        hours, days = {}, {}
        for c in clicks:
            if c.get('clicked_at'):
                clicked = dt.fromisoformat(c['clicked_at'].replace('Z', '+00:00'))
                hour = clicked.hour
                day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][clicked.weekday()]
                hours[hour] = hours.get(hour, 0) + 1
                days[day] = days.get(day, 0) + 1

        peak_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else None
        peak_day = max(days.items(), key=lambda x: x[1])[0] if days else None

        return {
            'hour_distribution': hours,
            'day_distribution': days,
            'peak_hour': peak_hour,
            'peak_day': peak_day
        }

    def _empty_analytics(self):
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
            'referrer_breakdown': {},
            'recent_clicks': []  # ✅ Empty array cuando no hay clicks
        }
