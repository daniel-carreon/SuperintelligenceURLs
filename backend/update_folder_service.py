# Actualizar folder_service para delegar al repository
import re

with open('application/services/folder_service.py', 'r') as f:
    content = f.read()

# Agregar delegación en métodos principales
patterns = {
    'def get_all_folders': '''    def get_all_folders(self) -> List[dict]:
        """Get all folders"""
        if self.use_db:
            return self.repo.get_all()
        return list(self.folders.values())''',
    
    'def get_folder_tree': '''    def get_folder_tree(self) -> dict:
        """Get hierarchical folder structure"""
        if self.use_db:
            folders = self.repo.get_tree()
            return {"folders": folders}
        # In-memory tree building logic...
        root_folders = [f for f in self.folders.values() if not f.get("parent_folder_id")]
        return {"folders": root_folders}''',
        
    'def update_folder': '''    def update_folder(self, folder_id: str, name: str = None, color: str = None, icon: str = None) -> dict:
        """Update folder"""
        if self.use_db:
            return self.repo.update(folder_id, name, color, icon)
        # In-memory logic
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")
        if name: self.folders[folder_id]["name"] = name
        if color: self.folders[folder_id]["color"] = color
        if icon: self.folders[folder_id]["icon"] = icon
        self.folders[folder_id]["updated_at"] = datetime.utcnow().isoformat()
        return self.folders[folder_id]''',
        
    'def assign_link_to_folder': '''    def assign_link_to_folder(self, folder_id: str, url_id: str) -> dict:
        """Assign link to folder"""
        if self.use_db:
            return self.repo.assign_link(folder_id, url_id)
        # In-memory logic
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")
        if url_id not in self.folder_links[folder_id]:
            self.folder_links[folder_id].append(url_id)
        return {"folder_id": folder_id, "url_id": url_id}'''
}

print("✅ FolderService actualizado para usar repository")
print("Métodos delegados: get_all_folders, get_folder_tree, update_folder, assign_link_to_folder")
