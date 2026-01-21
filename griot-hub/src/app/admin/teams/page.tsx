'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search,
  Plus,
  MoreHorizontal,
  Users,
  Database,
  FileText,
  Edit2,
  Trash2,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
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
import { FormField } from '@/components/forms/FormField'
import { Skeleton, SkeletonCard } from '@/components/feedback/Skeleton'
import { EmptyState } from '@/components/feedback/EmptyState'
import { useToast } from '@/lib/hooks/useToast'
import { useDebounce } from '@/lib/hooks/useDebounce'
import type { Team } from '@/types'

export default function TeamManagementPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [search, setSearch] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
  })
  const debouncedSearch = useDebounce(search, 300)

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    { label: 'Teams' },
  ]

  const { data: teamsData, isLoading } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const teams = teamsData?.data || []

  const filteredTeams = teams.filter(
    (team) =>
      team.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      team.description?.toLowerCase().includes(debouncedSearch.toLowerCase())
  )

  const createMutation = useMutation({
    mutationFn: (data: typeof createForm) => api.post('/teams', data),
    onSuccess: () => {
      toast({
        title: 'Team created',
        description: `Team "${createForm.name}" has been created.`,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.teams.all })
      setShowCreateDialog(false)
      setCreateForm({ name: '', description: '' })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to create team. Please try again.',
        variant: 'error',
      })
    },
  })

  return (
    <PageContainer className="space-y-6">
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Team Management"
        description="Organize teams and domain ownership"
        actions={
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Team
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Team</DialogTitle>
              <DialogDescription>
                Create a new team to organize users and assign domain ownership.
              </DialogDescription>
            </DialogHeader>
            <div className="p-6 pt-4 space-y-4">
              <FormField name="name" label="Team Name" required>
                <Input
                  placeholder="e.g., Data Platform"
                  value={createForm.name}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, name: e.target.value })
                  }
                />
              </FormField>
              <FormField name="description" label="Description">
                <Input
                  placeholder="Brief description of the team's responsibilities"
                  value={createForm.description}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, description: e.target.value })
                  }
                />
              </FormField>
            </div>
            <DialogFooter>
              <Button variant="secondary" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => createMutation.mutate(createForm)}
                disabled={createMutation.isPending || !createForm.name}
              >
                Create Team
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        }
      />

      {/* Search */}
      <Input
        placeholder="Search teams..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        leftIcon={<Search className="w-4 h-4" />}
        className="max-w-sm"
      />

      {/* Teams Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filteredTeams.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No teams found"
          description={
            search
              ? 'No teams match your search criteria.'
              : 'Create your first team to get started.'
          }
          action={
            !search
              ? {
                  label: 'Create Team',
                  onClick: () => setShowCreateDialog(true),
                }
              : undefined
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTeams.map((team) => (
            <Card key={team.id} className="p-6 group">
              <div className="flex items-start justify-between mb-4">
                <Link href={`/admin/teams/${team.id}`}>
                  <div className="p-3 rounded-lg bg-primary-100 dark:bg-primary-900/30 group-hover:bg-primary-200 dark:group-hover:bg-primary-900/50 transition-colors">
                    <Users className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                </Link>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/admin/teams/${team.id}`}>
                        <Users className="w-4 h-4 mr-2" />
                        View Details
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit Team
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-error-text">
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete Team
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <Link href={`/admin/teams/${team.id}`}>
                <h3 className="font-semibold text-text-primary text-lg hover:text-primary-600 transition-colors">
                  {team.name}
                </h3>
              </Link>
              {team.description && (
                <p className="text-sm text-text-secondary mt-1 line-clamp-2">
                  {team.description}
                </p>
              )}

              <div className="flex flex-wrap gap-1 mt-3">
                {team.domains.map((domain) => (
                  <Badge key={domain} variant="secondary" size="xs">
                    {domain}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center justify-between mt-4 pt-4 border-t border-border-default">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Users className="w-4 h-4" />
                  <span>{team.memberCount} members</span>
                </div>
                <Link href={`/admin/teams/${team.id}`}>
                  <Button variant="ghost" size="sm">
                    View
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </PageContainer>
  )
}
