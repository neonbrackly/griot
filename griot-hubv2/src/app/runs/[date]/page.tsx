'use client'

import { PageShell, PageContainer, PageHeader, Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Button, Badge, Input } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { Skeleton } from '@/components/feedback'
import { BackLink } from '@/components/navigation'
import { ArrowLeft, Download, Search } from 'lucide-react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api, queryKeys } from '@/lib/api/client'
import type { ContractRun, Contract } from '@/types'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo, useState } from 'react'
import { useDebounce } from '@/lib/hooks'

interface RunsForDateResponse {
  date: string
  summary: {
    total: number
    passed: number
    warnings: number
    failed: number
    duration: number
    startedAt: string
    completedAt: string
  }
  runs: ContractRun[]
}

export default function RunDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const date = params.date as string
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch runs for this date
  const {
    data: runsData,
    isLoading,
    error,
  } = useQuery<RunsForDateResponse>({
    queryKey: queryKeys.runs.byDate(date),
    queryFn: () => api.get(`/runs/${date}`),
  })

  // Fetch contracts to get names
  const { data: contractsData } = useQuery<{ data: Contract[] }>({
    queryKey: queryKeys.contracts.all,
    queryFn: () => api.get('/contracts'),
  })

  const contracts = useMemo(() => {
    return contractsData?.data || []
  }, [contractsData])

  // Get contract name by ID
  const getContractName = (contractId: string) => {
    const contract = contracts.find((c) => c.id === contractId)
    return contract?.name || contractId
  }

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  // Format time
  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Filter runs based on search
  const filteredRuns = useMemo(() => {
    if (!runsData?.runs) return []
    if (!debouncedSearch) return runsData.runs

    return runsData.runs.filter((run) => {
      const contractName = getContractName(run.contractId).toLowerCase()
      const search = debouncedSearch.toLowerCase()
      return contractName.includes(search) || run.contractId.toLowerCase().includes(search)
    })
  }, [runsData?.runs, debouncedSearch, contracts])

  // Define table columns
  const columns: ColumnDef<ContractRun>[] = useMemo(
    () => [
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => {
          const status = row.original.status
          const variant =
            status === 'passed' ? 'success' : status === 'failed' ? 'error' : status === 'warning' ? 'warning' : 'secondary'
          return <Badge variant={variant}>{status}</Badge>
        },
      },
      {
        accessorKey: 'contractId',
        header: 'Contract',
        cell: ({ row }) => {
          const contractName = getContractName(row.original.contractId)
          return (
            <div>
              <div className="font-medium text-text-primary">{contractName}</div>
              <div className="text-xs text-text-tertiary">{row.original.contractId}</div>
            </div>
          )
        },
      },
      {
        accessorKey: 'duration',
        header: 'Duration',
        cell: ({ row }) => <span className="text-text-secondary">{formatDuration(row.original.duration || 0)}</span>,
      },
      {
        accessorKey: 'summary',
        header: 'Issues',
        cell: ({ row }) => {
          const { failed, warnings } = row.original.summary
          const issueCount = failed + warnings
          return issueCount > 0 ? (
            <Badge variant={failed > 0 ? 'error' : 'warning'}>{issueCount}</Badge>
          ) : (
            <span className="text-text-tertiary text-sm">None</span>
          )
        },
      },
    ],
    [contracts]
  )

  if (error) {
    return (
      <PageShell>
        <PageContainer>
          <BackLink href="/" />
          <div className="text-center py-12">
            <p className="text-error-text">Failed to load run details</p>
          </div>
        </PageContainer>
      </PageShell>
    )
  }

  return (
    <PageShell>
      <PageContainer>
        <BackLink href="/" />

        <PageHeader
          title={`Contract Runs: ${date ? formatDate(date) : 'Loading...'}`}
          actions={
            <Button variant="secondary">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          }
        />

        {/* Summary Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-20" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-secondary">
                  <div className="text-sm text-text-secondary mb-1">Total</div>
                  <div className="text-2xl font-bold text-text-primary">{runsData?.summary.total}</div>
                </div>
                <div className="p-4 rounded-lg bg-success-bg/10">
                  <div className="text-sm text-text-secondary mb-1">Passed</div>
                  <div className="text-2xl font-bold text-success-text">{runsData?.summary.passed}</div>
                </div>
                <div className="p-4 rounded-lg bg-warning-bg/10">
                  <div className="text-sm text-text-secondary mb-1">Warnings</div>
                  <div className="text-2xl font-bold text-warning-text">{runsData?.summary.warnings}</div>
                </div>
                <div className="p-4 rounded-lg bg-error-bg/10">
                  <div className="text-sm text-text-secondary mb-1">Failed</div>
                  <div className="text-2xl font-bold text-error-text">{runsData?.summary.failed}</div>
                </div>
              </div>
            )}

            {runsData && (
              <div className="mt-4 pt-4 border-t border-border-default flex flex-wrap gap-4 text-sm text-text-secondary">
                <div>
                  <span className="font-medium">Duration:</span>{' '}
                  {formatDuration(runsData.summary.duration)}
                </div>
                <div>
                  <span className="font-medium">Started:</span>{' '}
                  {formatTime(runsData.summary.startedAt)}
                </div>
                <div>
                  <span className="font-medium">Completed:</span>{' '}
                  {formatTime(runsData.summary.completedAt)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Search and Filter */}
        <div className="mb-4 flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-tertiary" />
            <Input
              placeholder="Search by contract name or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Runs Table */}
        <Card>
          <CardContent className="p-0">
            <DataTable
              columns={columns}
              data={filteredRuns}
              loading={isLoading}
              enableSorting
              enablePagination
              pageSize={20}
              onRowClick={(row) => router.push(`/studio/contracts/${row.contractId}`)}
            />
          </CardContent>
        </Card>
      </PageContainer>
    </PageShell>
  )
}
