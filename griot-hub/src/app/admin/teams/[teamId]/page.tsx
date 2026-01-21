'use client'

import * as React from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Users,
  UserPlus,
  MoreHorizontal,
  Trash2,
  Shield,
  Edit2,
  Mail,
  Database,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/feedback/Skeleton'
import { EmptyState } from '@/components/feedback/EmptyState'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { FormField } from '@/components/forms/FormField'
import { toast } from '@/lib/hooks/useToast'

interface TeamMember {
  id: string
  userId: string
  name: string
  email: string
  avatar: string | null
  role: string
  joinedAt: string
}

interface TeamDetail {
  id: string
  name: string
  description: string
  memberCount: number
  defaultRole: string
  domains: string[]
  members: TeamMember[]
  createdAt: string
  updatedAt: string
}

interface Role {
  id: string
  name: string
  description: string
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
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

export default function TeamDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const teamId = params.teamId as string

  const [showAddMemberDialog, setShowAddMemberDialog] = React.useState(false)
  const [showChangeRoleDialog, setShowChangeRoleDialog] = React.useState(false)
  const [selectedMember, setSelectedMember] = React.useState<TeamMember | null>(null)
  const [addMemberForm, setAddMemberForm] = React.useState({
    email: '',
    name: '',
    role: '',
  })

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    { label: 'Teams', href: '/admin/teams' },
    { label: 'Team Details' },
  ]

  // Fetch team details
  const { data: team, isLoading } = useQuery({
    queryKey: queryKeys.teams.detail(teamId),
    queryFn: () => api.get<TeamDetail>(`/teams/${teamId}`),
    enabled: !!teamId,
  })

  // Fetch roles for dropdown
  const { data: rolesData } = useQuery({
    queryKey: ['roles'],
    queryFn: () => api.get<{ data: Role[] }>('/roles'),
  })

  const roles = rolesData?.data || []

  // Add member mutation
  const addMemberMutation = useMutation({
    mutationFn: (data: { email: string; name?: string; role?: string }) =>
      api.post(`/teams/${teamId}/members`, data),
    onSuccess: () => {
      toast.success('Member added', 'The user has been added to the team.')
      queryClient.invalidateQueries({ queryKey: queryKeys.teams.detail(teamId) })
      setShowAddMemberDialog(false)
      setAddMemberForm({ email: '', name: '', role: '' })
    },
    onError: (error) => {
      toast.error('Failed to add member', error instanceof Error ? error.message : 'User may already be in the team.')
    },
  })

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: (memberId: string) =>
      api.delete(`/teams/${teamId}/members/${memberId}`),
    onSuccess: () => {
      toast.success('Member removed', 'The user has been removed from the team.')
      queryClient.invalidateQueries({ queryKey: queryKeys.teams.detail(teamId) })
    },
    onError: (error) => {
      toast.error('Failed to remove member', error instanceof Error ? error.message : 'Please try again.')
    },
  })

  // Change member role mutation
  const changeRoleMutation = useMutation({
    mutationFn: ({ memberId, role }: { memberId: string; role: string }) =>
      api.patch(`/teams/${teamId}/members/${memberId}`, { role }),
    onSuccess: () => {
      toast.success('Role updated', 'Member role has been updated.')
      queryClient.invalidateQueries({ queryKey: queryKeys.teams.detail(teamId) })
      setShowChangeRoleDialog(false)
      setSelectedMember(null)
    },
    onError: (error) => {
      toast.error('Failed to update role', error instanceof Error ? error.message : 'Please try again.')
    },
  })

  const handleAddMember = () => {
    if (!addMemberForm.email) {
      toast.error('Email required', 'Please enter a valid email address.')
      return
    }
    addMemberMutation.mutate({
      email: addMemberForm.email,
      name: addMemberForm.name || addMemberForm.email.split('@')[0],
      role: addMemberForm.role || undefined,
    })
  }

  const openChangeRoleDialog = (member: TeamMember) => {
    setSelectedMember(member)
    setShowChangeRoleDialog(true)
  }

  if (isLoading) {
    return (
      <PageContainer className="space-y-6">
        <Breadcrumbs items={breadcrumbs} />
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-96" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Skeleton className="h-28" />
            <Skeleton className="h-28" />
            <Skeleton className="h-28 col-span-2" />
          </div>
          <Skeleton className="h-64" />
        </div>
      </PageContainer>
    )
  }

  if (!team) {
    return (
      <PageContainer className="space-y-6">
        <Breadcrumbs items={breadcrumbs} />
        <EmptyState
          icon={Users}
          title="Team not found"
          description="The team you're looking for doesn't exist."
          action={{
            label: 'Back to Teams',
            onClick: () => router.push('/admin/teams'),
          }}
        />
      </PageContainer>
    )
  }

  return (
    <PageContainer className="space-y-6">
      <Breadcrumbs items={breadcrumbs} />

      {/* Back Button */}
      <Link href="/admin/teams">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Teams
        </Button>
      </Link>

      <PageHeader
        title={team.name}
        description={team.description || 'No description provided'}
        actions={
          <div className="flex gap-3">
            <Button variant="secondary">
              <Edit2 className="h-4 w-4 mr-2" />
              Edit Team
            </Button>
            <Dialog open={showAddMemberDialog} onOpenChange={setShowAddMemberDialog}>
              <DialogTrigger asChild>
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Member
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Team Member</DialogTitle>
                  <DialogDescription>
                    Add a user to this team. They will inherit the team's default role ({team.defaultRole}) unless you specify one.
                  </DialogDescription>
                </DialogHeader>
                <div className="p-6 pt-4 space-y-4">
                  <FormField name="email" label="Email Address" required>
                    <Input
                      placeholder="user@example.com"
                      type="email"
                      leftIcon={<Mail className="h-4 w-4" />}
                      value={addMemberForm.email}
                      onChange={(e) =>
                        setAddMemberForm({ ...addMemberForm, email: e.target.value })
                      }
                    />
                  </FormField>
                  <FormField name="name" label="Full Name">
                    <Input
                      placeholder="John Doe (optional)"
                      value={addMemberForm.name}
                      onChange={(e) =>
                        setAddMemberForm({ ...addMemberForm, name: e.target.value })
                      }
                    />
                  </FormField>
                  <FormField name="role" label="Role">
                    <Select
                      value={addMemberForm.role}
                      onValueChange={(value) =>
                        setAddMemberForm({ ...addMemberForm, role: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={`Default: ${team.defaultRole}`} />
                      </SelectTrigger>
                      <SelectContent>
                        {roles.map((role) => (
                          <SelectItem key={role.id} value={role.name}>
                            {role.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormField>
                </div>
                <DialogFooter>
                  <Button variant="secondary" onClick={() => setShowAddMemberDialog(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleAddMember}
                    disabled={addMemberMutation.isPending || !addMemberForm.email}
                    loading={addMemberMutation.isPending}
                  >
                    Add Member
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Team Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/30">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-tertiary">Members</p>
              <p className="text-3xl font-bold text-text-primary">
                {team.members?.length || 0}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-purple-100 dark:bg-purple-900/30">
              <Shield className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-tertiary">Default Role</p>
              <Badge variant={getRoleBadgeVariant(team.defaultRole)} className="mt-1">
                {team.defaultRole}
              </Badge>
            </div>
          </div>
        </Card>
        <Card className="p-5 col-span-2">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-green-100 dark:bg-green-900/30">
              <Database className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-text-tertiary mb-2">Domains</p>
              <div className="flex flex-wrap gap-2">
                {team.domains?.length > 0 ? (
                  team.domains.map((domain) => (
                    <Badge key={domain} variant="secondary">
                      {domain}
                    </Badge>
                  ))
                ) : (
                  <span className="text-text-tertiary text-sm">No domains assigned</span>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Members List */}
      <Card className="overflow-hidden">
        <div className="p-6 border-b border-border-default">
          <h3 className="text-lg font-semibold text-text-primary">Team Members</h3>
          <p className="text-sm text-text-secondary mt-1">
            Manage who has access to this team and their roles
          </p>
        </div>
        {team.members?.length > 0 ? (
          <div className="divide-y divide-border-default">
            {team.members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-4 hover:bg-bg-hover transition-colors"
              >
                <div className="flex items-center gap-4">
                  <Avatar
                    src={member.avatar || undefined}
                    fallback={member.name}
                    size="md"
                  />
                  <div>
                    <div className="font-medium text-text-primary">{member.name}</div>
                    <div className="text-sm text-text-tertiary">{member.email}</div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <Badge variant={getRoleBadgeVariant(member.role)}>
                    {member.role}
                  </Badge>
                  <div className="text-sm text-text-tertiary w-32 text-right">
                    Joined {formatDate(member.joinedAt)}
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => openChangeRoleDialog(member)}>
                        <Shield className="w-4 h-4 mr-2" />
                        Change Role
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-error-text"
                        onClick={() => removeMemberMutation.mutate(member.id)}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove from Team
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8">
            <EmptyState
              icon={Users}
              title="No members yet"
              description="Add users to this team to get started."
              action={{
                label: 'Add Member',
                onClick: () => setShowAddMemberDialog(true),
              }}
            />
          </div>
        )}
      </Card>

      {/* Change Role Dialog */}
      <Dialog open={showChangeRoleDialog} onOpenChange={setShowChangeRoleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Member Role</DialogTitle>
            <DialogDescription>
              Update the role for {selectedMember?.name}. This will change their permissions within the team.
            </DialogDescription>
          </DialogHeader>
          <div className="p-6 pt-4">
            <FormField name="role" label="New Role">
              <Select
                value={selectedMember?.role || ''}
                onValueChange={(value) => {
                  if (selectedMember) {
                    changeRoleMutation.mutate({
                      memberId: selectedMember.id,
                      role: value,
                    })
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a role" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.name}>
                      <div className="flex items-center gap-2">
                        <Badge variant={getRoleBadgeVariant(role.name)} size="sm">
                          {role.name}
                        </Badge>
                        <span className="text-text-tertiary text-xs">
                          {role.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setShowChangeRoleDialog(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PageContainer>
  )
}
