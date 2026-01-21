'use client'

import * as React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Check, X, Plus, Edit2, Trash2, Users } from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Checkbox } from '@/components/ui/Checkbox'
import { Skeleton } from '@/components/feedback/Skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/Dialog'
import { FormField } from '@/components/forms/FormField'
import { toast } from '@/lib/hooks/useToast'

interface Permission {
  id: string
  name: string
  category: string
  description: string
}

interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
  isSystem: boolean
  userCount: number
  createdAt: string
}

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

function getRoleBadgeVariant(roleName: string): 'error' | 'warning' | 'info' | 'secondary' {
  switch (roleName.toLowerCase()) {
    case 'admin':
      return 'error'
    case 'editor':
      return 'warning'
    case 'viewer':
      return 'info'
    default:
      return 'secondary'
  }
}

export default function RolesPermissionsPage() {
  const queryClient = useQueryClient()
  const [showCreateDialog, setShowCreateDialog] = React.useState(false)
  const [showEditDialog, setShowEditDialog] = React.useState(false)
  const [selectedRole, setSelectedRole] = React.useState<Role | null>(null)
  const [createForm, setCreateForm] = React.useState({
    name: '',
    description: '',
    permissions: [] as string[],
  })

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    { label: 'Roles & Permissions' },
  ]

  // Fetch roles
  const { data: rolesData, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: () => api.get<{ data: Role[] }>('/roles'),
  })

  // Fetch permissions
  const { data: permissionsData, isLoading: permissionsLoading } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => api.get<{ data: Permission[] }>('/permissions'),
  })

  const roles = rolesData?.data || []
  const permissions = permissionsData?.data || []
  const isLoading = rolesLoading || permissionsLoading

  // Group permissions by category
  const permissionsByCategory = React.useMemo(() => {
    return permissions.reduce((acc, perm) => {
      if (!acc[perm.category]) {
        acc[perm.category] = []
      }
      acc[perm.category].push(perm)
      return acc
    }, {} as Record<string, Permission[]>)
  }, [permissions])

  // Create role mutation
  const createMutation = useMutation({
    mutationFn: (data: typeof createForm) => api.post('/roles', data),
    onSuccess: () => {
      toast.success('Role created', `Role "${createForm.name}" has been created.`)
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setShowCreateDialog(false)
      setCreateForm({ name: '', description: '', permissions: [] })
    },
    onError: (error) => {
      toast.error('Failed to create role', error instanceof Error ? error.message : 'Please try again.')
    },
  })

  const togglePermission = (permId: string) => {
    setCreateForm((prev) => ({
      ...prev,
      permissions: prev.permissions.includes(permId)
        ? prev.permissions.filter((p) => p !== permId)
        : [...prev.permissions, permId],
    }))
  }

  const hasPermission = (role: Role, permId: string) => {
    return role.permissions.some((p) => p.id === permId)
  }

  const openEditDialog = (role: Role) => {
    setSelectedRole(role)
    setCreateForm({
      name: role.name,
      description: role.description,
      permissions: role.permissions.map((p) => p.id),
    })
    setShowEditDialog(true)
  }

  return (
    <PageContainer className="space-y-6">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Roles & Permissions"
        description="View and manage role-based access control"
        actions={
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Role
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Role</DialogTitle>
                <DialogDescription>
                  Define a new role with custom permissions.
                </DialogDescription>
              </DialogHeader>
              <div className="p-6 pt-4 space-y-4">
                <FormField name="name" label="Role Name" required>
                  <Input
                    placeholder="e.g., Team Lead"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  />
                </FormField>
                <FormField name="description" label="Description">
                  <Input
                    placeholder="Brief description of this role"
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  />
                </FormField>
                <div className="space-y-4">
                  <h4 className="font-medium text-text-primary">Permissions</h4>
                  {Object.entries(permissionsByCategory).map(([category, perms]) => (
                    <div key={category} className="space-y-2">
                      <h5 className="text-sm font-medium text-text-secondary capitalize">{category}</h5>
                      <div className="grid grid-cols-2 gap-2">
                        {perms.map((perm) => (
                          <label
                            key={perm.id}
                            className="flex items-center gap-2 p-2 rounded-md border border-border-default hover:bg-bg-hover cursor-pointer"
                          >
                            <Checkbox
                              checked={createForm.permissions.includes(perm.id)}
                              onCheckedChange={() => togglePermission(perm.id)}
                            />
                            <div>
                              <div className="text-sm text-text-primary">{perm.name}</div>
                              <div className="text-xs text-text-tertiary">{perm.description}</div>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <DialogFooter>
                <Button variant="secondary" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => createMutation.mutate(createForm)}
                  disabled={createMutation.isPending || !createForm.name}
                  loading={createMutation.isPending}
                >
                  Create Role
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {isLoading ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-40" />
            ))}
          </div>
          <Skeleton className="h-96" />
        </>
      ) : (
        <>
          {/* Role Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roles.map((role) => (
              <Card key={role.id} className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-bg-tertiary">
                      <Shield className="w-5 h-5 text-text-secondary" />
                    </div>
                    <Badge variant={getRoleBadgeVariant(role.name)} size="md">
                      {role.name}
                    </Badge>
                  </div>
                  {!role.isSystem && (
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => openEditDialog(role)}
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon-sm">
                        <Trash2 className="w-4 h-4 text-error-500" />
                      </Button>
                    </div>
                  )}
                </div>
                <p className="text-sm text-text-secondary">{role.description}</p>
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border-default">
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <Shield className="w-4 h-4" />
                    <span>{role.permissions.length} permissions</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <Users className="w-4 h-4" />
                    <span>{role.userCount} users</span>
                  </div>
                </div>
                {role.isSystem && (
                  <div className="mt-2">
                    <Badge variant="secondary" size="xs">System Role</Badge>
                  </div>
                )}
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
                    <th key={role.id} className="text-center py-3 px-4 text-sm font-medium">
                      <Badge variant={getRoleBadgeVariant(role.name)} size="sm">
                        {role.name}
                      </Badge>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(permissionsByCategory).map(([category, perms]) => (
                  <React.Fragment key={category}>
                    <tr>
                      <td colSpan={roles.length + 1} className="py-2 text-xs font-medium text-text-tertiary uppercase tracking-wide bg-bg-tertiary px-2">
                        {category}
                      </td>
                    </tr>
                    {perms.map((permission) => (
                      <tr key={permission.id} className="border-b border-border-default">
                        <td className="py-3 pr-4 text-sm text-text-primary">
                          {permission.name}
                        </td>
                        {roles.map((role) => (
                          <td key={role.id} className="py-3 px-4">
                            <PermissionIcon allowed={hasPermission(role, permission.id)} />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Info Card */}
          <Card className="p-6 bg-info-bg border-info-text/20">
            <h3 className="font-semibold text-info-text mb-2">About Role Management</h3>
            <p className="text-sm text-info-text/80">
              Roles are assigned at the user level and determine what actions a user can perform
              within the system. System roles cannot be modified. Contact your system administrator to request custom roles.
            </p>
          </Card>
        </>
      )}
    </PageContainer>
  )
}
