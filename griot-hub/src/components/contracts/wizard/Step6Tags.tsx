'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { FormField } from '@/components/forms/FormField'
import { TagInput } from '@/components/forms/TagInput'
import { api, queryKeys } from '@/lib/api/client'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'
import type { Team, User } from '@/types'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

export function Step6Tags({ formData, updateFormData, onNext, onBack }: Props) {
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch teams for owner and reviewer dropdowns
  const { data: teams } = useQuery({
    queryKey: queryKeys.teams.list({}),
    queryFn: async () => {
      const response = await api.get<{ data: Team[] } | Team[]>('/teams')
      if (Array.isArray(response)) {
        return response
      }
      return response.data || []
    },
  })

  // Fetch users for reviewer dropdown
  const { data: users } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: async () => {
      const response = await api.get<{ data: User[] } | User[]>('/users')
      if (Array.isArray(response)) {
        return response
      }
      return response.data || []
    },
  })

  const handleReviewerTypeChange = (type: 'user' | 'team' | '') => {
    if (type === '') {
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

    // Clear error when reviewer is selected
    if (errors.reviewer) {
      setErrors((prev) => ({ ...prev, reviewer: '' }))
    }

    if (formData.reviewerType === 'user') {
      const user = users?.find((u) => u.id === id)
      updateFormData({
        reviewerId: id,
        reviewerName: user?.name || user?.email || id,
      })
    } else if (formData.reviewerType === 'team') {
      const team = teams?.find((t) => t.id === id)
      updateFormData({
        reviewerId: id,
        reviewerName: team?.name || id,
      })
    }
  }

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.reviewerId) {
      newErrors.reviewer = 'Please assign a reviewer for this contract'
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
        <h2 className="text-lg font-semibold text-text-primary mb-2">Ownership & Tags</h2>
        <p className="text-sm text-text-secondary">
          Assign ownership, reviewer, and add tags for organization
        </p>
      </div>

      {/* Owner Team */}
      <FormField
        name="ownerTeam"
        label="Owner Team"
        description="Assign a team responsible for this contract"
      >
        <Select
          value={formData.ownerTeamId || ''}
          onValueChange={(value) => updateFormData({ ownerTeamId: value || undefined })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select owner team (optional)" />
          </SelectTrigger>
          <SelectContent>
            {teams?.map((team) => (
              <SelectItem key={team.id} value={team.id}>
                {team.name}
              </SelectItem>
            ))}
            {(!teams || teams.length === 0) && (
              <div className="px-2 py-1.5 text-sm text-text-tertiary">
                No teams available
              </div>
            )}
          </SelectContent>
        </Select>
      </FormField>

      {/* Reviewer (Required) */}
      <FormField
        name="reviewer"
        label="Reviewer"
        description="Assign a user or team to review this contract before approval"
        error={errors.reviewer}
        required
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
                  users &&
                  users.length > 0 &&
                  users.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.name || user.email}
                    </SelectItem>
                  ))}
                {formData.reviewerType === 'team' &&
                  teams &&
                  teams.length > 0 &&
                  teams.map((team) => (
                    <SelectItem key={team.id} value={team.id}>
                      {team.name}
                    </SelectItem>
                  ))}
                {formData.reviewerType === 'user' && (!users || users.length === 0) && (
                  <div className="px-2 py-1.5 text-sm text-text-tertiary">
                    No users available
                  </div>
                )}
                {formData.reviewerType === 'team' && (!teams || teams.length === 0) && (
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

      {/* Tags */}
      <FormField
        name="tags"
        label="Tags"
        description="Add tags to help categorize and find this contract"
      >
        <TagInput
          value={formData.tags || []}
          onChange={(tags) => updateFormData({ tags })}
          suggestions={['analytics', 'customer', 'finance', 'ml', 'reporting', 'pii', 'gdpr']}
          placeholder="Add tags..."
        />
      </FormField>

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={handleNext}>Next: Review</Button>
      </div>
    </div>
  )
}
