'use client'

import { Button, Badge } from '@/components/ui'
import { Card } from '@/components/layout'
import { CheckCircle, AlertCircle } from 'lucide-react'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

interface Props {
  formData: ContractFormData
  onSubmit: () => void
  onBack: () => void
  isSubmitting: boolean
}

export function Step7Review({ formData, onSubmit, onBack, isSubmitting }: Props) {
  const validations = [
    { label: 'Contract name provided', valid: !!formData.name },
    { label: 'Description provided', valid: !!formData.description },
    { label: 'Domain selected', valid: !!formData.domain },
    { label: 'SLA configured', valid: !!formData.sla },
    { label: 'Owner team assigned', valid: !!formData.ownerTeamId },
  ]

  const allValid = validations.every((v) => v.valid)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Review & Create</h2>
        <p className="text-sm text-text-secondary">
          Review your contract before creating
        </p>
      </div>

      {/* Validation Checklist */}
      <Card className="p-4">
        <h3 className="font-medium text-text-primary mb-3">Validation</h3>
        <div className="space-y-2">
          {validations.map((validation) => (
            <div key={validation.label} className="flex items-center gap-2">
              {validation.valid ? (
                <CheckCircle className="h-4 w-4 text-success-text" />
              ) : (
                <AlertCircle className="h-4 w-4 text-error-text" />
              )}
              <span
                className={`text-sm ${
                  validation.valid ? 'text-text-primary' : 'text-error-text'
                }`}
              >
                {validation.label}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Contract Summary */}
      <Card className="p-4">
        <h3 className="font-medium text-text-primary mb-3">Contract Summary</h3>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-text-tertiary">Name</p>
            <p className="text-sm font-medium text-text-primary">{formData.name}</p>
          </div>
          <div>
            <p className="text-xs text-text-tertiary">Description</p>
            <p className="text-sm text-text-secondary">{formData.description}</p>
          </div>
          <div>
            <p className="text-xs text-text-tertiary mb-1">Domain & Status</p>
            <div className="flex gap-2">
              <Badge variant="secondary" size="sm">{formData.domain}</Badge>
              <Badge variant="secondary" size="sm">{formData.status}</Badge>
            </div>
          </div>
          <div>
            <p className="text-xs text-text-tertiary">SLA</p>
            <p className="text-sm text-text-secondary">
              Freshness: {formData.sla?.freshnessHours}h • Availability: {formData.sla?.availabilityPercent}%
            </p>
          </div>
          {formData.tags && formData.tags.length > 0 && (
            <div>
              <p className="text-xs text-text-tertiary mb-1">Tags</p>
              <div className="flex flex-wrap gap-1">
                {formData.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" size="xs">{tag}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={onSubmit} disabled={!allValid || isSubmitting}>
            Save as Draft
          </Button>
          <Button onClick={onSubmit} disabled={!allValid || isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Contract'}
          </Button>
        </div>
      </div>
    </div>
  )
}
