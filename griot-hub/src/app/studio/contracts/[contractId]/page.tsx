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
  UserPlus,
} from 'lucide-react'
import Link from 'next/link'

import { PageContainer, Card } from '@/components/layout'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { Button, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { EmptyState, Skeleton } from '@/components/feedback'
import { ReviewDialog, ConfirmDialog } from '@/components/contracts/ReviewDialog'
import { AssignReviewerDialog } from '@/components/contracts/AssignReviewerDialog'
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
  const [showAssignReviewerDialog, setShowAssignReviewerDialog] = useState(false)

  // Fetch contract data
  const { data: contract, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<RegistryContractResponse>(`/contracts/${contractId}`)
      return adaptContract(response)
    },
  })

  // Fetch owner team details if we have an ownerTeamId
  const { data: ownerTeam } = useQuery({
    queryKey: ['teams', contract?.ownerTeamId],
    queryFn: async () => {
      if (!contract?.ownerTeamId) return null
      try {
        const response = await api.get<{ id: string; name: string; description?: string }>(`/teams/${contract.ownerTeamId}`)
        return response
      } catch {
        return null
      }
    },
    enabled: !!contract?.ownerTeamId,
  })

  // Fetch reviewer details if we have a reviewerId
  const { data: reviewerDetails } = useQuery({
    queryKey: ['reviewer', contract?.reviewerId, contract?.reviewerType],
    queryFn: async () => {
      if (!contract?.reviewerId || !contract?.reviewerType) return null
      try {
        if (contract.reviewerType === 'team') {
          const response = await api.get<{ id: string; name: string }>(`/teams/${contract.reviewerId}`)
          return { name: response.name, type: 'team' as const }
        } else {
          const response = await api.get<{ id: string; name?: string; email?: string; username?: string }>(`/users/${contract.reviewerId}`)
          return { name: response.name || response.email || response.username || contract.reviewerId, type: 'user' as const }
        }
      } catch {
        return null
      }
    },
    enabled: !!contract?.reviewerId && !!contract?.reviewerType,
  })

  // Submit for review mutation - POST /contracts/{id}/submit
  const submitForReviewMutation = useMutation({
    mutationFn: async (message?: string) => {
      // Always include message field - use empty string if not provided
      return api.post<RegistryContractResponse>(`/contracts/${contractId}/submit`, {
        message: message || '',
      })
    },
    onSuccess: () => {
      toast.success('Submitted for Review', 'Contract has been submitted for review')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
    },
    onError: (error: Error) => {
      const msg = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to submit for review', msg)
    },
  })

  // Approve contract mutation - POST /contracts/{id}/approve
  const approveMutation = useMutation({
    mutationFn: async (comment?: string) => {
      // Always include comment field - use empty string if not provided
      return api.post<RegistryContractResponse>(`/contracts/${contractId}/approve`, {
        comment: comment || '',
      })
    },
    onSuccess: () => {
      toast.success('Contract Approved', 'Contract is now active')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
    },
    onError: (error: Error) => {
      const message = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to approve contract', message)
    },
  })

  // Reject contract mutation - POST /contracts/{id}/reject
  const rejectMutation = useMutation({
    mutationFn: async (feedback: string) => {
      return api.post<RegistryContractResponse>(`/contracts/${contractId}/reject`, {
        feedback,
      })
    },
    onSuccess: () => {
      toast.success('Changes Requested', 'Contract has been sent back to draft')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
    },
    onError: (error: Error) => {
      const message = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to reject contract', message)
    },
  })

  // Deprecate contract mutation - POST /contracts/{id}/deprecate
  const deprecateMutation = useMutation({
    mutationFn: async (reason: string) => {
      return api.post<RegistryContractResponse>(`/contracts/${contractId}/deprecate`, {
        reason,
      })
    },
    onSuccess: () => {
      toast.success('Contract Deprecated', 'Contract has been deprecated')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
    },
    onError: (error: Error) => {
      const message = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to deprecate contract', message)
    },
  })

  // Assign reviewer mutation - POST /contracts/{id}/reviewer
  const assignReviewerMutation = useMutation({
    mutationFn: async (data: { reviewerType: 'user' | 'team'; reviewerId: string }) => {
      return api.post<RegistryContractResponse>(`/contracts/${contractId}/reviewer`, {
        reviewer_type: data.reviewerType,
        reviewer_id: data.reviewerId,
      })
    },
    onSuccess: () => {
      toast.success('Reviewer Assigned', 'A reviewer has been assigned to this contract')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
    },
    onError: (error: Error) => {
      const message = error instanceof ApiError ? error.message : 'Please try again'
      toast.error('Failed to assign reviewer', message)
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
    submitForReviewMutation.mutate(notes || undefined)
    setShowSubmitDialog(false)
  }

  // Handle approve
  const handleApprove = () => {
    approveMutation.mutate(undefined)
    setShowApproveDialog(false)
  }

  // Handle request changes
  const handleRequestChanges = (feedback: string) => {
    rejectMutation.mutate(feedback)
    setShowRejectDialog(false)
  }

  // Handle deprecate
  const handleDeprecate = (reason: string) => {
    deprecateMutation.mutate(reason)
    setShowDeprecateDialog(false)
  }

  // Handle assign reviewer
  const handleAssignReviewer = (data: { reviewerType: 'user' | 'team'; reviewerId: string; reviewerName: string }) => {
    assignReviewerMutation.mutate({
      reviewerType: data.reviewerType,
      reviewerId: data.reviewerId,
    })
    setShowAssignReviewerDialog(false)
  }

  // Handle submit for review click - checks if reviewer is assigned first
  const handleSubmitClick = () => {
    if (!contract?.reviewerId) {
      // No reviewer assigned - show assign reviewer dialog
      toast.error('Reviewer Required', 'Please assign a reviewer before submitting for review')
      setShowAssignReviewerDialog(true)
    } else {
      // Reviewer assigned - show submit dialog
      setShowSubmitDialog(true)
    }
  }

  // Combined isPending for UI state
  const isStatusChangePending = submitForReviewMutation.isPending || approveMutation.isPending || rejectMutation.isPending || deprecateMutation.isPending || assignReviewerMutation.isPending

  // Check if current user can review
  const canReview = user?.role?.name === 'Admin' // TODO: Also check if user is assigned reviewer
  const isOwner = true // TODO: Check if current user is owner
  const canEdit = contract?.status === 'draft' || contract?.status === 'proposed'
  const hasReviewer = !!contract?.reviewerId

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
                onClick={handleSubmitClick}
                disabled={isStatusChangePending}
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
                  disabled={isStatusChangePending}
                >
                  <Check className="h-4 w-4" />
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setShowRejectDialog(true)}
                  disabled={isStatusChangePending}
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
                disabled={isStatusChangePending}
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
              {/* Owner Team */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-tertiary">
                  <Users className="h-4 w-4" />
                  <span>Owner Team</span>
                </div>
                <span className="text-sm font-medium text-text-primary">
                  {ownerTeam?.name || contract.ownerTeamName || contract.ownerTeamId || 'Not assigned'}
                </span>
              </div>

              {/* Reviewer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-tertiary">
                  <Eye className="h-4 w-4" />
                  <span>Reviewer</span>
                </div>
                {contract.reviewerId ? (
                  <div className="flex items-center gap-2">
                    {(reviewerDetails?.type || contract.reviewerType) === 'team' ? (
                      <Users className="h-3 w-3 text-text-tertiary" />
                    ) : (
                      <User className="h-3 w-3 text-text-tertiary" />
                    )}
                    <span className="text-sm font-medium text-text-primary">
                      {reviewerDetails?.name || contract.reviewerName || contract.reviewerId}
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-text-tertiary">Not assigned</span>
                    {contract.status === 'draft' && (
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => setShowAssignReviewerDialog(true)}
                      >
                        <UserPlus className="h-3 w-3 mr-1" />
                        Assign
                      </Button>
                    )}
                  </div>
                )}
              </div>

              {/* Show "Change Reviewer" button if reviewer is assigned and contract is draft */}
              {contract.reviewerId && contract.status === 'draft' && (
                <div className="pt-2 border-t border-border-subtle">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-center"
                    onClick={() => setShowAssignReviewerDialog(true)}
                  >
                    <UserPlus className="h-4 w-4 mr-2" />
                    Change Reviewer
                  </Button>
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
        isSubmitting={isStatusChangePending}
        type="submit_for_review"
      />

      <ConfirmDialog
        isOpen={showApproveDialog}
        onClose={() => setShowApproveDialog(false)}
        onConfirm={handleApprove}
        isSubmitting={isStatusChangePending}
        title="Approve Contract"
        description="This contract will be marked as active and can be used in production. Are you sure you want to approve it?"
        confirmLabel="Approve"
        icon={CheckCircle}
      />

      <ReviewDialog
        isOpen={showRejectDialog}
        onClose={() => setShowRejectDialog(false)}
        onSubmit={handleRequestChanges}
        isSubmitting={isStatusChangePending}
        type="request_changes"
      />

      <ReviewDialog
        isOpen={showDeprecateDialog}
        onClose={() => setShowDeprecateDialog(false)}
        onSubmit={handleDeprecate}
        isSubmitting={isStatusChangePending}
        type="deprecate"
      />

      <AssignReviewerDialog
        isOpen={showAssignReviewerDialog}
        onClose={() => setShowAssignReviewerDialog(false)}
        onAssign={handleAssignReviewer}
        isSubmitting={assignReviewerMutation.isPending}
        currentReviewerId={contract?.reviewerId}
        currentReviewerType={contract?.reviewerType}
      />
    </PageContainer>
  )
}
