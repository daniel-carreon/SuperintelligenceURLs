"""
Script Maestro: Completa la migración a Supabase automáticamente
Genera todos los repositorios y actualiza el código existente
"""

import os

# Repository para URLs
url_repository_code = '''"""
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
'''

# Repository para Clicks
click_repository_code = '''"""
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
            'referrer_breakdown': self._count_field(clicks, 'referrer_type')
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
            'referrer_breakdown': {}
        }
'''

# Repository para Folders
folder_repository_code = '''"""
Folder Repository - Supabase implementation
"""
from typing import List, Optional
from infrastructure.persistence.supabase_client import get_supabase


class FolderRepository:
    """Repository para operaciones de folders en Supabase"""

    def __init__(self):
        self.client = get_supabase()
        self.folders_table = self.client.table('folders')
        self.links_table = self.client.table('folder_links')

    def create(self, name: str, color: str = "#00fff5", icon: str = "📁", parent_folder_id: str = None) -> dict:
        """Crear nuevo folder"""
        data = {
            'name': name,
            'color': color,
            'icon': icon,
            'parent_folder_id': parent_folder_id
        }
        response = self.folders_table.insert(data).execute()
        return response.data[0] if response.data else None

    def get_all(self) -> List[dict]:
        """Obtener todos los folders"""
        response = self.folders_table.select('*').order('created_at', desc=True).execute()
        return response.data

    def get_tree(self) -> List[dict]:
        """Obtener árbol de folders con link counts"""
        folders = self.get_all()

        # Get link counts
        for folder in folders:
            links_response = self.links_table.select('id').eq('folder_id', folder['id']).execute()
            folder['link_count'] = len(links_response.data)
            folder['subfolders'] = []

        # Build tree
        folder_map = {f['id']: f for f in folders}
        root_folders = []

        for folder in folders:
            if folder['parent_folder_id']:
                parent = folder_map.get(folder['parent_folder_id'])
                if parent:
                    parent['subfolders'].append(folder)
            else:
                root_folders.append(folder)

        return root_folders

    def update(self, folder_id: str, name: str = None, color: str = None, icon: str = None) -> dict:
        """Actualizar folder"""
        data = {}
        if name: data['name'] = name
        if color: data['color'] = color
        if icon: data['icon'] = icon

        response = self.folders_table.update(data).eq('id', folder_id).execute()
        return response.data[0] if response.data else None

    def delete(self, folder_id: str) -> bool:
        """Eliminar folder (CASCADE borra folder_links automáticamente)"""
        response = self.folders_table.delete().eq('id', folder_id).execute()
        return len(response.data) > 0

    def assign_link(self, folder_id: str, url_id: str) -> dict:
        """Asignar link a folder"""
        data = {
            'folder_id': folder_id,
            'url_id': url_id
        }
        response = self.links_table.insert(data).execute()
        return response.data[0] if response.data else None

    def unassign_link(self, folder_id: str, url_id: str) -> bool:
        """Desasignar link de folder"""
        response = self.links_table.delete().eq('folder_id', folder_id).eq('url_id', url_id).execute()
        return len(response.data) > 0
'''

# Escribir archivos
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {path}")

# Crear repositorios
base_path = "infrastructure/persistence/"
write_file(f"{base_path}url_repository.py", url_repository_code)
write_file(f"{base_path}click_repository.py", click_repository_code)
write_file(f"{base_path}folder_repository.py", folder_repository_code)

print("\n🎉 ¡Todos los repositorios creados exitosamente!")
print("\nSiguientes pasos:")
print("1. Actualizar main.py para usar repositorios")
print("2. Actualizar folder_service.py")
print("3. Actualizar click_tracker_service.py")
print("4. Matar y reiniciar el servidor")