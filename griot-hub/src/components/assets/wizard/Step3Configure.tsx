'use client'

import * as React from 'react'
import { useQuery } from '@tanstack/react-query'
import { FormField } from '@/components/forms/FormField'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { TagInput } from '@/components/forms/TagInput'
import { Button } from '@/components/ui/Button'
import { api, queryKeys } from '@/lib/api/client'
import type { AssetFormData, Team } from '@/types'

interface Step3Props {
  data: AssetFormData
  onUpdate: (data: Partial<AssetFormData>) => void
  onBack: () => void
  onNext: () => void
}

const DOMAINS = [
  { value: 'analytics', label: 'Analytics' },
  { value: 'finance', label: 'Finance' },
  { value: 'crm', label: 'CRM' },
  { value: 'operations', label: 'Operations' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'ml', label: 'Machine Learning' },
]

const SUGGESTED_TAGS = ['pii', 'ml-ready', 'real-time', 'batch', 'core', 'customer', 'finance', 'transactions']

export function Step3Configure({ data, onUpdate, onBack, onNext }: Step3Props) {
  const [errors, setErrors] = React.useState<Record<string, string>>({})

  // Fetch teams for owner selection
  const { data: teams } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<Team[]>('/teams'),
  })

  const handleChange = (field: keyof AssetFormData, value: unknown) => {
    onUpdate({ [field]: value })
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const handleSLAChange = (field: 'freshnessHours' | 'availabilityPercent', value: number) => {
    onUpdate({
      sla: {
        ...data.sla!,
        [field]: value,
      },
    })
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!data.name || data.name.trim().length < 3) {
      newErrors.name = 'Name must be at least 3 characters'
    }

    if (!data.description || data.description.trim().length < 20) {
      newErrors.description = 'Description must be at least 20 characters'
    }

    if (!data.domain) {
      newErrors.domain = 'Domain is required'
    }

    if (!data.ownerTeamId) {
      newErrors.ownerTeamId = 'Owner team is required'
    }

    if (!data.sla?.freshnessHours || data.sla.freshnessHours < 1) {
      newErrors.freshnessHours = 'Freshness must be at least 1 hour'
    }

    if (!data.sla?.availabilityPercent || data.sla.availabilityPercent < 90) {
      newErrors.availabilityPercent = 'Availability must be at least 90%'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validateForm()) {
      onNext()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 3: Configure Asset
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Add metadata and configure service level agreements
        </p>
      </div>

      {/* Basic Information */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">Basic Information</h3>

        <FormField
          name="name"
          label="Asset Name"
          required
          error={errors.name}
          description="A clear, descriptive name for this data asset"
        >
          <Input
            value={data.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., Customer 360"
          />
        </FormField>

        <FormField
          name="description"
          label="Description"
          required
          error={errors.description}
          description="Describe what this data asset contains and its purpose"
        >
          <Textarea
            value={data.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Describe what this data asset contains and its purpose..."
            rows={3}
          />
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="domain"
            label="Domain"
            required
            error={errors.domain}
            description="Business domain for this asset"
          >
            <Select
              value={data.domain || ''}
              onValueChange={(value) => handleChange('domain', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select domain..." />
              </SelectTrigger>
              <SelectContent>
                {DOMAINS.map((domain) => (
                  <SelectItem key={domain.value} value={domain.value}>
                    {domain.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>

          <FormField
            name="ownerTeamId"
            label="Owner Team"
            required
            error={errors.ownerTeamId}
            description="Team responsible for this asset"
          >
            <Select
              value={data.ownerTeamId || ''}
              onValueChange={(value) => handleChange('ownerTeamId', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select team..." />
              </SelectTrigger>
              <SelectContent>
                {teams?.map((team) => (
                  <SelectItem key={team.id} value={team.id}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
        </div>

        <FormField
          name="tags"
          label="Tags"
          description="Add tags to help categorize and find this asset"
        >
          <TagInput
            value={data.tags || []}
            onChange={(tags) => handleChange('tags', tags)}
            suggestions={SUGGESTED_TAGS}
            placeholder="Add tags..."
          />
        </FormField>
      </div>

      {/* SLAs */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">
          Service Level Agreements
        </h3>
        <p className="text-sm text-text-tertiary">
          These SLAs will be inherited by all contracts using this asset
        </p>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="sla.freshnessHours"
            label="Data Freshness"
            description="Data should be updated within this many hours"
            error={errors.freshnessHours}
          >
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="1"
                max="720"
                value={data.sla?.freshnessHours || 24}
                onChange={(e) => handleSLAChange('freshnessHours', parseInt(e.target.value))}
                className="w-24"
              />
              <span className="text-sm text-text-secondary">hours</span>
            </div>
          </FormField>

          <FormField
            name="sla.availabilityPercent"
            label="Availability Target"
            description="Expected uptime percentage"
            error={errors.availabilityPercent}
          >
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="90"
                max="100"
                step="0.1"
                value={data.sla?.availabilityPercent || 99.5}
                onChange={(e) =>
                  handleSLAChange('availabilityPercent', parseFloat(e.target.value))
                }
                className="w-24"
              />
              <span className="text-sm text-text-secondary">%</span>
            </div>
          </FormField>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button type="button" variant="secondary" onClick={onBack}>
          Back
        </Button>
        <Button type="submit">Next: Review</Button>
      </div>
    </form>
  )
}
