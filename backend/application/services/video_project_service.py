"""
Video Project Service - Business logic for video-centric project organization
Integrates YouTube metadata and aggregated analytics
"""
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime
from infrastructure.persistence.supabase_client import get_supabase
from infrastructure.external_apis.youtube_metadata import get_youtube_metadata, extract_youtube_video_id
from domain.models.video_project import (
    VideoProject,
    VideoProjectCreate,
    VideoProjectUpdate,
    VideoProjectResponse,
    VideoProjectWithLinks,
    VideoProjectAnalytics,
    VideoProjectPerformance
)


class VideoProjectService:
    """Service for managing video-centric projects with YouTube integration"""

    def __init__(self, use_supabase: bool = True):
        """
        Initialize VideoProjectService

        Args:
            use_supabase: If True, use Supabase backend (default: True)
        """
        self.use_supabase = use_supabase
        if use_supabase:
            self.supabase = get_supabase()
        else:
            # In-memory fallback for testing
            self.projects: Dict[str, dict] = {}
            self.project_links: Dict[str, List[str]] = {}

    def generate_project_id(self) -> str:
        """Generate unique project ID"""
        return f"project_{secrets.token_urlsafe(12)}"

    async def create_video_project(
        self,
        title: str,
        youtube_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        """
        Create new video project with YouTube metadata

        Args:
            title: Project title (will be overwritten if YouTube URL provided)
            youtube_url: YouTube video URL (optional)
            description: Project description (optional)

        Returns:
            Created project dict with YouTube metadata
        """
        # Initialize project data
        project_data = {
            "title": title,
            "youtube_url": youtube_url,
            "youtube_video_id": None,
            "thumbnail_url": None,
            "description": description
        }

        # If YouTube URL provided, fetch metadata
        if youtube_url:
            try:
                # Extract video ID
                video_id = extract_youtube_video_id(youtube_url)
                project_data["youtube_video_id"] = video_id

                # Fetch metadata (includes thumbnail)
                metadata = await get_youtube_metadata(youtube_url)

                if metadata.get("thumbnail_url"):
                    project_data["thumbnail_url"] = metadata["thumbnail_url"]

                # If YouTube API returns title, use it
                if metadata.get("title"):
                    project_data["title"] = metadata["title"]

                if metadata.get("description") and not description:
                    project_data["description"] = metadata["description"]

            except Exception as e:
                print(f"⚠️ YouTube metadata fetch failed: {e}")
                # Continue with user-provided title

        if self.use_supabase:
            # Create in Supabase
            response = self.supabase.table('video_projects').insert({
                "title": project_data["title"],
                "youtube_url": project_data["youtube_url"],
                "youtube_video_id": project_data["youtube_video_id"],
                "thumbnail_url": project_data["thumbnail_url"],
                "description": project_data["description"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise ValueError("Failed to create video project")
        else:
            # In-memory fallback
            project_id = self.generate_project_id()
            project = {
                "id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                **project_data
            }
            self.projects[project_id] = project
            self.project_links[project_id] = []
            return project

    def get_video_project(self, project_id: str) -> Optional[dict]:
        """
        Get video project by ID

        Args:
            project_id: Project UUID

        Returns:
            Project dict or None if not found
        """
        if self.use_supabase:
            response = self.supabase.table('video_projects').select('*').eq('id', project_id).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        else:
            # In-memory fallback
            return self.projects.get(project_id)

    def get_all_video_projects(self) -> List[dict]:
        """
        Get all video projects with aggregated analytics

        Returns:
            List of projects with total_clicks, total_links, unique_visitors
        """
        if self.use_supabase:
            # Query materialized view for analytics
            response = self.supabase.table('mv_video_project_performance').select('*').execute()

            if response.data:
                # Transform materialized view data to API response format
                projects = []
                for row in response.data:
                    projects.append({
                        "id": row["project_id"],
                        "title": row["title"],
                        "youtube_url": row["youtube_url"],
                        "youtube_video_id": row["youtube_video_id"],
                        "thumbnail_url": row["thumbnail_url"],
                        "created_at": row["created_at"],
                        "total_links": row["total_links"],
                        "total_clicks": row["total_clicks"],
                        "unique_visitors": row["unique_visitors"]
                    })
                return projects
            return []
        else:
            # In-memory fallback
            result = []
            for project_id, project in self.projects.items():
                project_data = project.copy()
                project_data["total_links"] = len(self.project_links.get(project_id, []))
                project_data["total_clicks"] = 0  # TODO: Calculate from clicks
                project_data["unique_visitors"] = 0
                result.append(project_data)
            return result

    async def update_video_project(
        self,
        project_id: str,
        title: Optional[str] = None,
        youtube_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        """
        Update video project

        Args:
            project_id: Project UUID
            title: New title (optional)
            youtube_url: New YouTube URL (optional, triggers metadata refresh)
            thumbnail_url: New thumbnail URL (optional)
            description: New description (optional)

        Returns:
            Updated project dict
        """
        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }

        if title is not None:
            update_data["title"] = title
        if thumbnail_url is not None:
            update_data["thumbnail_url"] = thumbnail_url
        if description is not None:
            update_data["description"] = description

        # If YouTube URL changed, fetch new metadata
        if youtube_url is not None:
            update_data["youtube_url"] = youtube_url

            # Extract video ID
            video_id = extract_youtube_video_id(youtube_url)
            update_data["youtube_video_id"] = video_id

            # Fetch metadata
            try:
                metadata = await get_youtube_metadata(youtube_url)
                if metadata.get("thumbnail_url"):
                    update_data["thumbnail_url"] = metadata["thumbnail_url"]
                if metadata.get("title") and title is None:
                    update_data["title"] = metadata["title"]
            except Exception as e:
                print(f"⚠️ YouTube metadata fetch failed during update: {e}")

        if self.use_supabase:
            response = self.supabase.table('video_projects').update(update_data).eq('id', project_id).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise ValueError(f"Project {project_id} not found")
        else:
            # In-memory fallback
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")

            self.projects[project_id].update(update_data)
            return self.projects[project_id]

    def delete_video_project(self, project_id: str) -> bool:
        """
        Delete video project

        Args:
            project_id: Project UUID

        Returns:
            True if deleted successfully

        Note:
            CASCADE will automatically delete project_links entries
        """
        if self.use_supabase:
            try:
                print(f"🗑️ [DELETE] Attempting to delete project: {project_id}")

                # Delete the project directly (CASCADE will delete project_links)
                # No existence check needed - if project doesn't exist, Supabase returns empty data
                delete_response = self.supabase.table('video_projects').delete().eq('id', project_id).execute()
                print(f"🔍 [DELETE] Delete response - Data: {delete_response.data}")

                # Check if deletion affected any rows
                if not delete_response.data or len(delete_response.data) == 0:
                    print(f"❌ [DELETE] Project NOT found or already deleted: {project_id}")
                    return False

                print(f"✅ [DELETE] Project deleted successfully: {project_id}")

                # Refresh materialized view to update analytics
                print(f"🔄 [DELETE] Refreshing materialized view...")
                self.supabase.rpc('refresh_video_project_analytics').execute()
                print(f"✅ [DELETE] Materialized view refreshed")

                return True
            except Exception as e:
                print(f"❌ [DELETE] Error deleting project: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            # In-memory fallback
            if project_id not in self.projects:
                return False
            del self.projects[project_id]
            if project_id in self.project_links:
                del self.project_links[project_id]
            return True

    def assign_link_to_project(self, url_id: str, project_id: str) -> bool:
        """
        Assign URL to video project

        Args:
            url_id: URL UUID or short_code
            project_id: Project UUID

        Returns:
            True if assigned successfully
        """
        if self.use_supabase:
            try:
                # Check if already assigned
                existing = self.supabase.table('project_links').select('*').eq('project_id', project_id).eq('url_id', url_id).execute()

                if existing.data and len(existing.data) > 0:
                    # Already assigned
                    return True

                # Create assignment
                response = self.supabase.table('project_links').insert({
                    "project_id": project_id,
                    "url_id": url_id,
                    "added_at": datetime.utcnow().isoformat()
                }).execute()

                return response.data is not None and len(response.data) > 0
            except Exception as e:
                print(f"❌ Error assigning link to project: {e}")
                return False
        else:
            # In-memory fallback
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")

            if project_id not in self.project_links:
                self.project_links[project_id] = []

            if url_id not in self.project_links[project_id]:
                self.project_links[project_id].append(url_id)

            return True

    def remove_link_from_project(self, url_id: str, project_id: str) -> bool:
        """
        Remove URL from video project

        Args:
            url_id: URL UUID or short_code
            project_id: Project UUID

        Returns:
            True if removed successfully
        """
        if self.use_supabase:
            response = self.supabase.table('project_links').delete().eq('project_id', project_id).eq('url_id', url_id).execute()
            return response.data is not None and len(response.data) > 0
        else:
            # In-memory fallback
            if project_id not in self.project_links:
                return False
            if url_id in self.project_links[project_id]:
                self.project_links[project_id].remove(url_id)
                return True
            return False

    def get_project_links(self, project_id: str) -> List[dict]:
        """
        Get all URLs assigned to a project with their analytics

        Args:
            project_id: Project UUID

        Returns:
            List of URL dicts with click counts
        """
        if self.use_supabase:
            # Join project_links with urls table
            response = self.supabase.table('project_links').select(
                'url_id, added_at, urls(id, short_code, original_url, title, click_count, created_at)'
            ).eq('project_id', project_id).execute()

            if response.data:
                # Flatten the nested structure
                links = []
                for row in response.data:
                    if row.get('urls'):
                        link_data = row['urls']
                        link_data['added_at'] = row['added_at']
                        links.append(link_data)
                return links
            return []
        else:
            # In-memory fallback
            return self.project_links.get(project_id, [])

    def get_project_analytics(self, project_id: str) -> dict:
        """
        Get detailed analytics for a video project

        Args:
            project_id: Project UUID

        Returns:
            Analytics dict with aggregated metrics across all links
        """
        if self.use_supabase:
            # Query materialized view for project analytics
            response = self.supabase.table('mv_video_project_performance').select('*').eq('project_id', project_id).execute()

            if response.data and len(response.data) > 0:
                row = response.data[0]
                return {
                    "project_id": row["project_id"],
                    "title": row["title"],
                    "youtube_url": row["youtube_url"],
                    "youtube_video_id": row["youtube_video_id"],
                    "thumbnail_url": row["thumbnail_url"],
                    "created_at": row["created_at"],
                    "total_links": row["total_links"],
                    "total_clicks": row["total_clicks"],
                    "unique_visitors": row["unique_visitors"],
                    "countries_reached": row["countries_reached"],
                    "mobile_clicks": row["mobile_clicks"],
                    "desktop_clicks": row["desktop_clicks"],
                    "tablet_clicks": row["tablet_clicks"],
                    "last_click_at": row["last_click_at"],
                    "first_click_at": row["first_click_at"]
                }

            # If no analytics yet, return project with zero stats
            project = self.get_video_project(project_id)
            if project:
                return {
                    **project,
                    "total_links": 0,
                    "total_clicks": 0,
                    "unique_visitors": 0,
                    "countries_reached": 0,
                    "mobile_clicks": 0,
                    "desktop_clicks": 0,
                    "tablet_clicks": 0,
                    "last_click_at": None,
                    "first_click_at": None
                }

            raise ValueError(f"Project {project_id} not found")
        else:
            # In-memory fallback
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")

            return {
                **self.projects[project_id],
                "total_links": len(self.project_links.get(project_id, [])),
                "total_clicks": 0,
                "unique_visitors": 0
            }

    def get_video_performance_comparison(self, limit: int = 10) -> List[dict]:
        """
        Get performance comparison across all videos

        Args:
            limit: Maximum number of projects to return (default: 10)

        Returns:
            List of projects sorted by total_clicks descending
        """
        if self.use_supabase:
            response = self.supabase.table('mv_video_project_performance').select(
                'project_id, title, youtube_url, thumbnail_url, total_clicks, unique_visitors, total_links, created_at'
            ).order('total_clicks', desc=True).limit(limit).execute()

            return response.data if response.data else []
        else:
            # In-memory fallback
            projects = self.get_all_video_projects()
            # Sort by total_clicks descending
            sorted_projects = sorted(projects, key=lambda x: x.get('total_clicks', 0), reverse=True)
            return sorted_projects[:limit]

    def refresh_analytics(self) -> bool:
        """
        Refresh materialized view for analytics

        Returns:
            True if refresh successful
        """
        if self.use_supabase:
            try:
                # Call Postgres RPC function to refresh materialized view
                self.supabase.rpc('refresh_video_project_analytics').execute()
                print("✅ Video project analytics refreshed")
                return True
            except Exception as e:
                print(f"❌ Failed to refresh analytics: {e}")
                return False
        else:
            # In-memory mode doesn't need refresh
            return True


# Singleton instance
video_project_service = VideoProjectService(use_supabase=True)


# Convenience functions for easy access
async def create_video_project(title: str, youtube_url: Optional[str] = None, description: Optional[str] = None) -> dict:
    """Create video project"""
    return await video_project_service.create_video_project(title, youtube_url, description)


def get_all_video_projects() -> List[dict]:
    """Get all video projects with analytics"""
    return video_project_service.get_all_video_projects()


def get_project_analytics(project_id: str) -> dict:
    """Get project analytics"""
    return video_project_service.get_project_analytics(project_id)


def assign_link_to_project(url_id: str, project_id: str) -> bool:
    """Assign link to project"""
    return video_project_service.assign_link_to_project(url_id, project_id)
