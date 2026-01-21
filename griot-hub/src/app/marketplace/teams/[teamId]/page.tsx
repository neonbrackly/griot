'use client'

import { PageShell, PageContainer, PageHeader, Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Button, Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { AssetStatusBadge } from '@/components/data-display/StatusBadge'
import { Skeleton } from '@/components/feedback'
import { BackLink } from '@/components/navigation'
import { Users, Mail, Calendar, Database } from 'lucide-react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api, queryKeys } from '@/lib/api/client'
import type { Team, DataAsset } from '@/types'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo } from 'react'

export default function TeamDetailPage() {
  const params = useParams()
  const router = useRouter()
  const teamId = params.teamId as string

  // Fetch team details
  const {
    data: team,
    isLoading: teamLoading,
    error,
  } = useQuery<Team>({
    queryKey: queryKeys.teams.detail(teamId),
    queryFn: () => api.get(`/teams/${teamId}`),
  })

  // Fetch team's assets
  const {
    data: assetsData,
    isLoading: assetsLoading,
  } = useQuery<{ data: DataAsset[] }>({
    queryKey: queryKeys.assets.list({ ownerTeamId: teamId }),
    queryFn: () => api.get(`/assets?ownerTeamId=${teamId}`),
  })

  const assets = assetsData?.data || []

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
        accessorKey: 'tables',
        header: 'Tables',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.tables?.length || 0}</span>,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => <AssetStatusBadge status={row.original.status} />,
      },
      {
        accessorKey: 'lastSyncedAt',
        header: 'Last Synced',
        cell: ({ row }) => {
          const date = new Date(row.original.lastSyncedAt || '')
          return <span className="text-sm text-text-secondary">{date.toLocaleDateString()}</span>
        },
      },
    ],
    []
  )

  if (error) {
    return (
      <PageShell>
        <PageContainer>
          <BackLink href="/marketplace/teams" />
          <div className="text-center py-12">
            <p className="text-error-text">Failed to load team details</p>
          </div>
        </PageContainer>
      </PageShell>
    )
  }

  return (
    <PageShell>
      <PageContainer>
        <BackLink href="/marketplace/teams" />

        {teamLoading ? (
          <Skeleton className="h-32 w-full mb-6" />
        ) : (
          <>
            <div className="mb-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">
                      <Users className="w-6 h-6" />
                    </div>
                    <h1 className="text-3xl font-bold text-text-primary">{team?.name}</h1>
                  </div>
                  {team?.description && (
                    <p className="text-text-secondary mt-1">{team.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button variant="secondary">
                    <Mail className="w-4 h-4 mr-2" />
                    Contact Team
                  </Button>
                </div>
              </div>
            </div>

            {/* Team Info */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card padding="lg">
                <div className="text-xs text-text-tertiary mb-1">Members</div>
                <div className="text-2xl font-bold text-text-primary">{Math.floor(Math.random() * 20) + 5}</div>
              </Card>
              <Card padding="lg">
                <div className="text-xs text-text-tertiary mb-1">Data Assets</div>
                <div className="text-2xl font-bold text-text-primary">{assets.length}</div>
              </Card>
              <Card padding="lg">
                <div className="text-xs text-text-tertiary mb-1">Contracts</div>
                <div className="text-2xl font-bold text-text-primary">{Math.floor(Math.random() * 15) + 3}</div>
              </Card>
              <Card padding="lg">
                <div className="text-xs text-text-tertiary mb-1">Domains</div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {team?.domains && team.domains.length > 0 ? (
                    team.domains.map((domain) => (
                      <Badge key={domain} variant="secondary" size="sm">
                        {domain}
                      </Badge>
                    ))
                  ) : (
                    <Badge variant="secondary" size="sm">
                      General
                    </Badge>
                  )}
                </div>
              </Card>
            </div>
          </>
        )}

        {/* Team Members */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Team Members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {teamLoading ? (
                <>
                  <Skeleton className="h-12" />
                  <Skeleton className="h-12" />
                  <Skeleton className="h-12" />
                </>
              ) : (
                <>
                  {['Lead Data Engineer', 'Data Analyst', 'ML Engineer'].map((role, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg border border-border-default"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                          <Users className="w-5 h-5 text-primary-700 dark:text-primary-400" />
                        </div>
                        <div>
                          <div className="font-medium text-text-primary">Team Member {index + 1}</div>
                          <div className="text-xs text-text-tertiary">{role}</div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Mail className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Team Assets */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Team Assets
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <DataTable
              columns={columns}
              data={assets}
              loading={assetsLoading}
              enableSorting
              enablePagination
              pageSize={10}
              onRowClick={(row) => router.push(`/studio/assets/${row.id}`)}
            />
          </CardContent>
        </Card>
      </PageContainer>
    </PageShell>
  )
}
