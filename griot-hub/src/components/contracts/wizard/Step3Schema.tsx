'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight, Key, Shield, Lock, ExternalLink, Database } from 'lucide-react'
import { Button, Badge } from '@/components/ui'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

interface SchemaField {
  id: string
  name: string
  logicalType: string
  physicalType?: string
  description?: string
  required: boolean
  unique: boolean
  primaryKey: boolean
  piiClassification?: string
}

interface SchemaTable {
  id: string
  name: string
  physicalName?: string
  description?: string
  fields: SchemaField[]
}

const PII_LABELS: Record<string, string> = {
  email: 'Email',
  name: 'Name',
  phone: 'Phone',
  address: 'Address',
  ssn: 'SSN',
  financial: 'Financial',
  health: 'Health',
  other: 'Other PII',
}

export function Step3Schema({ formData, updateFormData, onNext, onBack }: Props) {
  // Get tables from formData (populated by Step2 schema selection)
  const tables: SchemaTable[] = (formData.tables || []).map((t: any, idx: number) => ({
    id: t.id || `table-${idx}`,
    name: t.name || '',
    physicalName: t.physicalName,
    description: t.description,
    fields: (t.fields || []).map((f: any, fidx: number) => ({
      id: f.id || `field-${idx}-${fidx}`,
      name: f.name || '',
      logicalType: f.logicalType || 'string',
      physicalType: f.physicalType,
      description: f.description,
      required: f.required || false,
      unique: f.unique || false,
      primaryKey: f.primaryKey || false,
      piiClassification: f.piiClassification,
    })),
  }))

  // Get selected schemas info
  const selectedSchemas = formData.selectedSchemas || []

  // Track which tables are expanded
  const [expandedTables, setExpandedTables] = useState<Set<string>>(
    new Set(tables.map((t) => t.id))
  )

  const toggleTableExpand = (tableId: string) => {
    setExpandedTables((prev) => {
      const next = new Set(prev)
      if (next.has(tableId)) {
        next.delete(tableId)
      } else {
        next.add(tableId)
      }
      return next
    })
  }

  const totalFields = tables.reduce((sum, t) => sum + (t.fields?.length || 0), 0)
  const totalPrimaryKeys = tables.reduce(
    (sum, t) => sum + (t.fields?.filter((f) => f.primaryKey)?.length || 0),
    0
  )
  const totalPiiFields = tables.reduce(
    (sum, t) => sum + (t.fields?.filter((f) => f.piiClassification)?.length || 0),
    0
  )

  // No tables means no schema selected
  if (tables.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary mb-2">Schema Review</h2>
          <p className="text-sm text-text-secondary">
            Review the schema structure for this contract.
          </p>
        </div>

        <div className="p-8 text-center border border-border-default rounded-lg bg-bg-secondary">
          <Lock className="h-8 w-8 mx-auto text-text-tertiary mb-3" />
          <p className="text-text-secondary mb-2">No schemas selected</p>
          <p className="text-sm text-text-tertiary">
            Please go back and select one or more schemas from your Data Assets.
          </p>
        </div>

        <div className="flex justify-between">
          <Button variant="secondary" onClick={onBack}>
            Back: Select Schemas
          </Button>
          <Button disabled>Next: Quality Rules</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Schema Review</h2>
        <p className="text-sm text-text-secondary">
          Review the schema structure from the selected Data Assets. These schemas are read-only.
        </p>
      </div>

      {/* Read-only Notice */}
      <div className="flex items-center gap-3 p-3 bg-bg-secondary border border-border-default rounded-lg">
        <Lock className="h-4 w-4 text-text-tertiary" />
        <span className="text-sm text-text-secondary">
          {selectedSchemas.length === 1 ? (
            <>
              Schema inherited from:{' '}
              <strong className="text-text-primary">{selectedSchemas[0].name}</strong>
            </>
          ) : (
            <>
              <strong className="text-text-primary">{selectedSchemas.length} schemas</strong> selected from Data Assets
            </>
          )}
        </span>
        <a
          href="/studio/assets"
          className="ml-auto text-sm text-primary-text hover:underline flex items-center gap-1"
        >
          Edit in Data Assets
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      {/* Summary Stats */}
      <div className="flex gap-4 p-4 bg-bg-secondary rounded-lg">
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{tables.length}</p>
          <p className="text-xs text-text-tertiary">Tables</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{totalFields}</p>
          <p className="text-xs text-text-tertiary">Fields</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{totalPrimaryKeys}</p>
          <p className="text-xs text-text-tertiary">Primary Keys</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{totalPiiFields}</p>
          <p className="text-xs text-text-tertiary">PII Fields</p>
        </div>
      </div>

      {/* Tables (Read-Only) */}
      <div className="space-y-4">
        {tables.map((table) => (
          <div
            key={table.id}
            className="border border-border-default rounded-lg overflow-hidden"
          >
            {/* Table Header */}
            <div className="flex items-center gap-3 p-4 bg-bg-secondary border-b border-border-default">
              <button
                type="button"
                onClick={() => toggleTableExpand(table.id)}
                className="p-1 hover:bg-bg-primary rounded"
              >
                {expandedTables.has(table.id) ? (
                  <ChevronDown className="h-4 w-4 text-text-secondary" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-text-secondary" />
                )}
              </button>

              <Database className="h-4 w-4 text-text-tertiary" />

              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-text-primary">{table.name}</span>
                  {table.physicalName && (
                    <span className="text-xs text-text-tertiary">({table.physicalName})</span>
                  )}
                </div>
                {table.description && (
                  <p className="text-xs text-text-tertiary mt-0.5">{table.description}</p>
                )}
              </div>

              <Badge variant="secondary" size="sm">
                {table.fields?.length || 0} fields
              </Badge>
            </div>

            {/* Table Fields (Read-Only) */}
            {expandedTables.has(table.id) && (
              <div className="p-4">
                {!table.fields || table.fields.length === 0 ? (
                  <p className="text-sm text-text-tertiary text-center py-4">
                    No fields defined in this table.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {/* Field Headers */}
                    <div className="grid grid-cols-12 gap-2 px-2 text-xs font-medium text-text-tertiary">
                      <div className="col-span-3">Name</div>
                      <div className="col-span-2">Type</div>
                      <div className="col-span-3">Description</div>
                      <div className="col-span-2">PII</div>
                      <div className="col-span-2">Properties</div>
                    </div>

                    {/* Field Rows (Read-Only) */}
                    {table.fields.map((field) => (
                      <div
                        key={field.id}
                        className="grid grid-cols-12 gap-2 items-center p-2 bg-bg-secondary/50 rounded-lg"
                      >
                        <div className="col-span-3">
                          <span className="text-sm text-text-primary font-medium">
                            {field.name}
                          </span>
                        </div>

                        <div className="col-span-2">
                          <Badge variant="secondary" size="xs">
                            {field.logicalType}
                          </Badge>
                        </div>

                        <div className="col-span-3">
                          <span className="text-sm text-text-tertiary truncate block">
                            {field.description || '-'}
                          </span>
                        </div>

                        <div className="col-span-2">
                          {field.piiClassification ? (
                            <Badge
                              variant="secondary"
                              size="xs"
                              className="bg-warning-bg/20 text-warning-text border border-warning-border"
                            >
                              <Shield className="h-3 w-3 mr-1" />
                              {PII_LABELS[field.piiClassification] || field.piiClassification}
                            </Badge>
                          ) : (
                            <span className="text-xs text-text-tertiary">-</span>
                          )}
                        </div>

                        <div className="col-span-2 flex gap-1">
                          {field.primaryKey && (
                            <span
                              className="p-1.5 rounded bg-primary-bg text-primary-text"
                              title="Primary Key"
                            >
                              <Key className="h-3.5 w-3.5" />
                            </span>
                          )}

                          {field.required && (
                            <span
                              className="p-1.5 rounded bg-error-bg text-error-text text-xs font-medium"
                              title="Required"
                            >
                              R
                            </span>
                          )}

                          {field.unique && (
                            <span
                              className="p-1.5 rounded bg-info-bg text-info-text text-xs font-medium"
                              title="Unique"
                            >
                              U
                            </span>
                          )}

                          {!field.primaryKey && !field.required && !field.unique && (
                            <span className="text-xs text-text-tertiary">-</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Help Text */}
      <div className="p-4 bg-bg-secondary rounded-lg text-sm text-text-secondary">
        <p className="font-medium mb-2">Field Properties:</p>
        <ul className="space-y-1 text-text-tertiary">
          <li>
            <Key className="inline h-3 w-3 mr-1" /> <strong>Primary Key</strong> - Identifies
            unique records
          </li>
          <li>
            <span className="inline-flex items-center justify-center h-4 w-4 text-xs font-medium bg-error-bg text-error-text rounded mr-1">
              R
            </span>{' '}
            <strong>Required</strong> - Field cannot be null
          </li>
          <li>
            <span className="inline-flex items-center justify-center h-4 w-4 text-xs font-medium bg-info-bg text-info-text rounded mr-1">
              U
            </span>{' '}
            <strong>Unique</strong> - All values must be distinct
          </li>
          <li>
            <Shield className="inline h-3 w-3 mr-1" /> <strong>PII</strong> - Contains personal
            data
          </li>
        </ul>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onNext}>Next: Quality Rules</Button>
      </div>
    </div>
  )
}
