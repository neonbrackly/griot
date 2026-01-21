import { http, HttpResponse, delay } from 'msw'

// Types for auth
interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
}

interface SignupRequest {
  name: string
  email: string
  password: string
  confirmPassword: string
  acceptTerms?: boolean
}

interface ForgotPasswordRequest {
  email: string
}

interface ResetPasswordRequest {
  token: string
  password: string
  confirmPassword: string
}

// Role type
interface Role {
  id: string
  name: string
  permissions: string[]
  description?: string
  isSystem: boolean
  userCount: number
  createdAt: string
}

// Team type
interface TeamSummary {
  id: string
  name: string
}

// User type for auth
interface AuthUser {
  id: string
  email: string
  name: string
  avatar: string | null
  role: Role
  team: TeamSummary | null
  status: 'active' | 'pending' | 'deactivated'
  lastLoginAt: string | null
  createdAt: string
}

// Hardcoded admin user
const ADMIN_USER: AuthUser = {
  id: 'user-admin-001',
  email: 'brackly@griot.com',
  name: 'Brackly Murunga',
  avatar: null,
  role: {
    id: 'role-admin',
    name: 'Admin',
    permissions: ['*'],
    description: 'Full system access',
    isSystem: true,
    userCount: 1,
    createdAt: '2024-01-01T00:00:00Z',
  },
  team: { id: 'team-001', name: 'Platform Team' },
  status: 'active',
  lastLoginAt: new Date().toISOString(),
  createdAt: '2024-01-01T00:00:00Z',
}

// Mock users database (in-memory)
const mockUsersDb = new Map<string, { user: AuthUser; password: string }>()

// Initialize with admin user
mockUsersDb.set(ADMIN_USER.email, { user: ADMIN_USER, password: 'melly' })

// Add some test users
const testUsers: Array<{ user: AuthUser; password: string }> = [
  {
    user: {
      id: 'user-002',
      email: 'jane@griot.com',
      name: 'Jane Doe',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100',
      role: {
        id: 'role-editor',
        name: 'Editor',
        permissions: ['contracts:read', 'contracts:create', 'contracts:edit', 'assets:read', 'assets:create'],
        description: 'Can create and edit contracts and assets',
        isSystem: true,
        userCount: 5,
        createdAt: '2024-01-01T00:00:00Z',
      },
      team: { id: 'team-001', name: 'Platform Team' },
      status: 'active',
      lastLoginAt: new Date(Date.now() - 3600000).toISOString(),
      createdAt: '2024-02-15T00:00:00Z',
    },
    password: 'password123',
  },
  {
    user: {
      id: 'user-003',
      email: 'viewer@griot.com',
      name: 'View Only',
      avatar: null,
      role: {
        id: 'role-viewer',
        name: 'Viewer',
        permissions: ['contracts:read', 'assets:read', 'reports:view'],
        description: 'Read-only access',
        isSystem: true,
        userCount: 10,
        createdAt: '2024-01-01T00:00:00Z',
      },
      team: { id: 'team-002', name: 'CRM Team' },
      status: 'active',
      lastLoginAt: null,
      createdAt: '2024-06-01T00:00:00Z',
    },
    password: 'password123',
  },
]

// Add test users to database
testUsers.forEach(({ user, password }) => {
  mockUsersDb.set(user.email, { user, password })
})

// Token storage (simulates backend token validation)
const tokenStore = new Map<string, AuthUser>()
const resetTokens = new Map<string, { email: string; expiresAt: number }>()

// Generate a mock JWT token
function generateMockToken(user: AuthUser): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const payload = btoa(JSON.stringify({
    sub: user.id,
    email: user.email,
    name: user.name,
    role: user.role.name,
    roles: [user.role.name.toLowerCase()],
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
  }))
  const signature = btoa('mock-signature')
  return `${header}.${payload}.${signature}`
}

// Extract user from Authorization header
function getUserFromToken(request: Request): AuthUser | null {
  const authHeader = request.headers.get('Authorization')
  if (!authHeader?.startsWith('Bearer ')) {
    return null
  }
  const token = authHeader.substring(7)
  return tokenStore.get(token) || null
}

export const authHandlers = [
  // Login with email/password
  http.post('/api/auth/login', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as LoginRequest

    // Validate required fields
    if (!body.email || !body.password) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email and password are required',
            details: [
              ...(!body.email ? [{ field: 'email', message: 'Email is required' }] : []),
              ...(!body.password ? [{ field: 'password', message: 'Password is required' }] : []),
            ],
          },
        },
        { status: 422 }
      )
    }

    // Find user by email
    const userRecord = mockUsersDb.get(body.email.toLowerCase())

    if (!userRecord || userRecord.password !== body.password) {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid email or password',
          },
        },
        { status: 401 }
      )
    }

    // Check if user is deactivated
    if (userRecord.user.status === 'deactivated') {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Your account has been deactivated. Please contact an administrator.',
          },
        },
        { status: 401 }
      )
    }

    // Generate token
    const token = generateMockToken(userRecord.user)
    tokenStore.set(token, userRecord.user)

    // Update last login
    userRecord.user.lastLoginAt = new Date().toISOString()

    return HttpResponse.json({
      user: userRecord.user,
      token,
      expiresAt: new Date(Date.now() + 86400000).toISOString(), // 24 hours
    })
  }),

  // Signup
  http.post('/api/auth/signup', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as SignupRequest

    // Validate required fields
    const errors: Array<{ field: string; message: string }> = []
    if (!body.name) errors.push({ field: 'name', message: 'Name is required' })
    if (!body.email) errors.push({ field: 'email', message: 'Email is required' })
    if (!body.password) errors.push({ field: 'password', message: 'Password is required' })
    if (body.password !== body.confirmPassword) {
      errors.push({ field: 'confirmPassword', message: 'Passwords do not match' })
    }
    if (body.password && body.password.length < 8) {
      errors.push({ field: 'password', message: 'Password must be at least 8 characters' })
    }

    if (errors.length > 0) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            details: errors,
          },
        },
        { status: 422 }
      )
    }

    // Check if email already exists
    if (mockUsersDb.has(body.email.toLowerCase())) {
      return HttpResponse.json(
        {
          error: {
            code: 'CONFLICT',
            message: 'An account with this email already exists',
          },
        },
        { status: 409 }
      )
    }

    // Create new user
    const newUser: AuthUser = {
      id: `user-${Date.now()}`,
      email: body.email.toLowerCase(),
      name: body.name,
      avatar: null,
      role: {
        id: 'role-viewer',
        name: 'Viewer',
        permissions: ['contracts:read', 'assets:read', 'reports:view'],
        description: 'Read-only access',
        isSystem: true,
        userCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
      },
      team: null,
      status: 'active',
      lastLoginAt: new Date().toISOString(),
      createdAt: new Date().toISOString(),
    }

    // Store user
    mockUsersDb.set(body.email.toLowerCase(), { user: newUser, password: body.password })

    // Generate token
    const token = generateMockToken(newUser)
    tokenStore.set(token, newUser)

    return HttpResponse.json(
      {
        user: newUser,
        token,
        expiresAt: new Date(Date.now() + 86400000).toISOString(),
      },
      { status: 201 }
    )
  }),

  // Logout
  http.post('/api/auth/logout', async ({ request }) => {
    await delay(200)

    const authHeader = request.headers.get('Authorization')
    if (authHeader?.startsWith('Bearer ')) {
      const token = authHeader.substring(7)
      tokenStore.delete(token)
    }

    return HttpResponse.json({ message: 'Logged out successfully' })
  }),

  // Get current user
  http.get('/api/auth/me', async ({ request }) => {
    await delay(200)

    const user = getUserFromToken(request)

    if (!user) {
      return HttpResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Not authenticated',
          },
        },
        { status: 401 }
      )
    }

    return HttpResponse.json(user)
  }),

  // Forgot password
  http.post('/api/auth/forgot-password', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as ForgotPasswordRequest

    if (!body.email) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Email is required',
          },
        },
        { status: 422 }
      )
    }

    // Generate reset token (if user exists)
    if (mockUsersDb.has(body.email.toLowerCase())) {
      const resetToken = `reset-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      resetTokens.set(resetToken, {
        email: body.email.toLowerCase(),
        expiresAt: Date.now() + 3600000, // 1 hour
      })
      console.log('[Mock] Reset token generated:', resetToken)
    }

    // Always return success (for security - don't reveal if email exists)
    return HttpResponse.json({
      message: 'If an account with that email exists, a reset link has been sent.',
    })
  }),

  // Reset password
  http.post('/api/auth/reset-password', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as ResetPasswordRequest

    // Validate fields
    const errors: Array<{ field: string; message: string }> = []
    if (!body.token) errors.push({ field: 'token', message: 'Reset token is required' })
    if (!body.password) errors.push({ field: 'password', message: 'Password is required' })
    if (body.password !== body.confirmPassword) {
      errors.push({ field: 'confirmPassword', message: 'Passwords do not match' })
    }
    if (body.password && body.password.length < 8) {
      errors.push({ field: 'password', message: 'Password must be at least 8 characters' })
    }

    if (errors.length > 0) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            details: errors,
          },
        },
        { status: 422 }
      )
    }

    // Validate token
    const resetData = resetTokens.get(body.token)
    if (!resetData || resetData.expiresAt < Date.now()) {
      return HttpResponse.json(
        {
          error: {
            code: 'INVALID_TOKEN',
            message: 'Invalid or expired reset token',
          },
        },
        { status: 400 }
      )
    }

    // Update password
    const userRecord = mockUsersDb.get(resetData.email)
    if (userRecord) {
      mockUsersDb.set(resetData.email, { ...userRecord, password: body.password })
    }

    // Remove used token
    resetTokens.delete(body.token)

    return HttpResponse.json({
      message: 'Password has been reset successfully',
    })
  }),

  // OAuth endpoints (mock - just return success with mock user)
  http.post('/api/auth/oauth/google', async () => {
    await delay(500)
    return HttpResponse.json({
      message: 'Google OAuth is not yet configured. Please use email/password login.',
    }, { status: 501 })
  }),

  http.post('/api/auth/oauth/microsoft', async () => {
    await delay(500)
    return HttpResponse.json({
      message: 'Microsoft OAuth is not yet configured. Please use email/password login.',
    }, { status: 501 })
  }),

  http.post('/api/auth/oauth/sso', async () => {
    await delay(500)
    return HttpResponse.json({
      message: 'Enterprise SSO is not yet configured. Please contact your administrator.',
    }, { status: 501 })
  }),
]

// Export for use in other handlers
export { mockUsersDb, getUserFromToken, ADMIN_USER }
export type { AuthUser, Role }
