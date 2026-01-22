'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Database,
  Key,
  Shield,
  FileCode2,
  Tag,
  Users,
  ChevronDown,
  ChevronUp,
  Loader2,
} from 'lucide-react'
import { Button, Badge } from '@/components/ui'
import { api, queryKeys } from '@/lib/api/client'
import { useToast } from '@/lib/hooks/useToast'
import type { SchemaFormData, Schema } from '@/types'

interface Props {
  formData: SchemaFormData
  onBack: () => void
  onComplete: () => void
}

interface ValidationItem {
  id: string
  label: string
  passed: boolean
  warning?: boolean
  message?: string
}

export function Step4Review({ formData, onBack, onComplete }: Props) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    schema: true,
    properties: true,
    quality: false,
  })

  // Validation checks
  const validations = useMemo<ValidationItem[]>(() => {
    const items: ValidationItem[] = []

    // Schema name
    items.push({
      id: 'name',
      label: 'Schema name is valid',
      passed: !!formData.name && formData.name.length >= 3 && /^[a-z][a-z0-9_]*$/.test(formData.name),
      message: formData.name ? undefined : 'Schema name is required',
    })

    // Logical type
    items.push({
      id: 'logicalType',
      label: 'Logical type is specified',
      passed: !!formData.logicalType,
    })

    // Properties
    items.push({
      id: 'properties',
      label: 'At least one property defined',
      passed: formData.properties.length > 0,
      message: formData.properties.length === 0 ? 'Add at least one property' : undefined,
    })

    // Property names valid
    const invalidProps = formData.properties.filter(p => !p.name || !/^[a-z][a-z0-9_]*$/.test(p.name))
    items.push({
      id: 'propertyNames',
      label: 'All property names are valid',
      passed: invalidProps.length === 0,
      message: invalidProps.length > 0 ? `${invalidProps.length} properties have invalid names` : undefined,
    })

    // Primary key
    const hasPrimaryKey = formData.properties.some(p => p.primaryKey)
    items.push({
      id: 'primaryKey',
      label: 'Primary key defined',
      passed: hasPrimaryKey,
      warning: !hasPrimaryKey,
      message: hasPrimaryKey ? undefined : 'Consider defining a primary key',
    })

    // PII flagged
    const hasPii = formData.properties.some(p => p.customProperties?.privacy?.is_pii)
    items.push({
      id: 'pii',
      label: 'PII fields identified',
      passed: true,
      warning: hasPii,
      message: hasPii ? `${formData.properties.filter(p => p.customProperties?.privacy?.is_pii).length} PII fields marked` : 'No PII fields identified',
    })

    // Description
    items.push({
      id: 'description',
      label: 'Description provided',
      passed: !!formData.description && formData.description.length >= 10,
      warning: !formData.description,
      message: !formData.description ? 'Consider adding a description' : undefined,
    })

    return items
  }, [formData])

  const allPassed = validations.every(v => v.passed)
  const warningsCount = validations.filter(v => v.warning).length

  // Calculate stats
  const stats = useMemo(() => ({
    properties: formData.properties.length,
    primaryKeys: formData.properties.filter(p => p.primaryKey).length,
    required: formData.properties.filter(p => p.required).length,
    pii: formData.properties.filter(p => p.customProperties?.privacy?.is_pii).length,
    schemaQuality: formData.quality?.length || 0,
    propertyQuality: formData.properties.reduce((acc, p) => acc + (p.quality?.length || 0), 0),
  }), [formData])

  // Create schema mutation
  const createSchemaMutation = useMutation({
    mutationFn: async (publish: boolean) => {
      // Transform form data to API format
      const payload = {
        name: formData.name,
        physicalName: formData.physicalName || undefined,
        logicalType: formData.logicalType,
        physicalType: formData.physicalType || undefined,
        description: formData.description || undefined,
        businessName: formData.businessName || undefined,
        domain: formData.domain || undefined,
        ownerTeamId: formData.ownerTeamId || undefined,
        tags: formData.tags || [],
        properties: formData.properties.map(p => ({
          name: p.name,
          logicalType: p.logicalType,
          physicalType: p.physicalType || undefined,
          description: p.description || undefined,
          primaryKey: p.primaryKey,
          required: p.required,
          nullable: p.nullable,
          unique: p.unique,
          customProperties: p.customProperties,
        })),
      }

      const response = await api.post<Schema>('/schemas', payload)

      // If publish requested, call publish endpoint
      if (publish && response.id) {
        await api.post<Schema>(`/schemas/${response.id}/publish`, {})
      }

      return response
    },
    onSuccess: (data, publish) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schemas.all })
      toast({
        title: publish ? 'Schema published' : 'Schema saved as draft',
        description: `Schema "${formData.name}" has been ${publish ? 'published' : 'created as a draft'}.`,
        variant: 'success',
      })
      onComplete()
      router.push(`/studio/schemas/${data.id}`)
    },
    onError: (error: any) => {
      toast({
        title: 'Error creating schema',
        description: error.message || 'An error occurred while creating the schema.',
        variant: 'destructive',
      })
    },
  })

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Review Schema</h2>
        <p className="text-sm text-text-secondary">
          Review your schema definition before saving. You can save as draft or publish immediately.
        </p>
      </div>

      {/* Validation Checklist */}
      <div className="p-4 bg-bg-secondary rounded-lg">
        <h3 className="text-sm font-medium text-text-primary mb-3">Validation Checklist</h3>
        <div className="space-y-2">
          {validations.map((item) => (
            <div key={item.id} className="flex items-center gap-2">
              {item.passed ? (
                item.warning ? (
                  <AlertTriangle className="h-4 w-4 text-warning-text" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-success-text" />
                )
              ) : (
                <XCircle className="h-4 w-4 text-error-text" />
              )}
              <span className={`text-sm ${item.passed ? 'text-text-secondary' : 'text-error-text'}`}>
                {item.label}
              </span>
              {item.message && (
                <span className="text-xs text-text-tertiary">— {item.message}</span>
              )}
            </div>
          ))}
        </div>

        {!allPassed && (
          <div className="mt-4 p-3 bg-error-bg border border-error-border rounded-lg">
            <p className="text-sm text-error-text">
              Please fix the validation errors above before publishing.
            </p>
          </div>
        )}

        {allPassed && warningsCount > 0 && (
          <div className="mt-4 p-3 bg-warning-bg border border-warning-border rounded-lg">
            <p className="text-sm text-warning-text">
              {warningsCount} warning{warningsCount > 1 ? 's' : ''} found. You can still save, but consider addressing them.
            </p>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-text-primary">{stats.properties}</p>
          <p className="text-xs text-text-tertiary">Properties</p>
        </div>
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-warning-text">{stats.primaryKeys}</p>
          <p className="text-xs text-text-tertiary">Primary Keys</p>
        </div>
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-text-primary">{stats.required}</p>
          <p className="text-xs text-text-tertiary">Required</p>
        </div>
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-error-text">{stats.pii}</p>
          <p className="text-xs text-text-tertiary">PII Fields</p>
        </div>
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-info-text">{stats.schemaQuality}</p>
          <p className="text-xs text-text-tertiary">Schema Rules</p>
        </div>
        <div className="p-3 bg-bg-secondary rounded-lg text-center">
          <p className="text-xl font-semibold text-success-text">{stats.propertyQuality}</p>
          <p className="text-xs text-text-tertiary">Property Rules</p>
        </div>
      </div>

      {/* Schema Information Section */}
      <div className="border border-border-default rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={() => toggleSection('schema')}
          className="w-full flex items-center justify-between p-4 bg-bg-secondary hover:bg-bg-tertiary transition-colors"
        >
          <div className="flex items-center gap-2">
            <FileCode2 className="h-5 w-5 text-primary-text" />
            <h3 className="font-medium text-text-primary">Schema Information</h3>
          </div>
          {expandedSections.schema ? (
            <ChevronUp className="h-5 w-5 text-text-tertiary" />
          ) : (
            <ChevronDown className="h-5 w-5 text-text-tertiary" />
          )}
        </button>

        {expandedSections.schema && (
          <div className="p-4 space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-text-tertiary">Name</span>
                <p className="text-sm font-medium text-text-primary">{formData.name || '—'}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Business Name</span>
                <p className="text-sm text-text-primary">{formData.businessName || '—'}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Physical Name</span>
                <p className="text-sm font-mono text-text-primary">{formData.physicalName || '—'}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Domain</span>
                <p className="text-sm text-text-primary capitalize">{formData.domain || '—'}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Logical Type</span>
                <p className="text-sm text-text-primary capitalize">{formData.logicalType}</p>
              </div>
              <div>
                <span className="text-xs text-text-tertiary">Physical Type</span>
                <p className="text-sm text-text-primary capitalize">{formData.physicalType || '—'}</p>
              </div>
            </div>

            {formData.description && (
              <div>
                <span className="text-xs text-text-tertiary">Description</span>
                <p className="text-sm text-text-secondary">{formData.description}</p>
              </div>
            )}

            {formData.ownerTeamId && (
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-text-tertiary" />
                <span className="text-sm text-text-secondary">Team: {formData.ownerTeamId}</span>
              </div>
            )}

            {formData.tags && formData.tags.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <Tag className="h-4 w-4 text-text-tertiary" />
                {formData.tags.map(tag => (
                  <Badge key={tag} variant="secondary" size="sm">{tag}</Badge>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Properties Section */}
      <div className="border border-border-default rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={() => toggleSection('properties')}
          className="w-full flex items-center justify-between p-4 bg-bg-secondary hover:bg-bg-tertiary transition-colors"
        >
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary-text" />
            <h3 className="font-medium text-text-primary">
              Properties ({formData.properties.length})
            </h3>
          </div>
          {expandedSections.properties ? (
            <ChevronUp className="h-5 w-5 text-text-tertiary" />
          ) : (
            <ChevronDown className="h-5 w-5 text-text-tertiary" />
          )}
        </button>

        {expandedSections.properties && (
          <div className="divide-y divide-border-default">
            {formData.properties.map((prop, index) => (
              <div key={prop.id || index} className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-mono text-sm font-medium text-text-primary">{prop.name}</span>
                  <Badge variant="outline" size="sm">{prop.logicalType}</Badge>
                  {prop.primaryKey && (
                    <Key className="h-4 w-4 text-warning-text" title="Primary Key" />
                  )}
                  {prop.customProperties?.privacy?.is_pii && (
                    <Shield className="h-4 w-4 text-error-text" title="PII" />
                  )}
                  {prop.required && <Badge variant="secondary" size="sm">Required</Badge>}
                  {prop.unique && <Badge variant="outline" size="sm">Unique</Badge>}
                </div>

                {prop.description && (
                  <p className="text-xs text-text-tertiary mb-2">{prop.description}</p>
                )}

                <div className="flex flex-wrap gap-4 text-xs text-text-tertiary">
                  {prop.physicalType && <span>Physical: {prop.physicalType}</span>}
                  {prop.customProperties?.constraints && prop.customProperties.constraints.length > 0 && (
                    <span>{prop.customProperties.constraints.length} constraints</span>
                  )}
                  {prop.quality && prop.quality.length > 0 && (
                    <span className="text-success-text">{prop.quality.length} quality rules</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Schema Quality Rules Section */}
      {formData.quality && formData.quality.length > 0 && (
        <div className="border border-border-default rounded-lg overflow-hidden">
          <button
            type="button"
            onClick={() => toggleSection('quality')}
            className="w-full flex items-center justify-between p-4 bg-bg-secondary hover:bg-bg-tertiary transition-colors"
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-success-text" />
              <h3 className="font-medium text-text-primary">
                Schema Quality Rules ({formData.quality.length})
              </h3>
            </div>
            {expandedSections.quality ? (
              <ChevronUp className="h-5 w-5 text-text-tertiary" />
            ) : (
              <ChevronDown className="h-5 w-5 text-text-tertiary" />
            )}
          </button>

          {expandedSections.quality && (
            <div className="divide-y divide-border-default">
              {formData.quality.map((rule) => (
                <div key={rule.id} className="p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm text-text-primary">{rule.name || 'Unnamed rule'}</span>
                    <Badge variant="outline" size="sm">{rule.metric}</Badge>
                  </div>
                  {rule.description && (
                    <p className="text-xs text-text-tertiary">{rule.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-4 border-t border-border-default">
        <Button variant="secondary" onClick={onBack} disabled={createSchemaMutation.isPending}>
          Back
        </Button>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={() => createSchemaMutation.mutate(false)}
            disabled={createSchemaMutation.isPending}
          >
            {createSchemaMutation.isPending ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Save as Draft
          </Button>
          <Button
            onClick={() => createSchemaMutation.mutate(true)}
            disabled={!allPassed || createSchemaMutation.isPending}
          >
            {createSchemaMutation.isPending ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Publish Schema
          </Button>
        </div>
      </div>
    </div>
  )
}
