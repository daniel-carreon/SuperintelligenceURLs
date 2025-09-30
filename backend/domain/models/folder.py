"""
Folder domain model - Organización de URLs
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class Folder(SQLModel, table=True):
    """Folder model para organizar URLs en categorías"""
    __tablename__ = "folders"

    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    color: str = Field(default="#00fff5")  # Hex color (default: neon cyan)
    icon: Optional[str] = Field(default="📁")  # Emoji icon
    parent_folder_id: Optional[str] = Field(default=None, foreign_key="folders.id")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Future: user_id for multi-tenant
    # user_id: Optional[str] = Field(default=None, foreign_key="users.id")


class FolderLink(SQLModel, table=True):
    """Many-to-many relationship between folders and URLs"""
    __tablename__ = "folder_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    folder_id: str = Field(foreign_key="folders.id")
    url_id: str = Field(foreign_key="urls.id")

    # Metadata
    added_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response schemas
class FolderCreate(SQLModel):
    """Schema para crear folder"""
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#00fff5", regex="^#[0-9A-Fa-f]{6}$")
    icon: str = Field(default="📁")
    parent_folder_id: Optional[str] = None


class FolderUpdate(SQLModel):
    """Schema para actualizar folder"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, regex="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(default=None)
    parent_folder_id: Optional[str] = None


class FolderResponse(SQLModel):
    """Schema de respuesta con analytics"""
    id: str
    name: str
    color: str
    icon: str
    parent_folder_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Analytics agregado
    link_count: int = 0
    total_clicks: int = 0
    subfolder_count: int = 0


class AssignLinkToFolder(SQLModel):
    """Schema para asignar link a folder"""
    url_id: str
    folder_id: str