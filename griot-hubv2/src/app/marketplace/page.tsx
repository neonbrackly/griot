'use client'

import { PageShell, PageContainer, PageHeader, Card } from '@/components/layout'
import { Button, Input, Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { AssetStatusBadge } from '@/components/data-display/StatusBadge'
import { Search, Filter, Star, TrendingUp, Users } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api, queryKeys } from '@/lib/api/client'
import type { DataAsset } from '@/types'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo, useState } from 'react'
import { useDebounce } from '@/lib/hooks'

export default function MarketplacePage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch all assets
  const {
    data: assetsData,
    isLoading,
  } = useQuery<{ data: DataAsset[] }>({
    queryKey: queryKeys.assets.all,
    queryFn: () => api.get('/assets'),
  })

  const assets = assetsData?.data || []

  // Get unique domains
  const domains = useMemo(() => {
    const uniqueDomains = new Set(assets.map((a) => a.domain))
    return ['all', ...Array.from(uniqueDomains)]
  }, [assets])

  // Filter assets
  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const matchesSearch =
        !debouncedSearch ||
        asset.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        asset.description?.toLowerCase().includes(debouncedSearch.toLowerCase())

      const matchesDomain = selectedDomain === 'all' || asset.domain === selectedDomain

      return matchesSearch && matchesDomain && asset.status === 'active'
    })
  }, [assets, debouncedSearch, selectedDomain])

  // Table columns
  const columns: ColumnDef<DataAsset>[] = useMemo(
    () => [
      {
        accessorKey: 'name',
        header: 'Asset',
        cell: ({ row }) => (
          <div>
            <div className="font-medium text-text-primary">{row.original.name}</div>
            <div className="text-xs text-text-tertiary line-clamp-1">{row.original.description}</div>
          </div>
        ),
      },
      {
        accessorKey: 'domain',
        header: 'Domain',
        cell: ({ row }) => <Badge variant="secondary">{row.original.domain}</Badge>,
      },
      {
        accessorKey: 'ownerTeamId',
        header: 'Owner',
        cell: ({ row }) => (
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-text-tertiary" />
            <span className="text-sm text-text-secondary">{row.original.ownerTeamId || 'Unassigned'}</span>
          </div>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => <AssetStatusBadge status={row.original.status} />,
      },
      {
        accessorKey: 'popularity',
        header: 'Popularity',
        cell: () => {
          const popularity = Math.floor(Math.random() * 100)
          return (
            <div className="flex items-center gap-1">
              <TrendingUp className="w-4 h-4 text-success-500" />
              <span className="text-sm text-text-secondary">{popularity}</span>
            </div>
          )
        },
      },
    ],
    []
  )

  return (
    <PageShell>
      <PageContainer>
        <PageHeader
          title="Data Marketplace"
          description="Discover and explore data assets across your organization"
          actions={
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => router.push('/marketplace/teams')}>
                <Users className="w-4 h-4 mr-2" />
                Teams
              </Button>
              <Button variant="secondary" onClick={() => router.push('/marketplace/lineage')}>
                <TrendingUp className="w-4 h-4 mr-2" />
                Lineage
              </Button>
            </div>
          }
        />

        {/* Featured Assets */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-text-primary mb-3">Featured Assets</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {assets.slice(0, 3).map((asset) => (
              <Card
                key={asset.id}
                padding="lg"
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => router.push(`/studio/assets/${asset.id}`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <Badge variant="secondary">{asset.domain}</Badge>
                  <Star className="w-5 h-5 text-warning-500" />
                </div>
                <h3 className="text-base font-semibold text-text-primary mb-1">{asset.name}</h3>
                <p className="text-sm text-text-secondary line-clamp-2">{asset.description}</p>
                <div className="mt-4 pt-4 border-t border-border-default flex items-center justify-between text-xs text-text-tertiary">
                  <span>{asset.tables?.length || 0} tables</span>
                  <span>{asset.ownerTeamId || 'Unassigned'}</span>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-4 flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-tertiary" />
            <Input
              placeholder="Search assets by name or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-tertiary" />
            <div className="flex gap-1">
              {domains.map((domain) => (
                <Button
                  key={domain}
                  variant={selectedDomain === domain ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedDomain(domain)}
                >
                  {domain}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Assets Table */}
        <Card>
          <DataTable
            columns={columns}
            data={filteredAssets}
            loading={isLoading}
            enableSorting
            enablePagination
            pageSize={20}
            onRowClick={(row) => router.push(`/studio/assets/${row.id}`)}
          />
        </Card>
      </PageContainer>
    </PageShell>
  )
}
