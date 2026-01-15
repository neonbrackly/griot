'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FileText,
  Edit,
  Play,
  Download,
  Eye,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowLeft,
} from 'lucide-react'
import Link from 'next/link'

import { PageContainer, Card } from '@/components/layout'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { Button, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { EmptyState, Skeleton } from '@/components/feedback'
import { api, queryKeys } from '@/lib/api/client'
import { toast } from '@/lib/hooks'
import type { Contract } from '@/types'

export default function ContractDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.contractId as string

  // Fetch contract data
  const { data: contract, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<Contract>(`/contracts/${contractId}`)
      return response
    },
  })

  // Run checks mutation
  const runChecksMutation = useMutation({
    mutationFn: () => api.post(`/contracts/${contractId}/run`),
    onSuccess: () => {
      toast.success('Checks started', 'Contract validation checks have been initiated')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
    },
    onError: () => {
      toast.error('Failed to run checks', 'Please try again')
    },
  })

  if (isLoading) {
    return (
      <PageContainer>
        <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </PageContainer>
    )
  }

  if (error || !contract) {
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
        <BackLink href="/studio/contracts" label="All Contracts" />

        <div className="mt-4 flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-text-secondary" />
              <div>
                <h1 className="text-2xl font-semibold text-text-primary">{contract.name}</h1>
                <div className="flex items-center gap-3 mt-1 text-sm text-text-secondary">
                  <span className="font-mono">{contract.version}</span>
                  <span>•</span>
                  <ContractStatusBadge status={contract.status} size="sm" />
                  <span>•</span>
                  <Badge variant="secondary" size="sm">{contract.domain}</Badge>
                  <span>•</span>
                  <span>ODCS {contract.odcsVersion}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push(`/studio/contracts/${contractId}/edit`)}
            >
              <Edit className="h-4 w-4" />
              Edit
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => runChecksMutation.mutate()}
              disabled={runChecksMutation.isPending}
            >
              <Play className="h-4 w-4" />
              {runChecksMutation.isPending ? 'Running...' : 'Run Checks'}
            </Button>
            <Button variant="secondary" size="sm">
              <Download className="h-4 w-4" />
              Generate
            </Button>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Contract Definition */}
        <div className="space-y-6">
          {/* Description */}
          {contract.description && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-3">Description</h3>
              <p className="text-text-primary">{contract.description}</p>
            </Card>
          )}

          {/* Schema */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-secondary mb-4">Schema</h3>
            <div className="space-y-4">
              {contract.schema.tables.map((table) => (
                <div key={table.name} className="border border-border-default rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-text-primary">{table.name}</h4>
                    <Badge variant="secondary" size="sm">{table.fields.length} fields</Badge>
                  </div>
                  <div className="space-y-2">
                    {table.fields.slice(0, 5).map((field) => (
                      <div
                        key={field.name}
                        className="flex items-center justify-between text-sm p-2 rounded bg-bg-secondary"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-text-primary">{field.name}</span>
                          {field.primaryKey && (
                            <Badge variant="primary" size="xs">PK</Badge>
                          )}
                          {field.required && (
                            <Badge variant="secondary" size="xs">Required</Badge>
                          )}
                        </div>
                        <span className="text-text-secondary font-mono text-xs">
                          {field.logicalType}
                        </span>
                      </div>
                    ))}
                    {table.fields.length > 5 && (
                      <p className="text-sm text-text-tertiary text-center py-2">
                        + {table.fields.length - 5} more fields
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Data Asset */}
          {contract.assetId && contract.asset && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-3">Data Asset</h3>
              <Link
                href={`/studio/assets/${contract.assetId}`}
                className="flex items-center justify-between p-3 rounded-lg border border-border-default hover:bg-bg-secondary transition-colors"
              >
                <div>
                  <p className="font-medium text-text-primary">{contract.asset.name}</p>
                  <p className="text-sm text-text-secondary mt-1">
                    {contract.asset.description}
                  </p>
                </div>
                <ArrowLeft className="h-4 w-4 text-text-tertiary rotate-180" />
              </Link>
            </Card>
          )}

          {/* SLA */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-secondary mb-4">Service Level Agreement</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-text-tertiary mb-1">Freshness</p>
                <p className="text-lg font-semibold text-text-primary">
                  {contract.sla.freshnessHours}h
                </p>
              </div>
              <div>
                <p className="text-xs text-text-tertiary mb-1">Availability</p>
                <p className="text-lg font-semibold text-text-primary">
                  {contract.sla.availabilityPercent}%
                </p>
              </div>
              {contract.sla.responseTimeMs && (
                <div>
                  <p className="text-xs text-text-tertiary mb-1">Response Time</p>
                  <p className="text-lg font-semibold text-text-primary">
                    {contract.sla.responseTimeMs}ms
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right Column - Runtime & Governance */}
        <div className="space-y-6">
          {/* Last Run Status */}
          {contract.lastRunAt && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-4">Last Run</h3>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {contract.lastRunStatus === 'passed' ? (
                    <CheckCircle className="h-8 w-8 text-success-text" />
                  ) : (
                    <AlertCircle className="h-8 w-8 text-error-text" />
                  )}
                  <div>
                    <p className="font-medium text-text-primary capitalize">
                      {contract.lastRunStatus}
                    </p>
                    <p className="text-sm text-text-secondary">
                      {new Date(contract.lastRunAt).toLocaleString()}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push(`/studio/contracts/${contractId}/runs`)}
                >
                  View History
                </Button>
              </div>
            </Card>
          )}

          {/* Quality Rules */}
          {contract.qualityRules && contract.qualityRules.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-4">
                Quality Rules ({contract.qualityRules.length})
              </h3>
              <div className="space-y-3">
                {contract.qualityRules.slice(0, 5).map((rule) => (
                  <div
                    key={rule.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary"
                  >
                    <div>
                      <p className="font-medium text-text-primary text-sm">{rule.name}</p>
                      <p className="text-xs text-text-tertiary mt-1">
                        {rule.type} • {rule.field || rule.table}
                      </p>
                    </div>
                    <Badge variant={rule.enabled ? 'success' : 'secondary'} size="sm">
                      {rule.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                ))}
                {contract.qualityRules.length > 5 && (
                  <p className="text-sm text-text-tertiary text-center py-2">
                    + {contract.qualityRules.length - 5} more rules
                  </p>
                )}
              </div>
            </Card>
          )}

          {/* Issues */}
          {contract.issueCount && contract.issueCount > 0 && (
            <Card className="p-6 border-warning-border bg-warning-bg/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-warning-text">
                  Active Issues ({contract.issueCount})
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push(`/studio/issues?contract=${contractId}`)}
                >
                  View All
                </Button>
              </div>
              <p className="text-sm text-text-secondary">
                This contract has {contract.issueCount} active {contract.issueCount === 1 ? 'issue' : 'issues'} that need attention.
              </p>
            </Card>
          )}

          {/* Tags */}
          {contract.tags && contract.tags.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {contract.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" size="sm">
                    {tag}
                  </Badge>
                ))}
              </div>
            </Card>
          )}

          {/* Metadata */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-secondary mb-4">Metadata</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-text-tertiary">Created</span>
                <span className="text-text-primary">
                  {new Date(contract.createdAt).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-tertiary">Last Updated</span>
                <span className="text-text-primary">
                  {new Date(contract.updatedAt).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-tertiary">Contract ID</span>
                <span className="text-text-primary font-mono">{contract.id}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  )
}
