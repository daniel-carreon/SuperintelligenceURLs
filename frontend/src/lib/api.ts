/**
 * API Client for SuperintelligenceURLs Backend
 * Handles all HTTP requests to the FastAPI backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ==================== Types ====================

export interface URLCreate {
  original_url: string;
  title?: string;
  folder_id?: string;
  is_active?: boolean;
}

export interface URLResponse {
  id: string;
  short_code: string;
  original_url: string;
  title?: string;
  domain?: string;
  is_active: boolean;
  created_at: string;
  click_count: number;
  last_clicked_at?: string;
  folder_id?: string;
}

export interface ClickData {
  id: string;
  url_id: string;
  short_code: string;
  ip_address: string;
  user_agent: string;
  referer?: string;
  country_code?: string;
  country_name?: string;
  city?: string;
  device_type?: string;
  browser_name?: string;
  os_name?: string;
  referrer_domain?: string;
  referrer_type?: string;
  referrer_source?: string;
  video_id?: string;
  video_platform?: string;
  platform?: string;
  is_returning_visitor?: boolean;
  session_id?: string;
  clicked_at: string;
}

export interface DeviceBreakdown {
  device_type: string;
  count: number;
  percentage: number;
}

export interface CountryBreakdown {
  country_name: string;
  country_code: string;
  count: number;
  percentage: number;
}

export interface CityBreakdown {
  city: string;
  country_name: string;
  count: number;
  percentage: number;
}

export interface PlatformBreakdown {
  platform: string;
  count: number;
  percentage: number;
}

export interface VideoSource {
  video_id: string;
  video_platform: string;
  clicks: number;
}

export interface TimePattern {
  hour: number;
  clicks: number;
}

export interface ReferrerBreakdown {
  referrer_type: string;
  count: number;
  percentage: number;
}

export interface AnalyticsResponse {
  short_code: string;
  original_url: string;
  created_at: string;
  total_clicks: number;
  unique_visitors: number;
  returning_visitors: number;
  device_breakdown: DeviceBreakdown[];
  country_breakdown: CountryBreakdown[];
  city_breakdown: CityBreakdown[];
  platform_breakdown: PlatformBreakdown[];
  video_sources: VideoSource[];
  time_patterns: TimePattern[];
  referrer_breakdown: ReferrerBreakdown[];
  recent_clicks: ClickData[];
}

// ==================== API Functions ====================

/**
 * Create a shortened URL
 */
export async function createShortURL(data: URLCreate): Promise<URLResponse> {
  const response = await fetch(`${API_URL}/shorten`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create short URL');
  }

  return response.json();
}

/**
 * Get all URLs
 */
export async function getAllURLs(): Promise<URLResponse[]> {
  const response = await fetch(`${API_URL}/urls/all`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch URLs');
  }

  const data = await response.json();
  return data.urls || [];
}

/**
 * Get analytics for a specific short code
 */
export async function getAnalytics(shortCode: string): Promise<AnalyticsResponse> {
  const response = await fetch(`${API_URL}/analytics/${shortCode}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch analytics');
  }

  return response.json();
}

/**
 * Delete a shortened URL
 */
export async function deleteURL(shortCode: string): Promise<void> {
  const response = await fetch(`${API_URL}/${shortCode}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete URL');
  }
}

/**
 * Health check
 */
export async function healthCheck() {
  const response = await fetch(`${API_URL}/`);

  if (!response.ok) {
    throw new Error('API is not responding');
  }

  return response.json();
}
