/**
 * Authentication utilities
 * Simple token-based authentication
 */

const TOKEN_KEY = 'auth_token';

/**
 * Save authentication token to sessionStorage
 */
export function saveToken(token: string): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Get authentication token from sessionStorage
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove authentication token from sessionStorage
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Login with password
 */
export async function login(password: string): Promise<{ success: boolean; token?: string; error?: string }> {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.detail || 'Login failed',
      };
    }

    // Save token
    saveToken(data.token);

    return {
      success: true,
      token: data.token,
    };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: 'Network error',
    };
  }
}

/**
 * Logout - remove token and invalidate on server
 */
export async function logout(): Promise<void> {
  const token = getToken();

  if (token) {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  removeToken();
}

/**
 * Get Authorization header for API requests
 */
export function getAuthHeader(): Record<string, string> {
  const token = getToken();

  if (token) {
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  return {};
}
