'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Badge } from '@/components/ui'
import { api, queryKeys } from '@/lib/api/client'
import { Database, Search, ChevronDown, AlertCircle, Check, X } from 'lucide-react'
import type { ContractFormData, SelectedSchemaInfo } from '@/app/studio/contracts/new/wizard/page'

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
  const selectedSchemas = formData.selectedSchemas || []

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

  // Check if a schema is selected
  const isSchemaSelected = (schemaId: string) => {
    return selectedSchemas.some((s) => s.id === schemaId)
  }

  // Transform schema to table format for form data
  const schemaToTable = (schema: StandaloneSchema, tableIndex: number) => {
    const fields = (schema.properties || []).map((prop, fidx) => {
      // Extract PII classification from customProperties
      let piiClassification: string | undefined
      if (prop.customProperties?.privacy?.is_pii) {
        piiClassification = prop.customProperties.privacy.pii_type || 'other'
      }

      return {
        id: `field-${tableIndex}-${fidx}`,
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

    return {
      id: `table-${tableIndex}`,
      name: schema.name,
      physicalName: schema.physicalName,
      description: schema.description,
      fields,
    }
  }

  const handleToggleSchema = async (schema: StandaloneSchema) => {
    const isCurrentlySelected = isSchemaSelected(schema.id)
    const currentTables = formData.tables || []

    if (isCurrentlySelected) {
      // Remove the schema - filter out its table by matching name
      const newSelectedSchemas = selectedSchemas.filter((s) => s.id !== schema.id)
      const newTables = currentTables.filter((t: any) => t.name !== schema.name)
      // Re-index table IDs
      const reindexedTables = newTables.map((t: any, idx: number) => ({
        ...t,
        id: `table-${idx}`,
      }))

      updateFormData({
        selectedSchemas: newSelectedSchemas,
        tables: reindexedTables,
      })
    } else {
      // Add the schema - fetch full details to ensure we have all properties
      let fullSchema = schema

      // If properties are missing or empty, fetch full schema details
      if (!schema.properties || schema.properties.length === 0) {
        try {
          const fetchedSchema = await api.get<StandaloneSchema>(`/schemas/${schema.id}`)
          fullSchema = fetchedSchema
        } catch (error) {
          console.error('Failed to fetch schema details:', error)
          // Fall back to the list data
        }
      }

      const schemaInfo: SelectedSchemaInfo = {
        id: fullSchema.id,
        name: fullSchema.businessName || fullSchema.name,
        physicalName: fullSchema.physicalName,
        description: fullSchema.description,
        domain: fullSchema.domain,
        fieldCount: fullSchema.propertyCount ?? fullSchema.properties?.length ?? 0,
        hasPii: fullSchema.hasPii,
      }

      const newSelectedSchemas = [...selectedSchemas, schemaInfo]
      const newTableIndex = currentTables.length
      const newTable = schemaToTable(fullSchema, newTableIndex)

      updateFormData({
        selectedSchemas: newSelectedSchemas,
        tables: [...currentTables, newTable],
      })
    }
  }

  const handleRemoveSchema = (schemaId: string) => {
    const schemaToRemove = selectedSchemas.find((s) => s.id === schemaId)
    if (!schemaToRemove) return

    const currentTables = formData.tables || []
    const newSelectedSchemas = selectedSchemas.filter((s) => s.id !== schemaId)
    // Filter out the table that matches the schema name
    const newTables = currentTables.filter((t: any) => t.name !== schemaToRemove.name && t.name !== schemaToRemove.physicalName)
    // Re-index table IDs
    const reindexedTables = newTables.map((t: any, idx: number) => ({
      ...t,
      id: `table-${idx}`,
    }))

    updateFormData({
      selectedSchemas: newSelectedSchemas,
      tables: reindexedTables,
    })
  }

  const handleClearAll = () => {
    updateFormData({
      selectedSchemas: [],
      tables: [],
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Select Schemas</h2>
        <p className="text-sm text-text-secondary">
          Choose one or more schemas from your Data Assets. Each schema will become a table in your contract.
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
              section. You can select multiple schemas to include in this contract.
            </p>
          </div>
        </div>
      </div>

      {/* Selected Schemas Display */}
      {selectedSchemas.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-text-primary">
              Selected Schemas ({selectedSchemas.length})
            </label>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearAll}
              className="text-text-tertiary hover:text-error-text"
            >
              Clear All
            </Button>
          </div>
          <div className="space-y-2">
            {selectedSchemas.map((schema) => (
              <div
                key={schema.id}
                className="flex items-center justify-between p-3 border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Database className="h-4 w-4 text-primary-text" />
                  <div>
                    <p className="font-medium text-text-primary">{schema.name}</p>
                    <div className="flex gap-2 mt-1">
                      {schema.domain && (
                        <Badge variant="secondary" size="xs">{schema.domain}</Badge>
                      )}
                      <Badge variant="secondary" size="xs">
                        {schema.fieldCount} fields
                      </Badge>
                      {schema.hasPii && (
                        <Badge variant="secondary" size="xs" className="bg-warning-bg/20 text-warning-text">
                          PII
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveSchema(schema.id)}
                  className="text-text-tertiary hover:text-error-text"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schema Selector */}
      <div className="relative">
        <label className="block text-sm font-medium text-text-primary mb-2">
          {selectedSchemas.length === 0 ? (
            <>Add Schema <span className="text-error-text">*</span></>
          ) : (
            'Add More Schemas'
          )}
        </label>

        {/* Searchable Dropdown */}
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
                filteredSchemas.map((schema) => {
                  const isSelected = isSchemaSelected(schema.id)
                  return (
                    <div
                      key={schema.id}
                      onClick={() => handleToggleSchema(schema)}
                      className={`p-3 cursor-pointer border-b border-border-default last:border-b-0 ${
                        isSelected
                          ? 'bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30'
                          : 'hover:bg-bg-secondary'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`mt-1 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center ${
                          isSelected
                            ? 'bg-primary-500 border-primary-500'
                            : 'border-border-default'
                        }`}>
                          {isSelected && <Check className="h-3 w-3 text-white" />}
                        </div>
                        <Database className="h-4 w-4 mt-1 text-text-tertiary flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary">
                            {schema.businessName || schema.name}
                          </p>
                          {schema.physicalName && (
                            <p className="text-xs text-text-tertiary mt-0.5">
                              Physical: {schema.physicalName}
                            </p>
                          )}
                          <div className="flex flex-wrap gap-2 mt-1">
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
                  )
                })
              )}
            </div>
          )}
        </div>

        {/* Help Text */}
        <p className="mt-2 text-xs text-text-tertiary">
          {selectedSchemas.length} selected • Showing {filteredSchemas.length} of {schemas.length} schemas
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
        <Button onClick={onNext} disabled={selectedSchemas.length === 0}>
          Next: Review Schema
        </Button>
      </div>

      {selectedSchemas.length === 0 && (
        <p className="text-sm text-warning-text text-center">
          Please select at least one schema to continue.
        </p>
      )}
    </div>
  )
}
