// Mock auth data - shared between API routes and MSW handlers

// Role type
export interface Role {
  id: string
  name: string
  permissions: string[]
  description?: string
  isSystem: boolean
  userCount: number
  createdAt: string
}

// Team type
export interface TeamSummary {
  id: string
  name: string
}

// User type for auth
export interface AuthUser {
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
export const ADMIN_USER: AuthUser = {
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
// Note: This resets on server restart, which is fine for development
const mockUsersDb = new Map<string, { user: AuthUser; password: string }>()

// Initialize with admin user
mockUsersDb.set(ADMIN_USER.email, { user: ADMIN_USER, password: 'melly' })

// Add test users
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

// Generate a mock JWT token
export function generateMockToken(user: AuthUser): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64')
  const payload = Buffer.from(JSON.stringify({
    sub: user.id,
    email: user.email,
    name: user.name,
    role: user.role.name,
    roles: [user.role.name.toLowerCase()],
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
  })).toString('base64')
  const signature = Buffer.from('mock-signature').toString('base64')
  return `${header}.${payload}.${signature}`
}

// Store token
export function storeToken(token: string, user: AuthUser): void {
  tokenStore.set(token, user)
}

// Get user from token
export function getUserFromToken(token: string): AuthUser | null {
  return tokenStore.get(token) || null
}

// Remove token
export function removeToken(token: string): void {
  tokenStore.delete(token)
}

// Get user by email
export function getUserByEmail(email: string): { user: AuthUser; password: string } | undefined {
  return mockUsersDb.get(email.toLowerCase())
}

// Check if email exists
export function emailExists(email: string): boolean {
  return mockUsersDb.has(email.toLowerCase())
}

// Create new user
export function createUser(email: string, password: string, name: string): AuthUser {
  const newUser: AuthUser = {
    id: `user-${Date.now()}`,
    email: email.toLowerCase(),
    name,
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

  mockUsersDb.set(email.toLowerCase(), { user: newUser, password })
  return newUser
}

// Update user's last login
export function updateLastLogin(email: string): void {
  const record = mockUsersDb.get(email.toLowerCase())
  if (record) {
    record.user.lastLoginAt = new Date().toISOString()
  }
}
