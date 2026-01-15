'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, AlertCircle, Loader2 } from 'lucide-react'

import { PageContainer, Card } from '@/components/layout'
import { Button, Input, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { FormField } from '@/components/forms/FormField'
import { TagInput } from '@/components/forms/TagInput'
import { EmptyState, Skeleton } from '@/components/feedback'
import { ContractStatusBadge } from '@/components/data-display/StatusBadge'
import { api, queryKeys } from '@/lib/api/client'
import { toast } from '@/lib/hooks'
import type { Contract, ContractStatus } from '@/types'

const DOMAINS = ['Analytics', 'CRM', 'Finance', 'Marketing', 'Operations', 'Sales', 'Engineering']
const STATUS_OPTIONS: { value: ContractStatus; label: string }[] = [
  { value: 'draft', label: 'Draft' },
  { value: 'proposed', label: 'Proposed' },
  { value: 'pending_review', label: 'Pending Review' },
  { value: 'active', label: 'Active' },
  { value: 'deprecated', label: 'Deprecated' },
]

interface EditFormData {
  name: string
  description: string
  domain: string
  status: ContractStatus
  tags: string[]
  sla: {
    freshnessHours: number
    availabilityPercent: number
    responseTimeMs?: number
  }
}

export default function ContractEditPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.contractId as string

  const [formData, setFormData] = useState<EditFormData | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch contract data
  const { data: contract, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<Contract>(`/contracts/${contractId}`)
      return response
    },
  })

  // Initialize form data when contract loads
  useEffect(() => {
    if (contract && !formData) {
      setFormData({
        name: contract.name,
        description: contract.description || '',
        domain: contract.domain,
        status: contract.status,
        tags: contract.tags || [],
        sla: {
          freshnessHours: contract.sla.freshnessHours,
          availabilityPercent: contract.sla.availabilityPercent,
          responseTimeMs: contract.sla.responseTimeMs,
        },
      })
    }
  }, [contract, formData])

  // Update contract mutation
  const updateMutation = useMutation({
    mutationFn: async (data: EditFormData) => {
      const response = await api.patch<Contract>(`/contracts/${contractId}`, data)
      return response
    },
    onSuccess: () => {
      toast.success('Contract updated', 'Your changes have been saved successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${contractId}`)
    },
    onError: () => {
      toast.error('Failed to update contract', 'Please try again')
    },
  })

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData?.name || formData.name.length < 3) {
      newErrors.name = 'Name must be at least 3 characters'
    }
    if (!formData?.description || formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    }
    if (!formData?.domain) {
      newErrors.domain = 'Domain is required'
    }
    if (!formData?.sla.freshnessHours || formData.sla.freshnessHours < 1) {
      newErrors.freshnessHours = 'Freshness must be at least 1 hour'
    }
    if (!formData?.sla.availabilityPercent || formData.sla.availabilityPercent < 0 || formData.sla.availabilityPercent > 100) {
      newErrors.availabilityPercent = 'Availability must be between 0 and 100'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validateForm() && formData) {
      updateMutation.mutate(formData)
    }
  }

  const updateField = (field: keyof EditFormData, value: any) => {
    setFormData((prev) => prev ? { ...prev, [field]: value } : null)
    setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  const updateSLA = (field: keyof EditFormData['sla'], value: number) => {
    setFormData((prev) =>
      prev ? { ...prev, sla: { ...prev.sla, [field]: value } } : null
    )
  }

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
          description="The contract you're trying to edit doesn't exist or you don't have access to it."
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
      <BackLink href={`/studio/contracts/${contractId}`} label="Back to Contract" />

      <div className="mt-6 mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Edit Contract</h1>
          <div className="flex items-center gap-3 mt-2 text-sm text-text-secondary">
            <span className="font-mono">{contract.version}</span>
            <span>•</span>
            <ContractStatusBadge status={contract.status} size="sm" />
          </div>
        </div>
        <Button
          type="submit"
          form="edit-contract-form"
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </div>

      {formData && (
        <form id="edit-contract-form" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Basic Info */}
            <div className="space-y-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Basic Information</h3>
                <div className="space-y-4">
                  <FormField name="name" label="Contract Name" required error={errors.name}>
                    <Input
                      value={formData.name}
                      onChange={(e) => updateField('name', e.target.value)}
                      placeholder="Enter contract name"
                    />
                  </FormField>

                  <FormField name="description" label="Description" required error={errors.description}>
                    <textarea
                      className="flex min-h-[100px] w-full rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
                      value={formData.description}
                      onChange={(e) => updateField('description', e.target.value)}
                      placeholder="Describe what this contract defines..."
                    />
                  </FormField>

                  <FormField name="domain" label="Domain" required error={errors.domain}>
                    <select
                      className="flex h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
                      value={formData.domain}
                      onChange={(e) => updateField('domain', e.target.value)}
                    >
                      <option value="">Select domain</option>
                      {DOMAINS.map((domain) => (
                        <option key={domain} value={domain}>{domain}</option>
                      ))}
                    </select>
                  </FormField>

                  <FormField name="status" label="Status" required>
                    <select
                      className="flex h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
                      value={formData.status}
                      onChange={(e) => updateField('status', e.target.value as ContractStatus)}
                    >
                      {STATUS_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </FormField>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Tags</h3>
                <TagInput
                  value={formData.tags}
                  onChange={(tags) => updateField('tags', tags)}
                  placeholder="Add tags..."
                />
              </Card>
            </div>

            {/* Right Column - SLA & Schema Info */}
            <div className="space-y-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Service Level Agreement</h3>
                <div className="space-y-4">
                  <FormField name="freshnessHours" label="Freshness (hours)" required error={errors.freshnessHours}>
                    <Input
                      type="number"
                      value={formData.sla.freshnessHours}
                      onChange={(e) => updateSLA('freshnessHours', parseInt(e.target.value) || 0)}
                      min={1}
                    />
                  </FormField>

                  <FormField name="availabilityPercent" label="Availability (%)" required error={errors.availabilityPercent}>
                    <Input
                      type="number"
                      value={formData.sla.availabilityPercent}
                      onChange={(e) => updateSLA('availabilityPercent', parseFloat(e.target.value) || 0)}
                      min={0}
                      max={100}
                      step={0.1}
                    />
                  </FormField>

                  <FormField name="responseTimeMs" label="Response Time (ms)" description="Optional">
                    <Input
                      type="number"
                      value={formData.sla.responseTimeMs || ''}
                      onChange={(e) => updateSLA('responseTimeMs', parseInt(e.target.value) || 0)}
                      min={0}
                      placeholder="Optional"
                    />
                  </FormField>
                </div>
              </Card>

              {/* Schema Info (Read-only) */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Schema</h3>
                <p className="text-sm text-text-secondary mb-4">
                  Schema is read-only. To modify schema, re-sync from the linked data asset.
                </p>
                <div className="space-y-3">
                  {contract.schema.tables.map((table) => (
                    <div
                      key={table.name}
                      className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary"
                    >
                      <span className="font-medium text-text-primary">{table.name}</span>
                      <Badge variant="secondary" size="sm">{table.fields.length} fields</Badge>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Quality Rules Info (Read-only summary) */}
              {contract.qualityRules && contract.qualityRules.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-4">Quality Rules</h3>
                  <p className="text-sm text-text-secondary mb-2">
                    {contract.qualityRules.length} rule{contract.qualityRules.length !== 1 ? 's' : ''} configured
                  </p>
                  <div className="flex gap-2">
                    <Badge variant="success" size="sm">
                      {contract.qualityRules.filter(r => r.enabled).length} enabled
                    </Badge>
                    <Badge variant="secondary" size="sm">
                      {contract.qualityRules.filter(r => !r.enabled).length} disabled
                    </Badge>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </form>
      )}
    </PageContainer>
  )
}
