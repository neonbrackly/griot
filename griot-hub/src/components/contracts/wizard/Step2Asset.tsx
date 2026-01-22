'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Badge } from '@/components/ui'
import { api, queryKeys } from '@/lib/api/client'
import { Database, Search, ChevronDown, AlertCircle } from 'lucide-react'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

// StandaloneSchema from Registry API
// Matches the format from GET /schemas endpoint
interface StandaloneSchemaProperty {
  name: string
  logicalType: string
  physicalType?: string
  description?: string
  primaryKey?: boolean
  required?: boolean
  nullable?: boolean
  unique?: boolean
  defaultValue?: string
  customProperties?: {
    privacy?: {
      is_pii?: boolean
      pii_type?: string
    }
  }
}

interface StandaloneSchema {
  id: string
  name: string
  physicalName?: string
  logicalType?: string
  physicalType?: string
  description?: string
  businessName?: string
  domain?: string
  tags?: string[]
  properties: StandaloneSchemaProperty[]
  version?: string
  status?: 'draft' | 'active' | 'deprecated'
  ownerId?: string
  ownerTeamId?: string
  source?: 'manual' | 'connection' | 'import'
  connectionId?: string
  propertyCount?: number
  hasPii?: boolean
  createdAt?: string
  createdBy?: string
  updatedAt?: string
  updatedBy?: string
}

export function Step2Asset({ formData, updateFormData, onNext, onBack }: Props) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  // Fetch standalone schemas from Registry API
  // Uses GET /schemas?activeOnly=true for contract wizard
  const { data: schemasData, isLoading, error } = useQuery({
    queryKey: queryKeys.schemas.all,
    queryFn: async () => {
      try {
        // GET /schemas returns StandaloneSchemaListResponse { items, total, limit, offset }
        const response = await api.get<{ items: StandaloneSchema[]; total: number } | StandaloneSchema[]>('/schemas?activeOnly=true')
        if (Array.isArray(response)) {
          return response
        }
        return response.items || []
      } catch {
        // Return empty array if API fails - show error message
        return []
      }
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  const schemas = schemasData || []

  // Filter schemas based on search query
  const filteredSchemas = useMemo(() => {
    if (!searchQuery.trim()) return schemas
    const query = searchQuery.toLowerCase()
    return schemas.filter(
      (schema) =>
        schema.name.toLowerCase().includes(query) ||
        schema.physicalName?.toLowerCase().includes(query) ||
        schema.domain?.toLowerCase().includes(query) ||
        schema.description?.toLowerCase().includes(query) ||
        schema.businessName?.toLowerCase().includes(query)
    )
  }, [schemas, searchQuery])

  // Get selected schema details
  const selectedSchema = useMemo(() => {
    if (!formData.assetId) return null
    return schemas.find((s) => s.id === formData.assetId)
  }, [schemas, formData.assetId])

  const handleSelectSchema = (schema: StandaloneSchema) => {
    // Transform StandaloneSchema to formData.tables format
    // StandaloneSchema represents a single table/object with properties as fields
    const fields = (schema.properties || []).map((prop, fidx) => {
      // Extract PII classification from customProperties
      let piiClassification: string | undefined
      if (prop.customProperties?.privacy?.is_pii) {
        piiClassification = prop.customProperties.privacy.pii_type || 'other'
      }

      return {
        id: `field-0-${fidx}`,
        name: prop.name,
        logicalType: prop.logicalType,
        physicalType: prop.physicalType,
        description: prop.description,
        required: prop.required ?? !prop.nullable ?? false,
        unique: prop.unique ?? false,
        primaryKey: prop.primaryKey ?? false,
        piiClassification,
      }
    })

    const tables = [{
      id: 'table-0',
      name: schema.name,
      physicalName: schema.physicalName,
      description: schema.description,
      fields,
    }]

    updateFormData({
      assetId: schema.id,
      isProposed: false,
      // Store the selected schema's tables for Step3 to display
      tables,
      // Also store reference info for the review step
      selectedSchemaName: schema.businessName || schema.name,
      selectedAssetName: schema.physicalName || schema.name,
    })
    setIsDropdownOpen(false)
    setSearchQuery('')
  }

  const handleClearSelection = () => {
    updateFormData({
      assetId: undefined,
      isProposed: false,
      tables: undefined,
      selectedSchemaName: undefined,
      selectedAssetName: undefined,
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Select Schema</h2>
        <p className="text-sm text-text-secondary">
          Choose an existing schema from your Data Assets. Schemas define the structure of your contract.
        </p>
      </div>

      {/* Info Box */}
      <div className="p-4 bg-info-bg/30 border border-info-border rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-info-text mt-0.5" />
          <div className="text-sm text-info-text">
            <p className="font-medium">Schemas are managed in Data Assets</p>
            <p className="mt-1">
              Create and manage your schemas in the{' '}
              <a href="/studio/assets" className="underline hover:no-underline">
                Data Assets
              </a>{' '}
              section. Once created, you can select them here for your contract.
            </p>
          </div>
        </div>
      </div>

      {/* Schema Selector */}
      <div className="relative">
        <label className="block text-sm font-medium text-text-primary mb-2">
          Schema <span className="text-error-text">*</span>
        </label>

        {/* Selected Schema Display */}
        {selectedSchema ? (
          <div className="p-4 border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Database className="h-5 w-5 mt-1 text-primary-text" />
                <div>
                  <p className="font-medium text-text-primary">
                    {selectedSchema.businessName || selectedSchema.name}
                  </p>
                  {selectedSchema.physicalName && (
                    <p className="text-sm text-text-secondary mt-1">
                      Physical: {selectedSchema.physicalName}
                    </p>
                  )}
                  {selectedSchema.description && (
                    <p className="text-sm text-text-tertiary mt-1">{selectedSchema.description}</p>
                  )}
                  <div className="flex gap-2 mt-2">
                    {selectedSchema.domain && (
                      <Badge variant="secondary" size="xs">{selectedSchema.domain}</Badge>
                    )}
                    {selectedSchema.source && (
                      <Badge variant="secondary" size="xs">{selectedSchema.source}</Badge>
                    )}
                    <Badge variant="secondary" size="xs">
                      {selectedSchema.propertyCount ?? selectedSchema.properties?.length ?? 0} fields
                    </Badge>
                    {selectedSchema.hasPii && (
                      <Badge variant="secondary" size="xs" className="bg-warning-bg/20 text-warning-text">
                        Contains PII
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearSelection}
                className="text-text-tertiary hover:text-text-primary"
              >
                Change
              </Button>
            </div>
          </div>
        ) : (
          /* Searchable Dropdown */
          <div className="relative">
            <div
              className="flex items-center gap-2 p-3 border border-border-default rounded-lg cursor-pointer hover:border-border-hover"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <Search className="h-4 w-4 text-text-tertiary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setIsDropdownOpen(true)
                }}
                placeholder="Search schemas by name, asset, or domain..."
                className="flex-1 bg-transparent outline-none text-text-primary placeholder:text-text-tertiary"
                onClick={(e) => {
                  e.stopPropagation()
                  setIsDropdownOpen(true)
                }}
              />
              <ChevronDown className={`h-4 w-4 text-text-tertiary transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </div>

            {/* Dropdown List */}
            {isDropdownOpen && (
              <div className="absolute z-50 w-full mt-1 bg-bg-primary border border-border-default rounded-lg shadow-lg max-h-80 overflow-y-auto">
                {isLoading ? (
                  <div className="p-4 text-center text-text-secondary">
                    Loading schemas...
                  </div>
                ) : error ? (
                  <div className="p-4 text-center text-error-text">
                    Failed to load schemas. Please try again.
                  </div>
                ) : filteredSchemas.length === 0 ? (
                  <div className="p-4 text-center text-text-tertiary">
                    {searchQuery ? (
                      <span>No schemas match "{searchQuery}"</span>
                    ) : (
                      <span>No schemas available. Create one in Data Assets first.</span>
                    )}
                  </div>
                ) : (
                  filteredSchemas.map((schema) => (
                    <div
                      key={schema.id}
                      onClick={() => handleSelectSchema(schema)}
                      className="p-3 hover:bg-bg-secondary cursor-pointer border-b border-border-default last:border-b-0"
                    >
                      <div className="flex items-start gap-3">
                        <Database className="h-4 w-4 mt-1 text-text-tertiary" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">
                            {schema.businessName || schema.name}
                          </p>
                          {schema.physicalName && (
                            <p className="text-xs text-text-tertiary mt-0.5">
                              Physical: {schema.physicalName}
                            </p>
                          )}
                          <div className="flex gap-2 mt-1">
                            {schema.domain && (
                              <Badge variant="secondary" size="xs">{schema.domain}</Badge>
                            )}
                            <Badge variant="secondary" size="xs">
                              {schema.propertyCount ?? schema.properties?.length ?? 0} fields
                            </Badge>
                            {schema.hasPii && (
                              <Badge variant="secondary" size="xs" className="bg-warning-bg/20 text-warning-text">
                                PII
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        <p className="mt-2 text-xs text-text-tertiary">
          Showing {filteredSchemas.length} of {schemas.length} schemas
        </p>
      </div>

      {/* Close dropdown when clicking outside */}
      {isDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext} disabled={!formData.assetId}>
          Next: Review Schema
        </Button>
      </div>

      {!formData.assetId && (
        <p className="text-sm text-warning-text text-center">
          Please select a schema to continue.
        </p>
      )}
    </div>
  )
}
