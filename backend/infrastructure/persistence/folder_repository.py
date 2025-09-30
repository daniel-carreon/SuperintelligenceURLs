"""
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

    def update(self, folder_id: str, name: str = None, color: str = None, icon: str = None, parent_folder_id: str = None) -> dict:
        """Actualizar folder"""
        data = {}
        if name: data['name'] = name
        if color: data['color'] = color
        if icon: data['icon'] = icon
        if parent_folder_id is not None: data['parent_folder_id'] = parent_folder_id

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

    def get_links(self, folder_id: str) -> List[str]:
        """Obtener todos los URL IDs en un folder"""
        response = self.links_table.select('url_id').eq('folder_id', folder_id).execute()
        return [item['url_id'] for item in response.data]

    def get(self, folder_id: str) -> Optional[dict]:
        """Obtener un folder por ID"""
        response = self.folders_table.select('*').eq('id', folder_id).execute()
        return response.data[0] if response.data else None
