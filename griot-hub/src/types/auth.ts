// Authentication types for Griot Hub

// Role type
export interface AuthRole {
  id: string
  name: string
  permissions: string[]
  description?: string
  isSystem?: boolean
}

// Team summary type
export interface AuthTeamSummary {
  id: string
  name: string
}

// Auth user type (from API)
export interface AuthUser {
  id: string
  email: string
  name: string
  avatar: string | null
  role: AuthRole
  team: AuthTeamSummary | null
  status: 'active' | 'pending' | 'deactivated'
  lastLoginAt: string | null
  createdAt: string
}

// Legacy support - simple user format
export interface LegacyAuthUser {
  id: string
  email: string | null
  name: string | null
  roles: string[]
}

export interface AuthTokens {
  accessToken: string
  refreshToken?: string
  expiresIn?: number
  expiresAt?: string
}

// Login credentials - email/password based
export interface LoginCredentials {
  email: string
  password: string
  rememberMe?: boolean
}

// Signup data
export interface SignupData {
  name: string
  email: string
  password: string
  confirmPassword: string
  acceptTerms?: boolean
}

// Legacy login credentials (for backward compatibility)
export interface LegacyLoginCredentials {
  userId: string
  roles?: string[]
}

export interface AuthState {
  user: AuthUser | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
}

// API Response types
export interface AuthResponse {
  user: AuthUser
  token: string
  expiresAt: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserInfoResponse {
  id: string
  roles: string[]
  auth_method: string
}

// Error response
export interface AuthError {
  error: {
    code: string
    message: string
    details?: Array<{ field: string; message: string }>
  }
}
