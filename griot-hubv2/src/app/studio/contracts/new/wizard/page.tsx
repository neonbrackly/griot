'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { PageContainer, Card } from '@/components/layout'
import { Button } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { WizardStepper } from '@/components/forms/WizardStepper'
import { toast } from '@/lib/hooks'
import { api, queryKeys } from '@/lib/api/client'
import type { Contract } from '@/types'

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

  // Create contract mutation
  const createMutation = useMutation({
    mutationFn: async (data: ContractFormData) => {
      const response = await api.post<Contract>('/contracts', {
        name: data.name,
        description: data.description,
        domain: data.domain,
        status: data.status,
        assetId: data.assetId,
        ownerTeamId: data.ownerTeamId,
        tags: data.tags || [],
        schema: {
          tables: data.tables || [],
        },
        qualityRules: data.qualityRules || [],
        sla: data.sla,
        odcsVersion: '3.3.0',
        version: '1.0.0',
      })
      return response
    },
    onSuccess: (data) => {
      toast.success('Contract created', 'Your data contract has been created successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${data.id}`)
    },
    onError: () => {
      toast.error('Failed to create contract', 'Please try again')
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

  const handleSubmit = () => {
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
        return <Step7Review formData={formData} onSubmit={handleSubmit} onBack={handleBack} isSubmitting={createMutation.isPending} />
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
