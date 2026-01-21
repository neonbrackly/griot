'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { Check, AlertCircle, Table, Database, Tag } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api/client'
import { useToast } from '@/lib/hooks/useToast'
import type { AssetFormData, DataAsset, AssetStatus } from '@/types'

interface Step4Props {
  data: AssetFormData
  onBack: () => void
  onComplete: () => void
}

interface ValidationCheck {
  label: string
  passed: boolean
}

export function Step4Review({ data, onBack, onComplete }: Step4Props) {
  const router = useRouter()
  const { toast } = useToast()

  // Create asset mutation
  const createMutation = useMutation({
    mutationFn: async (status: AssetStatus) => {
      // Convert form data to asset creation payload
      const payload = {
        name: data.name,
        description: data.description,
        domain: data.domain,
        connectionId: data.connectionId,
        ownerTeamId: data.ownerTeamId,
        tags: data.tags || [],
        status,
        tables: data.selectedTables?.map((t) => ({
          id: t.id,
          name: t.name,
          physicalName: `${t.schema}.${t.name}`,
          description: '',
          fields: t.columns.map((col) => ({
            name: col.name,
            type: col.type,
            isPrimaryKey: col.primaryKey || false,
            isNullable: col.nullable,
            description: '',
          })),
          rowCount: t.rowCount,
        })),
        sla: data.sla,
      }

      return api.post<DataAsset>('/assets', payload)
    },
    onSuccess: (asset) => {
      toast({
        title: 'Asset created',
        description: `${asset.name} has been created successfully`,
        variant: 'success',
      })
      onComplete()
      router.push(`/studio/assets/${asset.id}`)
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to create asset',
        description: error.message || 'An error occurred while creating the asset',
        variant: 'error',
      })
    },
  })

  // Validation checks
  const validations: ValidationCheck[] = [
    {
      label: 'Connection verified',
      passed: !!data.connection && data.connection.status === 'active',
    },
    {
      label: 'Tables selected',
      passed: (data.selectedTables?.length || 0) > 0,
    },
    {
      label: 'Metadata complete',
      passed: !!(data.name && data.description && data.domain && data.ownerTeamId),
    },
    {
      label: 'SLAs configured',
      passed: !!(data.sla?.freshnessHours && data.sla?.availabilityPercent),
    },
  ]

  const allPassed = validations.every((v) => v.passed)

  const handleSaveDraft = () => {
    createMutation.mutate('draft')
  }

  const handlePublish = () => {
    createMutation.mutate('active')
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">Step 4: Review & Save</h2>
        <p className="text-sm text-text-secondary mt-1">
          Review your asset configuration before saving
        </p>
      </div>

      {/* Validation Results */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Validation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 mt-3">
          {validations.map((validation, i) => (
            <div key={i} className="flex items-center gap-2">
              {validation.passed ? (
                <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0" />
              )}
              <span
                className={cn(
                  'text-sm',
                  validation.passed ? 'text-text-primary' : 'text-text-secondary'
                )}
              >
                {validation.label}
              </span>
            </div>
          ))}

          {!allPassed && (
            <div className="mt-4 p-3 bg-warning-bg rounded-md">
              <p className="text-sm text-warning-text">
                Some validation checks failed. You can save as draft to continue later.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Asset Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Asset Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 mt-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Name</div>
              <div className="text-sm text-text-primary font-medium">{data.name}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Domain</div>
              <div className="text-sm text-text-primary capitalize">{data.domain}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Connection</div>
              <div className="text-sm text-text-primary">{data.connection?.name}</div>
            </div>
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Tables</div>
              <div className="text-sm text-text-primary">
                {data.selectedTables?.length || 0} tables
              </div>
            </div>
          </div>

          {data.description && (
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Description</div>
              <div className="text-sm text-text-secondary">{data.description}</div>
            </div>
          )}

          <div>
            <div className="text-xs text-text-tertiary uppercase mb-1">SLAs</div>
            <div className="flex gap-2">
              <Badge variant="secondary">Freshness: {data.sla?.freshnessHours}h</Badge>
              <Badge variant="secondary">
                Availability: {data.sla?.availabilityPercent}%
              </Badge>
            </div>
          </div>

          {data.tags && data.tags.length > 0 && (
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Tags</div>
              <div className="flex flex-wrap gap-2">
                {data.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Tables Preview */}
      {data.selectedTables && data.selectedTables.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Table className="w-4 h-4" />
              Selected Tables ({data.selectedTables.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-3">
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {data.selectedTables.map((table) => (
                <div
                  key={table.id}
                  className="flex items-center justify-between p-2 bg-bg-tertiary rounded"
                >
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-text-tertiary" />
                    <span className="text-sm text-text-primary font-mono">{table.id}</span>
                  </div>
                  <span className="text-xs text-text-tertiary">
                    {table.columns?.length || 0} columns
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={handleSaveDraft}
            loading={createMutation.isPending && createMutation.variables === 'draft'}
          >
            Save as Draft
          </Button>
          <Button
            onClick={handlePublish}
            disabled={!allPassed}
            loading={createMutation.isPending && createMutation.variables === 'active'}
          >
            Publish Asset
          </Button>
        </div>
      </div>
    </div>
  )
}
