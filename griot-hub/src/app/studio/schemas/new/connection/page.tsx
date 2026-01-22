'use client'

import * as React from 'react'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { WizardStepper } from '@/components/forms/WizardStepper'
import { useUnsavedChanges } from '@/lib/hooks/useUnsavedChanges'
import { PageContainer } from '@/components/layout/PageShell'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { Step1Connection } from '@/components/schemas/wizard/connection/Step1Connection'
import { Step2Tables } from '@/components/schemas/wizard/connection/Step2Tables'
import { Step3Configure } from '@/components/schemas/wizard/connection/Step3Configure'
import { Step4Review } from '@/components/schemas/wizard/connection/Step4Review'
import type { ConnectionSchemaFormData } from '@/types'

const steps = [
  { id: 'connection', label: 'Connection', description: 'Select database' },
  { id: 'tables', label: 'Tables', description: 'Choose tables' },
  { id: 'configure', label: 'Configure', description: 'Set metadata' },
  { id: 'review', label: 'Review', description: 'Confirm & save' },
]

export default function ConnectionSchemaWizardPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<ConnectionSchemaFormData>({
    connectionId: undefined,
    connection: undefined,
    selectedTables: [],
    name: '',
    description: '',
    domain: '',
    ownerTeamId: '',
    tags: [],
  })
  const [isDirty, setIsDirty] = useState(false)

  // Block navigation when form has unsaved changes
  useUnsavedChanges(isDirty)

  const updateFormData = React.useCallback((data: Partial<ConnectionSchemaFormData>) => {
    setFormData((prev) => ({ ...prev, ...data }))
    setIsDirty(true)
  }, [])

  const goToStep = (step: number) => {
    // Allow backward navigation without validation
    if (step < currentStep) {
      setCurrentStep(step)
      return
    }

    // Validate current step before proceeding forward
    if (step > currentStep) {
      const isValid = validateStep(currentStep)
      if (!isValid) {
        return
      }
    }

    setCurrentStep(step)
  }

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 0: // Connection step
        return !!formData.connectionId
      case 1: // Tables step
        return (formData.selectedTables?.length || 0) > 0
      case 2: // Configure step
        return !!(
          formData.name &&
          formData.description &&
          formData.domain &&
          formData.ownerTeamId
        )
      default:
        return true
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Step1Connection
            data={formData}
            onUpdate={updateFormData}
            onNext={() => goToStep(1)}
          />
        )
      case 1:
        return (
          <Step2Tables
            data={formData}
            onUpdate={updateFormData}
            onBack={() => goToStep(0)}
            onNext={() => goToStep(2)}
          />
        )
      case 2:
        return (
          <Step3Configure
            data={formData}
            onUpdate={updateFormData}
            onBack={() => goToStep(1)}
            onNext={() => goToStep(3)}
          />
        )
      case 3:
        return (
          <Step4Review
            data={formData}
            onBack={() => goToStep(2)}
            onComplete={() => {
              setIsDirty(false)
              // Navigation will be handled by Step4Review after successful creation
            }}
          />
        )
      default:
        return null
    }
  }

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        <BackLink href="/studio/schemas/new" label="Choose Method" className="mb-6" />

        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-text-primary">
            Create Schema from Database
          </h1>
          <p className="text-text-secondary mt-1">
            Connect to your database and import the schema structure
          </p>
        </div>

        <WizardStepper
          steps={steps}
          currentStep={currentStep}
          onStepClick={goToStep}
          allowNavigation={true}
        />

        <div className="mt-8">{renderStep()}</div>
      </div>
    </PageContainer>
  )
}
