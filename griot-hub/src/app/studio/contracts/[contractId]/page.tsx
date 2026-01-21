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
  Send,
  Check,
  X,
  Archive,
  Users,
  User,
  Shield,
  History,
} from 'lucide-react'
import Link from 'next/link'

import { PageContainer, Card } from '@/components/layout'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { Button, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { EmptyState, Skeleton } from '@/components/feedback'
import { ReviewDialog, ConfirmDialog } from '@/components/contracts/ReviewDialog'
import { PIISummaryCard, extractPIIFields } from '@/components/contracts/PIISummaryCard'
import { QualityRulesCard } from '@/components/contracts/QualityRulesCard'
import { api, queryKeys, ApiError } from '@/lib/api/client'
import { adaptContract, type RegistryContractResponse } from '@/lib/api/adapters'
import { toast } from '@/lib/hooks'
import { useAuth } from '@/components/providers/AuthProvider'
import type { Contract, ContractStatus } from '@/types'

export default function ContractDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.contractId as string
  const { user } = useAuth()

  // Dialog states
  const [showSubmitDialog, setShowSubmitDialog] = useState(false)
  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [showDeprecateDialog, setShowDeprecateDialog] = useState(false)

  // Fetch contract data
  const { data: contract, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<RegistryContractResponse>(`/contracts/${contractId}`)
      return adaptContract(response)
    },
  })

  // Status change mutation
  const statusMutation = useMutation({
    mutationFn: async ({
      status,
      feedback,
    }: {
      status: ContractStatus
      feedback?: string
    }) => {
      const payload: Record<string, unknown> = { status }
      if (feedback) {
        payload.review_feedback = feedback
      }
      return api.put<RegistryContractResponse>(`/contracts/${contractId}`, payload)
    },
    onSuccess: (_, { status }) => {
      const messages: Record<ContractStatus, { title: string; desc: string }> = {
        pending_review: { title: 'Submitted for Review', desc: 'Contract has been submitted for review' },
        active: { title: 'Contract Approved', desc: 'Contract is now active' },
        draft: { title: 'Changes Requested', desc: 'Contract has been sent back to draft' },
        deprecated: { title: 'Contract Deprecated', desc: 'Contract has been deprecated' },
        proposed: { title: 'Status Updated', desc: 'Contract status has been updated' },
      }
      const msg = messages[status] || { title: 'Status Updated', desc: 'Contract status has been updated' }
      toast.success(msg.title, msg.desc)
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
    },
    onError: (error: Error) => {
      const message = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to update status', message)
    },
  })

  // Run checks mutation - creates a new run via registry API
  const runChecksMutation = useMutation({
    mutationFn: () =>
      api.post('/runs', {
        contract_id: contractId,
        environment: 'development',
      }),
    onSuccess: () => {
      toast.success('Checks started', 'Contract validation run has been created')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
    },
    onError: () => {
      toast.error('Failed to run checks', 'Please try again')
    },
  })

  // Handle submit for review
  const handleSubmitForReview = (notes: string) => {
    statusMutation.mutate({ status: 'pending_review', feedback: notes || undefined })
    setShowSubmitDialog(false)
  }

  // Handle approve
  const handleApprove = () => {
    statusMutation.mutate({ status: 'active' })
    setShowApproveDialog(false)
  }

  // Handle request changes
  const handleRequestChanges = (feedback: string) => {
    statusMutation.mutate({ status: 'draft', feedback })
    setShowRejectDialog(false)
  }

  // Handle deprecate
  const handleDeprecate = (reason: string) => {
    statusMutation.mutate({ status: 'deprecated', feedback: reason })
    setShowDeprecateDialog(false)
  }

  // Check if current user can review
  const canReview = user?.role?.name === 'Admin' // TODO: Also check if user is assigned reviewer
  const isOwner = true // TODO: Check if current user is owner
  const canEdit = contract?.status === 'draft' || contract?.status === 'proposed'

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
            {/* Edit button - available for draft/proposed */}
            {canEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push(`/studio/contracts/${contractId}/edit`)}
              >
                <Edit className="h-4 w-4" />
                Edit
              </Button>
            )}

            {/* Submit for Review - available for draft contracts */}
            {contract.status === 'draft' && isOwner && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowSubmitDialog(true)}
                disabled={statusMutation.isPending}
              >
                <Send className="h-4 w-4" />
                Submit for Review
              </Button>
            )}

            {/* Review Actions - available for pending_review contracts when user can review */}
            {contract.status === 'pending_review' && canReview && (
              <>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setShowApproveDialog(true)}
                  disabled={statusMutation.isPending}
                >
                  <Check className="h-4 w-4" />
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setShowRejectDialog(true)}
                  disabled={statusMutation.isPending}
                >
                  <X className="h-4 w-4" />
                  Request Changes
                </Button>
              </>
            )}

            {/* Deprecate - available for active contracts when user is owner/admin */}
            {contract.status === 'active' && (isOwner || canReview) && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeprecateDialog(true)}
                disabled={statusMutation.isPending}
              >
                <Archive className="h-4 w-4" />
                Deprecate
              </Button>
            )}

            {/* Run Checks - available for active contracts */}
            {contract.status === 'active' && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => runChecksMutation.mutate()}
                disabled={runChecksMutation.isPending}
              >
                <Play className="h-4 w-4" />
                {runChecksMutation.isPending ? 'Running...' : 'Run Checks'}
              </Button>
            )}

            <Button variant="secondary" size="sm">
              <Download className="h-4 w-4" />
              Generate
            </Button>
          </div>
        </div>
      </div>

      {/* Pending Review Banner */}
      {contract.status === 'pending_review' && (
        <div className="mb-6 p-4 rounded-lg border border-warning-border bg-warning-bg/10">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-warning-text" />
            <span className="font-medium text-warning-text">Awaiting Review</span>
          </div>
          <p className="text-sm text-text-secondary mt-1">
            This contract has been submitted for review and is awaiting approval.
            {canReview && ' You can approve or request changes.'}
          </p>
        </div>
      )}

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
              {/* Schema is in adapted format: { tables: [...] } with fields */}
              {(contract.schema?.tables || []).map((table) => (
                <div key={table.name} className="border border-border-default rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-text-primary">{table.name}</h4>
                    <Badge variant="secondary" size="sm">{table.fields?.length || 0} fields</Badge>
                  </div>
                  <div className="space-y-2">
                    {(table.fields || []).slice(0, 5).map((field) => (
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
                          {field.piiClassification && (
                            <Badge variant="warning" size="xs" className="flex items-center gap-1">
                              <Shield className="h-3 w-3" />
                              PII
                            </Badge>
                          )}
                        </div>
                        <span className="text-text-secondary font-mono text-xs">
                          {field.logicalType}
                        </span>
                      </div>
                    ))}
                    {(table.fields?.length || 0) > 5 && (
                      <p className="text-sm text-text-tertiary text-center py-2">
                        + {(table.fields?.length || 0) - 5} more fields
                      </p>
                    )}
                  </div>
                </div>
              ))}
              {(!contract.schema?.tables || contract.schema.tables.length === 0) && (
                <p className="text-sm text-text-tertiary text-center py-4">No schema defined</p>
              )}
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
          {contract.sla && (
            <Card className="p-6">
              <h3 className="text-sm font-semibold text-text-secondary mb-4">Service Level Agreement</h3>
              <div className="grid grid-cols-2 gap-4">
                {contract.sla.freshnessHours != null && (
                  <div>
                    <p className="text-xs text-text-tertiary mb-1">Freshness</p>
                    <p className="text-lg font-semibold text-text-primary">
                      {contract.sla.freshnessHours}h
                    </p>
                  </div>
                )}
                {contract.sla.availabilityPercent != null && (
                  <div>
                    <p className="text-xs text-text-tertiary mb-1">Availability</p>
                    <p className="text-lg font-semibold text-text-primary">
                      {contract.sla.availabilityPercent}%
                    </p>
                  </div>
                )}
                {contract.sla.responseTimeMs != null && (
                  <div>
                    <p className="text-xs text-text-tertiary mb-1">Response Time</p>
                    <p className="text-lg font-semibold text-text-primary">
                      {contract.sla.responseTimeMs}ms
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column - Runtime & Governance */}
        <div className="space-y-6">
          {/* Ownership & Governance */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-text-secondary mb-4">Ownership & Governance</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-tertiary">
                  <Users className="h-4 w-4" />
                  <span>Owner Team</span>
                </div>
                <span className="text-sm font-medium text-text-primary">
                  {contract.ownerTeamId || 'Not assigned'}
                </span>
              </div>
              {(contract as unknown as { owner?: string }).owner && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <User className="h-4 w-4" />
                    <span>Owner</span>
                  </div>
                  <span className="text-sm font-medium text-text-primary">
                    {(contract as unknown as { owner?: string }).owner}
                  </span>
                </div>
              )}
              {(contract as unknown as { reviewer_id?: string; reviewerName?: string }).reviewer_id && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <Eye className="h-4 w-4" />
                    <span>Reviewer</span>
                  </div>
                  <span className="text-sm font-medium text-text-primary">
                    {(contract as unknown as { reviewerName?: string }).reviewerName || 'Assigned'}
                  </span>
                </div>
              )}
              {(contract as unknown as { approved_by?: string }).approved_by && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <CheckCircle className="h-4 w-4" />
                    <span>Approved By</span>
                  </div>
                  <span className="text-sm font-medium text-text-primary">
                    {(contract as unknown as { approved_by?: string }).approved_by}
                  </span>
                </div>
              )}
            </div>
          </Card>

          {/* PII Summary - Enhanced */}
          <PIISummaryCard piiFields={extractPIIFields(contract.schema)} />

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

          {/* Quality Rules - Enhanced */}
          {contract.qualityRules && contract.qualityRules.length > 0 && (
            <QualityRulesCard
              rules={contract.qualityRules}
              onViewAll={() => router.push(`/studio/contracts/${contractId}/quality`)}
            />
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

          {/* Version History */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-text-secondary">Version History</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push(`/studio/contracts/${contractId}/versions`)}
              >
                View All
              </Button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-2 rounded bg-bg-secondary">
                <div className="flex-shrink-0">
                  <History className="h-4 w-4 text-text-tertiary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-text-primary">v{contract.version}</span>
                    <Badge variant="success" size="xs">Current</Badge>
                  </div>
                  <p className="text-xs text-text-tertiary mt-1">
                    {new Date(contract.updatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </Card>

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
                <span className="text-text-tertiary">ODCS Version</span>
                <span className="text-text-primary font-mono">{contract.odcsVersion}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-tertiary">Contract ID</span>
                <span className="text-text-primary font-mono text-xs">{contract.id}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Status Workflow Dialogs */}
      <ReviewDialog
        isOpen={showSubmitDialog}
        onClose={() => setShowSubmitDialog(false)}
        onSubmit={handleSubmitForReview}
        isSubmitting={statusMutation.isPending}
        type="submit_for_review"
      />

      <ConfirmDialog
        isOpen={showApproveDialog}
        onClose={() => setShowApproveDialog(false)}
        onConfirm={handleApprove}
        isSubmitting={statusMutation.isPending}
        title="Approve Contract"
        description="This contract will be marked as active and can be used in production. Are you sure you want to approve it?"
        confirmLabel="Approve"
      />

      <ReviewDialog
        isOpen={showRejectDialog}
        onClose={() => setShowRejectDialog(false)}
        onSubmit={handleRequestChanges}
        isSubmitting={statusMutation.isPending}
        type="request_changes"
      />

      <ReviewDialog
        isOpen={showDeprecateDialog}
        onClose={() => setShowDeprecateDialog(false)}
        onSubmit={handleDeprecate}
        isSubmitting={statusMutation.isPending}
        type="deprecate"
      />
    </PageContainer>
  )
}
