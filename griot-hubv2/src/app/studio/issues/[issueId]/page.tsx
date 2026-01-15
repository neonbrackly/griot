'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  AlertTriangle,
  AlertCircle,
  Info,
  XCircle,
  Clock,
  User,
  CheckCircle,
  ExternalLink,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { PageContainer } from '@/components/layout'
import { Card } from '@/components/layout/Card'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { Skeleton } from '@/components/feedback/Skeleton'
import { useToast } from '@/lib/hooks/useToast'
import type { Issue, Team } from '@/types'

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

function SeverityIcon({ severity, size = 'md' }: { severity: Issue['severity']; size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }
  const containerClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
  }

  const iconClass = sizeClasses[size]
  const containerClass = containerClasses[size]

  switch (severity) {
    case 'critical':
      return (
        <div className={cn('rounded-lg bg-red-100 dark:bg-red-900/30', containerClass)}>
          <XCircle className={cn(iconClass, 'text-red-600 dark:text-red-400')} />
        </div>
      )
    case 'warning':
      return (
        <div className={cn('rounded-lg bg-yellow-100 dark:bg-yellow-900/30', containerClass)}>
          <AlertTriangle className={cn(iconClass, 'text-yellow-600 dark:text-yellow-400')} />
        </div>
      )
    case 'info':
      return (
        <div className={cn('rounded-lg bg-blue-100 dark:bg-blue-900/30', containerClass)}>
          <Info className={cn(iconClass, 'text-blue-600 dark:text-blue-400')} />
        </div>
      )
    default:
      return (
        <div className={cn('rounded-lg bg-bg-tertiary', containerClass)}>
          <AlertCircle className={cn(iconClass, 'text-text-tertiary')} />
        </div>
      )
  }
}

function getSeverityBadgeVariant(
  severity: Issue['severity']
): 'error' | 'warning' | 'info' | 'default' {
  switch (severity) {
    case 'critical':
      return 'error'
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return 'default'
  }
}

function getStatusBadgeVariant(
  status: Issue['status']
): 'success' | 'warning' | 'secondary' | 'default' {
  switch (status) {
    case 'resolved':
      return 'success'
    case 'in_progress':
      return 'warning'
    case 'ignored':
      return 'secondary'
    default:
      return 'default'
  }
}

function getCategoryLabel(category: Issue['category']): string {
  switch (category) {
    case 'pii_exposure':
      return 'PII Detection'
    case 'schema_drift':
      return 'Schema Drift'
    case 'sla_breach':
      return 'SLA Breach'
    case 'quality_failure':
      return 'Quality Failure'
    default:
      return 'Other'
  }
}

function IssueDetailSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-6 w-20" />
      </div>
      <div className="flex items-start gap-4">
        <Skeleton className="w-14 h-14 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-5 w-1/3" />
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Skeleton className="h-32 w-full rounded-lg" />
          <Skeleton className="h-48 w-full rounded-lg" />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-32 w-full rounded-lg" />
          <Skeleton className="h-48 w-full rounded-lg" />
        </div>
      </div>
    </div>
  )
}

export default function IssueDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const issueId = params.issueId as string

  const [selectedStatus, setSelectedStatus] = useState<string | null>(null)
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  const { data: issue, isLoading } = useQuery({
    queryKey: queryKeys.issues.detail(issueId),
    queryFn: () => api.get<Issue>(`/issues/${issueId}`),
  })

  const { data: teamsData } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const teams = teamsData?.data || []

  const updateIssueMutation = useMutation({
    mutationFn: (updates: Partial<Issue>) =>
      api.patch(`/issues/${issueId}`, updates),
    onSuccess: () => {
      toast({
        title: 'Issue updated',
        description: 'The issue has been updated successfully.',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.issues.detail(issueId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.issues.all })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to update issue. Please try again.',
        variant: 'error',
      })
    },
  })

  const handleStatusChange = (newStatus: string) => {
    setSelectedStatus(newStatus)
    updateIssueMutation.mutate({ status: newStatus as Issue['status'] })
  }

  const handleTeamChange = (teamId: string) => {
    setSelectedTeam(teamId)
    updateIssueMutation.mutate({ assignedTeamId: teamId })
  }

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio/contracts' },
    { label: 'Issues', href: '/studio/issues' },
    { label: issue?.title || 'Issue Details' },
  ]

  if (isLoading) {
    return <IssueDetailSkeleton />
  }

  if (!issue) {
    return (
      <PageContainer>
        <Breadcrumbs items={breadcrumbs} />
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-text-tertiary mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Issue not found</h2>
          <p className="text-text-secondary mb-4">
            The issue you&apos;re looking for doesn&apos;t exist or has been deleted.
          </p>
          <Button variant="secondary" onClick={() => router.push('/studio/issues')}>
            Back to Issues
          </Button>
        </div>
      </PageContainer>
    )
  }

  const currentStatus = selectedStatus || issue.status
  const currentTeam = selectedTeam || issue.assignedTeamId

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />

      {/* Header */}
      <div className="flex items-start gap-4">
        <SeverityIcon severity={issue.severity} size="lg" />
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-semibold text-text-primary">{issue.title}</h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <Badge variant={getSeverityBadgeVariant(issue.severity)}>
              {issue.severity}
            </Badge>
            <Badge variant={getStatusBadgeVariant(currentStatus as Issue['status'])}>
              {currentStatus}
            </Badge>
            <span className="text-sm text-text-tertiary">
              {getCategoryLabel(issue.category)}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Description</h2>
            <p className="text-text-secondary whitespace-pre-wrap">{issue.description}</p>
          </Card>

          {/* Affected Resource */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Affected Resource</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-tertiary">Contract</span>
                <Link
                  href={`/studio/contracts/${issue.contractId}`}
                  className="flex items-center gap-2 text-primary-600 hover:underline"
                >
                  {issue.contractName}
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>
              {issue.contractVersion && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-tertiary">Version</span>
                  <span className="text-sm text-text-primary">{issue.contractVersion}</span>
                </div>
              )}
              {issue.table && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-tertiary">Table</span>
                  <code className="text-sm bg-bg-tertiary px-2 py-1 rounded">
                    {issue.table}
                  </code>
                </div>
              )}
              {issue.field && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-tertiary">Field</span>
                  <code className="text-sm bg-bg-tertiary px-2 py-1 rounded">
                    {issue.field}
                  </code>
                </div>
              )}
            </div>
          </Card>

          {/* Timeline */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Timeline</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="p-2 rounded-full bg-red-100 dark:bg-red-900/30">
                  <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-text-primary">Issue Detected</p>
                  <p className="text-xs text-text-tertiary">
                    {formatRelativeTime(issue.detectedAt)} ({new Date(issue.detectedAt).toLocaleString()})
                  </p>
                </div>
              </div>
              {issue.resolvedAt && (
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-full bg-green-100 dark:bg-green-900/30">
                    <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary">Issue Resolved</p>
                    <p className="text-xs text-text-tertiary">
                      {formatRelativeTime(issue.resolvedAt)} ({new Date(issue.resolvedAt).toLocaleString()})
                    </p>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right Column - Actions & Metadata */}
        <div className="space-y-6">
          {/* Status Update */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">Update Status</h3>
            <Select
              value={currentStatus}
              onValueChange={handleStatusChange}
              disabled={updateIssueMutation.isPending}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="ignored">Ignored</SelectItem>
              </SelectContent>
            </Select>
          </Card>

          {/* Assignment */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">Assignment</h3>
            <Select
              value={currentTeam || ''}
              onValueChange={handleTeamChange}
              disabled={updateIssueMutation.isPending}
            >
              <SelectTrigger>
                <SelectValue placeholder="Assign to team" />
              </SelectTrigger>
              <SelectContent>
                {teams.map((team) => (
                  <SelectItem key={team.id} value={team.id}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Card>

          {/* Metadata */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">Metadata</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <Clock className="w-4 h-4 text-text-tertiary" />
                <div>
                  <p className="text-text-tertiary">Created</p>
                  <p className="text-text-primary">
                    {new Date(issue.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Clock className="w-4 h-4 text-text-tertiary" />
                <div>
                  <p className="text-text-tertiary">Last Updated</p>
                  <p className="text-text-primary">
                    {new Date(issue.updatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <User className="w-4 h-4 text-text-tertiary" />
                <div>
                  <p className="text-text-tertiary">Issue ID</p>
                  <code className="text-xs text-text-secondary bg-bg-tertiary px-2 py-1 rounded">
                    {issue.id}
                  </code>
                </div>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Button
                variant="secondary"
                className="w-full justify-start"
                onClick={() => router.push(`/studio/contracts/${issue.contractId}`)}
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Contract
              </Button>
              {issue.status !== 'resolved' && (
                <Button
                  variant="primary"
                  className="w-full justify-start"
                  onClick={() => handleStatusChange('resolved')}
                  disabled={updateIssueMutation.isPending}
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Mark as Resolved
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  )
}
