"""
Folder Service - Business logic para organización de URLs
"""
import secrets
from typing import List, Optional, Dict
from datetime import datetime


class FolderService:
    """Service para gestionar folders y organización de links"""

    def __init__(self, folder_repository=None):
        if folder_repository:
            # Use Supabase repository
            self.repo = folder_repository
            self.use_db = True
        else:
            # Fallback to in-memory storage
            self.folders: Dict[str, dict] = {}
            self.folder_links: Dict[str, List[str]] = {}
            self.use_db = False

    def generate_folder_id(self) -> str:
        """Generate unique folder ID"""
        return f"folder_{secrets.token_urlsafe(8)}"

    def create_folder(
        self,
        name: str,
        color: str = "#00fff5",
        icon: str = "📁",
        parent_folder_id: Optional[str] = None
    ) -> dict:
        """
        Create new folder

        Args:
            name: Folder name
            color: Hex color code
            icon: Emoji icon
            parent_folder_id: Parent folder for nesting

        Returns:
            Created folder dict
        """
        # Validate parent exists
        if parent_folder_id and parent_folder_id not in self.folders:
            raise ValueError(f"Parent folder {parent_folder_id} not found")

        folder_id = self.generate_folder_id()
        folder = {
            "id": folder_id,
            "name": name,
            "color": color,
            "icon": icon,
            "parent_folder_id": parent_folder_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.folders[folder_id] = folder
        self.folder_links[folder_id] = []

        return folder

    def get_folder(self, folder_id: str) -> Optional[dict]:
        """Get folder by ID"""
        return self.folders.get(folder_id)

    def get_all_folders(self) -> List[dict]:
        """Get all folders with analytics"""
        result = []
        for folder_id, folder in self.folders.items():
            folder_data = folder.copy()
            folder_data["link_count"] = len(self.folder_links.get(folder_id, []))
            folder_data["subfolder_count"] = sum(
                1 for f in self.folders.values()
                if f.get("parent_folder_id") == folder_id
            )
            result.append(folder_data)
        return result

    def update_folder(
        self,
        folder_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        parent_folder_id: Optional[str] = None
    ) -> dict:
        """Update folder properties"""
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")

        folder = self.folders[folder_id]

        if name is not None:
            folder["name"] = name
        if color is not None:
            folder["color"] = color
        if icon is not None:
            folder["icon"] = icon
        if parent_folder_id is not None:
            # Validate parent exists and no circular reference
            if parent_folder_id != folder_id and parent_folder_id in self.folders:
                folder["parent_folder_id"] = parent_folder_id

        folder["updated_at"] = datetime.utcnow().isoformat()
        return folder

    def delete_folder(self, folder_id: str, delete_links: bool = False) -> bool:
        """
        Delete folder

        Args:
            folder_id: Folder to delete
            delete_links: If True, also remove link associations

        Returns:
            True if deleted
        """
        if folder_id not in self.folders:
            return False

        # Handle subfolders - move to parent or orphan
        parent_id = self.folders[folder_id].get("parent_folder_id")
        for folder in self.folders.values():
            if folder.get("parent_folder_id") == folder_id:
                folder["parent_folder_id"] = parent_id

        # Handle links
        if delete_links:
            del self.folder_links[folder_id]
        else:
            # Move links to parent folder
            if parent_id and parent_id in self.folder_links:
                self.folder_links[parent_id].extend(self.folder_links.get(folder_id, []))
            del self.folder_links[folder_id]

        del self.folders[folder_id]
        return True

    def assign_link_to_folder(self, url_id: str, folder_id: str) -> bool:
        """
        Assign URL to folder

        Args:
            url_id: URL short code
            folder_id: Target folder

        Returns:
            True if assigned
        """
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")

        if folder_id not in self.folder_links:
            self.folder_links[folder_id] = []

        if url_id not in self.folder_links[folder_id]:
            self.folder_links[folder_id].append(url_id)

        return True

    def remove_link_from_folder(self, url_id: str, folder_id: str) -> bool:
        """Remove URL from folder"""
        if folder_id not in self.folder_links:
            return False

        if url_id in self.folder_links[folder_id]:
            self.folder_links[folder_id].remove(url_id)
            return True

        return False

    def get_folder_links(self, folder_id: str) -> List[str]:
        """Get all URL IDs in folder"""
        return self.folder_links.get(folder_id, [])

    def get_folder_tree(self) -> List[dict]:
        """
        Get folder hierarchy as tree structure

        Returns:
            List of root folders with nested subfolders
        """
        def build_tree(parent_id: Optional[str] = None) -> List[dict]:
            result = []
            for folder_id, folder in self.folders.items():
                if folder.get("parent_folder_id") == parent_id:
                    folder_data = folder.copy()
                    folder_data["link_count"] = len(self.folder_links.get(folder_id, []))
                    folder_data["subfolders"] = build_tree(folder_id)
                    result.append(folder_data)
            return sorted(result, key=lambda x: x["name"])

        return build_tree(None)

    def get_folder_analytics(self, folder_id: str, urls_data: dict, clicks_data: List[dict]) -> dict:
        """
        Get aggregated analytics for folder

        Args:
            folder_id: Folder to analyze
            urls_data: Dict of URL data {url_id: url_obj}
            clicks_data: List of click dicts

        Returns:
            Analytics summary
        """
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")

        folder = self.folders[folder_id]
        link_ids = self.folder_links.get(folder_id, [])

        # Aggregate metrics
        total_clicks = 0
        unique_visitors = set()
        device_breakdown = {}
        country_breakdown = {}

        for click in clicks_data:
            if click.get("url_id") in link_ids:
                total_clicks += 1
                unique_visitors.add(click.get("ip_address"))

                device = click.get("device_type", "unknown")
                device_breakdown[device] = device_breakdown.get(device, 0) + 1

                country = click.get("country_name", "Unknown")
                country_breakdown[country] = country_breakdown.get(country, 0) + 1

        return {
            "folder_id": folder_id,
            "folder_name": folder["name"],
            "link_count": len(link_ids),
            "total_clicks": total_clicks,
            "unique_visitors": len(unique_visitors),
            "device_breakdown": device_breakdown,
            "country_breakdown": country_breakdown,
        }