'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Input } from '@/components/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { FormField } from '@/components/forms/FormField'
import { api, queryKeys } from '@/lib/api/client'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

// Simple types for users and teams
interface SimpleUser {
  id: string
  name: string
  email: string
}

interface SimpleTeam {
  id: string
  name: string
}

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
}

export function Step1BasicInfo({ formData, updateFormData, onNext }: Props) {
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch users for reviewer dropdown
  const { data: usersData } = useQuery({
    queryKey: queryKeys.users?.all ?? ['users'],
    queryFn: async () => {
      try {
        const response = await api.get<{ items: SimpleUser[] } | SimpleUser[]>('/users')
        // Handle both array and object response formats
        if (Array.isArray(response)) {
          return response
        }
        return response.items || []
      } catch {
        // Return empty array if API fails - reviewer is optional
        return []
      }
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  // Fetch teams for reviewer dropdown
  const { data: teamsData } = useQuery({
    queryKey: queryKeys.teams?.all ?? ['teams'],
    queryFn: async () => {
      try {
        const response = await api.get<{ items: SimpleTeam[] } | SimpleTeam[]>('/teams')
        // Handle both array and object response formats
        if (Array.isArray(response)) {
          return response
        }
        return response.items || []
      } catch {
        // Return empty array if API fails - reviewer is optional
        return []
      }
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  const users = usersData || []
  const teams = teamsData || []

  const handleReviewerTypeChange = (type: 'user' | 'team' | '') => {
    if (type === '') {
      // Clear reviewer when type is cleared
      updateFormData({
        reviewerType: undefined,
        reviewerId: undefined,
        reviewerName: undefined,
      })
    } else {
      updateFormData({
        reviewerType: type,
        reviewerId: undefined,
        reviewerName: undefined,
      })
    }
  }

  const handleReviewerChange = (id: string) => {
    if (!id) {
      updateFormData({ reviewerId: undefined, reviewerName: undefined })
      return
    }

    if (formData.reviewerType === 'user') {
      const user = users.find((u) => u.id === id)
      updateFormData({
        reviewerId: id,
        reviewerName: user?.name || user?.email || id,
      })
    } else if (formData.reviewerType === 'team') {
      const team = teams.find((t) => t.id === id)
      updateFormData({
        reviewerId: id,
        reviewerName: team?.name || id,
      })
    }
  }

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

      {/* Reviewer Field */}
      <FormField
        name="reviewer"
        label="Reviewer"
        description="Optionally assign a user or team to review this contract"
      >
        <div className="flex gap-2">
          <div className="w-32">
            <Select
              value={formData.reviewerType || ''}
              onValueChange={(value) => handleReviewerTypeChange(value as 'user' | 'team' | '')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="team">Team</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1">
            <Select
              value={formData.reviewerId || ''}
              onValueChange={handleReviewerChange}
              disabled={!formData.reviewerType}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={
                    !formData.reviewerType
                      ? 'Select type first'
                      : formData.reviewerType === 'user'
                      ? 'Select user...'
                      : 'Select team...'
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {formData.reviewerType === 'user' &&
                  users.length > 0 &&
                  users.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.name || user.email}
                    </SelectItem>
                  ))}
                {formData.reviewerType === 'team' &&
                  teams.length > 0 &&
                  teams.map((team) => (
                    <SelectItem key={team.id} value={team.id}>
                      {team.name}
                    </SelectItem>
                  ))}
                {formData.reviewerType === 'user' && users.length === 0 && (
                  <div className="px-2 py-1.5 text-sm text-text-tertiary">
                    No users available
                  </div>
                )}
                {formData.reviewerType === 'team' && teams.length === 0 && (
                  <div className="px-2 py-1.5 text-sm text-text-tertiary">
                    No teams available
                  </div>
                )}
              </SelectContent>
            </Select>
          </div>
          {formData.reviewerId && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() =>
                updateFormData({
                  reviewerType: undefined,
                  reviewerId: undefined,
                  reviewerName: undefined,
                })
              }
            >
              Clear
            </Button>
          )}
        </div>
      </FormField>

      <div className="flex justify-end">
        <Button onClick={handleNext}>Next: Data Asset</Button>
      </div>
    </div>
  )
}
