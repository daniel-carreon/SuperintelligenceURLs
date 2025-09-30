"""
Folders API Router - Endpoints para organización de URLs
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

# Importar service (será singleton en main.py)
folder_service = None


# Request/Response models
class FolderCreate(BaseModel):
    name: str
    color: str = "#00fff5"
    icon: str = "📁"
    parent_folder_id: Optional[str] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_folder_id: Optional[str] = None


class FolderResponse(BaseModel):
    id: str
    name: str
    color: str
    icon: str
    parent_folder_id: Optional[str]
    created_at: str
    updated_at: str
    link_count: int = 0
    subfolder_count: int = 0


class AssignLinkRequest(BaseModel):
    url_id: str
    folder_id: str


# Router
router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(folder_data: FolderCreate):
    """
    Create new folder

    - **name**: Folder name (required)
    - **color**: Hex color code (default: #00fff5)
    - **icon**: Emoji icon (default: 📁)
    - **parent_folder_id**: Parent folder for nesting (optional)
    """
    try:
        folder = folder_service.create_folder(
            name=folder_data.name,
            color=folder_data.color,
            icon=folder_data.icon,
            parent_folder_id=folder_data.parent_folder_id
        )
        folder["link_count"] = 0
        folder["subfolder_count"] = 0
        return folder
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[FolderResponse])
async def get_all_folders():
    """
    Get all folders with analytics

    Returns list of folders with:
    - link_count: Number of URLs in folder
    - subfolder_count: Number of subfolders
    """
    folders = folder_service.get_all_folders()
    return folders


@router.get("/tree")
async def get_folder_tree():
    """
    Get folder hierarchy as tree structure

    Returns nested structure:
    - Root folders at top level
    - Subfolders nested within parents
    - Sorted alphabetically
    """
    tree = folder_service.get_folder_tree()
    return {"folders": tree}


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: str):
    """Get folder by ID"""
    folder = folder_service.get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder_data = folder.copy()
    folder_data["link_count"] = len(folder_service.get_folder_links(folder_id))
    folder_data["subfolder_count"] = sum(
        1 for f in folder_service.folders.values()
        if f.get("parent_folder_id") == folder_id
    )
    return folder_data


@router.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(folder_id: str, folder_data: FolderUpdate):
    """
    Update folder properties

    - **name**: New name (optional)
    - **color**: New color (optional)
    - **icon**: New icon (optional)
    - **parent_folder_id**: Move to new parent (optional)
    """
    try:
        folder = folder_service.update_folder(
            folder_id=folder_id,
            name=folder_data.name,
            color=folder_data.color,
            icon=folder_data.icon,
            parent_folder_id=folder_data.parent_folder_id
        )
        folder["link_count"] = len(folder_service.get_folder_links(folder_id))
        folder["subfolder_count"] = sum(
            1 for f in folder_service.folders.values()
            if f.get("parent_folder_id") == folder_id
        )
        return folder
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: str, delete_links: bool = False):
    """
    Delete folder

    - **delete_links**: If true, remove link associations (default: false)

    If false, links are moved to parent folder or orphaned
    """
    success = folder_service.delete_folder(folder_id, delete_links=delete_links)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")


@router.post("/assign")
async def assign_link_to_folder(data: AssignLinkRequest):
    """
    Assign URL to folder

    - **url_id**: URL short code
    - **folder_id**: Target folder ID
    """
    try:
        folder_service.assign_link_to_folder(data.url_id, data.folder_id)
        return {"message": "Link assigned to folder successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/assign")
async def remove_link_from_folder(data: AssignLinkRequest):
    """
    Remove URL from folder

    - **url_id**: URL short code
    - **folder_id**: Folder ID
    """
    success = folder_service.remove_link_from_folder(data.url_id, data.folder_id)
    if not success:
        return {"message": "Link not in folder"}
    return {"message": "Link removed from folder successfully"}


@router.get("/{folder_id}/links")
async def get_folder_links(folder_id: str):
    """
    Get all links in folder

    Returns list of URL IDs
    """
    if folder_id not in folder_service.folders:
        raise HTTPException(status_code=404, detail="Folder not found")

    link_ids = folder_service.get_folder_links(folder_id)
    return {"folder_id": folder_id, "link_ids": link_ids, "count": len(link_ids)}


@router.get("/{folder_id}/analytics")
async def get_folder_analytics(folder_id: str):
    """
    Get aggregated analytics for folder

    Returns:
    - Total clicks across all links
    - Unique visitors
    - Device breakdown
    - Country breakdown
    """
    try:
        # Import global data from main
        from main import urls, clicks

        analytics = folder_service.get_folder_analytics(
            folder_id=folder_id,
            urls_data=urls,
            clicks_data=clicks
        )
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))