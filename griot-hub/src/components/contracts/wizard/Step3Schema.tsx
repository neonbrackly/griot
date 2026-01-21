'use client'

import { useState } from 'react'
import { Plus, Trash2, ChevronDown, ChevronRight, GripVertical, Key, Shield } from 'lucide-react'
import { Button, Input, Badge } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
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
  isExpanded: boolean
}

const FIELD_TYPES = [
  'string',
  'integer',
  'number',
  'boolean',
  'date',
  'datetime',
  'timestamp',
  'array',
  'object',
  'binary',
  'uuid',
]

const PII_TYPES = [
  { value: '', label: 'None' },
  { value: 'email', label: 'Email' },
  { value: 'name', label: 'Name' },
  { value: 'phone', label: 'Phone' },
  { value: 'address', label: 'Address' },
  { value: 'ssn', label: 'SSN' },
  { value: 'financial', label: 'Financial' },
  { value: 'health', label: 'Health' },
  { value: 'other', label: 'Other PII' },
]

const generateId = () => Math.random().toString(36).substring(2, 9)

export function Step3Schema({ formData, updateFormData, onNext, onBack }: Props) {
  // Initialize tables from formData or empty
  const [tables, setTables] = useState<SchemaTable[]>(() => {
    if (formData.tables && formData.tables.length > 0) {
      return formData.tables.map((t: any) => ({
        ...t,
        isExpanded: true,
        fields: t.fields?.map((f: any) => ({ ...f, id: f.id || generateId() })) || [],
      }))
    }
    return []
  })

  const syncToFormData = (newTables: SchemaTable[]) => {
    const cleanedTables = newTables.map(({ isExpanded, ...table }) => ({
      ...table,
      fields: table.fields.map(({ id, ...field }) => field),
    }))
    updateFormData({ tables: cleanedTables })
  }

  const addTable = () => {
    const newTable: SchemaTable = {
      id: generateId(),
      name: '',
      description: '',
      fields: [],
      isExpanded: true,
    }
    const newTables = [...tables, newTable]
    setTables(newTables)
    syncToFormData(newTables)
  }

  const removeTable = (tableId: string) => {
    const newTables = tables.filter((t) => t.id !== tableId)
    setTables(newTables)
    syncToFormData(newTables)
  }

  const updateTable = (tableId: string, updates: Partial<SchemaTable>) => {
    const newTables = tables.map((t) =>
      t.id === tableId ? { ...t, ...updates } : t
    )
    setTables(newTables)
    syncToFormData(newTables)
  }

  const toggleTableExpand = (tableId: string) => {
    setTables(tables.map((t) =>
      t.id === tableId ? { ...t, isExpanded: !t.isExpanded } : t
    ))
  }

  const addField = (tableId: string) => {
    const newField: SchemaField = {
      id: generateId(),
      name: '',
      logicalType: 'string',
      required: false,
      unique: false,
      primaryKey: false,
    }
    const newTables = tables.map((t) =>
      t.id === tableId ? { ...t, fields: [...t.fields, newField] } : t
    )
    setTables(newTables)
    syncToFormData(newTables)
  }

  const removeField = (tableId: string, fieldId: string) => {
    const newTables = tables.map((t) =>
      t.id === tableId
        ? { ...t, fields: t.fields.filter((f) => f.id !== fieldId) }
        : t
    )
    setTables(newTables)
    syncToFormData(newTables)
  }

  const updateField = (tableId: string, fieldId: string, updates: Partial<SchemaField>) => {
    const newTables = tables.map((t) =>
      t.id === tableId
        ? {
            ...t,
            fields: t.fields.map((f) =>
              f.id === fieldId ? { ...f, ...updates } : f
            ),
          }
        : t
    )
    setTables(newTables)
    syncToFormData(newTables)
  }

  const totalFields = tables.reduce((sum, t) => sum + t.fields.length, 0)
  const hasValidSchema = tables.length > 0 && tables.every((t) => t.name && t.fields.length > 0)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Schema Definition</h2>
        <p className="text-sm text-text-secondary">
          Define the tables and fields for this contract. Each table should have at least one field.
        </p>
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
          <p className="text-2xl font-semibold text-text-primary">
            {tables.reduce((sum, t) => sum + t.fields.filter(f => f.primaryKey).length, 0)}
          </p>
          <p className="text-xs text-text-tertiary">Primary Keys</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">
            {tables.reduce((sum, t) => sum + t.fields.filter(f => f.piiClassification).length, 0)}
          </p>
          <p className="text-xs text-text-tertiary">PII Fields</p>
        </div>
      </div>

      {/* Tables */}
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
                {table.isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-text-secondary" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-text-secondary" />
                )}
              </button>

              <div className="flex-1 grid grid-cols-2 gap-4">
                <Input
                  placeholder="Table name"
                  value={table.name}
                  onChange={(e) => updateTable(table.id, { name: e.target.value })}
                />
                <Input
                  placeholder="Description (optional)"
                  value={table.description || ''}
                  onChange={(e) => updateTable(table.id, { description: e.target.value })}
                />
              </div>

              <Badge variant="secondary" size="sm">
                {table.fields.length} fields
              </Badge>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeTable(table.id)}
                className="text-error-text hover:bg-error-bg"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            {/* Table Fields */}
            {table.isExpanded && (
              <div className="p-4 space-y-3">
                {table.fields.length === 0 ? (
                  <p className="text-sm text-text-tertiary text-center py-4">
                    No fields defined. Add at least one field to this table.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {/* Field Headers */}
                    <div className="grid grid-cols-12 gap-2 px-2 text-xs font-medium text-text-tertiary">
                      <div className="col-span-3">Name</div>
                      <div className="col-span-2">Type</div>
                      <div className="col-span-3">Description</div>
                      <div className="col-span-2">PII</div>
                      <div className="col-span-1">Options</div>
                      <div className="col-span-1"></div>
                    </div>

                    {/* Field Rows */}
                    {table.fields.map((field) => (
                      <div
                        key={field.id}
                        className="grid grid-cols-12 gap-2 items-center p-2 bg-bg-secondary rounded-lg"
                      >
                        <div className="col-span-3">
                          <Input
                            placeholder="Field name"
                            value={field.name}
                            onChange={(e) => updateField(table.id, field.id, { name: e.target.value })}
                            className="h-8 text-sm"
                          />
                        </div>

                        <div className="col-span-2">
                          <select
                            value={field.logicalType}
                            onChange={(e) => updateField(table.id, field.id, { logicalType: e.target.value })}
                            className="h-8 w-full rounded-md border border-border-default bg-bg-primary px-2 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                          >
                            {FIELD_TYPES.map((type) => (
                              <option key={type} value={type}>{type}</option>
                            ))}
                          </select>
                        </div>

                        <div className="col-span-3">
                          <Input
                            placeholder="Description"
                            value={field.description || ''}
                            onChange={(e) => updateField(table.id, field.id, { description: e.target.value })}
                            className="h-8 text-sm"
                          />
                        </div>

                        <div className="col-span-2">
                          <select
                            value={field.piiClassification || ''}
                            onChange={(e) => updateField(table.id, field.id, { piiClassification: e.target.value || undefined })}
                            className={`h-8 w-full rounded-md border px-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary-border ${
                              field.piiClassification
                                ? 'border-warning-border bg-warning-bg/20 text-warning-text'
                                : 'border-border-default bg-bg-primary text-text-primary'
                            }`}
                          >
                            {PII_TYPES.map((type) => (
                              <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                          </select>
                        </div>

                        <div className="col-span-1 flex gap-1">
                          <button
                            type="button"
                            onClick={() => updateField(table.id, field.id, { primaryKey: !field.primaryKey })}
                            className={`p-1.5 rounded ${
                              field.primaryKey
                                ? 'bg-primary-bg text-primary-text'
                                : 'bg-bg-primary text-text-tertiary hover:text-text-primary'
                            }`}
                            title="Primary Key"
                          >
                            <Key className="h-3.5 w-3.5" />
                          </button>

                          <button
                            type="button"
                            onClick={() => updateField(table.id, field.id, { required: !field.required })}
                            className={`p-1.5 rounded text-xs font-medium ${
                              field.required
                                ? 'bg-error-bg text-error-text'
                                : 'bg-bg-primary text-text-tertiary hover:text-text-primary'
                            }`}
                            title="Required"
                          >
                            R
                          </button>

                          <button
                            type="button"
                            onClick={() => updateField(table.id, field.id, { unique: !field.unique })}
                            className={`p-1.5 rounded text-xs font-medium ${
                              field.unique
                                ? 'bg-info-bg text-info-text'
                                : 'bg-bg-primary text-text-tertiary hover:text-text-primary'
                            }`}
                            title="Unique"
                          >
                            U
                          </button>
                        </div>

                        <div className="col-span-1 flex justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeField(table.id, field.id)}
                            className="h-8 w-8 p-0 text-error-text hover:bg-error-bg"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => addField(table.id)}
                  className="w-full border border-dashed border-border-default hover:border-primary-border"
                >
                  <Plus className="h-4 w-4" />
                  Add Field
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add Table Button */}
      <Button
        variant="secondary"
        onClick={addTable}
        className="w-full"
      >
        <Plus className="h-4 w-4" />
        Add Table
      </Button>

      {/* Help Text */}
      <div className="p-4 bg-bg-secondary rounded-lg text-sm text-text-secondary">
        <p className="font-medium mb-2">Field Options:</p>
        <ul className="space-y-1 text-text-tertiary">
          <li><Key className="inline h-3 w-3 mr-1" /> <strong>Primary Key</strong> - Identifies unique records</li>
          <li><span className="inline-flex items-center justify-center h-4 w-4 text-xs font-medium bg-error-bg text-error-text rounded mr-1">R</span> <strong>Required</strong> - Field cannot be null</li>
          <li><span className="inline-flex items-center justify-center h-4 w-4 text-xs font-medium bg-info-bg text-info-text rounded mr-1">U</span> <strong>Unique</strong> - All values must be distinct</li>
          <li><Shield className="inline h-3 w-3 mr-1" /> <strong>PII</strong> - Mark fields containing personal data</li>
        </ul>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext} disabled={!hasValidSchema}>
          Next: Quality Rules
        </Button>
      </div>

      {!hasValidSchema && tables.length > 0 && (
        <p className="text-sm text-warning-text text-center">
          Each table must have a name and at least one field to continue.
        </p>
      )}
    </div>
  )
}
