import { http, HttpResponse, delay } from 'msw'

// Permission type
interface Permission {
  id: string
  name: string
  category: 'contracts' | 'assets' | 'issues' | 'admin' | 'reports'
  description: string
}

// Role type
interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
  isSystem: boolean
  userCount: number
  createdAt: string
}

// All available permissions
const allPermissions: Permission[] = [
  // Contracts
  { id: 'contracts:read', name: 'View Contracts', category: 'contracts', description: 'View and search contracts' },
  { id: 'contracts:create', name: 'Create Contracts', category: 'contracts', description: 'Create new contracts' },
  { id: 'contracts:edit', name: 'Edit Contracts', category: 'contracts', description: 'Edit existing contracts' },
  { id: 'contracts:delete', name: 'Delete Contracts', category: 'contracts', description: 'Delete contracts' },
  { id: 'contracts:approve', name: 'Approve Contracts', category: 'contracts', description: 'Approve contract changes' },
  // Assets
  { id: 'assets:read', name: 'View Assets', category: 'assets', description: 'View and search data assets' },
  { id: 'assets:create', name: 'Create Assets', category: 'assets', description: 'Create new data assets' },
  { id: 'assets:edit', name: 'Edit Assets', category: 'assets', description: 'Edit existing assets' },
  { id: 'assets:delete', name: 'Delete Assets', category: 'assets', description: 'Delete data assets' },
  // Issues
  { id: 'issues:read', name: 'View Issues', category: 'issues', description: 'View and search issues' },
  { id: 'issues:create', name: 'Create Issues', category: 'issues', description: 'Create new issues' },
  { id: 'issues:edit', name: 'Edit Issues', category: 'issues', description: 'Edit and resolve issues' },
  { id: 'issues:assign', name: 'Assign Issues', category: 'issues', description: 'Assign issues to teams' },
  // Reports
  { id: 'reports:view', name: 'View Reports', category: 'reports', description: 'View analytics and reports' },
  { id: 'reports:export', name: 'Export Reports', category: 'reports', description: 'Export reports and data' },
  // Admin
  { id: 'admin:users', name: 'Manage Users', category: 'admin', description: 'View, invite, and manage users' },
  { id: 'admin:teams', name: 'Manage Teams', category: 'admin', description: 'Create and manage teams' },
  { id: 'admin:roles', name: 'Manage Roles', category: 'admin', description: 'Create and edit roles' },
  { id: 'admin:settings', name: 'System Settings', category: 'admin', description: 'Configure system settings' },
]

// Default roles
const mockRoles: Role[] = [
  {
    id: 'role-admin',
    name: 'Admin',
    description: 'Full system access with administrative privileges',
    permissions: allPermissions,
    isSystem: true,
    userCount: 1,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'role-editor',
    name: 'Editor',
    description: 'Can create and edit contracts and assets',
    permissions: allPermissions.filter(p =>
      ['contracts:read', 'contracts:create', 'contracts:edit', 'assets:read', 'assets:create', 'assets:edit', 'issues:read', 'issues:create', 'issues:edit', 'reports:view'].includes(p.id)
    ),
    isSystem: true,
    userCount: 5,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'role-viewer',
    name: 'Viewer',
    description: 'Read-only access to contracts, assets, and reports',
    permissions: allPermissions.filter(p =>
      ['contracts:read', 'assets:read', 'issues:read', 'reports:view'].includes(p.id)
    ),
    isSystem: true,
    userCount: 10,
    createdAt: '2024-01-01T00:00:00Z',
  },
]

// In-memory roles storage
const rolesDb = new Map<string, Role>()
mockRoles.forEach(role => rolesDb.set(role.id, role))

export const roleHandlers = [
  // List all roles
  http.get('/api/roles', async () => {
    await delay(200)
    return HttpResponse.json({
      data: Array.from(rolesDb.values()),
    })
  }),

  // Get single role
  http.get('/api/roles/:roleId', async ({ params }) => {
    await delay(150)

    const role = rolesDb.get(params.roleId as string)
    if (!role) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found' } },
        { status: 404 }
      )
    }

    return HttpResponse.json(role)
  }),

  // Create role
  http.post('/api/roles', async ({ request }) => {
    await delay(300)

    const body = (await request.json()) as {
      name: string
      description?: string
      permissions: string[]
    }

    if (!body.name) {
      return HttpResponse.json(
        { error: { code: 'VALIDATION_ERROR', message: 'Name is required' } },
        { status: 422 }
      )
    }

    const newRole: Role = {
      id: `role-${Date.now()}`,
      name: body.name,
      description: body.description || '',
      permissions: allPermissions.filter(p => body.permissions.includes(p.id)),
      isSystem: false,
      userCount: 0,
      createdAt: new Date().toISOString(),
    }

    rolesDb.set(newRole.id, newRole)

    return HttpResponse.json(newRole, { status: 201 })
  }),

  // Update role
  http.patch('/api/roles/:roleId', async ({ params, request }) => {
    await delay(300)

    const role = rolesDb.get(params.roleId as string)
    if (!role) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found' } },
        { status: 404 }
      )
    }

    if (role.isSystem) {
      return HttpResponse.json(
        { error: { code: 'FORBIDDEN', message: 'Cannot modify system roles' } },
        { status: 403 }
      )
    }

    const body = (await request.json()) as Partial<{
      name: string
      description: string
      permissions: string[]
    }>

    const updated: Role = {
      ...role,
      ...(body.name && { name: body.name }),
      ...(body.description !== undefined && { description: body.description }),
      ...(body.permissions && { permissions: allPermissions.filter(p => body.permissions!.includes(p.id)) }),
    }

    rolesDb.set(role.id, updated)

    return HttpResponse.json(updated)
  }),

  // Delete role
  http.delete('/api/roles/:roleId', async ({ params }) => {
    await delay(300)

    const role = rolesDb.get(params.roleId as string)
    if (!role) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Role not found' } },
        { status: 404 }
      )
    }

    if (role.isSystem) {
      return HttpResponse.json(
        { error: { code: 'FORBIDDEN', message: 'Cannot delete system roles' } },
        { status: 403 }
      )
    }

    if (role.userCount > 0) {
      return HttpResponse.json(
        { error: { code: 'CONFLICT', message: 'Cannot delete role that is in use' } },
        { status: 409 }
      )
    }

    rolesDb.delete(role.id)

    return HttpResponse.json({ message: 'Role deleted successfully' })
  }),

  // List all permissions
  http.get('/api/permissions', async () => {
    await delay(150)
    return HttpResponse.json({
      data: allPermissions,
    })
  }),
]

// Export for use in other handlers
export { mockRoles, allPermissions, rolesDb }
export type { Role, Permission }
