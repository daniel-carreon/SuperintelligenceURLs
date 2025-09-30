"""
URL Repository - Supabase implementation
"""
from typing import Optional, List
from datetime import datetime
from infrastructure.persistence.supabase_client import get_supabase


class URLRepository:
    """Repository para operaciones CRUD de URLs en Supabase"""

    def __init__(self):
        self.client = get_supabase()
        self.table = self.client.table('urls')

    def create(self, short_code: str, original_url: str, title: str = None, domain: str = None) -> dict:
        """Crear nueva URL"""
        data = {
            'short_code': short_code,
            'original_url': original_url,
            'title': title,
            'domain': domain,
            'is_active': True,
            'click_count': 0
        }
        response = self.table.insert(data).execute()
        return response.data[0] if response.data else None

    def get_by_short_code(self, short_code: str) -> Optional[dict]:
        """Obtener URL por short_code"""
        response = self.table.select('*').eq('short_code', short_code).eq('is_active', True).execute()
        return response.data[0] if response.data else None

    def get_all(self, limit: int = 100) -> List[dict]:
        """Obtener todas las URLs activas"""
        response = self.table.select('*').eq('is_active', True).order('created_at', desc=True).limit(limit).execute()
        return response.data

    def update_click_count(self, url_id: str):
        """Incrementar click count"""
        response = self.table.update({
            'click_count': self.client.rpc('increment_click_count', {'p_url_id': url_id}).execute(),
            'last_clicked_at': datetime.utcnow().isoformat()
        }).eq('id', url_id).execute()
        return response.data

    def delete(self, short_code: str) -> bool:
        """Soft delete - marcar como inactiva"""
        response = self.table.update({'is_active': False}).eq('short_code', short_code).execute()
        return len(response.data) > 0
