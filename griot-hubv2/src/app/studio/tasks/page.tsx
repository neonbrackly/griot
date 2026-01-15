'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Clock,
  CheckCircle,
  FileEdit,
  MessageSquare,
  AlertTriangle,
  Trash2,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { PageContainer, PageHeader, Card } from '@/components/layout'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/navigation/Tabs'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { EmptyState } from '@/components/feedback/EmptyState'
import { SkeletonCard } from '@/components/feedback/Skeleton'
import { useToast } from '@/lib/hooks/useToast'
import type { MyTasks, PendingAuthorization, CommentToReview, Draft } from '@/types'

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

// Pending Authorizations List
function PendingAuthorizationsList({
  items,
  isLoading,
}: {
  items?: PendingAuthorization[]
  isLoading: boolean
}) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const approveMutation = useMutation({
    mutationFn: (id: string) =>
      api.post(`/tasks/authorize/${id}/approve`),
    onSuccess: () => {
      toast({
        title: 'Contract approved',
        description: 'The contract has been approved successfully.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.my() })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to approve contract. Please try again.',
        variant: 'error',
      })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (id: string) =>
      api.post(`/tasks/authorize/${id}/reject`),
    onSuccess: () => {
      toast({
        title: 'Changes requested',
        description: 'The contract has been sent back for changes.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.my() })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to request changes. Please try again.',
        variant: 'error',
      })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (!items?.length) {
    return (
      <EmptyState
        icon={CheckCircle}
        title="All caught up!"
        description="No contracts waiting for your approval"
      />
    )
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <Card key={item.id} className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4 min-w-0">
              <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 shrink-0">
                <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="min-w-0">
                <Link
                  href={`/studio/contracts/${item.contractId}`}
                  className="font-medium text-text-primary hover:text-primary-600 transition-colors"
                >
                  {item.contractName}
                </Link>
                <p className="text-sm text-text-secondary mt-1">
                  Requested by {item.requestedBy} • {formatRelativeTime(item.requestedAt)}
                </p>
                {item.description && (
                  <p className="text-sm text-text-tertiary mt-1 line-clamp-2">
                    {item.description}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary">{item.domain}</Badge>
                  <Badge
                    variant={
                      item.priority === 'high'
                        ? 'warning'
                        : item.priority === 'low'
                        ? 'secondary'
                        : 'default'
                    }
                  >
                    {item.priority} priority
                  </Badge>
                </div>
              </div>
            </div>

            <div className="flex gap-2 shrink-0">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => rejectMutation.mutate(item.id)}
                disabled={rejectMutation.isPending || approveMutation.isPending}
              >
                Request Changes
              </Button>
              <Button
                size="sm"
                onClick={() => approveMutation.mutate(item.id)}
                disabled={approveMutation.isPending || rejectMutation.isPending}
              >
                Approve
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

// Comments to Review List
function CommentsToReviewList({
  items,
  isLoading,
}: {
  items?: CommentToReview[]
  isLoading: boolean
}) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const markReviewedMutation = useMutation({
    mutationFn: (id: string) =>
      api.post(`/tasks/comments/${id}/review`),
    onSuccess: () => {
      toast({
        title: 'Comment marked as reviewed',
        description: 'The comment has been marked as reviewed.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.my() })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (!items?.length) {
    return (
      <EmptyState
        icon={MessageSquare}
        title="No comments to review"
        description="Comments requiring your attention will appear here"
      />
    )
  }

  const getTypeIcon = (type: CommentToReview['type']) => {
    switch (type) {
      case 'question':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'approval':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      default:
        return <MessageSquare className="w-4 h-4 text-blue-500" />
    }
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <Card key={item.id} className="p-4">
          <div className="flex items-start gap-4">
            <Avatar
              src={item.commentByAvatar}
              fallback={item.commentBy}
              size="sm"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-text-primary">
                  {item.commentBy}
                </span>
                <span className="text-text-tertiary">commented on</span>
                <Link
                  href={`/studio/contracts/${item.contractId}`}
                  className="font-medium text-primary-600 hover:underline"
                >
                  {item.contractName}
                </Link>
              </div>
              <p className="text-text-secondary mt-1">{item.comment}</p>
              <div className="flex items-center gap-3 mt-3">
                <div className="flex items-center gap-1.5 text-xs text-text-tertiary">
                  {getTypeIcon(item.type)}
                  <span className="capitalize">{item.type}</span>
                </div>
                <span className="text-xs text-text-tertiary">
                  {formatRelativeTime(item.commentAt)}
                </span>
              </div>
            </div>
            <div className="shrink-0">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => markReviewedMutation.mutate(item.id)}
                disabled={markReviewedMutation.isPending}
              >
                Mark Reviewed
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

// Drafts List
function DraftsList({
  items,
  isLoading,
}: {
  items?: Draft[]
  isLoading: boolean
}) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      api.delete(`/tasks/drafts/${id}`),
    onSuccess: () => {
      toast({
        title: 'Draft deleted',
        description: 'The draft has been permanently deleted.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.my() })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to delete draft. Please try again.',
        variant: 'error',
      })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (!items?.length) {
    return (
      <EmptyState
        icon={FileEdit}
        title="No drafts"
        description="Contracts you save as draft will appear here"
        action={{
          label: 'Create Contract',
          onClick: () => router.push('/studio/contracts/new'),
        }}
      />
    )
  }

  return (
    <div className="space-y-3">
      {items.map((draft) => (
        <Card key={draft.id} className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 min-w-0">
              <div className="p-2 rounded-lg bg-bg-tertiary shrink-0">
                <FileEdit className="w-5 h-5 text-text-secondary" />
              </div>
              <div className="min-w-0">
                <div className="font-medium text-text-primary">
                  {draft.name || 'Untitled ' + (draft.type === 'contract' ? 'Contract' : 'Asset')}
                </div>
                <div className="text-sm text-text-secondary">
                  Last edited {formatRelativeTime(draft.updatedAt)}
                  {draft.completionPercent !== undefined && (
                    <span className="ml-2">• {draft.completionPercent}% complete</span>
                  )}
                </div>
                {draft.domain && (
                  <Badge variant="secondary" size="xs" className="mt-1">
                    {draft.domain}
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex gap-2 shrink-0">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteMutation.mutate(draft.id)}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </Button>
              <Button
                size="sm"
                onClick={() =>
                  router.push(
                    draft.type === 'contract'
                      ? `/studio/contracts/new/wizard?draft=${draft.id}`
                      : `/studio/assets/new?draft=${draft.id}`
                  )
                }
              >
                Continue Editing
              </Button>
            </div>
          </div>

          {draft.completionPercent !== undefined && (
            <div className="mt-3 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 rounded-full transition-all duration-300"
                style={{ width: `${draft.completionPercent}%` }}
              />
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}

export default function MyTasksPage() {
  const { data: tasks, isLoading } = useQuery({
    queryKey: queryKeys.tasks.my(),
    queryFn: () => api.get<MyTasks>('/tasks/my'),
  })

  const counts = useMemo(
    () => ({
      authorizations: tasks?.authorizations?.length || 0,
      comments: tasks?.comments?.length || 0,
      drafts: tasks?.drafts?.length || 0,
    }),
    [tasks]
  )

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio/contracts' },
    { label: 'My Tasks' },
  ]

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="My Tasks"
        description="Items requiring your attention"
      />

      <Tabs defaultValue="authorizations">
        <TabsList>
          <TabsTrigger value="authorizations" className="flex items-center gap-2">
            Pending Authorization
            {counts.authorizations > 0 && (
              <Badge variant="primary" size="xs">
                {counts.authorizations}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="comments" className="flex items-center gap-2">
            Comments to Review
            {counts.comments > 0 && (
              <Badge variant="primary" size="xs">
                {counts.comments}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="drafts" className="flex items-center gap-2">
            My Drafts
            {counts.drafts > 0 && (
              <Badge variant="secondary" size="xs">
                {counts.drafts}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="authorizations" className="mt-6">
          <PendingAuthorizationsList
            items={tasks?.authorizations}
            isLoading={isLoading}
          />
        </TabsContent>

        <TabsContent value="comments" className="mt-6">
          <CommentsToReviewList
            items={tasks?.comments}
            isLoading={isLoading}
          />
        </TabsContent>

        <TabsContent value="drafts" className="mt-6">
          <DraftsList items={tasks?.drafts} isLoading={isLoading} />
        </TabsContent>
      </Tabs>
    </PageContainer>
  )
}
