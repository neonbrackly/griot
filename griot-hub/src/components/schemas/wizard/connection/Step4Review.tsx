'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, AlertCircle, Table, Database, Tag, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { api, queryKeys } from '@/lib/api/client'
import { useToast } from '@/lib/hooks/useToast'
import type { ConnectionSchemaFormData, Schema, SchemaStatus } from '@/types'

interface Step4Props {
  data: ConnectionSchemaFormData
  onBack: () => void
  onComplete: () => void
}

interface ValidationCheck {
  label: string
  passed: boolean
}

export function Step4Review({ data, onBack, onComplete }: Step4Props) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // Create schema mutation
  const createMutation = useMutation({
    mutationFn: async (publish: boolean) => {
      // Convert selected tables to schema properties
      const properties = data.selectedTables?.flatMap((table) =>
        table.columns.map((col) => ({
          name: col.name,
          logicalType: mapDatabaseTypeToLogical(col.type),
          physicalType: col.type,
          primaryKey: col.primaryKey || false,
          required: !col.nullable,
          nullable: col.nullable,
          unique: false,
        }))
      ) || []

      // Create schema payload
      const payload = {
        name: data.name,
        physicalName: data.selectedTables?.[0]?.name || data.name,
        logicalType: 'object',
        physicalType: 'table',
        description: data.description,
        domain: data.domain,
        ownerTeamId: data.ownerTeamId,
        tags: data.tags || [],
        properties,
        // Store connection info for reference
        connectionId: data.connectionId,
      }

      const response = await api.post<Schema>('/schemas', payload)

      // If publish requested, call publish endpoint
      if (publish && response.id) {
        await api.post<Schema>(`/schemas/${response.id}/publish`, {})
      }

      return response
    },
    onSuccess: (schema, publish) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schemas.all })
      toast({
        title: publish ? 'Schema published' : 'Schema saved as draft',
        description: `Schema "${data.name}" has been ${publish ? 'published' : 'created as a draft'}.`,
        variant: 'success',
      })
      onComplete()
      router.push(`/studio/schemas/${schema.id}`)
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to create schema',
        description: error.message || 'An error occurred while creating the schema',
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
  ]

  const allPassed = validations.every((v) => v.passed)

  const handleSaveDraft = () => {
    createMutation.mutate(false)
  }

  const handlePublish = () => {
    createMutation.mutate(true)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">Step 4: Review & Save</h2>
        <p className="text-sm text-text-secondary mt-1">
          Review your schema configuration before saving
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

      {/* Schema Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Schema Summary</CardTitle>
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
              <div className="text-xs text-text-tertiary uppercase mb-1">Source</div>
              <Badge variant="outline">Connection</Badge>
            </div>
          </div>

          {data.description && (
            <div>
              <div className="text-xs text-text-tertiary uppercase mb-1">Description</div>
              <div className="text-sm text-text-secondary">{data.description}</div>
            </div>
          )}

          <div>
            <div className="text-xs text-text-tertiary uppercase mb-1">Properties</div>
            <div className="text-sm text-text-primary">
              {data.selectedTables?.reduce((acc, t) => acc + (t.columns?.length || 0), 0) || 0} properties from {data.selectedTables?.length || 0} tables
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
        <Button variant="secondary" onClick={onBack} disabled={createMutation.isPending}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={handleSaveDraft}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Save as Draft
          </Button>
          <Button
            onClick={handlePublish}
            disabled={!allPassed || createMutation.isPending}
          >
            {createMutation.isPending ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Publish Schema
          </Button>
        </div>
      </div>
    </div>
  )
}

// Helper function to map database types to logical types
function mapDatabaseTypeToLogical(dbType: string): string {
  const type = dbType.toLowerCase()
  if (type.includes('int') || type.includes('serial')) return 'integer'
  if (type.includes('float') || type.includes('double') || type.includes('decimal') || type.includes('numeric')) return 'number'
  if (type.includes('bool')) return 'boolean'
  if (type.includes('date') && !type.includes('time')) return 'date'
  if (type.includes('timestamp') || type.includes('datetime')) return 'datetime'
  if (type.includes('time')) return 'datetime'
  if (type.includes('json') || type.includes('object')) return 'object'
  if (type.includes('array')) return 'array'
  if (type.includes('binary') || type.includes('blob') || type.includes('bytea')) return 'binary'
  return 'string'
}
