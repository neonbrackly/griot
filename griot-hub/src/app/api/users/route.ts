import { NextRequest, NextResponse } from 'next/server'
import {
  getUserByEmail,
  createUser,
  generateMockToken,
  storeToken,
  ADMIN_USER,
} from '@/lib/auth/mock-data'
import { getAllRoles, getRoleByName } from '@/lib/auth/mock-roles'

// In-memory users list (extends the auth mock data)
const usersListDb = new Map<string, any>()

// Initialize with users from auth mock
function initializeUsersList() {
  if (usersListDb.size === 0) {
    // Add admin
    usersListDb.set(ADMIN_USER.id, {
      id: ADMIN_USER.id,
      email: ADMIN_USER.email,
      name: ADMIN_USER.name,
      avatar: ADMIN_USER.avatar,
      role: ADMIN_USER.role.name,
      team: ADMIN_USER.team?.name || null,
      status: ADMIN_USER.status,
      lastLoginAt: ADMIN_USER.lastLoginAt,
      createdAt: ADMIN_USER.createdAt,
    })

    // Add other users
    const otherUsers = [
      {
        id: 'user-002',
        email: 'jane@griot.com',
        name: 'Jane Doe',
        avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100',
        role: 'Editor',
        team: 'Platform Team',
        status: 'active',
        lastLoginAt: new Date(Date.now() - 3600000).toISOString(),
        createdAt: '2024-02-15T00:00:00Z',
      },
      {
        id: 'user-003',
        email: 'viewer@griot.com',
        name: 'View Only',
        avatar: null,
        role: 'Viewer',
        team: 'CRM Team',
        status: 'active',
        lastLoginAt: null,
        createdAt: '2024-06-01T00:00:00Z',
      },
      {
        id: 'user-004',
        email: 'john.smith@griot.com',
        name: 'John Smith',
        avatar: null,
        role: 'Editor',
        team: 'Analytics Team',
        status: 'active',
        lastLoginAt: new Date(Date.now() - 86400000).toISOString(),
        createdAt: '2024-04-01T00:00:00Z',
      },
      {
        id: 'user-005',
        email: 'sarah.johnson@griot.com',
        name: 'Sarah Johnson',
        avatar: null,
        role: 'Analyst',
        team: 'Analytics Team',
        status: 'pending',
        lastLoginAt: null,
        createdAt: '2024-07-01T00:00:00Z',
      },
    ]

    otherUsers.forEach((user) => {
      usersListDb.set(user.id, user)
    })
  }
}

// GET /api/users - List all users
export async function GET(request: NextRequest) {
  try {
    initializeUsersList()

    const { searchParams } = new URL(request.url)
    const search = searchParams.get('search')?.toLowerCase()
    const role = searchParams.get('role')
    const status = searchParams.get('status')

    let users = Array.from(usersListDb.values())

    // Apply filters
    if (search) {
      users = users.filter(
        (u) =>
          u.name.toLowerCase().includes(search) ||
          u.email.toLowerCase().includes(search)
      )
    }

    if (role && role !== 'all') {
      users = users.filter((u) => u.role.toLowerCase() === role.toLowerCase())
    }

    if (status && status !== 'all') {
      users = users.filter((u) => u.status === status)
    }

    return NextResponse.json({ data: users })
  } catch (error) {
    console.error('[API] Get users error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to fetch users' } },
      { status: 500 }
    )
  }
}

// POST /api/users - Invite/create a new user
export async function POST(request: NextRequest) {
  try {
    initializeUsersList()

    const body = await request.json()

    if (!body.email) {
      return NextResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Email is required' } },
        { status: 422 }
      )
    }

    // Check if user already exists
    const existingUser = Array.from(usersListDb.values()).find(
      (u) => u.email.toLowerCase() === body.email.toLowerCase()
    )

    if (existingUser) {
      return NextResponse.json(
        { error: { code: 'CONFLICT', message: 'User with this email already exists' } },
        { status: 409 }
      )
    }

    const newUser = {
      id: `user-${Date.now()}`,
      email: body.email.toLowerCase(),
      name: body.name || body.email.split('@')[0],
      avatar: null,
      role: body.role || 'Viewer',
      team: body.team || null,
      status: 'pending',
      lastLoginAt: null,
      createdAt: new Date().toISOString(),
    }

    usersListDb.set(newUser.id, newUser)

    return NextResponse.json(newUser, { status: 201 })
  } catch (error) {
    console.error('[API] Create user error:', error)
    return NextResponse.json(
      { error: { code: 'INTERNAL_ERROR', message: 'Failed to create user' } },
      { status: 500 }
    )
  }
}
