// API Client Configuration
import { QueryClient } from '@tanstack/react-query'

// Base API URL - uses real API or falls back to /api for mocking
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

// Auth storage key - must match AuthProvider
const AUTH_STORAGE_KEY = 'griot_auth'

// Get auth token from storage
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!stored) return null
    const data = JSON.parse(stored)
    return data.tokens?.accessToken || null
  } catch {
    return null
  }
}

// Create the Query Client with default options
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
        retry: (failureCount, error) => {
          // Don't retry on 4xx errors
          if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
            return false
          }
          return failureCount < 3
        },
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// Custom API Error class
export class ApiError extends Error {
  status: number
  code: string
  details?: Record<string, unknown>

  constructor(
    message: string,
    status: number,
    code: string = 'UNKNOWN_ERROR',
    details?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

// HTTP client wrapper
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  // Get auth token and include in headers
  const token = getAuthToken()
  const authHeaders: Record<string, string> = token
    ? { Authorization: `Bearer ${token}` }
    : {}

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...options.headers,
    },
  }

  try {
    const response = await fetch(url, config)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new ApiError(
        errorData.message || `HTTP error ${response.status}`,
        response.status,
        errorData.code,
        errorData.details
      )
    }

    // Handle empty responses
    const text = await response.text()
    if (!text) return {} as T

    return JSON.parse(text) as T
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    // Network or parsing errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      0,
      'NETWORK_ERROR'
    )
  }
}

// API methods
export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    }),

  put: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  patch: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
}

// Query key factories
export const queryKeys = {
  // Contracts
  contracts: {
    all: ['contracts'] as const,
    lists: () => [...queryKeys.contracts.all, 'list'] as const,
    list: (filters: Record<string, unknown>) =>
      [...queryKeys.contracts.lists(), filters] as const,
    details: () => [...queryKeys.contracts.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.contracts.details(), id] as const,
  },

  // Assets
  assets: {
    all: ['assets'] as const,
    lists: () => [...queryKeys.assets.all, 'list'] as const,
    list: (filters: Record<string, unknown>) =>
      [...queryKeys.assets.lists(), filters] as const,
    details: () => [...queryKeys.assets.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.assets.details(), id] as const,
  },

  // Connections
  connections: {
    all: ['connections'] as const,
    lists: () => [...queryKeys.connections.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.connections.lists(), filters] as const,
    details: () => [...queryKeys.connections.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.connections.details(), id] as const,
    browse: (id: string) =>
      [...queryKeys.connections.all, 'browse', id] as const,
  },

  // Issues
  issues: {
    all: ['issues'] as const,
    lists: () => [...queryKeys.issues.all, 'list'] as const,
    list: (filters: Record<string, unknown>) =>
      [...queryKeys.issues.lists(), filters] as const,
    details: () => [...queryKeys.issues.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.issues.details(), id] as const,
  },

  // Dashboard
  dashboard: {
    all: ['dashboard'] as const,
    metrics: ['dashboard', 'metrics'] as const,
    timeline: (filters: Record<string, unknown>) =>
      ['dashboard', 'timeline', filters] as const,
    recommendations: ['dashboard', 'recommendations'] as const,
  },

  // Runs
  runs: {
    all: ['runs'] as const,
    byDate: (date: string) => [...queryKeys.runs.all, 'by-date', date] as const,
    detail: (date: string, runId: string) =>
      [...queryKeys.runs.all, 'detail', date, runId] as const,
  },

  // Tasks
  tasks: {
    all: ['tasks'] as const,
    my: () => [...queryKeys.tasks.all, 'my'] as const,
  },

  // Users
  users: {
    all: ['users'] as const,
    current: () => [...queryKeys.users.all, 'current'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.users.all, 'list', filters] as const,
  },

  // Teams
  teams: {
    all: ['teams'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.teams.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.teams.all, 'detail', id] as const,
  },

  // Notifications
  notifications: {
    all: ['notifications'] as const,
    list: () => [...queryKeys.notifications.all, 'list'] as const,
    unreadCount: () => [...queryKeys.notifications.all, 'unread'] as const,
  },

  // Search
  search: {
    all: ['search'] as const,
    global: (query: string) => [...queryKeys.search.all, 'global', query] as const,
  },
}
