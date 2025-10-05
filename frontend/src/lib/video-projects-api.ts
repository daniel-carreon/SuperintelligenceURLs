/**
 * Video Projects API Client
 * Handles video-centric project management and aggregated analytics
 */

import { getAuthHeader } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ==================== Types ====================

export interface VideoProjectCreate {
  title: string;
  youtube_url?: string;
  description?: string;
}

export interface VideoProjectUpdate {
  title?: string;
  youtube_url?: string;
  thumbnail_url?: string;
  description?: string;
}

export interface VideoProject {
  id: string;
  title: string;
  youtube_url?: string;
  youtube_video_id?: string;
  thumbnail_url?: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  total_links?: number;
  total_clicks?: number;
  unique_visitors?: number;
}

export interface VideoProjectAnalytics extends VideoProject {
  countries_reached: number;
  mobile_clicks: number;
  desktop_clicks: number;
  tablet_clicks: number;
  last_click_at?: string;
  first_click_at?: string;
}

export interface ProjectLink {
  id: string;
  short_code: string;
  original_url: string;
  title?: string;
  click_count: number;
  created_at: string;
  added_at: string;
}

export interface AssignLinkRequest {
  url_id: string;
  project_id: string;
}

export interface VideoPerformance {
  project_id: string;
  title: string;
  youtube_url?: string;
  thumbnail_url?: string;
  total_clicks: number;
  unique_visitors: number;
  total_links: number;
  created_at: string;
}

// ==================== API Functions ====================

/**
 * Create a new video project with YouTube metadata
 */
export async function createVideoProject(data: VideoProjectCreate): Promise<VideoProject> {
  const response = await fetch(`${API_URL}/video-projects/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create video project');
  }

  return response.json();
}

/**
 * Get all video projects with aggregated analytics
 */
export async function getAllVideoProjects(): Promise<VideoProject[]> {
  const response = await fetch(`${API_URL}/video-projects/`, {
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch video projects');
  }

  return response.json();
}

/**
 * Get video project by ID
 */
export async function getVideoProject(projectId: string): Promise<VideoProject> {
  const response = await fetch(`${API_URL}/video-projects/${projectId}`, {
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch video project');
  }

  return response.json();
}

/**
 * Update video project
 */
export async function updateVideoProject(
  projectId: string,
  data: VideoProjectUpdate
): Promise<VideoProject> {
  const response = await fetch(`${API_URL}/video-projects/${projectId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update video project');
  }

  return response.json();
}

/**
 * Delete video project
 */
export async function deleteVideoProject(projectId: string): Promise<void> {
  const response = await fetch(`${API_URL}/video-projects/${projectId}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete video project');
  }
}

/**
 * Assign link to video project
 */
export async function assignLinkToProject(urlId: string, projectId: string): Promise<void> {
  const response = await fetch(`${API_URL}/video-projects/assign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify({ url_id: urlId, project_id: projectId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to assign link to project');
  }
}

/**
 * Remove link from video project
 */
export async function removeLinkFromProject(urlId: string, projectId: string): Promise<void> {
  const response = await fetch(`${API_URL}/video-projects/assign`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify({ url_id: urlId, project_id: projectId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to remove link from project');
  }
}

/**
 * Get all links in a video project
 */
export async function getProjectLinks(projectId: string): Promise<ProjectLink[]> {
  const response = await fetch(`${API_URL}/video-projects/${projectId}/links`, {
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch project links');
  }

  const data = await response.json();
  return data.links || [];
}

/**
 * Get aggregated analytics for video project
 */
export async function getProjectAnalytics(projectId: string): Promise<VideoProjectAnalytics> {
  const response = await fetch(`${API_URL}/video-projects/${projectId}/analytics`, {
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch project analytics');
  }

  return response.json();
}

/**
 * Get video performance comparison
 */
export async function getVideoPerformanceComparison(limit: number = 10): Promise<VideoPerformance[]> {
  const response = await fetch(`${API_URL}/video-projects/performance/comparison?limit=${limit}`, {
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch video performance');
  }

  return response.json();
}

/**
 * Refresh analytics materialized view
 */
export async function refreshProjectAnalytics(): Promise<void> {
  const response = await fetch(`${API_URL}/video-projects/refresh-analytics`, {
    method: 'POST',
    headers: {
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to refresh analytics');
  }
}
