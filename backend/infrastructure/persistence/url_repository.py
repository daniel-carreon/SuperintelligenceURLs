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
        """Obtener todas las URLs activas con folder_id"""
        # Get all URLs
        response = self.table.select('*').eq('is_active', True).order('created_at', desc=True).limit(limit).execute()
        urls = response.data

        # Get folder assignments
        folder_links_response = self.client.table('folder_links').select('url_id, folder_id').execute()
        folder_map = {link['url_id']: link['folder_id'] for link in folder_links_response.data}

        # Add folder_id to each URL
        for url in urls:
            url['folder_id'] = folder_map.get(url['id'])

        return urls

    def update_click_count(self, url_id: str):
        """Incrementar click count"""
        # Get current count
        url = self.table.select('click_count').eq('id', url_id).execute()
        if not url.data:
            return None

        current_count = url.data[0].get('click_count', 0)

        # Update with incremented count
        response = self.table.update({
            'click_count': current_count + 1,
            'last_clicked_at': datetime.utcnow().isoformat()
        }).eq('id', url_id).execute()
        return response.data[0] if response.data else None

    def delete(self, short_code: str) -> bool:
        """Soft delete - marcar como inactiva"""
        response = self.table.update({'is_active': False}).eq('short_code', short_code).execute()
        return len(response.data) > 0
