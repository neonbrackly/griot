'use client'

import { useState, useEffect, useRef } from 'react'
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
import { SchemaEditor, type SchemaTable } from '@/components/contracts/SchemaEditor'
import { SchemaChangeDialog } from '@/components/contracts/SchemaChangeDialog'
import { api, queryKeys, ApiError } from '@/lib/api/client'
import { adaptContract, type RegistryContractResponse } from '@/lib/api/adapters'
import { compareSchemas, type SchemaDiff } from '@/lib/utils/schema-diff'
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

// Change type options for contract updates (controls version increment)
type ChangeType = 'patch' | 'minor' | 'major'
const CHANGE_TYPE_OPTIONS: { value: ChangeType; label: string; description: string }[] = [
  { value: 'patch', label: 'Patch', description: 'Bug fixes, typos (1.0.0 → 1.0.1)' },
  { value: 'minor', label: 'Minor', description: 'New fields, non-breaking changes (1.0.0 → 1.1.0)' },
  { value: 'major', label: 'Major', description: 'Breaking changes, removed fields (1.0.0 → 2.0.0)' },
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
  // Schema
  schema: {
    tables: SchemaTable[]
  }
  // Change metadata required by API
  changeType: ChangeType
  changeNotes: string
}

export default function ContractEditPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.contractId as string

  const [formData, setFormData] = useState<EditFormData | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})
  // Store the original ODCS response for the PUT request
  // Using useRef instead of useState to avoid race condition - refs update synchronously
  const originalOdcsContractRef = useRef<RegistryContractResponse | null>(null)
  // Store original schema for comparison
  const originalSchemaRef = useRef<{ tables: SchemaTable[] } | null>(null)
  // Re-approval dialog state
  const [showReapprovalDialog, setShowReapprovalDialog] = useState(false)
  const [schemaDiff, setSchemaDiff] = useState<SchemaDiff | null>(null)
  const [schemaChangeReason, setSchemaChangeReason] = useState<string>('')

  // Fetch contract data - adapt for display
  const { data: contract, isLoading, error } = useQuery({
    queryKey: queryKeys.contracts.detail(contractId),
    queryFn: async () => {
      const response = await api.get<RegistryContractResponse>(`/contracts/${contractId}`)
      // Store the original ODCS format for PUT request (ref updates synchronously)
      originalOdcsContractRef.current = response
      // Return adapted format for display
      return adaptContract(response)
    },
  })

  // Initialize form data when contract loads
  useEffect(() => {
    if (contract && !formData) {
      // Transform contract schema to SchemaTable format
      const tables: SchemaTable[] = (contract.schema?.tables || []).map((table) => ({
        name: table.name,
        physicalName: table.physicalName,
        description: table.description,
        fields: (table.fields || []).map((field) => ({
          name: field.name,
          logicalType: field.logicalType || 'string',
          physicalType: field.physicalType,
          description: field.description,
          required: field.required || false,
          unique: field.unique || false,
          primaryKey: field.primaryKey || false,
          piiClassification: field.piiClassification,
        })),
      }))

      // Store original schema for comparison
      originalSchemaRef.current = { tables: JSON.parse(JSON.stringify(tables)) }

      setFormData({
        name: contract.name,
        description: contract.description || '',
        domain: contract.domain || '',
        status: contract.status,
        tags: contract.tags || [],
        sla: {
          freshnessHours: contract.sla?.freshnessHours ?? 24,
          availabilityPercent: contract.sla?.availabilityPercent ?? 99.5,
          responseTimeMs: contract.sla?.responseTimeMs,
        },
        schema: { tables },
        // Default to minor change type
        changeType: 'minor',
        changeNotes: '',
      })
    }
  }, [contract, formData])

  // Update contract mutation - use PUT as backend doesn't support PATCH
  const updateMutation = useMutation({
    mutationFn: async (data: EditFormData) => {
      const originalOdcsContract = originalOdcsContractRef.current
      if (!originalOdcsContract) {
        throw new Error('Original contract data not available')
      }

      // Transform schema tables to ODCS format
      const odcsSchema = data.schema.tables.map((table, tableIndex) => ({
        name: table.name,
        id: `schema-${tableIndex + 1}`,
        logicalType: 'object',
        description: table.description,
        properties: table.fields.map((field) => ({
          name: field.name,
          logicalType: field.logicalType || 'string',
          description: field.description,
          nullable: !field.required,
          primary_key: field.primaryKey,
          unique: field.unique,
          customProperties: field.piiClassification
            ? {
                privacy: {
                  is_pii: true,
                  sensitivity: field.piiClassification === 'sensitive' || field.piiClassification === 'financial'
                    ? 'restricted'
                    : field.piiClassification === 'personal'
                    ? 'confidential'
                    : 'internal',
                },
              }
            : undefined,
        })),
      }))

      // Transform form data to ODCS format expected by backend
      // Use original ODCS contract as base and apply form changes
      const payload = {
        // Change metadata required by API (will be extracted by backend)
        change_type: data.changeType,
        change_notes: data.changeNotes || undefined,
        // Contract data
        ...originalOdcsContract,
        name: data.name,
        description: data.description,
        status: data.status,
        tags: data.tags,
        schema: odcsSchema,
        sla: {
          ...((originalOdcsContract as Record<string, unknown>).sla || {}),
          freshness: data.sla.freshnessHours ? { target: `PT${data.sla.freshnessHours}H` } : undefined,
          availability: { targetPercent: data.sla.availabilityPercent },
          responseTime: data.sla.responseTimeMs ? { target: `${data.sla.responseTimeMs}ms` } : undefined,
        },
      }
      const response = await api.put<RegistryContractResponse>(`/contracts/${contractId}`, payload)
      return response
    },
    onSuccess: () => {
      toast.success('Contract updated', 'Your changes have been saved successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.detail(contractId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${contractId}`)
    },
    onError: (error: Error) => {
      // Extract meaningful error message from API response
      let errorMessage = 'Please try again'
      let errorTitle = 'Failed to update contract'

      if (error instanceof ApiError) {
        if (error.status === 409) {
          // Breaking changes detected
          errorTitle = 'Breaking changes detected'
          errorMessage = error.message || 'This update contains breaking changes. Use "Major" change type to allow breaking changes.'
        } else if (error.status === 422) {
          // Validation error
          errorTitle = 'Validation failed'
          errorMessage = error.message || 'Contract validation failed. Please check your changes.'
        } else if (error.status === 400) {
          // Bad request
          errorTitle = 'Invalid request'
          errorMessage = error.message || 'The request data is invalid.'
        } else if (error.status === 404) {
          // Not found
          errorTitle = 'Contract not found'
          errorMessage = error.message || 'The contract no longer exists.'
        } else {
          errorMessage = error.message || 'An unexpected error occurred.'
        }
      } else if (error?.message) {
        errorMessage = error.message
      }

      toast.error(errorTitle, errorMessage)
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
    if (!validateForm() || !formData) return

    // Check if this is an active contract with schema changes
    if (contract?.status === 'active' && originalSchemaRef.current) {
      const diff = compareSchemas(originalSchemaRef.current, formData.schema)
      if (diff.hasChanges) {
        // Show re-approval dialog
        setSchemaDiff(diff)
        setShowReapprovalDialog(true)
        return
      }
    }

    // No schema changes or not an active contract - proceed normally
    updateMutation.mutate(formData)
  }

  // Handle confirmation of schema change re-approval
  const handleReapprovalConfirm = (reason: string) => {
    if (!formData) return

    // Store the reason and proceed with mutation
    setSchemaChangeReason(reason)
    setShowReapprovalDialog(false)

    // Mutate with schema change reason - this will trigger re-approval workflow
    updateMutation.mutate({
      ...formData,
      changeType: 'major', // Schema changes on active contracts are always major
      changeNotes: `Schema change requiring re-approval: ${reason}`,
    })
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
          {/* Change Details - Full width at top */}
          <Card className="p-6 mb-6 border-primary-border bg-primary-bg/5">
            <h3 className="text-lg font-semibold text-text-primary mb-2">Change Details</h3>
            <p className="text-sm text-text-secondary mb-4">
              Describe your changes. The version will be automatically incremented based on the change type.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField name="changeType" label="Change Type" required>
                <select
                  className="flex h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
                  value={formData.changeType}
                  onChange={(e) => updateField('changeType', e.target.value as ChangeType)}
                >
                  {CHANGE_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label} - {option.description}
                    </option>
                  ))}
                </select>
              </FormField>
              <div className="md:col-span-2">
                <FormField name="changeNotes" label="Change Notes" description="Describe what changed">
                  <textarea
                    className="flex min-h-[40px] w-full rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
                    value={formData.changeNotes}
                    onChange={(e) => updateField('changeNotes', e.target.value)}
                    placeholder="e.g., Updated description and SLA requirements"
                    rows={1}
                  />
                </FormField>
              </div>
            </div>
          </Card>

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

              {/* Schema Editor */}
              <Card className="p-6">
                <SchemaEditor
                  tables={formData.schema.tables}
                  onChange={(tables) =>
                    setFormData((prev) => (prev ? { ...prev, schema: { tables } } : null))
                  }
                  status={contract.status}
                  isReadOnly={contract.status === 'deprecated' || (contract.status as string) === 'retired'}
                />
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

      {/* Schema Change Re-approval Dialog */}
      {schemaDiff && (
        <SchemaChangeDialog
          isOpen={showReapprovalDialog}
          onClose={() => setShowReapprovalDialog(false)}
          onConfirm={handleReapprovalConfirm}
          isSubmitting={updateMutation.isPending}
          diff={schemaDiff}
        />
      )}
    </PageContainer>
  )
}
