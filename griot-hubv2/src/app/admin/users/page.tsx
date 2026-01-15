'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search,
  UserPlus,
  MoreHorizontal,
  Shield,
  Trash2,
  RefreshCw,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/Dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu'
import { DataTable } from '@/components/data-display/DataTable'
import { FormField } from '@/components/forms/FormField'
import { useToast } from '@/lib/hooks/useToast'
import { useDebounce } from '@/lib/hooks/useDebounce'
import type { User, Team, PaginatedResponse } from '@/types'

function formatRelativeTime(dateString: string | undefined): string {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function getRoleBadgeVariant(role: User['role']): 'error' | 'warning' | 'info' | 'secondary' {
  switch (role) {
    case 'admin':
      return 'error'
    case 'manager':
      return 'warning'
    case 'member':
      return 'info'
    default:
      return 'secondary'
  }
}

export default function UserManagementPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [showInviteDialog, setShowInviteDialog] = useState(false)
  const [inviteForm, setInviteForm] = useState({
    name: '',
    email: '',
    role: 'member' as User['role'],
    teamId: '',
  })
  const debouncedSearch = useDebounce(search, 300)

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    { label: 'Users' },
  ]

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: queryKeys.users.list({ search: debouncedSearch, role: roleFilter }),
    queryFn: () => {
      const params = new URLSearchParams()
      if (debouncedSearch) params.set('search', debouncedSearch)
      if (roleFilter !== 'all') params.set('role', roleFilter)
      return api.get<PaginatedResponse<User>>(`/users?${params.toString()}`)
    },
  })

  const { data: teamsData } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const users = usersData?.data || []
  const teams = teamsData?.data || []

  const inviteMutation = useMutation({
    mutationFn: (data: typeof inviteForm) => api.post('/users/invite', data),
    onSuccess: () => {
      toast({
        title: 'Invitation sent',
        description: `An invitation has been sent to ${inviteForm.email}.`,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
      setShowInviteDialog(false)
      setInviteForm({ name: '', email: '', role: 'member', teamId: '' })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to send invitation. Please try again.',
        variant: 'error',
      })
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: (userId: string) => api.post(`/users/${userId}/deactivate`),
    onSuccess: () => {
      toast({
        title: 'User deactivated',
        description: 'The user has been deactivated.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
    },
  })

  const columns = [
    {
      header: 'User',
      accessorKey: 'name',
      cell: ({ row }: { row: { original: User } }) => (
        <div className="flex items-center gap-3">
          <Avatar src={row.original.avatar} fallback={row.original.name} size="sm" />
          <div>
            <div className="font-medium text-text-primary">{row.original.name}</div>
            <div className="text-sm text-text-tertiary">{row.original.email}</div>
          </div>
        </div>
      ),
    },
    {
      header: 'Role',
      accessorKey: 'role',
      cell: ({ row }: { row: { original: User } }) => (
        <Badge variant={getRoleBadgeVariant(row.original.role)}>
          {row.original.role}
        </Badge>
      ),
    },
    {
      header: 'Team',
      accessorKey: 'teamId',
      cell: ({ row }: { row: { original: User } }) => {
        const team = teams.find((t) => t.id === row.original.teamId)
        return <span className="text-text-primary">{team?.name || '-'}</span>
      },
    },
    {
      header: 'Status',
      accessorKey: 'status',
      cell: ({ row }: { row: { original: User } }) => (
        <Badge variant={row.original.status === 'active' ? 'success' : 'secondary'}>
          {row.original.status}
        </Badge>
      ),
    },
    {
      header: 'Last Login',
      accessorKey: 'lastLoginAt',
      cell: ({ row }: { row: { original: User } }) => (
        <span className="text-text-secondary">
          {formatRelativeTime(row.original.lastLoginAt)}
        </span>
      ),
    },
    {
      header: '',
      id: 'actions',
      cell: ({ row }: { row: { original: User } }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Shield className="w-4 h-4 mr-2" />
              Change Role
            </DropdownMenuItem>
            <DropdownMenuItem>
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset Password
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-error-text"
              onClick={() => deactivateMutation.mutate(row.original.id)}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Deactivate User
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="User Management"
        description="Manage user accounts and permissions"
        actions={
          <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="w-4 h-4 mr-2" />
              Invite User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite New User</DialogTitle>
              <DialogDescription>
                Send an invitation email to add a new user to the platform.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <FormField name="name" label="Full Name" required>
                <Input
                  placeholder="John Doe"
                  value={inviteForm.name}
                  onChange={(e) =>
                    setInviteForm({ ...inviteForm, name: e.target.value })
                  }
                />
              </FormField>
              <FormField name="email" label="Email Address" required>
                <Input
                  type="email"
                  placeholder="john@example.com"
                  value={inviteForm.email}
                  onChange={(e) =>
                    setInviteForm({ ...inviteForm, email: e.target.value })
                  }
                />
              </FormField>
              <FormField name="role" label="Role" required>
                <Select
                  value={inviteForm.role}
                  onValueChange={(value) =>
                    setInviteForm({ ...inviteForm, role: value as User['role'] })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="member">Member</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </FormField>
              <FormField name="team" label="Team" required>
                <Select
                  value={inviteForm.teamId}
                  onValueChange={(value) =>
                    setInviteForm({ ...inviteForm, teamId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a team" />
                  </SelectTrigger>
                  <SelectContent>
                    {teams.map((team) => (
                      <SelectItem key={team.id} value={team.id}>
                        {team.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormField>
            </div>
            <DialogFooter>
              <Button variant="secondary" onClick={() => setShowInviteDialog(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => inviteMutation.mutate(inviteForm)}
                disabled={
                  inviteMutation.isPending ||
                  !inviteForm.name ||
                  !inviteForm.email ||
                  !inviteForm.teamId
                }
              >
                Send Invitation
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        }
      />

      {/* Filters */}
      <div className="flex gap-4">
        <Input
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
          className="max-w-sm"
        />
        <Select value={roleFilter} onValueChange={setRoleFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="All Roles" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Roles</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="manager">Manager</SelectItem>
            <SelectItem value="member">Member</SelectItem>
            <SelectItem value="viewer">Viewer</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Users Table */}
      <Card className="p-0">
        <DataTable
          data={users}
          columns={columns}
          loading={usersLoading}
        />
      </Card>
    </PageContainer>
  )
}
