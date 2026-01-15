'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import {
  Search,
  Download,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
} from 'lucide-react'
import { api, queryKeys } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { useDebounce } from '@/lib/hooks/useDebounce'
import { PageContainer, PageHeader, Card } from '@/components/layout'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { Tabs, TabsList, TabsTrigger } from '@/components/navigation/Tabs'
import { EmptyState } from '@/components/feedback/EmptyState'
import { Skeleton } from '@/components/feedback/Skeleton'
import type { Issue, PaginatedResponse } from '@/types'

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

function SeverityIcon({ severity }: { severity: Issue['severity'] }) {
  switch (severity) {
    case 'critical':
      return (
        <div className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30">
          <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
        </div>
      )
    case 'warning':
      return (
        <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30">
          <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
        </div>
      )
    case 'info':
      return (
        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
          <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
      )
    default:
      return (
        <div className="p-2 rounded-lg bg-bg-tertiary">
          <AlertCircle className="w-5 h-5 text-text-tertiary" />
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

function IssueCard({ issue }: { issue: Issue }) {
  return (
    <Card className="p-4 hover:border-border-strong transition-colors">
      <div className="flex items-start gap-4">
        <SeverityIcon severity={issue.severity} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <Link
              href={`/studio/issues/${issue.id}`}
              className="font-medium text-text-primary hover:text-primary-600 transition-colors"
            >
              {issue.title}
            </Link>
            <Badge variant={getSeverityBadgeVariant(issue.severity)} size="xs">
              {issue.severity}
            </Badge>
            {issue.status === 'resolved' && (
              <Badge variant="success" size="xs">
                Resolved
              </Badge>
            )}
          </div>

          <p className="text-sm text-text-secondary mt-1 line-clamp-2">
            {issue.description}
          </p>

          <div className="flex items-center gap-2 mt-2 text-sm text-text-tertiary">
            <span>{getCategoryLabel(issue.category)}</span>
            <span>•</span>
            <span>Detected {formatRelativeTime(issue.detectedAt)}</span>
          </div>

          <div className="flex items-center gap-2 mt-2 text-sm">
            <span className="text-text-tertiary">Contract:</span>
            <Link
              href={`/studio/contracts/${issue.contractId}`}
              className="text-primary-600 hover:underline"
            >
              {issue.contractName}
            </Link>
            {issue.contractVersion && (
              <Badge variant="secondary" size="xs">
                v{issue.contractVersion}
              </Badge>
            )}
          </div>

          {issue.field && (
            <div className="text-sm text-text-tertiary mt-1">
              Field:{' '}
              <code className="bg-bg-tertiary px-1.5 py-0.5 rounded text-text-secondary">
                {issue.table && `${issue.table}.`}
                {issue.field}
              </code>
            </div>
          )}
        </div>

        {issue.assignedTeamId && (
          <div className="text-right shrink-0">
            <div className="text-xs text-text-tertiary">Assigned to</div>
            <div className="text-sm text-text-primary">{issue.assignedTeamId}</div>
          </div>
        )}
      </div>
    </Card>
  )
}

function IssuesListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="p-4">
          <div className="flex items-start gap-4">
            <Skeleton className="w-10 h-10 rounded-lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-5 w-2/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-1/2" />
              <div className="flex gap-2">
                <Skeleton className="h-5 w-20" />
                <Skeleton className="h-5 w-24" />
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

export default function IssuesPage() {
  const [severity, setSeverity] = useState<string>('all')
  const [category, setCategory] = useState<string>('all')
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.issues.list({
      severity: severity !== 'all' ? severity : undefined,
      search: debouncedSearch || undefined,
    }),
    queryFn: () => {
      const params = new URLSearchParams()
      if (severity !== 'all') params.set('severity', severity)
      if (severity === 'resolved') {
        params.set('status', 'resolved')
        params.delete('severity')
      }
      if (debouncedSearch) params.set('search', debouncedSearch)
      return api.get<PaginatedResponse<Issue>>(`/issues?${params.toString()}`)
    },
  })

  const issues = data?.data || []

  const severityCounts = useMemo(() => {
    const all = issues.length
    const critical = issues.filter((i) => i.severity === 'critical' && i.status !== 'resolved').length
    const warning = issues.filter((i) => i.severity === 'warning' && i.status !== 'resolved').length
    const info = issues.filter((i) => i.severity === 'info' && i.status !== 'resolved').length
    const resolved = issues.filter((i) => i.status === 'resolved').length
    return { all, critical, warning, info, resolved }
  }, [issues])

  const filteredIssues = useMemo(() => {
    let filtered = [...issues]

    if (category !== 'all') {
      filtered = filtered.filter((i) => i.category === category)
    }

    if (severity === 'resolved') {
      filtered = filtered.filter((i) => i.status === 'resolved')
    } else if (severity !== 'all') {
      filtered = filtered.filter((i) => i.severity === severity && i.status !== 'resolved')
    }

    return filtered
  }, [issues, severity, category])

  const handleExportCSV = () => {
    const headers = ['Title', 'Severity', 'Status', 'Category', 'Contract', 'Detected At']
    const rows = filteredIssues.map((i) => [
      i.title,
      i.severity,
      i.status,
      getCategoryLabel(i.category),
      i.contractName || '',
      new Date(i.detectedAt).toISOString(),
    ])
    const csv = [headers, ...rows].map((r) => r.map((c) => `"${c}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `issues-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio/contracts' },
    { label: 'Issues' },
  ]

  return (
    <PageContainer>
      <Breadcrumbs items={breadcrumbs} />
      <PageHeader
        title="Issues"
        description="All issues across your contracts"
        actions={
          <Button variant="secondary" onClick={handleExportCSV}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        }
      />

      <Tabs
        value={severity}
        onValueChange={setSeverity}
      >
        <TabsList>
          <TabsTrigger value="all">All ({severityCounts.all})</TabsTrigger>
          <TabsTrigger value="critical" className="data-[state=active]:text-red-600">
            Critical ({severityCounts.critical})
          </TabsTrigger>
          <TabsTrigger value="warning" className="data-[state=active]:text-yellow-600">
            Warning ({severityCounts.warning})
          </TabsTrigger>
          <TabsTrigger value="info">Info ({severityCounts.info})</TabsTrigger>
          <TabsTrigger value="resolved" className="data-[state=active]:text-green-600">
            Resolved ({severityCounts.resolved})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex gap-4">
        <Input
          placeholder="Search issues..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
          className="max-w-sm"
        />
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="pii_exposure">PII Detection</SelectItem>
            <SelectItem value="schema_drift">Schema Drift</SelectItem>
            <SelectItem value="sla_breach">SLA Breach</SelectItem>
            <SelectItem value="quality_failure">Quality Failure</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <IssuesListSkeleton />
      ) : filteredIssues.length === 0 ? (
        <EmptyState
          icon={CheckCircle}
          title="No issues found"
          description={
            search || category !== 'all' || severity !== 'all'
              ? 'No issues match your current filters.'
              : 'Great! There are no issues in your contracts.'
          }
        />
      ) : (
        <div className="space-y-4">
          {filteredIssues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}
    </PageContainer>
  )
}
