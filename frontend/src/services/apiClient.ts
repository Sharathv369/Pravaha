/**
 * Centralized API client for the PRAVAHA FastAPI backend.
 */

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail || message;
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function apiFetch<T>(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined | null>,
  options?: RequestInit
): Promise<T> {
  const url = new URL(endpoint.startsWith('/') ? `${API_BASE_URL}${endpoint}` : `${API_BASE_URL}/${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });
  }

  try {
    const res = await fetch(url.toString(), {
      ...options,
      headers: {
        'Accept': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      let detail = `HTTP Error ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson && errorJson.detail) {
          detail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // use fallback detail
      }
      throw new ApiError(res.status, `Request failed with status ${res.status}`, detail);
    }

    return (await res.json()) as T;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    const error = err as Error;
    if (error.name === 'AbortError') {
      throw error;
    }
    throw new ApiError(
      0,
      'Failed to connect to PRAVAHA backend. Ensure server is running at http://127.0.0.1:8000.',
      error.message
    );
  }
}

export const apiClient = {
  get: <T>(endpoint: string, params?: Record<string, string | number | boolean | undefined | null>, options?: RequestInit) =>
    apiFetch<T>(endpoint, params, { method: 'GET', ...options }),
  getBaseUrl: () => API_BASE_URL,
};

