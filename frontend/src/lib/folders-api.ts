/**
 * Folders API Client
 * Handles folder organization and management
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ==================== Types ====================

export interface Folder {
  id: string;
  name: string;
  color: string;
  icon: string;
  parent_folder_id?: string;
  created_at: string;
  updated_at: string;
  link_count: number;
  subfolder_count: number;
  subfolders?: Folder[];
}

export interface FolderCreate {
  name: string;
  color?: string;
  icon?: string;
  parent_folder_id?: string;
}

export interface FolderUpdate {
  name?: string;
  color?: string;
  icon?: string;
  parent_folder_id?: string;
}

export interface FolderTree {
  folders: Folder[];
}

export interface AssignLinkData {
  url_id: string;
  folder_id: string;
}

export interface FolderLinks {
  folder_id: string;
  link_ids: string[];
  count: number;
}

// ==================== API Functions ====================

/**
 * Get all folders
 */
export async function getAllFolders(): Promise<Folder[]> {
  const response = await fetch(`${API_URL}/folders/`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch folders');
  }

  return response.json();
}

/**
 * Get folder tree structure
 */
export async function getFolderTree(): Promise<FolderTree> {
  const response = await fetch(`${API_URL}/folders/tree`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch folder tree');
  }

  return response.json();
}

/**
 * Get folder by ID
 */
export async function getFolder(folderId: string): Promise<Folder> {
  const response = await fetch(`${API_URL}/folders/${folderId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch folder');
  }

  return response.json();
}

/**
 * Create new folder
 */
export async function createFolder(data: FolderCreate): Promise<Folder> {
  const response = await fetch(`${API_URL}/folders/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: data.name,
      color: data.color || '#00fff5',
      icon: data.icon || '📁',
      parent_folder_id: data.parent_folder_id,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create folder');
  }

  return response.json();
}

/**
 * Update folder
 */
export async function updateFolder(
  folderId: string,
  data: FolderUpdate
): Promise<Folder> {
  const response = await fetch(`${API_URL}/folders/${folderId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update folder');
  }

  return response.json();
}

/**
 * Delete folder
 */
export async function deleteFolder(
  folderId: string,
  deleteLinks: boolean = false
): Promise<void> {
  const response = await fetch(
    `${API_URL}/folders/${folderId}?delete_links=${deleteLinks}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete folder');
  }
}

/**
 * Assign link to folder
 */
export async function assignLinkToFolder(
  urlId: string,
  folderId: string
): Promise<void> {
  const response = await fetch(`${API_URL}/folders/assign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url_id: urlId,
      folder_id: folderId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to assign link to folder');
  }
}

/**
 * Remove link from folder
 */
export async function removeLinkFromFolder(
  urlId: string,
  folderId: string
): Promise<void> {
  const response = await fetch(`${API_URL}/folders/assign`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url_id: urlId,
      folder_id: folderId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to remove link from folder');
  }
}

/**
 * Get all links in a folder
 */
export async function getFolderLinks(folderId: string): Promise<FolderLinks> {
  const response = await fetch(`${API_URL}/folders/${folderId}/links`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch folder links');
  }

  return response.json();
}

/**
 * Get folder analytics
 */
export async function getFolderAnalytics(folderId: string): Promise<any> {
  const response = await fetch(`${API_URL}/folders/${folderId}/analytics`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch folder analytics');
  }

  return response.json();
}
