'use client'

import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import { TagInput } from '@/components/forms/TagInput'
import { api, queryKeys } from '@/lib/api/client'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'
import type { Team } from '@/types'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

export function Step6Tags({ formData, updateFormData, onNext, onBack }: Props) {
  const { data: teams } = useQuery({
    queryKey: queryKeys.teams.list({}),
    queryFn: async () => {
      const response = await api.get<Team[]>('/teams')
      return response
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Tags & Ownership</h2>
        <p className="text-sm text-text-secondary">
          Add tags and assign an owner team
        </p>
      </div>

      <FormField name="ownerTeam" label="Owner Team" required>
        <select
          className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          value={formData.ownerTeamId || ''}
          onChange={(e) => updateFormData({ ownerTeamId: e.target.value })}
        >
          <option value="">Select a team</option>
          {teams?.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
      </FormField>

      <FormField name="tags" label="Tags">
        <TagInput
          value={formData.tags || []}
          onChange={(tags) => updateFormData({ tags })}
          suggestions={['analytics', 'customer', 'finance', 'ml', 'reporting']}
          placeholder="Add tags..."
        />
      </FormField>

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext}>Next: Review</Button>
      </div>
    </div>
  )
}
