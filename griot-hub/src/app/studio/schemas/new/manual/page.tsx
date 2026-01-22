'use client'

import * as React from 'react'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { WizardStepper } from '@/components/forms/WizardStepper'
import { useUnsavedChanges } from '@/lib/hooks/useUnsavedChanges'
import { PageContainer } from '@/components/layout/PageShell'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { Step1SchemaInfo } from '@/components/schemas/wizard/manual/Step1SchemaInfo'
import { Step2Properties } from '@/components/schemas/wizard/manual/Step2Properties'
import { Step3Ownership } from '@/components/schemas/wizard/manual/Step3Ownership'
import { Step4Review } from '@/components/schemas/wizard/manual/Step4Review'
import type { SchemaFormData, SchemaLogicalType } from '@/types'

const steps = [
  { id: 'info', label: 'Schema Info', description: 'Basic details & quality' },
  { id: 'properties', label: 'Properties', description: 'Fields & constraints' },
  { id: 'ownership', label: 'Ownership', description: 'Team & tags' },
  { id: 'review', label: 'Review', description: 'Confirm & save' },
]

const initialFormData: SchemaFormData = {
  name: '',
  physicalName: '',
  logicalType: 'object' as SchemaLogicalType,
  physicalType: 'table',
  description: '',
  businessName: '',
  domain: '',
  quality: [],
  properties: [],
  ownerTeamId: '',
  tags: [],
}

export default function ManualSchemaWizardPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<SchemaFormData>(initialFormData)
  const [isDirty, setIsDirty] = useState(false)

  // Block navigation when form has unsaved changes
  useUnsavedChanges(isDirty)

  const updateFormData = React.useCallback((data: Partial<SchemaFormData>) => {
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
      case 0: // Schema Info step
        return !!(
          formData.name &&
          formData.name.length >= 3 &&
          formData.logicalType
        )
      case 1: // Properties step
        return formData.properties.length > 0
      case 2: // Ownership step
        return true // Ownership is optional
      default:
        return true
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Step1SchemaInfo
            formData={formData}
            updateFormData={updateFormData}
            onNext={() => goToStep(1)}
          />
        )
      case 1:
        return (
          <Step2Properties
            formData={formData}
            updateFormData={updateFormData}
            onBack={() => goToStep(0)}
            onNext={() => goToStep(2)}
          />
        )
      case 2:
        return (
          <Step3Ownership
            formData={formData}
            updateFormData={updateFormData}
            onBack={() => goToStep(1)}
            onNext={() => goToStep(3)}
          />
        )
      case 3:
        return (
          <Step4Review
            formData={formData}
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
            Create Schema Manually
          </h1>
          <p className="text-text-secondary mt-1">
            Define your schema structure, properties, constraints, and quality rules
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
