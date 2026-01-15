'use client'

import { Shield, Check, X } from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Badge } from '@/components/ui/Badge'

interface RolePermission {
  name: string
  admin: boolean
  manager: boolean
  member: boolean
  viewer: boolean
}

const permissions: RolePermission[] = [
  {
    name: 'View contracts',
    admin: true,
    manager: true,
    member: true,
    viewer: true,
  },
  {
    name: 'Create contracts',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
  {
    name: 'Edit contracts',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
  {
    name: 'Delete contracts',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'Approve contracts',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'View assets',
    admin: true,
    manager: true,
    member: true,
    viewer: true,
  },
  {
    name: 'Create assets',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
  {
    name: 'Edit assets',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
  {
    name: 'Delete assets',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'View issues',
    admin: true,
    manager: true,
    member: true,
    viewer: true,
  },
  {
    name: 'Resolve issues',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
  {
    name: 'View reports',
    admin: true,
    manager: true,
    member: true,
    viewer: true,
  },
  {
    name: 'Export reports',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'Manage users',
    admin: true,
    manager: false,
    member: false,
    viewer: false,
  },
  {
    name: 'Manage teams',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'Manage roles',
    admin: true,
    manager: false,
    member: false,
    viewer: false,
  },
  {
    name: 'View audit logs',
    admin: true,
    manager: true,
    member: false,
    viewer: false,
  },
  {
    name: 'API access',
    admin: true,
    manager: true,
    member: true,
    viewer: false,
  },
]

const roles = [
  {
    name: 'Admin',
    key: 'admin' as const,
    description: 'Full system access with user and settings management',
    color: 'error' as const,
  },
  {
    name: 'Manager',
    key: 'manager' as const,
    description: 'Team management and contract approval capabilities',
    color: 'warning' as const,
  },
  {
    name: 'Member',
    key: 'member' as const,
    description: 'Standard access to create and manage data artifacts',
    color: 'info' as const,
  },
  {
    name: 'Viewer',
    key: 'viewer' as const,
    description: 'Read-only access to contracts, assets, and reports',
    color: 'secondary' as const,
  },
]

function PermissionIcon({ allowed }: { allowed: boolean }) {
  return allowed ? (
    <div className="flex justify-center">
      <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
    </div>
  ) : (
    <div className="flex justify-center">
      <X className="w-5 h-5 text-text-tertiary" />
    </div>
  )
}

export default function RolesPermissionsPage() {
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    { label: 'Roles & Permissions' },
  ]

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Roles & Permissions"
        description="View and manage role-based access control"
      />

      {/* Role Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {roles.map((role) => (
          <Card key={role.key} className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-bg-tertiary">
                <Shield className="w-5 h-5 text-text-secondary" />
              </div>
              <Badge variant={role.color} size="md">
                {role.name}
              </Badge>
            </div>
            <p className="text-sm text-text-secondary">{role.description}</p>
          </Card>
        ))}
      </div>

      {/* Permissions Matrix */}
      <Card className="p-6 overflow-x-auto">
        <h3 className="text-lg font-semibold text-text-primary mb-6">
          Permission Matrix
        </h3>
        <table className="w-full min-w-[600px]">
          <thead>
            <tr className="border-b border-border-default">
              <th className="text-left py-3 pr-4 text-sm font-medium text-text-tertiary">
                Permission
              </th>
              {roles.map((role) => (
                <th
                  key={role.key}
                  className="text-center py-3 px-4 text-sm font-medium"
                >
                  <Badge variant={role.color} size="sm">
                    {role.name}
                  </Badge>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {permissions.map((permission, index) => (
              <tr
                key={permission.name}
                className={index !== permissions.length - 1 ? 'border-b border-border-default' : ''}
              >
                <td className="py-3 pr-4 text-sm text-text-primary">
                  {permission.name}
                </td>
                <td className="py-3 px-4">
                  <PermissionIcon allowed={permission.admin} />
                </td>
                <td className="py-3 px-4">
                  <PermissionIcon allowed={permission.manager} />
                </td>
                <td className="py-3 px-4">
                  <PermissionIcon allowed={permission.member} />
                </td>
                <td className="py-3 px-4">
                  <PermissionIcon allowed={permission.viewer} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {/* Info Card */}
      <Card className="p-6 bg-info-bg border-info-text/20">
        <h3 className="font-semibold text-info-text mb-2">About Role Management</h3>
        <p className="text-sm text-info-text/80">
          Roles are assigned at the user level and determine what actions a user can perform
          within the system. Contact your system administrator to request a role change or
          custom permissions.
        </p>
      </Card>
    </PageContainer>
  )
}
