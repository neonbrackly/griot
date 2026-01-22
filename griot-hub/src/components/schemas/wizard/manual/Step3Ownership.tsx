'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, Users, Tag, Plus } from 'lucide-react'
import { Button, Input, Badge } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import { Skeleton } from '@/components/feedback/Skeleton'
import { api, queryKeys } from '@/lib/api/client'
import type { SchemaFormData, Team } from '@/types'

interface Props {
  formData: SchemaFormData
  updateFormData: (data: Partial<SchemaFormData>) => void
  onNext: () => void
  onBack: () => void
}

const SUGGESTED_TAGS = [
  'pii',
  'sensitive',
  'analytics',
  'reporting',
  'core',
  'dimension',
  'fact',
  'staging',
  'raw',
  'curated',
  'ml-feature',
  'deprecated',
]

export function Step3Ownership({ formData, updateFormData, onBack, onNext }: Props) {
  const [tagInput, setTagInput] = useState('')

  // Fetch teams
  const { data: teamsData, isLoading: teamsLoading } = useQuery({
    queryKey: queryKeys.teams.all,
    queryFn: () => api.get<{ data: Team[] }>('/teams'),
  })

  const teams = teamsData?.data || []

  const addTag = (tag: string) => {
    const normalizedTag = tag.toLowerCase().trim().replace(/[^a-z0-9-]/g, '-')
    if (normalizedTag && !formData.tags?.includes(normalizedTag)) {
      updateFormData({ tags: [...(formData.tags || []), normalizedTag] })
    }
    setTagInput('')
  }

  const removeTag = (tag: string) => {
    updateFormData({ tags: (formData.tags || []).filter((t) => t !== tag) })
  }

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      if (tagInput.trim()) {
        addTag(tagInput)
      }
    }
  }

  return (
    <div className="space-y-8">
      {/* Ownership Section */}
      <section>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            <Users className="h-5 w-5" />
            Ownership
          </h2>
          <p className="text-sm text-text-secondary">
            Assign an owner team for this schema
          </p>
        </div>

        <FormField label="Owner Team">
          {teamsLoading ? (
            <Skeleton className="h-10 w-full" />
          ) : (
            <select
              value={formData.ownerTeamId || ''}
              onChange={(e) => updateFormData({ ownerTeamId: e.target.value })}
              className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
            >
              <option value="">Select a team...</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
          )}
          <p className="text-xs text-text-tertiary mt-1">
            The team responsible for maintaining this schema
          </p>
        </FormField>
      </section>

      {/* Tags Section */}
      <section className="border-t border-border-default pt-8">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            <Tag className="h-5 w-5" />
            Tags
          </h2>
          <p className="text-sm text-text-secondary">
            Add tags to categorize and filter this schema
          </p>
        </div>

        <FormField label="Tags">
          <div className="space-y-3">
            {/* Current Tags */}
            {formData.tags && formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="gap-1 pr-1"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 rounded-full p-0.5 hover:bg-bg-tertiary"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* Tag Input */}
            <div className="flex gap-2">
              <Input
                placeholder="Type a tag and press Enter..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagKeyDown}
                className="flex-1"
              />
              <Button
                type="button"
                variant="secondary"
                onClick={() => tagInput.trim() && addTag(tagInput)}
                disabled={!tagInput.trim()}
              >
                <Plus className="h-4 w-4 mr-1" />
                Add
              </Button>
            </div>

            {/* Suggested Tags */}
            <div>
              <p className="text-xs text-text-tertiary mb-2">Suggested tags:</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_TAGS.filter((tag) => !formData.tags?.includes(tag)).map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => addTag(tag)}
                    className="px-2 py-1 text-xs rounded-md border border-border-default text-text-secondary hover:bg-bg-secondary hover:border-primary-border transition-colors"
                  >
                    + {tag}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </FormField>
      </section>

      {/* Summary */}
      <section className="p-4 bg-bg-secondary rounded-lg">
        <h4 className="text-sm font-medium text-text-primary mb-3">Summary</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-text-tertiary">Owner Team:</span>
            <span className="ml-2 text-text-primary">
              {formData.ownerTeamId
                ? teams.find((t) => t.id === formData.ownerTeamId)?.name || formData.ownerTeamId
                : 'Not assigned'}
            </span>
          </div>
          <div>
            <span className="text-text-tertiary">Tags:</span>
            <span className="ml-2 text-text-primary">
              {formData.tags?.length ? formData.tags.join(', ') : 'None'}
            </span>
          </div>
        </div>
      </section>

      {/* Navigation */}
      <div className="flex justify-between pt-4 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext}>
          Next: Review
        </Button>
      </div>
    </div>
  )
}
