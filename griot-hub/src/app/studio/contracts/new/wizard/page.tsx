'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { PageContainer, Card } from '@/components/layout'
import { Button } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { WizardStepper } from '@/components/forms/WizardStepper'
import { toast } from '@/lib/hooks'
import { api, queryKeys } from '@/lib/api/client'
import type { Contract } from '@/types'

// Validation result type from the API
interface ValidationResult {
  is_valid: boolean
  has_errors: boolean
  has_warnings: boolean
  error_count: number
  warning_count: number
  issues: Array<{
    code: string
    field: string | null
    message: string
    severity: 'error' | 'warning'
    suggestion: string | null
  }>
}

// Placeholder step components (simplified for token efficiency)
import { Step1BasicInfo } from '@/components/contracts/wizard/Step1BasicInfo'
import { Step2Asset } from '@/components/contracts/wizard/Step2Asset'
import { Step3Schema } from '@/components/contracts/wizard/Step3Schema'
import { Step4Quality } from '@/components/contracts/wizard/Step4Quality'
import { Step5SLA } from '@/components/contracts/wizard/Step5SLA'
import { Step6Tags } from '@/components/contracts/wizard/Step6Tags'
import { Step7Review } from '@/components/contracts/wizard/Step7Review'

export interface ContractFormData {
  // Basic Info (Step 1)
  name?: string
  description?: string
  domain?: string
  status?: 'draft' | 'proposed'

  // Reviewer (Step 1)
  reviewerType?: 'user' | 'team'
  reviewerId?: string
  reviewerName?: string

  // Asset (Step 2)
  assetId?: string
  isProposed?: boolean

  // Schema (Step 3)
  tables?: any[]

  // Quality (Step 4)
  qualityRules?: any[]

  // SLA (Step 5)
  sla?: {
    freshnessHours?: number
    availabilityPercent?: number
    responseTimeMs?: number
  }

  // Tags (Step 6)
  tags?: string[]
  ownerTeamId?: string
}

const wizardSteps = [
  { id: 'basic', label: 'Basic Info', description: 'Contract name and details' },
  { id: 'asset', label: 'Data Asset', description: 'Link to existing asset or propose new' },
  { id: 'schema', label: 'Schema', description: 'Define tables and fields' },
  { id: 'quality', label: 'Quality Rules', description: 'Add validation rules' },
  { id: 'sla', label: 'SLA', description: 'Service level agreement' },
  { id: 'tags', label: 'Tags & Owner', description: 'Metadata and ownership' },
  { id: 'review', label: 'Review', description: 'Review and create' },
]

export default function ContractWizardPage() {
  const router = useRouter()
  const queryClient = useQueryClient()

  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<ContractFormData>({
    status: 'draft',
    sla: {
      freshnessHours: 24,
      availabilityPercent: 99.5,
    },
    qualityRules: [],
    tags: [],
  })

  const updateFormData = (updates: Partial<ContractFormData>) => {
    setFormData((prev) => ({ ...prev, ...updates }))
  }

  // Transform wizard form data to ODCS contract format expected by registry
  const transformToODCSContract = useCallback((data: ContractFormData) => {
    // Generate a unique ID from name
    const contractId = data.name
      ? `${data.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${Date.now().toString(36)}`
      : `contract-${Date.now().toString(36)}`

    // Transform tables to ODCS schema format
    const schema = (data.tables || []).map((table: any, tableIndex: number) => ({
      name: table.name || `table_${tableIndex + 1}`,
      id: table.id || `schema-${tableIndex + 1}`,
      logicalType: 'object',
      description: table.description,
      properties: (table.fields || []).map((field: any) => ({
        name: field.name,
        logicalType: field.logicalType || 'string',
        description: field.description,
        nullable: field.required === true ? false : true,
        primary_key: field.primaryKey === true,
        unique: field.unique === true,
        customProperties: field.piiClassification
          ? {
              privacy: {
                is_pii: true,
                sensitivity: field.piiClassification === 'ssn' || field.piiClassification === 'financial'
                  ? 'restricted'
                  : field.piiClassification === 'email' || field.piiClassification === 'phone'
                  ? 'confidential'
                  : 'internal',
              },
            }
          : undefined,
      })),
    }))

    return {
      apiVersion: 'v1.0.0',
      kind: 'DataContract',
      id: contractId,
      name: data.name,
      version: '1.0.0',
      status: data.status || 'draft',
      description: data.description
        ? { logicalType: 'string', value: data.description }
        : { logicalType: 'string' },
      schema,
      // Optional fields
      ...(data.ownerTeamId && { owner: data.ownerTeamId }),
      ...(data.reviewerId && {
        reviewer_id: data.reviewerId,
        reviewer_type: data.reviewerType
      }),
      ...(data.tags && data.tags.length > 0 && { tags: data.tags }),
      ...(data.sla && {
        sla: {
          freshness: data.sla.freshnessHours ? `PT${data.sla.freshnessHours}H` : undefined,
          availability: data.sla.availabilityPercent,
          responseTime: data.sla.responseTimeMs,
        },
      }),
      ...(data.qualityRules && data.qualityRules.length > 0 && {
        quality: data.qualityRules.map((rule: any) => ({
          type: rule.type,
          field: rule.field,
          table: rule.table,
          threshold: rule.threshold,
          enabled: rule.enabled,
          expression: rule.expression,
        })),
      }),
    }
  }, [])

  // Validation state
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [isValidating, setIsValidating] = useState(false)

  // Validate contract via API
  const validateContract = useCallback(async (data: ContractFormData): Promise<ValidationResult> => {
    setIsValidating(true)
    try {
      const odcsContract = transformToODCSContract(data)
      const result = await api.post<ValidationResult>('/contracts/validate', odcsContract)
      setValidationResult(result)
      return result
    } catch (error: unknown) {
      const errorMessage = error instanceof Error
        ? error.message
        : (error as Record<string, unknown>)?.detail as string || 'Validation failed'
      const failResult: ValidationResult = {
        is_valid: false,
        has_errors: true,
        has_warnings: false,
        error_count: 1,
        warning_count: 0,
        issues: [{
          code: 'API_ERROR',
          field: null,
          message: errorMessage,
          severity: 'error',
          suggestion: 'Please check your contract data and try again',
        }],
      }
      setValidationResult(failResult)
      return failResult
    } finally {
      setIsValidating(false)
    }
  }, [transformToODCSContract])

  // Create contract mutation
  const createMutation = useMutation({
    mutationFn: async (data: ContractFormData) => {
      const odcsContract = transformToODCSContract(data)
      const response = await api.post<Contract>('/contracts', odcsContract)
      return response
    },
    onSuccess: (data) => {
      toast.success('Contract created', 'Your data contract has been created successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${data.id}`)
    },
    onError: (error: unknown) => {
      const message = error instanceof Error
        ? error.message
        : (error as Record<string, unknown>)?.detail as string || 'Please try again'
      toast.error('Failed to create contract', message)
    },
  })

  const handleNext = () => {
    if (currentStep < wizardSteps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  // Validate and then create
  const handleSubmit = async () => {
    // Validate first
    const result = await validateContract(formData)
    if (!result.is_valid) {
      toast.error(
        'Validation failed',
        `Found ${result.error_count} error${result.error_count !== 1 ? 's' : ''}${
          result.warning_count > 0 ? ` and ${result.warning_count} warning${result.warning_count !== 1 ? 's' : ''}` : ''
        }. Please fix the issues before creating.`
      )
      return
    }
    // Create if valid
    createMutation.mutate(formData)
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <Step1BasicInfo formData={formData} updateFormData={updateFormData} onNext={handleNext} />
      case 1:
        return <Step2Asset formData={formData} updateFormData={updateFormData} onNext={handleNext} onBack={handleBack} />
      case 2:
        return <Step3Schema formData={formData} updateFormData={updateFormData} onNext={handleNext} onBack={handleBack} />
      case 3:
        return <Step4Quality formData={formData} updateFormData={updateFormData} onNext={handleNext} onBack={handleBack} />
      case 4:
        return <Step5SLA formData={formData} updateFormData={updateFormData} onNext={handleNext} onBack={handleBack} />
      case 5:
        return <Step6Tags formData={formData} updateFormData={updateFormData} onNext={handleNext} onBack={handleBack} />
      case 6:
        return (
          <Step7Review
            formData={formData}
            onSubmit={handleSubmit}
            onBack={handleBack}
            isSubmitting={createMutation.isPending}
            isValidating={isValidating}
            validationResult={validationResult}
          />
        )
      default:
        return null
    }
  }

  return (
    <PageContainer>
      <BackLink href="/studio/contracts/new" label="Back to Method Selection" />

      <div className="mt-6 mb-6">
        <h1 className="text-2xl font-semibold text-text-primary">Create Contract - UI Builder</h1>
        <p className="mt-2 text-text-secondary">
          Follow the steps to build your data contract
        </p>
      </div>

      <WizardStepper
        steps={wizardSteps}
        currentStep={currentStep}
        onStepClick={(step) => {
          // Allow navigation to previous steps only
          if (step < currentStep) {
            setCurrentStep(step)
          }
        }}
      />

      <Card className="mt-6 p-6">
        {renderStep()}
      </Card>
    </PageContainer>
  )
}
