'use client'

import { useState } from 'react'
import { Button, Input } from '@/components/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { FormField } from '@/components/forms/FormField'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
}

export function Step1BasicInfo({ formData, updateFormData, onNext }: Props) {
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name || formData.name.length < 3) {
      newErrors.name = 'Contract name must be at least 3 characters'
    }

    if (!formData.description || formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    }

    if (!formData.domain) {
      newErrors.domain = 'Please select a domain'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validate()) {
      onNext()
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Basic Information</h2>
        <p className="text-sm text-text-secondary">
          Start by providing the contract name, description, and domain
        </p>
      </div>

      <FormField name="name" label="Contract Name" error={errors.name} required>
        <Input
          placeholder="e.g. Customer Analytics Contract"
          value={formData.name || ''}
          onChange={(e) => updateFormData({ name: e.target.value })}
        />
      </FormField>

      <FormField name="description" label="Description" error={errors.description} required>
        <textarea
          className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Describe the purpose and contents of this contract..."
          value={formData.description || ''}
          onChange={(e) => updateFormData({ description: e.target.value })}
          rows={4}
        />
      </FormField>

      <FormField name="domain" label="Domain" error={errors.domain} required>
        <Select
          value={formData.domain || ''}
          onValueChange={(value) => updateFormData({ domain: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a domain" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="analytics">Analytics</SelectItem>
            <SelectItem value="finance">Finance</SelectItem>
            <SelectItem value="crm">CRM</SelectItem>
            <SelectItem value="marketing">Marketing</SelectItem>
            <SelectItem value="sales">Sales</SelectItem>
            <SelectItem value="ml">Machine Learning</SelectItem>
          </SelectContent>
        </Select>
      </FormField>

      <FormField name="status" label="Status">
        <Select
          value={formData.status || 'draft'}
          onValueChange={(value: 'draft' | 'proposed') => updateFormData({ status: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="proposed">Proposed</SelectItem>
          </SelectContent>
        </Select>
      </FormField>

      <div className="flex justify-end">
        <Button onClick={handleNext}>Next: Data Asset</Button>
      </div>
    </div>
  )
}
