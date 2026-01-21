import { http, HttpResponse, delay } from 'msw'
import { mockUsersDb, ADMIN_USER, type AuthUser, type Role } from './auth'
import { rolesDb } from './roles'

// Get all users from the auth database
function getAllUsers(): AuthUser[] {
  return Array.from(mockUsersDb.values()).map(record => record.user)
}

export const userHandlers = [
  // Get current user
  http.get('/api/users/me', async () => {
    await delay(200)
    return HttpResponse.json(ADMIN_USER)
  }),

  // List all users
  http.get('/api/users', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const role = url.searchParams.get('role')
    const teamId = url.searchParams.get('teamId')
    const status = url.searchParams.get('status')
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '20')

    let filtered = getAllUsers()

    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(
        (u) =>
          u.name.toLowerCase().includes(searchLower) ||
          u.email.toLowerCase().includes(searchLower)
      )
    }

    if (role && role !== 'all') {
      filtered = filtered.filter((u) => u.role.name.toLowerCase() === role.toLowerCase())
    }

    if (teamId && teamId !== 'all') {
      filtered = filtered.filter((u) => u.team?.id === teamId)
    }

    if (status && status !== 'all') {
      filtered = filtered.filter((u) => u.status === status)
    }

    const total = filtered.length
    const startIndex = (page - 1) * limit
    const paginatedData = filtered.slice(startIndex, startIndex + limit)

    return HttpResponse.json({
      data: paginatedData,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    })
  }),

  // Get user by ID
  http.get('/api/users/:id', async ({ params }) => {
    await delay(200)

    const users = getAllUsers()
    const user = users.find((u) => u.id === params.id)
    if (!user) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'User not found' } },
        { status: 404 }
      )
    }

    return HttpResponse.json(user)
  }),

  // Update user
  http.patch('/api/users/:id', async ({ params, request }) => {
    await delay(300)

    const userId = params.id as string
    let foundRecord: { user: AuthUser; password: string } | undefined

    for (const [email, record] of mockUsersDb.entries()) {
      if (record.user.id === userId) {
        foundRecord = record
        break
      }
    }

    if (!foundRecord) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'User not found' } },
        { status: 404 }
      )
    }

    const body = (await request.json()) as Partial<{
      name: string
      email: string
      avatar: string
    }>

    const updated: AuthUser = {
      ...foundRecord.user,
      ...(body.name && { name: body.name }),
      ...(body.email && { email: body.email }),
      ...(body.avatar !== undefined && { avatar: body.avatar }),
    }

    // Update in db
    mockUsersDb.set(foundRecord.user.email, { user: updated, password: foundRecord.password })

    return HttpResponse.json(updated)
  }),

  // Change user role
  http.patch('/api/users/:id/role', async ({ params, request }) => {
    await delay(300)

    const userId = params.id as string
    let foundRecord: { user: AuthUser; password: string } | undefined
    let foundEmail: string | undefined

    for (const [email, record] of mockUsersDb.entries()) {
      if (record.user.id === userId) {
        foundRecord = record
        foundEmail = email
        break
      }
    }

    if (!foundRecord || !foundEmail) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'User not found' } },
        { status: 404 }
      )
    }

    const body = (await request.json()) as { roleId: string }

    const newRole = rolesDb.get(body.roleId)
    if (!newRole) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found' } },
        { status: 404 }
      )
    }

    // Convert to AuthUser role format
    const roleForUser: Role = {
      id: newRole.id,
      name: newRole.name,
      permissions: newRole.permissions.map(p => p.id),
      description: newRole.description,
      isSystem: newRole.isSystem,
      userCount: newRole.userCount,
      createdAt: newRole.createdAt,
    }

    const updated: AuthUser = {
      ...foundRecord.user,
      role: roleForUser,
    }

    // Update in db
    mockUsersDb.set(foundEmail, { user: updated, password: foundRecord.password })

    return HttpResponse.json(updated)
  }),

  // Invite user
  http.post('/api/users/invite', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as {
      email: string
      roleId?: string
      teamId?: string
    }

    if (!body.email) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Email is required' } },
        { status: 422 }
      )
    }

    // Check if user already exists
    if (mockUsersDb.has(body.email.toLowerCase())) {
      return HttpResponse.json(
        { error: { code: 'CONFLICT', message: 'User with this email already exists' } },
        { status: 409 }
      )
    }

    // Get role (default to viewer)
    const roleId = body.roleId || 'role-viewer'
    const role = rolesDb.get(roleId)

    const newUser: AuthUser = {
      id: `user-${Date.now()}`,
      email: body.email.toLowerCase(),
      name: body.email.split('@')[0], // Use email prefix as name
      avatar: null,
      role: role ? {
        id: role.id,
        name: role.name,
        permissions: role.permissions.map(p => p.id),
        description: role.description,
        isSystem: role.isSystem,
        userCount: role.userCount,
        createdAt: role.createdAt,
      } : {
        id: 'role-viewer',
        name: 'Viewer',
        permissions: ['contracts:read', 'assets:read', 'reports:view'],
        description: 'Read-only access',
        isSystem: true,
        userCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
      },
      team: body.teamId ? { id: body.teamId, name: 'Unknown Team' } : null,
      status: 'pending',
      lastLoginAt: null,
      createdAt: new Date().toISOString(),
    }

    // Store user with default password (they'll set it when accepting invite)
    mockUsersDb.set(body.email.toLowerCase(), { user: newUser, password: 'pending-invite' })

    return HttpResponse.json(newUser, { status: 201 })
  }),

  // Deactivate user
  http.delete('/api/users/:id', async ({ params }) => {
    await delay(300)

    const userId = params.id as string
    let foundRecord: { user: AuthUser; password: string } | undefined
    let foundEmail: string | undefined

    for (const [email, record] of mockUsersDb.entries()) {
      if (record.user.id === userId) {
        foundRecord = record
        foundEmail = email
        break
      }
    }

    if (!foundRecord || !foundEmail) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'User not found' } },
        { status: 404 }
      )
    }

    // Don't allow deactivating the admin
    if (foundRecord.user.id === ADMIN_USER.id) {
      return HttpResponse.json(
        { error: { code: 'FORBIDDEN', message: 'Cannot deactivate the admin user' } },
        { status: 403 }
      )
    }

    const updated: AuthUser = {
      ...foundRecord.user,
      status: 'deactivated',
    }

    mockUsersDb.set(foundEmail, { user: updated, password: foundRecord.password })

    return HttpResponse.json({ message: 'User deactivated successfully' })
  }),
]
