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
import type { ConnectionSchemaFormData, Team } from '@/types'

interface Step3Props {
  data: ConnectionSchemaFormData
  onUpdate: (data: Partial<ConnectionSchemaFormData>) => void
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
  const { data: teamsData } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const teams = teamsData?.data || []

  const handleChange = (field: keyof ConnectionSchemaFormData, value: unknown) => {
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
          Step 3: Configure Schema
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Add metadata to describe your schema
        </p>
      </div>

      {/* Basic Information */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-text-primary">Basic Information</h3>

        <FormField
          name="name"
          label="Schema Name"
          required
          error={errors.name}
          description="A clear, descriptive name for this schema"
        >
          <Input
            value={data.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., customer_360"
          />
        </FormField>

        <FormField
          name="description"
          label="Description"
          required
          error={errors.description}
          description="Describe what this schema represents and its purpose"
        >
          <Textarea
            value={data.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Describe the purpose and contents of this schema..."
            rows={3}
          />
        </FormField>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="domain"
            label="Domain"
            required
            error={errors.domain}
            description="Business domain for this schema"
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
            description="Team responsible for this schema"
          >
            <Select
              value={data.ownerTeamId || ''}
              onValueChange={(value) => handleChange('ownerTeamId', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select team..." />
              </SelectTrigger>
              <SelectContent>
                {teams.map((team) => (
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
          description="Add tags to help categorize and find this schema"
        >
          <TagInput
            value={data.tags || []}
            onChange={(tags) => handleChange('tags', tags)}
            suggestions={SUGGESTED_TAGS}
            placeholder="Add tags..."
          />
        </FormField>
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
