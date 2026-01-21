'use client'

import * as React from 'react'
import { Suspense } from 'react'
import Link from 'next/link'
import { useRouter, useParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Database,
  RefreshCw,
  Edit2,
  FileText,
  Clock,
  Server,
  ChevronRight,
  ChevronDown,
  Table,
  Key,
  Shield,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'

import { PageContainer, PageHeader } from '@/components/layout/PageShell'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/feedback/Skeleton'
import { AssetStatusBadge } from '@/components/data-display/StatusBadge'
import { api, queryKeys } from '@/lib/api/client'
import { cn, formatRelativeTime, formatNumber, formatDate } from '@/lib/utils'
import { useToast } from '@/lib/hooks/useToast'
import type { DataAsset, Connection, DataTable, DataField } from '@/types'

// Type icons based on data type
function getTypeIcon(type: string): string {
  const upperType = type.toUpperCase()
  if (upperType.includes('VARCHAR') || upperType.includes('TEXT') || upperType.includes('STRING')) {
    return 'Aa'
  }
  if (upperType.includes('INT') || upperType.includes('NUMBER') || upperType.includes('DECIMAL') || upperType.includes('FLOAT')) {
    return '#'
  }
  if (upperType.includes('DATE') || upperType.includes('TIME')) {
    return 'D'
  }
  if (upperType.includes('BOOL')) {
    return 'B'
  }
  if (upperType.includes('JSON') || upperType.includes('OBJECT')) {
    return '{}'
  }
  return '?'
}

// PII badge for sensitive fields
function PIIBadge({ piiType }: { piiType: string }) {
  return (
    <Badge variant="secondary" className="text-xs bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
      <Shield className="w-3 h-3 mr-1" />
      {piiType}
    </Badge>
  )
}

// Individual field row component
function FieldRow({ field }: { field: DataField }) {
  return (
    <div className="flex items-center justify-between py-2 px-3 hover:bg-bg-hover rounded transition-colors">
      <div className="flex items-center gap-3">
        <span className="w-6 h-6 flex items-center justify-center bg-bg-tertiary rounded text-xs font-mono text-text-secondary">
          {getTypeIcon(field.type)}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn(
            'font-mono text-sm',
            field.isPrimaryKey ? 'font-semibold text-primary-600' : 'text-text-primary'
          )}>
            {field.name}
          </span>
          {field.isPrimaryKey && (
            <Key className="w-3.5 h-3.5 text-primary-500" aria-label="Primary Key" />
          )}
          {field.piiType && <PIIBadge piiType={field.piiType} />}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-text-tertiary font-mono">
          {field.type}
        </span>
        {!field.isNullable && (
          <span className="text-xs text-text-tertiary">NOT NULL</span>
        )}
      </div>
    </div>
  )
}

// Expandable table card component
function TableCard({ table }: { table: DataTable }) {
  const [isExpanded, setIsExpanded] = React.useState(true)

  return (
    <Card padding="none" className="overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-bg-hover transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-text-tertiary" />
          ) : (
            <ChevronRight className="w-4 h-4 text-text-tertiary" />
          )}
          <Table className="w-4 h-4 text-text-secondary" />
          <span className="font-medium text-text-primary">{table.name}</span>
          <Badge variant="secondary" className="text-xs">
            {table.fields?.length || 0} fields
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          {table.rowCount !== undefined && (
            <span className="text-xs text-text-tertiary">
              {formatNumber(table.rowCount)} rows
            </span>
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-border-default">
          {table.description && (
            <div className="px-4 py-2 bg-bg-tertiary border-b border-border-default">
              <p className="text-sm text-text-secondary">{table.description}</p>
            </div>
          )}
          <div className="divide-y divide-border-default">
            {table.fields?.map((field, index) => (
              <FieldRow key={`${field.name}-${index}`} field={field} />
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}

// Schema viewer component
function SchemaViewer({ tables }: { tables: DataTable[] }) {
  if (!tables || tables.length === 0) {
    return (
      <Card className="text-center py-8">
        <Table className="w-8 h-8 mx-auto mb-2 text-text-tertiary" />
        <p className="text-text-secondary">No tables in this asset</p>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {tables.map((table) => (
        <TableCard key={table.id || table.name} table={table} />
      ))}
    </div>
  )
}

// Connection info card
function ConnectionInfoCard({ connectionId }: { connectionId: string }) {
  const { data: connection, isLoading } = useQuery({
    queryKey: queryKeys.connections.detail(connectionId),
    queryFn: () => api.get<Connection>(`/connections/${connectionId}`),
    enabled: !!connectionId,
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    )
  }

  if (!connection) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Server className="w-4 h-4" />
          Connection
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 mt-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Database</span>
          <span className="text-sm font-medium text-text-primary">{connection.name}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Type</span>
          <Badge variant="secondary" className="capitalize">{connection.type}</Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Status</span>
          <span className={cn(
            'flex items-center gap-1 text-sm',
            connection.status === 'active' ? 'text-green-600' : 'text-text-secondary'
          )}>
            {connection.status === 'active' ? (
              <CheckCircle2 className="w-3.5 h-3.5" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5" />
            )}
            {connection.status === 'active' ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <Link
          href={`/settings/connections`}
          className="flex items-center gap-1 text-sm text-text-link hover:underline mt-2"
        >
          Manage Connection
          <ExternalLink className="w-3.5 h-3.5" />
        </Link>
      </CardContent>
    </Card>
  )
}

// SLA card
function SLACard({ sla }: { sla: DataAsset['sla'] }) {
  if (!sla) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Service Level Agreements
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 mt-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Freshness</span>
          <span className="text-sm font-medium text-text-primary">
            {sla.freshnessHours} hours
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Availability</span>
          <span className="text-sm font-medium text-text-primary">
            {sla.availabilityPercent}%
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

// Contracts using this asset card
function ContractsCard({ assetId }: { assetId: string }) {
  // In a real app, this would fetch contracts using the asset
  const mockContracts = [
    { id: 'contract-1', name: 'Customer Analytics v2.0', status: 'active' },
    { id: 'contract-2', name: 'Churn Prediction v1.5', status: 'active' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Contracts Using This Asset
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 mt-3">
        {mockContracts.length === 0 ? (
          <p className="text-sm text-text-tertiary">No contracts use this asset yet</p>
        ) : (
          mockContracts.map((contract) => (
            <Link
              key={contract.id}
              href={`/studio/contracts/${contract.id}`}
              className="flex items-center justify-between py-2 px-3 -mx-3 hover:bg-bg-hover rounded transition-colors"
            >
              <span className="text-sm text-text-link">{contract.name}</span>
              <ChevronRight className="w-4 h-4 text-text-tertiary" />
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  )
}

// Audit trail card
function AuditTrailCard({ asset }: { asset: DataAsset }) {
  const auditEvents = [
    { action: 'Schema synced', date: asset.lastSyncedAt },
    { action: 'Asset updated', date: asset.updatedAt },
    { action: 'Asset created', date: asset.createdAt },
  ].filter(e => e.date)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Audit Trail
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 mt-3">
        {auditEvents.map((event, index) => (
          <div key={index} className="flex items-center justify-between py-1">
            <span className="text-sm text-text-secondary">{event.action}</span>
            <span className="text-xs text-text-tertiary">
              {formatRelativeTime(event.date)}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

// Loading skeleton
function AssetDetailSkeleton() {
  return (
    <PageContainer>
      <div className="mb-6">
        <Skeleton className="h-4 w-24 mb-4" />
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    </PageContainer>
  )
}

// Main content component
function AssetDetailContent() {
  const router = useRouter()
  const params = useParams()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const assetId = params.assetId as string

  // Fetch asset data
  const { data: asset, isLoading, error } = useQuery({
    queryKey: queryKeys.assets.detail(assetId),
    queryFn: () => api.get<DataAsset>(`/assets/${assetId}`),
    enabled: !!assetId,
  })

  // Sync schema mutation
  const syncMutation = useMutation({
    mutationFn: () => api.post<DataAsset>(`/assets/${assetId}/sync`),
    onMutate: async () => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: queryKeys.assets.detail(assetId) })

      // Snapshot current state
      const previousAsset = queryClient.getQueryData(queryKeys.assets.detail(assetId))

      // Optimistically update
      queryClient.setQueryData(queryKeys.assets.detail(assetId), (old: DataAsset | undefined) => {
        if (!old) return old
        return {
          ...old,
          lastSyncedAt: new Date().toISOString(),
        }
      })

      return { previousAsset }
    },
    onSuccess: () => {
      toast({
        title: 'Schema synced',
        description: 'Schema has been updated from database',
        variant: 'success',
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.assets.detail(assetId) })
    },
    onError: (error: Error, _, context) => {
      // Rollback on error
      if (context?.previousAsset) {
        queryClient.setQueryData(queryKeys.assets.detail(assetId), context.previousAsset)
      }
      toast({
        title: 'Sync failed',
        description: error.message || 'Failed to sync schema',
        variant: 'error',
      })
    },
  })

  if (isLoading) {
    return <AssetDetailSkeleton />
  }

  if (error || !asset) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-error-text" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Asset not found</h2>
          <p className="text-text-secondary mb-4">
            The requested data asset could not be found or you dont have permission to view it.
          </p>
          <Button onClick={() => router.push('/studio/assets')}>
            Back to Assets
          </Button>
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      {/* Header */}
      <div className="mb-6">
        <BackLink href="/studio/assets" label="All Assets" className="mb-4" />

        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 dark:bg-primary-900/30">
              <Database className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-3">
                {asset.name}
                <AssetStatusBadge status={asset.status} />
              </h1>
              <p className="text-text-secondary mt-1 flex items-center gap-2">
                <Badge variant="secondary" className="capitalize">{asset.domain}</Badge>
                <span className="text-text-tertiary">|</span>
                <span>{asset.tables?.length || 0} tables</span>
                <span className="text-text-tertiary">|</span>
                <span>Last synced {formatRelativeTime(asset.lastSyncedAt)}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
            >
              <RefreshCw className={cn(
                'w-4 h-4 mr-2',
                syncMutation.isPending && 'animate-spin'
              )} />
              Sync Schema
            </Button>
            <Button variant="secondary">
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button onClick={() => router.push(`/studio/contracts/new?assetId=${assetId}`)}>
              <FileText className="w-4 h-4 mr-2" />
              Create Contract
            </Button>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Schema */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-lg font-medium text-text-primary mb-4 flex items-center gap-2">
              <Table className="w-5 h-5" />
              Schema ({asset.tables?.length || 0} tables)
            </h2>
            <SchemaViewer tables={asset.tables || []} />
          </div>

          {/* Description */}
          {asset.description && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Description</CardTitle>
              </CardHeader>
              <CardContent className="mt-3">
                <p className="text-sm text-text-secondary">{asset.description}</p>
              </CardContent>
            </Card>
          )}

          {/* Tags */}
          {asset.tags && asset.tags.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Tags</CardTitle>
              </CardHeader>
              <CardContent className="mt-3">
                <div className="flex flex-wrap gap-2">
                  {asset.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right column - Metadata */}
        <div className="space-y-4">
          <ConnectionInfoCard connectionId={asset.connectionId} />
          <SLACard sla={asset.sla} />
          <ContractsCard assetId={asset.id} />
          <AuditTrailCard asset={asset} />
        </div>
      </div>
    </PageContainer>
  )
}

// Main page component with Suspense boundary
export default function AssetDetailPage() {
  return (
    <Suspense fallback={<AssetDetailSkeleton />}>
      <AssetDetailContent />
    </Suspense>
  )
}
