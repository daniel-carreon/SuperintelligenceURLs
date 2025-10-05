"""
Video Projects API Router - Endpoints for video-centric organization
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

# Import service (será singleton en main.py)
video_project_service = None


# Request/Response models
class VideoProjectCreateRequest(BaseModel):
    """Request model for creating video project"""
    title: str
    youtube_url: Optional[str] = None
    description: Optional[str] = None


class VideoProjectUpdateRequest(BaseModel):
    """Request model for updating video project"""
    title: Optional[str] = None
    youtube_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class VideoProjectResponse(BaseModel):
    """Response model for video project"""
    id: str
    title: str
    youtube_url: Optional[str]
    youtube_video_id: Optional[str]
    thumbnail_url: Optional[str]
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    total_links: int = 0
    total_clicks: int = 0
    unique_visitors: int = 0


class VideoProjectAnalyticsResponse(BaseModel):
    """Response model for video project analytics"""
    project_id: str
    title: str
    youtube_url: Optional[str]
    youtube_video_id: Optional[str]
    thumbnail_url: Optional[str]
    created_at: str
    total_links: int
    total_clicks: int
    unique_visitors: int
    countries_reached: int
    mobile_clicks: int
    desktop_clicks: int
    tablet_clicks: int
    last_click_at: Optional[str]
    first_click_at: Optional[str]


class AssignLinkToProjectRequest(BaseModel):
    """Request model for assigning link to project"""
    url_id: str
    project_id: str


class VideoPerformanceResponse(BaseModel):
    """Response model for video performance comparison"""
    project_id: str
    title: str
    youtube_url: Optional[str]
    thumbnail_url: Optional[str]
    total_clicks: int
    unique_visitors: int
    total_links: int
    created_at: str


# Router
router = APIRouter(prefix="/video-projects", tags=["video-projects"])


@router.post("/", response_model=VideoProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_video_project(project_data: VideoProjectCreateRequest):
    """
    Create new video project with optional YouTube metadata

    - **title**: Project title (will be auto-fetched from YouTube if URL provided)
    - **youtube_url**: YouTube video URL (optional, triggers metadata fetch)
    - **description**: Project description (optional)

    Returns:
        Created video project with YouTube metadata (thumbnail, video_id)
    """
    try:
        project = await video_project_service.create_video_project(
            title=project_data.title,
            youtube_url=project_data.youtube_url,
            description=project_data.description
        )

        # Add analytics defaults for new project
        project["total_links"] = 0
        project["total_clicks"] = 0
        project["unique_visitors"] = 0

        # Refresh materialized view to show new project immediately
        video_project_service.refresh_analytics()

        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create video project: {str(e)}")


@router.get("/")
async def get_all_video_projects():
    """
    Get all video projects with aggregated analytics

    Returns:
        List of video projects with:
        - total_links: Number of URLs in project
        - total_clicks: Aggregated clicks across all links
        - unique_visitors: Unique IP addresses across all links
    """
    try:
        projects = video_project_service.get_all_video_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve video projects: {str(e)}")


@router.get("/{project_id}", response_model=VideoProjectResponse)
async def get_video_project(project_id: str):
    """
    Get video project by ID

    Args:
        project_id: Project UUID

    Returns:
        Video project details
    """
    project = video_project_service.get_video_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Video project not found")

    # Add basic analytics
    project["total_links"] = 0  # Will be calculated from project_links
    project["total_clicks"] = 0
    project["unique_visitors"] = 0

    return project


@router.patch("/{project_id}", response_model=VideoProjectResponse)
async def update_video_project(project_id: str, project_data: VideoProjectUpdateRequest):
    """
    Update video project

    - **title**: New title (optional)
    - **youtube_url**: New YouTube URL (optional, triggers metadata refresh)
    - **thumbnail_url**: New thumbnail URL (optional)
    - **description**: New description (optional)

    Returns:
        Updated video project
    """
    try:
        project = await video_project_service.update_video_project(
            project_id=project_id,
            title=project_data.title,
            youtube_url=project_data.youtube_url,
            thumbnail_url=project_data.thumbnail_url,
            description=project_data.description
        )

        # Add analytics
        project["total_links"] = 0
        project["total_clicks"] = 0
        project["unique_visitors"] = 0

        # Refresh materialized view to show updated project immediately
        video_project_service.refresh_analytics()

        return project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update video project: {str(e)}")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video_project(project_id: str):
    """
    Delete video project

    CASCADE will automatically delete all project_links associations.

    Args:
        project_id: Project UUID
    """
    success = video_project_service.delete_video_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video project not found")


@router.post("/assign", status_code=status.HTTP_200_OK)
async def assign_link_to_project(data: AssignLinkToProjectRequest):
    """
    Assign URL to video project

    - **url_id**: URL UUID or short_code
    - **project_id**: Target project UUID

    Returns:
        Success message
    """
    try:
        success = video_project_service.assign_link_to_project(data.url_id, data.project_id)
        if success:
            return {"message": "Link assigned to video project successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to assign link to project")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign link: {str(e)}")


@router.delete("/assign", status_code=status.HTTP_200_OK)
async def remove_link_from_project(data: AssignLinkToProjectRequest):
    """
    Remove URL from video project

    - **url_id**: URL UUID or short_code
    - **project_id**: Project UUID

    Returns:
        Success message
    """
    success = video_project_service.remove_link_from_project(data.url_id, data.project_id)
    if not success:
        return {"message": "Link not in project"}
    return {"message": "Link removed from video project successfully"}


@router.get("/{project_id}/links")
async def get_project_links(project_id: str):
    """
    Get all links in video project with analytics

    Args:
        project_id: Project UUID

    Returns:
        List of URLs with click counts
    """
    try:
        links = video_project_service.get_project_links(project_id)
        return {
            "project_id": project_id,
            "links": links,
            "count": len(links)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project links: {str(e)}")


@router.get("/{project_id}/analytics", response_model=VideoProjectAnalyticsResponse)
async def get_project_analytics(project_id: str):
    """
    Get aggregated analytics for video project

    Returns detailed analytics:
    - Total clicks across all links
    - Unique visitors (by IP)
    - Countries reached
    - Device breakdown (mobile, desktop, tablet)
    - Time tracking (first/last click)

    Args:
        project_id: Project UUID

    Returns:
        Comprehensive analytics from materialized view
    """
    try:
        analytics = video_project_service.get_project_analytics(project_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@router.get("/performance/comparison", response_model=List[VideoPerformanceResponse])
async def get_video_performance_comparison(limit: int = 10):
    """
    Get video performance comparison across all projects

    Returns top performing videos sorted by total clicks.

    Args:
        limit: Maximum number of projects to return (default: 10)

    Returns:
        List of video projects with performance metrics
    """
    try:
        performance_data = video_project_service.get_video_performance_comparison(limit=limit)
        return performance_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance data: {str(e)}")


@router.post("/refresh-analytics", status_code=status.HTTP_200_OK)
async def refresh_analytics():
    """
    Refresh materialized view for video project analytics

    Call this endpoint after significant click activity to update
    aggregated analytics data.

    Returns:
        Success message
    """
    try:
        success = video_project_service.refresh_analytics()
        if success:
            return {"message": "Video project analytics refreshed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh analytics")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh analytics: {str(e)}")
