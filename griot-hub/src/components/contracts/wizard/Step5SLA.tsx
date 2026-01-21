'use client'

import { Button, Input } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

export function Step5SLA({ formData, updateFormData, onNext, onBack }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Service Level Agreement</h2>
        <p className="text-sm text-text-secondary">
          Define expected freshness, availability, and performance
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormField name="freshness" label="Freshness (hours)" required>
          <Input
            type="number"
            value={formData.sla?.freshnessHours || 24}
            onChange={(e) =>
              updateFormData({
                sla: { ...formData.sla, freshnessHours: Number(e.target.value) },
              })
            }
          />
        </FormField>

        <FormField name="availability" label="Availability (%)" required>
          <Input
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={formData.sla?.availabilityPercent || 99.5}
            onChange={(e) =>
              updateFormData({
                sla: { ...formData.sla, availabilityPercent: Number(e.target.value) },
              })
            }
          />
        </FormField>

        <FormField name="responseTime" label="Response Time (ms)">
          <Input
            type="number"
            value={formData.sla?.responseTimeMs || ''}
            onChange={(e) =>
              updateFormData({
                sla: { ...formData.sla, responseTimeMs: Number(e.target.value) },
              })
            }
          />
        </FormField>
      </div>

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext}>Next: Tags & Owner</Button>
      </div>
    </div>
  )
}
