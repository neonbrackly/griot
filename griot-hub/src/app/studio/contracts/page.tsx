'use client'

import { useState, useMemo, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { FileText, Plus, Search, Filter, AlertCircle } from 'lucide-react'
import Link from 'next/link'

import { PageContainer, PageHeader, Card } from '@/components/layout'
import { DataTable } from '@/components/data-display'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { Button, Input, Select, Badge } from '@/components/ui'
import { Tabs, TabsList, TabsTrigger } from '@/components/navigation'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { EmptyState, Skeleton } from '@/components/feedback'
import { useDebounce } from '@/lib/hooks'
import { api, queryKeys } from '@/lib/api/client'
import {
  adaptContractsList,
  type RegistryContractResponse,
  type RegistryListResponse,
} from '@/lib/api/adapters'
import type { Contract, ContractStatus } from '@/types'
import { ColumnDef } from '@tanstack/react-table'

const statusOptions: { value: ContractStatus | 'all'; label: string; count?: number }[] = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'proposed', label: 'Proposed' },
  { value: 'pending_review', label: 'Pending Review' },
  { value: 'active', label: 'Active' },
  { value: 'deprecated', label: 'Deprecated' },
]

const domainOptions = [
  { value: 'all', label: 'All Domains' },
  { value: 'analytics', label: 'Analytics' },
  { value: 'finance', label: 'Finance' },
  { value: 'crm', label: 'CRM' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'sales', label: 'Sales' },
]

function ContractsListPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  // URL state
  const statusFilter = (searchParams.get('status') as ContractStatus | 'all') || 'all'
  const domainFilter = searchParams.get('domain') || 'all'
  const searchQuery = searchParams.get('search') || ''

  // Local state
  const [search, setSearch] = useState(searchQuery)
  const debouncedSearch = useDebounce(search, 300)

  // Fetch contracts
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.list({
      status: statusFilter === 'all' ? undefined : statusFilter,
      domain: domainFilter === 'all' ? undefined : domainFilter,
      search: debouncedSearch || undefined,
    }),
    queryFn: async () => {
      const params = new URLSearchParams()
      // Map hub status to registry status
      if (statusFilter !== 'all') {
        // Registry uses: draft, active, deprecated, retired
        const statusMap: Record<string, string> = {
          draft: 'draft',
          active: 'active',
          deprecated: 'deprecated',
          proposed: 'draft', // No direct mapping
          pending_review: 'draft', // No direct mapping
        }
        params.append('status', statusMap[statusFilter] || statusFilter)
      }
      // Domain filter not supported by registry API
      // Search not directly supported - would need to use /search endpoint

      const response = await api.get<RegistryListResponse<RegistryContractResponse>>(
        `/contracts?${params.toString()}`
      )
      const adapted = adaptContractsList(response)
      return adapted.data
    },
  })

  const contracts = useMemo(() => data || [], [data])

  // Calculate status counts
  const statusCounts = useMemo(() => {
    const all = contracts
    return {
      all: all.length,
      draft: all.filter((c) => c.status === 'draft').length,
      proposed: all.filter((c) => c.status === 'proposed').length,
      pending_review: all.filter((c) => c.status === 'pending_review').length,
      active: all.filter((c) => c.status === 'active').length,
      deprecated: all.filter((c) => c.status === 'deprecated').length,
    }
  }, [contracts])

  // Update URL when filters change
  const updateFilters = (updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams.toString())
    Object.entries(updates).forEach(([key, value]) => {
      if (value && value !== 'all') {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    router.push(`/studio/contracts?${params.toString()}`, { scroll: false })
  }

  // Table columns
  const columns: ColumnDef<Contract>[] = [
    {
      accessorKey: 'name',
      header: 'Contract',
      cell: ({ row }) => (
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-text-tertiary" />
            <Link
              href={`/studio/contracts/${row.original.id}`}
              className="font-medium text-text-primary hover:text-primary transition-colors"
            >
              {row.original.name}
            </Link>
          </div>
          {row.original.description && (
            <p className="text-sm text-text-secondary line-clamp-1">
              {row.original.description}
            </p>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'asset',
      header: 'Data Asset',
      cell: ({ row }) => {
        if (row.original.assetId && row.original.asset) {
          return (
            <Link
              href={`/studio/assets/${row.original.assetId}`}
              className="text-text-link hover:underline"
            >
              {row.original.asset.name}
            </Link>
          )
        }
        return (
          <span className="text-text-tertiary italic text-sm">
            No asset (proposed)
          </span>
        )
      },
    },
    {
      accessorKey: 'domain',
      header: 'Domain',
      cell: ({ row }) => (
        <Badge variant="secondary" size="sm">
          {row.original.domain}
        </Badge>
      ),
    },
    {
      accessorKey: 'version',
      header: 'Version',
      cell: ({ row }) => (
        <span className="text-sm font-mono text-text-secondary">
          {row.original.version}
        </span>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <div className="flex flex-col gap-1">
          <ContractStatusBadge status={row.original.status} />
          {row.original.issueCount && row.original.issueCount > 0 && (
            <div className="flex items-center gap-1 text-xs text-warning-text">
              <AlertCircle className="h-3 w-3" />
              <span>{row.original.issueCount} {row.original.issueCount === 1 ? 'issue' : 'issues'}</span>
            </div>
          )}
        </div>
      ),
    },
  ]

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio' },
    { label: 'Contracts', href: '/studio/contracts' },
  ]

  return (
    <PageContainer>
      <PageHeader
        title="Data Contracts"
        description="Manage data contracts between producers and consumers"
        breadcrumbs={<Breadcrumbs items={breadcrumbs} />}
        actions={
          <Button onClick={() => router.push('/studio/contracts/new')}>
            <Plus className="h-4 w-4 mr-2" />
            New Contract
          </Button>
        }
      />

      {/* Status Tabs */}
      <div className="mb-6">
        <Tabs value={statusFilter} onValueChange={(value) => updateFilters({ status: value })}>
          <TabsList>
            {statusOptions.map((option) => (
              <TabsTrigger key={option.value} value={option.value}>
                {option.label}
                {statusCounts[option.value as keyof typeof statusCounts] > 0 && (
                  <Badge
                    variant={statusFilter === option.value ? 'primary' : 'secondary'}
                    size="sm"
                    className="ml-2"
                  >
                    {statusCounts[option.value as keyof typeof statusCounts]}
                  </Badge>
                )}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <Card className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <Input
              placeholder="Search by name, ID, or description..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                updateFilters({ search: e.target.value })
              }}
              leftIcon={<Search className="h-4 w-4" />}
            />
          </div>

          {/* Domain Filter */}
          <Select
            value={domainFilter}
            onValueChange={(value) => updateFilters({ domain: value })}
          >
            <option value="all">All Domains</option>
            {domainOptions.slice(1).map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>

          {/* Clear Filters */}
          {(statusFilter !== 'all' || domainFilter !== 'all' || search) && (
            <Button
              variant="ghost"
              onClick={() => {
                setSearch('')
                router.push('/studio/contracts')
              }}
            >
              Clear Filters
            </Button>
          )}
        </div>
        </Card>
      </div>

      {/* Table */}
      <Card>
        {isLoading ? (
          <div className="p-8 space-y-4">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        ) : error ? (
          <EmptyState
            icon={AlertCircle}
            title="Failed to load contracts"
            description="There was an error loading the contracts. Please try again."
            action={{
              label: 'Retry',
              onClick: () => window.location.reload(),
            }}
          />
        ) : contracts.length === 0 ? (
          <EmptyState
            icon={FileText}
            title={search || statusFilter !== 'all' ? "No contracts found" : "No contracts yet"}
            description={
              search || statusFilter !== 'all'
                ? "Try adjusting your filters or search query."
                : "Get started by creating your first data contract."
            }
            action={
              (!search && statusFilter === 'all')
                ? {
                    label: 'Create Contract',
                    onClick: () => router.push('/studio/contracts/new'),
                  }
                : undefined
            }
          />
        ) : (
          <DataTable
            columns={columns}
            data={contracts}
            enableSorting
            enablePagination
            pageSize={20}
            onRowClick={(row) => router.push(`/studio/contracts/${row.id}`)}
          />
        )}
      </Card>
    </PageContainer>
  )
}

export default function ContractsListPage() {
  return (
    <Suspense fallback={
      <PageContainer>
        <div className="space-y-6">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </PageContainer>
    }>
      <ContractsListPageContent />
    </Suspense>
  )
}
