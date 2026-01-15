'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import {
  FileText,
  AlertCircle,
  CheckCircle,
  Clock,
  AlertTriangle,
  Download,
  Filter,
  Calendar,
} from 'lucide-react'

import { PageContainer, Card } from '@/components/layout'
import { Button, Badge, Input } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { EmptyState, Skeleton } from '@/components/feedback'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { api, queryKeys } from '@/lib/api/client'
import type { Contract, ContractRun, RunStatus } from '@/types'

const STATUS_COLORS: Record<RunStatus, string> = {
  passed: 'text-success-text bg-success-bg',
  failed: 'text-error-text bg-error-bg',
  warning: 'text-warning-text bg-warning-bg',
  running: 'text-info-text bg-info-bg',
}

const STATUS_ICONS: Record<RunStatus, React.ComponentType<{ className?: string }>> = {
  passed: CheckCircle,
  failed: AlertCircle,
  warning: AlertTriangle,
  running: Clock,
}

// Generate mock run history
function generateRunHistory(contractId: string, days: number = 30): ContractRun[] {
  const runs: ContractRun[] = []
  const now = new Date()

  for (let i = 0; i < days; i++) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]

    // 70% passed, 20% warning, 10% failed
    const rand = Math.random()
    const status: RunStatus = rand < 0.7 ? 'passed' : rand < 0.9 ? 'warning' : 'failed'
    const duration = Math.floor(Math.random() * 300) + 30

    const totalRules = Math.floor(Math.random() * 10) + 5
    const failed = status === 'failed' ? Math.floor(Math.random() * 3) + 1 : 0
    const warnings = status === 'warning' ? Math.floor(Math.random() * 3) + 1 : 0
    const passed = totalRules - failed - warnings

    runs.push({
      id: `run-${contractId}-${dateStr}`,
      contractId,
      status,
      startedAt: `${dateStr}T02:00:00Z`,
      completedAt: `${dateStr}T02:${String(Math.floor(duration / 60)).padStart(2, '0')}:${String(duration % 60).padStart(2, '0')}Z`,
      duration,
      ruleResults: [],
      summary: {
        totalRules,
        passed,
        failed,
        warnings,
      },
      createdAt: `${dateStr}T02:00:00Z`,
      updatedAt: `${dateStr}T02:00:00Z`,
    })
  }

  return runs
}

export default function ContractRunsPage() {
  const params = useParams()
  const router = useRouter()
  const contractId = params.contractId as string

  const [statusFilter, setStatusFilter] = useState<RunStatus | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch contract data
  const { data: contract, isLoading: contractLoading, error: contractError } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<Contract>(`/contracts/${contractId}`)
      return response
    },
  })

  // Generate mock runs (in a real app, this would be an API call)
  const runs = generateRunHistory(contractId, 30)

  // Filter runs
  const filteredRuns = runs.filter((run) => {
    if (statusFilter !== 'all' && run.status !== statusFilter) return false
    if (searchQuery) {
      const dateStr = new Date(run.startedAt).toLocaleDateString()
      if (!dateStr.toLowerCase().includes(searchQuery.toLowerCase())) return false
    }
    return true
  })

  // Calculate stats
  const stats = {
    total: runs.length,
    passed: runs.filter((r) => r.status === 'passed').length,
    warning: runs.filter((r) => r.status === 'warning').length,
    failed: runs.filter((r) => r.status === 'failed').length,
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (contractLoading) {
    return (
      <PageContainer>
        <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </PageContainer>
    )
  }

  if (contractError || !contract) {
    return (
      <PageContainer>
        <EmptyState
          icon={AlertCircle}
          title="Contract not found"
          description="The contract you're looking for doesn't exist or you don't have access to it."
          action={{
            label: 'Back to Contracts',
            onClick: () => router.push('/studio/contracts'),
          }}
        />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      {/* Header */}
      <div className="mb-6">
        <BackLink href={`/studio/contracts/${contractId}`} label="Back to Contract" />

        <div className="mt-4 flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-text-secondary" />
              <div>
                <h1 className="text-2xl font-semibold text-text-primary">
                  Run History: {contract.name}
                </h1>
                <div className="flex items-center gap-3 mt-1 text-sm text-text-secondary">
                  <span className="font-mono">{contract.version}</span>
                  <span>•</span>
                  <ContractStatusBadge status={contract.status} size="sm" />
                </div>
              </div>
            </div>
          </div>

          <Button variant="secondary" size="sm">
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-bg-secondary">
              <Calendar className="h-5 w-5 text-text-secondary" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-text-primary">{stats.total}</p>
              <p className="text-sm text-text-secondary">Total Runs</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-success-bg">
              <CheckCircle className="h-5 w-5 text-success-text" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-success-text">{stats.passed}</p>
              <p className="text-sm text-text-secondary">Passed</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-warning-bg">
              <AlertTriangle className="h-5 w-5 text-warning-text" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-warning-text">{stats.warning}</p>
              <p className="text-sm text-text-secondary">Warnings</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-error-bg">
              <AlertCircle className="h-5 w-5 text-error-text" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-error-text">{stats.failed}</p>
              <p className="text-sm text-text-secondary">Failed</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Search by date..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Filter className="h-4 w-4" />}
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={statusFilter === 'all' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setStatusFilter('all')}
            >
              All
            </Button>
            <Button
              variant={statusFilter === 'passed' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setStatusFilter('passed')}
            >
              <CheckCircle className="h-4 w-4" />
              Passed
            </Button>
            <Button
              variant={statusFilter === 'warning' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setStatusFilter('warning')}
            >
              <AlertTriangle className="h-4 w-4" />
              Warnings
            </Button>
            <Button
              variant={statusFilter === 'failed' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setStatusFilter('failed')}
            >
              <AlertCircle className="h-4 w-4" />
              Failed
            </Button>
          </div>
        </div>
      </Card>

      {/* Runs List */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-bg-secondary border-b border-border-default">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Started
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Duration
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Rules
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Results
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-default">
              {filteredRuns.map((run) => {
                const StatusIcon = STATUS_ICONS[run.status]
                return (
                  <tr
                    key={run.id}
                    className="hover:bg-bg-secondary/50 cursor-pointer transition-colors"
                    onClick={() => {
                      const date = run.startedAt.split('T')[0]
                      router.push(`/runs/${date}`)
                    }}
                  >
                    <td className="px-4 py-3">
                      <div className={`inline-flex items-center gap-2 px-2 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[run.status]}`}>
                        <StatusIcon className="h-4 w-4" />
                        <span className="capitalize">{run.status}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-text-primary">
                      {formatDate(run.startedAt)}
                    </td>
                    <td className="px-4 py-3 text-sm text-text-secondary">
                      {formatTime(run.startedAt)}
                    </td>
                    <td className="px-4 py-3 text-sm text-text-secondary font-mono">
                      {formatDuration(run.duration || 0)}
                    </td>
                    <td className="px-4 py-3 text-sm text-text-primary">
                      {run.summary.totalRules} rules
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        {run.summary.passed > 0 && (
                          <Badge variant="success" size="sm">
                            {run.summary.passed} passed
                          </Badge>
                        )}
                        {run.summary.warnings > 0 && (
                          <Badge variant="warning" size="sm">
                            {run.summary.warnings} warnings
                          </Badge>
                        )}
                        {run.summary.failed > 0 && (
                          <Badge variant="error" size="sm">
                            {run.summary.failed} failed
                          </Badge>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {filteredRuns.length === 0 && (
          <div className="p-8 text-center">
            <p className="text-text-secondary">No runs match your filters.</p>
          </div>
        )}
      </Card>

      {/* Pagination info */}
      <div className="mt-4 text-sm text-text-secondary text-center">
        Showing {filteredRuns.length} of {runs.length} runs (last 30 days)
      </div>
    </PageContainer>
  )
}
