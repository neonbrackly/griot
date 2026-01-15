'use client'

import { useQuery } from '@tanstack/react-query'
import { Button, Badge } from '@/components/ui'
// FormField not needed for this step
import { api, queryKeys } from '@/lib/api/client'
import { Database, Plus } from 'lucide-react'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'
import type { DataAsset } from '@/types'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

export function Step2Asset({ formData, updateFormData, onNext, onBack }: Props) {
  const { data: assets, isLoading } = useQuery({
    queryKey: queryKeys.assets.list({ status: 'active' }),
    queryFn: async () => {
      const response = await api.get<{ data: DataAsset[] }>('/assets')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Data Asset</h2>
        <p className="text-sm text-text-secondary">
          Link this contract to an existing data asset or create a proposed contract
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div
          onClick={() => updateFormData({ assetId: undefined, isProposed: true })}
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
            formData.isProposed
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-border-default hover:border-border-hover'
          }`}
        >
          <div className="flex items-center gap-3">
            <Plus className="h-5 w-5" />
            <div>
              <p className="font-medium">Proposed Contract</p>
              <p className="text-sm text-text-secondary">
                Create a contract without linking to an existing asset
              </p>
            </div>
          </div>
        </div>

        {isLoading ? (
          <p className="text-sm text-text-secondary">Loading assets...</p>
        ) : (
          assets?.map((asset) => (
            <div
              key={asset.id}
              onClick={() => updateFormData({ assetId: asset.id, isProposed: false })}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                formData.assetId === asset.id
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-border-default hover:border-border-hover'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <Database className="h-5 w-5 mt-1" />
                  <div>
                    <p className="font-medium">{asset.name}</p>
                    <p className="text-sm text-text-secondary mt-1">{asset.description}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="secondary" size="xs">{asset.domain}</Badge>
                      <Badge variant="secondary" size="xs">{asset.tables.length} tables</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext} disabled={!formData.assetId && !formData.isProposed}>
          Next: Schema
        </Button>
      </div>
    </div>
  )
}
