// Mock roles and permissions data

export interface Permission {
  id: string
  name: string
  category: string
  description: string
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
  isSystem: boolean
  userCount: number
  createdAt: string
}

// All available permissions
export const allPermissions: Permission[] = [
  // Contracts
  { id: 'contracts:read', name: 'View Contracts', category: 'contracts', description: 'View contract details and list' },
  { id: 'contracts:create', name: 'Create Contracts', category: 'contracts', description: 'Create new data contracts' },
  { id: 'contracts:edit', name: 'Edit Contracts', category: 'contracts', description: 'Modify existing contracts' },
  { id: 'contracts:delete', name: 'Delete Contracts', category: 'contracts', description: 'Remove contracts from the system' },
  { id: 'contracts:approve', name: 'Approve Contracts', category: 'contracts', description: 'Approve or reject contract changes' },

  // Assets
  { id: 'assets:read', name: 'View Assets', category: 'assets', description: 'View data asset details' },
  { id: 'assets:create', name: 'Create Assets', category: 'assets', description: 'Register new data assets' },
  { id: 'assets:edit', name: 'Edit Assets', category: 'assets', description: 'Modify data asset metadata' },
  { id: 'assets:delete', name: 'Delete Assets', category: 'assets', description: 'Remove data assets' },

  // Quality Rules
  { id: 'rules:read', name: 'View Rules', category: 'quality', description: 'View quality rules' },
  { id: 'rules:create', name: 'Create Rules', category: 'quality', description: 'Define new quality rules' },
  { id: 'rules:edit', name: 'Edit Rules', category: 'quality', description: 'Modify quality rules' },
  { id: 'rules:delete', name: 'Delete Rules', category: 'quality', description: 'Remove quality rules' },

  // Reports
  { id: 'reports:view', name: 'View Reports', category: 'reports', description: 'Access reports and dashboards' },
  { id: 'reports:create', name: 'Create Reports', category: 'reports', description: 'Create custom reports' },
  { id: 'reports:export', name: 'Export Reports', category: 'reports', description: 'Export report data' },

  // Admin
  { id: 'admin:users', name: 'Manage Users', category: 'admin', description: 'Create, edit, and delete users' },
  { id: 'admin:teams', name: 'Manage Teams', category: 'admin', description: 'Create and manage teams' },
  { id: 'admin:roles', name: 'Manage Roles', category: 'admin', description: 'Create and configure roles' },
  { id: 'admin:settings', name: 'System Settings', category: 'admin', description: 'Configure system settings' },
]

// Helper to get permission objects by IDs
function getPermissionsByIds(ids: string[]): Permission[] {
  if (ids.includes('*')) return [...allPermissions]
  return allPermissions.filter((p) => ids.includes(p.id))
}

// Use global to survive hot reloads in development
declare global {
  // eslint-disable-next-line no-var
  var __rolesDb: Map<string, Role> | undefined
}

// Mock roles storage - persist across hot reloads
const rolesDb = globalThis.__rolesDb || new Map<string, Role>()
globalThis.__rolesDb = rolesDb

// Default roles
const defaultRoles: Array<Omit<Role, 'permissions'> & { permissionIds: string[] }> = [
  {
    id: 'role-admin',
    name: 'Admin',
    description: 'Full system access with all permissions',
    permissionIds: ['*'],
    isSystem: true,
    userCount: 1,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'role-editor',
    name: 'Editor',
    description: 'Can create and edit contracts, assets, and rules',
    permissionIds: [
      'contracts:read', 'contracts:create', 'contracts:edit',
      'assets:read', 'assets:create', 'assets:edit',
      'rules:read', 'rules:create', 'rules:edit',
      'reports:view', 'reports:create',
    ],
    isSystem: true,
    userCount: 5,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'role-viewer',
    name: 'Viewer',
    description: 'Read-only access to view contracts, assets, and reports',
    permissionIds: [
      'contracts:read',
      'assets:read',
      'rules:read',
      'reports:view',
    ],
    isSystem: true,
    userCount: 10,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'role-analyst',
    name: 'Analyst',
    description: 'Focus on reports and data quality analysis',
    permissionIds: [
      'contracts:read',
      'assets:read',
      'rules:read', 'rules:create', 'rules:edit',
      'reports:view', 'reports:create', 'reports:export',
    ],
    isSystem: false,
    userCount: 3,
    createdAt: '2024-02-15T00:00:00Z',
  },
]

// Initialize roles only if Map is empty (survives hot reloads)
if (rolesDb.size === 0) {
  defaultRoles.forEach((roleData) => {
    const { permissionIds, ...rest } = roleData
    const role: Role = {
      ...rest,
      permissions: getPermissionsByIds(permissionIds),
    }
    rolesDb.set(role.id, role)
  })
}

// Role CRUD operations
export function getAllRoles(): Role[] {
  return Array.from(rolesDb.values())
}

export function getRoleById(id: string): Role | undefined {
  return rolesDb.get(id)
}

export function getRoleByName(name: string): Role | undefined {
  return Array.from(rolesDb.values()).find(
    (r) => r.name.toLowerCase() === name.toLowerCase()
  )
}

export function createRole(data: {
  name: string
  description?: string
  permissions: string[]
}): Role {
  const id = `role-${Date.now()}`
  const newRole: Role = {
    id,
    name: data.name,
    description: data.description || '',
    permissions: getPermissionsByIds(data.permissions),
    isSystem: false,
    userCount: 0,
    createdAt: new Date().toISOString(),
  }
  rolesDb.set(id, newRole)
  return newRole
}

export function updateRole(
  id: string,
  data: { name?: string; description?: string; permissions?: string[] }
): Role | null {
  const role = rolesDb.get(id)
  if (!role) return null
  if (role.isSystem) return null // Can't edit system roles

  const updated: Role = {
    ...role,
    name: data.name ?? role.name,
    description: data.description ?? role.description,
    permissions: data.permissions
      ? getPermissionsByIds(data.permissions)
      : role.permissions,
  }
  rolesDb.set(id, updated)
  return updated
}

export function deleteRole(id: string): boolean {
  const role = rolesDb.get(id)
  if (!role || role.isSystem) return false // Can't delete system roles
  return rolesDb.delete(id)
}

export function getAllPermissions(): Permission[] {
  return [...allPermissions]
}

export function getPermissionsByCategory(): Record<string, Permission[]> {
  return allPermissions.reduce((acc, perm) => {
    if (!acc[perm.category]) {
      acc[perm.category] = []
    }
    acc[perm.category].push(perm)
    return acc
  }, {} as Record<string, Permission[]>)
}
