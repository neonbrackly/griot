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
  FileCode2,
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
import { EmptyState } from '@/components/feedback/EmptyState'
import { Skeleton } from '@/components/feedback/Skeleton'
import { useDebounce } from '@/lib/hooks/useDebounce'
import { api, queryKeys } from '@/lib/api/client'
import { cn, formatRelativeTime } from '@/lib/utils'
import type { Schema, PaginatedResponse, SchemaStatus, SchemaSource } from '@/types'
import type { ColumnDef } from '@tanstack/react-table'

// Status configuration
const statusConfig: Record<SchemaStatus | 'all', { label: string; value: SchemaStatus | 'all' }> = {
  all: { label: 'All', value: 'all' },
  active: { label: 'Active', value: 'active' },
  draft: { label: 'Draft', value: 'draft' },
  deprecated: { label: 'Deprecated', value: 'deprecated' },
}

// Source configuration
const sourceConfig: Record<SchemaSource, { label: string; icon: React.ComponentType<{ className?: string }> }> = {
  manual: { label: 'Manual', icon: FileCode2 },
  connection: { label: 'Connection', icon: Database },
  import: { label: 'Imported', icon: FileCode2 },
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

// Status badge component
function SchemaStatusBadge({ status }: { status: SchemaStatus }) {
  const variants: Record<SchemaStatus, 'success' | 'warning' | 'secondary'> = {
    active: 'success',
    draft: 'warning',
    deprecated: 'secondary',
  }
  return (
    <Badge variant={variants[status]} className="capitalize">
      {status}
    </Badge>
  )
}

// Loading skeleton for the page
function SchemasListSkeleton() {
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

// Main content component
function SchemasListContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()

  // Get filters from URL
  const statusFilter = (searchParams.get('status') as SchemaStatus | 'all') || 'all'
  const domainFilter = searchParams.get('domain') || ''
  const sourceFilter = searchParams.get('source') as SchemaSource | null
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
    router.push(`/studio/schemas?${params.toString()}`, { scroll: false })
  }, [router, searchParams])

  // Update URL when debounced search changes
  React.useEffect(() => {
    if (debouncedSearch !== searchQuery) {
      updateFilters({ search: debouncedSearch || undefined, page: '1' })
    }
  }, [debouncedSearch, searchQuery, updateFilters])

  // Fetch schemas from API
  const { data, isLoading, isFetching } = useQuery({
    queryKey: queryKeys.schemas.list({
      status: statusFilter,
      domain: domainFilter,
      source: sourceFilter,
      search: debouncedSearch,
      page,
      pageSize,
    }),
    queryFn: () => {
      const params = new URLSearchParams()
      if (statusFilter && statusFilter !== 'all') params.set('status', statusFilter)
      if (domainFilter) params.set('domain', domainFilter)
      if (sourceFilter) params.set('source', sourceFilter)
      if (debouncedSearch) params.set('search', debouncedSearch)
      params.set('limit', String(pageSize))
      params.set('offset', String((page - 1) * pageSize))
      return api.get<{ items: Schema[]; total: number }>(`/schemas?${params.toString()}`)
    },
  })

  const schemas = data?.items || []
  const totalSchemas = data?.total || 0

  // Count schemas by status for tab badges
  const statusCounts = React.useMemo(() => {
    return {
      all: totalSchemas,
      active: schemas.filter(s => s.status === 'active').length,
      draft: schemas.filter(s => s.status === 'draft').length,
      deprecated: schemas.filter(s => s.status === 'deprecated').length,
    }
  }, [schemas, totalSchemas])

  // Handle status tab change
  const handleStatusChange = (status: string) => {
    updateFilters({ status: status === 'all' ? undefined : status, page: '1' })
  }

  // Handle domain filter change
  const handleDomainChange = (domain: string) => {
    updateFilters({ domain: domain === 'All Domains' ? undefined : domain, page: '1' })
  }

  // Prefetch schema detail on hover
  const handleRowHover = (schema: Schema) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.schemas.detail(schema.id),
      queryFn: () => api.get<Schema>(`/schemas/${schema.id}`),
      staleTime: 30000,
    })
  }

  // Navigate to schema detail
  const handleRowClick = (schema: Schema) => {
    router.push(`/studio/schemas/${schema.id}`)
  }

  // Table columns definition
  const columns: ColumnDef<Schema>[] = React.useMemo(
    () => [
      {
        accessorKey: 'name',
        header: 'Schema',
        cell: ({ row }) => {
          const SourceIcon = sourceConfig[row.original.source]?.icon || Database
          return (
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-50 dark:bg-primary-900/30">
                <SourceIcon className="h-4 w-4 text-primary-600" />
              </div>
              <div>
                <div className="font-medium text-text-primary">{row.original.name}</div>
                {row.original.businessName && row.original.businessName !== row.original.name && (
                  <div className="text-xs text-text-tertiary">{row.original.businessName}</div>
                )}
                {row.original.description && (
                  <div className="text-xs text-text-tertiary line-clamp-1 max-w-[300px]">
                    {row.original.description}
                  </div>
                )}
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: 'domain',
        header: 'Domain',
        cell: ({ row }) => row.original.domain ? (
          <Badge variant="secondary" className="capitalize">
            {row.original.domain}
          </Badge>
        ) : (
          <span className="text-text-tertiary">—</span>
        ),
      },
      {
        accessorKey: 'source',
        header: 'Source',
        cell: ({ row }) => (
          <Badge variant="outline" className="capitalize">
            {sourceConfig[row.original.source]?.label || row.original.source}
          </Badge>
        ),
      },
      {
        accessorKey: 'propertyCount',
        header: 'Properties',
        cell: ({ row }) => (
          <span className="text-text-secondary">
            {row.original.propertyCount || row.original.properties?.length || 0}
          </span>
        ),
      },
      {
        accessorKey: 'hasPii',
        header: 'PII',
        cell: ({ row }) => row.original.hasPii ? (
          <Badge variant="warning">PII</Badge>
        ) : (
          <span className="text-text-tertiary">—</span>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => (
          <SchemaStatusBadge status={row.original.status} />
        ),
      },
      {
        accessorKey: 'version',
        header: 'Version',
        cell: ({ row }) => (
          <span className="text-text-secondary text-sm font-mono">
            {row.original.version || '1.0.0'}
          </span>
        ),
      },
      {
        accessorKey: 'updatedAt',
        header: 'Updated',
        cell: ({ row }) => (
          <span className="text-text-secondary text-sm">
            {formatRelativeTime(row.original.updatedAt)}
          </span>
        ),
      },
    ],
    []
  )

  // Breadcrumbs
  const breadcrumbItems: BreadcrumbItem[] = [
    { label: 'Studio', href: '/studio' },
    { label: 'Schemas' },
  ]

  return (
    <PageContainer>
      <PageHeader
        title="Schemas"
        description="Manage your data schemas - define structure, constraints, and quality rules"
        breadcrumbs={<Breadcrumbs items={breadcrumbItems} />}
        actions={
          <Button onClick={() => router.push('/studio/schemas/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Schema
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
            placeholder="Search schemas..."
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
      {!isLoading && schemas.length === 0 ? (
        debouncedSearch || domainFilter || statusFilter !== 'all' ? (
          <EmptyState
            icon={Database}
            title="No schemas found"
            description="No schemas match your current filters. Try adjusting your search or filters."
            action={{
              label: 'Clear Filters',
              onClick: () => {
                setSearchInput('')
                router.push('/studio/schemas')
              },
              variant: 'secondary',
            }}
          />
        ) : (
          <EmptyState
            icon={Database}
            title="No schemas yet"
            description="Schemas define the structure, constraints, and quality rules for your data. Create your first schema to get started."
            action={{
              label: 'Create Schema',
              onClick: () => router.push('/studio/schemas/new'),
            }}
          />
        )
      ) : (
        <DataTable
          columns={columns}
          data={schemas}
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
export default function SchemasListPage() {
  return (
    <Suspense fallback={<SchemasListSkeleton />}>
      <SchemasListContent />
    </Suspense>
  )
}
