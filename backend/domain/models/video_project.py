"""
Video Project Domain Models
SQLModel entities for video-centric organization
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
import re


class VideoProjectBase(SQLModel):
    """Base VideoProject model with shared fields"""
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Video title - cached from YouTube API or manually entered"
    )
    youtube_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="Full YouTube video URL"
    )
    youtube_video_id: Optional[str] = Field(
        None,
        max_length=20,
        description="YouTube video ID extracted from URL (e.g., dQw4w9WgXcQ)"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="YouTube video thumbnail URL for display"
    )
    # description removed - not in database schema yet


class VideoProject(VideoProjectBase, table=True):
    """VideoProject table model for database"""
    __tablename__ = "video_projects"

    id: Optional[str] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Future: user ownership
    user_id: Optional[str] = Field(None)


class ProjectLink(SQLModel, table=True):
    """Junction table linking video projects to URLs"""
    __tablename__ = "project_links"

    id: Optional[str] = Field(default=None, primary_key=True)
    project_id: str = Field(foreign_key="video_projects.id")
    url_id: str = Field(foreign_key="urls.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)


class VideoProjectCreate(SQLModel):
    """Schema for creating new video projects"""
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Video title - will be auto-fetched from YouTube if URL provided"
    )
    youtube_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="YouTube video URL (optional)"
    )

    def validate_youtube_url(self) -> bool:
        """Validate YouTube URL format"""
        if not self.youtube_url:
            return True

        youtube_patterns = [
            r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})',
            r'youtu\.be/([A-Za-z0-9_-]{11})',
            r'youtube\.com/embed/([A-Za-z0-9_-]{11})',
            r'youtube\.com/shorts/([A-Za-z0-9_-]{11})'
        ]

        return any(re.search(pattern, self.youtube_url) for pattern in youtube_patterns)


class VideoProjectUpdate(SQLModel):
    """Schema for updating video projects"""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500
    )
    youtube_url: Optional[str] = Field(None, max_length=2048)
    thumbnail_url: Optional[str] = Field(None, max_length=2048)


class VideoProjectResponse(VideoProjectBase):
    """Schema for video project API responses"""
    id: str
    created_at: datetime
    updated_at: datetime

    # Analytics aggregated (from materialized view)
    total_links: int = 0
    total_clicks: int = 0
    unique_visitors: int = 0


class VideoProjectWithLinks(VideoProjectResponse):
    """Video project response with associated links"""
    links: List[dict] = []  # Will contain URL details with click counts


class VideoProjectAnalytics(SQLModel):
    """Aggregated analytics for a video project"""
    project_id: str
    title: str
    youtube_url: Optional[str]
    thumbnail_url: Optional[str]

    # Link statistics
    total_links: int
    total_clicks: int
    unique_visitors: int
    countries_reached: int

    # Device breakdown
    mobile_clicks: int
    desktop_clicks: int
    tablet_clicks: int

    # Time tracking
    last_click_at: Optional[datetime]
    first_click_at: Optional[datetime]
    created_at: datetime


class AssignLinkToProject(SQLModel):
    """Schema for assigning a URL to a video project"""
    url_id: str = Field(description="URL short code or ID")
    project_id: str = Field(description="Video project ID")


class VideoProjectPerformance(SQLModel):
    """Schema for video performance comparison"""
    project_id: str
    title: str
    youtube_url: Optional[str]
    thumbnail_url: Optional[str]
    total_clicks: int
    unique_visitors: int
    total_links: int
    created_at: datetime
