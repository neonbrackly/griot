'use client'

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Search,
  Plus,
  Database,
  Loader2,
  Filter,
  ChevronDown,
} from 'lucide-react'

import { PageContainer, PageHeader } from '@/components/layout/PageShell'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import type { BreadcrumbItem } from '@/components/navigation/Breadcrumbs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import {
  Tabs,
  TabsList,
  TabsTrigger,
} from '@/components/navigation/Tabs'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuCheckboxItem,
} from '@/components/ui/DropdownMenu'
import { DataTable } from '@/components/data-display/DataTable'
import { AssetStatusBadge } from '@/components/data-display/StatusBadge'
import { EmptyState } from '@/components/feedback/EmptyState'
import { Skeleton } from '@/components/feedback/Skeleton'
import { useDebounce } from '@/lib/hooks/useDebounce'
import { api, queryKeys } from '@/lib/api/client'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { DataAsset, PaginatedResponse, AssetStatus } from '@/types'
import type { ColumnDef } from '@tanstack/react-table'

// Status configuration with icons and colors
const statusConfig: Record<AssetStatus | 'all', { label: string; value: AssetStatus | 'all' }> = {
  all: { label: 'All', value: 'all' },
  active: { label: 'Active', value: 'active' },
  draft: { label: 'Draft', value: 'draft' },
  deprecated: { label: 'Deprecated', value: 'deprecated' },
}

// Domain options
const domains = [
  'All Domains',
  'analytics',
  'finance',
  'crm',
  'operations',
  'marketing',
  'ml',
]

// Loading skeleton for the page
function AssetsListSkeleton() {
  return (
    <PageContainer>
      <div className="mb-6">
        <Skeleton className="h-8 w-48 mb-2" />
        <Skeleton className="h-4 w-80" />
      </div>
      <div className="mb-6">
        <Skeleton className="h-10 w-96" />
      </div>
      <div className="mb-6 flex gap-4">
        <Skeleton className="h-10 flex-1 max-w-md" />
        <Skeleton className="h-10 w-40" />
      </div>
      <div className="rounded-lg border border-border-default">
        <div className="bg-bg-tertiary px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </div>
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="border-t border-border-default px-4 py-4">
            <Skeleton className="h-6 w-full" />
          </div>
        ))}
      </div>
    </PageContainer>
  )
}

// Main content component that uses useSearchParams
function AssetsListContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()

  // Get filters from URL
  const statusFilter = (searchParams.get('status') as AssetStatus | 'all') || 'all'
  const domainFilter = searchParams.get('domain') || ''
  const searchQuery = searchParams.get('search') || ''
  const page = parseInt(searchParams.get('page') || '1', 10)
  const pageSize = 20

  // Local state for search input (debounced)
  const [searchInput, setSearchInput] = React.useState(searchQuery)
  const debouncedSearch = useDebounce(searchInput, 300)

  // Update URL filters
  const updateFilters = React.useCallback((updates: Record<string, string | undefined>) => {
    const params = new URLSearchParams(searchParams.toString())
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    router.push(`/studio/assets?${params.toString()}`, { scroll: false })
  }, [router, searchParams])

  // Update URL when debounced search changes
  React.useEffect(() => {
    if (debouncedSearch !== searchQuery) {
      updateFilters({ search: debouncedSearch || undefined, page: '1' })
    }
  }, [debouncedSearch, searchQuery, updateFilters])

  // Fetch assets from API
  const { data, isLoading, isFetching } = useQuery({
    queryKey: queryKeys.assets.list({
      status: statusFilter,
      domain: domainFilter,
      search: debouncedSearch,
      page,
      pageSize,
    }),
    queryFn: () => {
      const params = new URLSearchParams()
      if (statusFilter && statusFilter !== 'all') params.set('status', statusFilter)
      if (domainFilter) params.set('domain', domainFilter)
      if (debouncedSearch) params.set('search', debouncedSearch)
      params.set('page', String(page))
      params.set('pageSize', String(pageSize))
      return api.get<PaginatedResponse<DataAsset>>(`/assets?${params.toString()}`)
    },
  })

  const assets = data?.data || []
  const totalAssets = data?.meta?.total || 0

  // Count assets by status for tab badges
  const statusCounts = React.useMemo(() => {
    return {
      all: totalAssets,
      active: assets.filter(a => a.status === 'active').length,
      draft: assets.filter(a => a.status === 'draft').length,
      deprecated: assets.filter(a => a.status === 'deprecated').length,
    }
  }, [assets, totalAssets])

  // Handle status tab change
  const handleStatusChange = (status: string) => {
    updateFilters({ status: status === 'all' ? undefined : status, page: '1' })
  }

  // Handle domain filter change
  const handleDomainChange = (domain: string) => {
    updateFilters({ domain: domain === 'All Domains' ? undefined : domain, page: '1' })
  }

  // Prefetch asset detail on hover
  const handleRowHover = (asset: DataAsset) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.assets.detail(asset.id),
      queryFn: () => api.get<DataAsset>(`/assets/${asset.id}`),
      staleTime: 30000,
    })
  }

  // Navigate to asset detail
  const handleRowClick = (asset: DataAsset) => {
    router.push(`/studio/assets/${asset.id}`)
  }

  // Table columns definition
  const columns: ColumnDef<DataAsset>[] = React.useMemo(
    () => [
      {
        accessorKey: 'name',
        header: 'Asset',
        cell: ({ row }) => (
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-50 dark:bg-primary-900/30">
              <Database className="h-4 w-4 text-primary-600" />
            </div>
            <div>
              <div className="font-medium text-text-primary">{row.original.name}</div>
              {row.original.description && (
                <div className="text-xs text-text-tertiary line-clamp-1 max-w-[300px]">
                  {row.original.description}
                </div>
              )}
            </div>
          </div>
        ),
      },
      {
        accessorKey: 'domain',
        header: 'Domain',
        cell: ({ row }) => (
          <Badge variant="secondary" className="capitalize">
            {row.original.domain}
          </Badge>
        ),
      },
      {
        accessorKey: 'tables',
        header: 'Tables',
        cell: ({ row }) => (
          <span className="text-text-secondary">
            {row.original.tables?.length || 0}
          </span>
        ),
      },
      {
        accessorKey: 'ownerTeamId',
        header: 'Owner',
        cell: ({ row }) => (
          <span className="text-text-secondary">
            Team {row.original.ownerTeamId.replace('team-', '')}
          </span>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => (
          <AssetStatusBadge status={row.original.status} />
        ),
      },
      {
        accessorKey: 'lastSyncedAt',
        header: 'Last Synced',
        cell: ({ row }) => (
          <span className="text-text-secondary text-sm">
            {formatRelativeTime(row.original.lastSyncedAt)}
          </span>
        ),
      },
    ],
    []
  )

  // Breadcrumbs
  const breadcrumbItems: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio' },
    { label: 'Data Assets' },
  ]

  return (
    <PageContainer>
      <PageHeader
        title="Data Assets"
        description="Manage your registered data assets from connected databases"
        breadcrumbs={<Breadcrumbs items={breadcrumbItems} />}
        actions={
          <Button onClick={() => router.push('/studio/assets/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Asset
          </Button>
        }
      />

      {/* Status Tabs */}
      <div className="mb-6">
        <Tabs value={statusFilter} onValueChange={handleStatusChange}>
          <TabsList>
            {Object.entries(statusConfig).map(([key, config]) => (
              <TabsTrigger key={key} value={key} className="gap-2">
                {config.label}
                <Badge
                  variant="secondary"
                  className={cn(
                    'ml-1 text-xs',
                    statusFilter === key && 'bg-primary-100 text-primary-700 dark:bg-primary-900/40'
                  )}
                >
                  {statusCounts[key as keyof typeof statusCounts] || 0}
                </Badge>
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Filters Bar */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Input
            placeholder="Search assets..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            leftIcon={<Search className="h-4 w-4" />}
            rightIcon={
              isFetching && debouncedSearch ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : undefined
            }
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Domain Filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="secondary" className="gap-2">
                <Filter className="h-4 w-4" />
                {domainFilter || 'All Domains'}
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuLabel>Filter by Domain</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {domains.map((domain) => (
                <DropdownMenuCheckboxItem
                  key={domain}
                  checked={domainFilter === domain || (!domainFilter && domain === 'All Domains')}
                  onCheckedChange={() => handleDomainChange(domain)}
                >
                  {domain === 'All Domains' ? domain : domain.charAt(0).toUpperCase() + domain.slice(1)}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Data Table or Empty State */}
      {!isLoading && assets.length === 0 ? (
        debouncedSearch || domainFilter || statusFilter !== 'all' ? (
          <EmptyState
            icon={Database}
            title="No assets found"
            description="No assets match your current filters. Try adjusting your search or filters."
            action={{
              label: 'Clear Filters',
              onClick: () => {
                setSearchInput('')
                router.push('/studio/assets')
              },
              variant: 'secondary',
            }}
          />
        ) : (
          <EmptyState
            icon={Database}
            title="No data assets yet"
            description="Data assets represent tables and datasets from your data warehouse. Create your first asset to get started."
            action={{
              label: 'Create Data Asset',
              onClick: () => router.push('/studio/assets/new'),
            }}
          />
        )
      ) : (
        <DataTable
          columns={columns}
          data={assets}
          loading={isLoading}
          enableSorting
          enablePagination
          pageSize={pageSize}
          onRowClick={handleRowClick}
          onRowHover={handleRowHover}
        />
      )}
    </PageContainer>
  )
}

// Main page component with Suspense boundary
export default function AssetsListPage() {
  return (
    <Suspense fallback={<AssetsListSkeleton />}>
      <AssetsListContent />
    </Suspense>
  )
}
