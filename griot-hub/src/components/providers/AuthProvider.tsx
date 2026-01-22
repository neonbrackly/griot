'use client'

import * as React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import type {
  AuthContextValue,
  AuthState,
  AuthTokens,
  AuthUser,
  LoginCredentials,
  SignupData,
  AuthResponse,
  AuthError,
} from '@/types/auth'

const AUTH_STORAGE_KEY = 'griot_auth'
const PUBLIC_PATHS = ['/login', '/signup', '/forgot-password', '/reset-password']

// Create the context
const AuthContext = React.createContext<AuthContextValue | null>(null)

// Check if token is expired based on expiresAt timestamp
function isTokenExpired(expiresAt: string): boolean {
  // Add 30 second buffer
  return Date.now() >= new Date(expiresAt).getTime() - 30000
}

// Get auth data from storage
function getStoredAuth(): { tokens: AuthTokens; user: AuthUser } | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!stored) return null
    const data = JSON.parse(stored)
    // Check if token is expired
    if (data.tokens?.expiresAt && isTokenExpired(data.tokens.expiresAt)) {
      // Token expired, clear storage
      localStorage.removeItem(AUTH_STORAGE_KEY)
      return null
    }
    return data
  } catch {
    return null
  }
}

// Save auth data to storage
function saveAuth(tokens: AuthTokens, user: AuthUser): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ tokens, user }))
}

// Clear auth data from storage
function clearAuth(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [state, setState] = React.useState<AuthState>({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: true,
  })

  // Initialize auth state from storage
  React.useEffect(() => {
    const stored = getStoredAuth()
    if (stored) {
      setState({
        user: stored.user,
        tokens: stored.tokens,
        isAuthenticated: true,
        isLoading: false,
      })
    } else {
      setState((prev) => ({ ...prev, isLoading: false }))
    }
  }, [])

  // Redirect to login if not authenticated and on protected route
  React.useEffect(() => {
    if (state.isLoading) return

    const isPublicPath = PUBLIC_PATHS.some((path) => pathname?.startsWith(path))

    if (!state.isAuthenticated && !isPublicPath) {
      router.push('/login')
    } else if (state.isAuthenticated && (pathname === '/login' || pathname === '/signup')) {
      router.push('/')
    }
  }, [state.isAuthenticated, state.isLoading, pathname, router])

  const login = React.useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true }))

    try {
      // Use local /api route which proxies to registry when NEXT_PUBLIC_USE_MOCKS=false
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const errorData: AuthError = await response.json().catch(() => ({
          error: { code: 'UNKNOWN', message: 'Login failed' },
        }))
        throw new Error(errorData.error?.message || 'Login failed')
      }

      const data: AuthResponse = await response.json()

      const tokens: AuthTokens = {
        accessToken: data.token,
        expiresAt: data.expiresAt,
      }

      saveAuth(tokens, data.user)

      setState({
        user: data.user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      })

      router.push('/')
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }))
      throw error
    }
  }, [router])

  const signup = React.useCallback(async (data: SignupData) => {
    setState((prev) => ({ ...prev, isLoading: true }))

    try {
      // Use local /api route which proxies to registry when NEXT_PUBLIC_USE_MOCKS=false
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData: AuthError = await response.json().catch(() => ({
          error: { code: 'UNKNOWN', message: 'Signup failed' },
        }))
        throw new Error(errorData.error?.message || 'Signup failed')
      }

      const responseData: AuthResponse = await response.json()

      const tokens: AuthTokens = {
        accessToken: responseData.token,
        expiresAt: responseData.expiresAt,
      }

      saveAuth(tokens, responseData.user)

      setState({
        user: responseData.user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      })

      router.push('/')
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }))
      throw error
    }
  }, [router])

  const logout = React.useCallback(async () => {
    // Call logout endpoint (best effort) - registry returns 204 No Content
    try {
      // Use local /api route which proxies to registry when NEXT_PUBLIC_USE_MOCKS=false
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: state.tokens?.accessToken
          ? { Authorization: `Bearer ${state.tokens.accessToken}` }
          : undefined,
      })
      // Note: Registry API returns 204 No Content on successful logout
    } catch {
      // Ignore logout API errors - still clear local state
    }

    clearAuth()
    setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
    })
    router.push('/login')
  }, [router, state.tokens?.accessToken])

  const refreshAccessToken = React.useCallback(async () => {
    // For now, just logout if refresh is needed
    // In a real app, you'd call a refresh endpoint
    logout()
  }, [logout])

  const value = React.useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      signup,
      logout,
      refreshAccessToken,
    }),
    [state, login, signup, logout, refreshAccessToken]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Hook to use auth context
export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Hook to get current user
export function useCurrentUser(): AuthUser | null {
  const { user } = useAuth()
  return user
}

// Hook to check if user has a specific role
export function useHasRole(roleName: string): boolean {
  const { user } = useAuth()
  return user?.role?.name?.toLowerCase() === roleName.toLowerCase()
}

// Hook to check if user is admin
export function useIsAdmin(): boolean {
  return useHasRole('Admin')
}

// Hook to check if user has a specific permission
export function useHasPermission(permission: string): boolean {
  const { user } = useAuth()
  // If permissions array is not provided (e.g., from /auth/me), fall back to role-based check
  if (!user?.role?.permissions) {
    // Admin role has all permissions
    return user?.role?.name?.toLowerCase() === 'admin'
  }
  return user.role.permissions.includes('*') || user.role.permissions.includes(permission)
}
