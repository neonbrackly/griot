'use client'

import { useState } from 'react'
import {
  Plus,
  Trash2,
  Info,
  AlertCircle,
  CheckCircle,
  Code,
  HelpCircle,
} from 'lucide-react'
import { Button, Input, Badge } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import type { SchemaFormData, SchemaQualityRule, SchemaLogicalType } from '@/types'

interface Props {
  formData: SchemaFormData
  updateFormData: (data: Partial<SchemaFormData>) => void
  onNext: () => void
}

const LOGICAL_TYPES: { value: SchemaLogicalType; label: string; description: string }[] = [
  { value: 'object', label: 'Object', description: 'A structured record with named properties (e.g., a table row)' },
  { value: 'array', label: 'Array', description: 'An ordered collection of items' },
  { value: 'primitive', label: 'Primitive', description: 'A single value type (string, number, etc.)' },
]

const PHYSICAL_TYPES = [
  { value: 'table', label: 'Table' },
  { value: 'view', label: 'View' },
  { value: 'topic', label: 'Topic (Kafka/Event)' },
  { value: 'file', label: 'File' },
  { value: 'api', label: 'API Response' },
]

const DOMAINS = [
  { value: 'analytics', label: 'Analytics' },
  { value: 'finance', label: 'Finance' },
  { value: 'crm', label: 'CRM' },
  { value: 'operations', label: 'Operations' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'ml', label: 'ML / Data Science' },
]

// Schema-level quality rule metrics
const SCHEMA_QUALITY_METRICS = [
  {
    value: 'duplicateValues',
    label: 'Duplicate Values',
    description: 'Check for duplicate records based on specified properties',
    hasArguments: true,
    argumentsLabel: 'Properties to check (comma-separated)',
  },
  {
    value: 'recordCount',
    label: 'Record Count',
    description: 'Validate the number of records in the schema',
    hasArguments: false,
  },
  {
    value: 'distributionShift',
    label: 'Distribution Shift',
    description: 'Monitor for statistical distribution changes',
    hasArguments: true,
    argumentsLabel: 'Threshold (0-1)',
  },
  {
    value: 'freshness',
    label: 'Data Freshness',
    description: 'Check that data was updated within expected timeframe',
    hasArguments: true,
    argumentsLabel: 'Max age in hours',
  },
  {
    value: 'custom',
    label: 'Custom SQL',
    description: 'Write a custom validation query',
    hasArguments: true,
    argumentsLabel: 'SQL expression',
  },
]

const generateId = () => `sqr-${Math.random().toString(36).substring(2, 9)}`

export function Step1SchemaInfo({ formData, updateFormData, onNext }: Props) {
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [qualityRules, setQualityRules] = useState<SchemaQualityRule[]>(formData.quality || [])

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.name || formData.name.length < 3) {
      newErrors.name = 'Schema name must be at least 3 characters'
    }

    if (!/^[a-z][a-z0-9_]*$/.test(formData.name || '')) {
      newErrors.name = 'Schema name must be lowercase, start with a letter, and contain only letters, numbers, and underscores'
    }

    if (!formData.logicalType) {
      newErrors.logicalType = 'Please select a logical type'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validate()) {
      updateFormData({ quality: qualityRules })
      onNext()
    }
  }

  const addQualityRule = () => {
    const newRule: SchemaQualityRule = {
      id: generateId(),
      name: '',
      type: 'library',
      metric: 'duplicateValues',
      description: '',
      mustBe: 0,
      unit: 'rows',
    }
    const newRules = [...qualityRules, newRule]
    setQualityRules(newRules)
    updateFormData({ quality: newRules })
  }

  const updateQualityRule = (id: string, updates: Partial<SchemaQualityRule>) => {
    const newRules = qualityRules.map((r) =>
      r.id === id ? { ...r, ...updates } : r
    )
    setQualityRules(newRules)
    updateFormData({ quality: newRules })
  }

  const removeQualityRule = (id: string) => {
    const newRules = qualityRules.filter((r) => r.id !== id)
    setQualityRules(newRules)
    updateFormData({ quality: newRules })
  }

  return (
    <div className="space-y-8">
      {/* Schema Information Section */}
      <section>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-text-primary">Schema Information</h2>
          <p className="text-sm text-text-secondary">
            Define the basic metadata for your schema
          </p>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Schema Name" required error={errors.name}>
              <Input
                placeholder="e.g., customers, orders, products"
                value={formData.name}
                onChange={(e) => updateFormData({ name: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_') })}
              />
              <p className="text-xs text-text-tertiary mt-1">
                Lowercase, letters, numbers, and underscores only
              </p>
            </FormField>

            <FormField label="Business Name">
              <Input
                placeholder="e.g., Customer Records, Order History"
                value={formData.businessName || ''}
                onChange={(e) => updateFormData({ businessName: e.target.value })}
              />
              <p className="text-xs text-text-tertiary mt-1">
                Human-friendly display name
              </p>
            </FormField>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormField label="Physical Name">
              <Input
                placeholder="e.g., dim_customers, fact_orders"
                value={formData.physicalName || ''}
                onChange={(e) => updateFormData({ physicalName: e.target.value })}
              />
              <p className="text-xs text-text-tertiary mt-1">
                Name in the data system (table name, topic name, etc.)
              </p>
            </FormField>

            <FormField label="Domain">
              <select
                value={formData.domain || ''}
                onChange={(e) => updateFormData({ domain: e.target.value })}
                className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
              >
                <option value="">Select a domain...</option>
                {DOMAINS.map((domain) => (
                  <option key={domain.value} value={domain.value}>
                    {domain.label}
                  </option>
                ))}
              </select>
            </FormField>
          </div>

          <FormField label="Description">
            <textarea
              placeholder="Describe the purpose and contents of this schema..."
              value={formData.description || ''}
              onChange={(e) => updateFormData({ description: e.target.value })}
              className="w-full h-24 rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-1 focus:ring-primary-border"
            />
          </FormField>

          <div className="grid grid-cols-2 gap-4">
            <FormField label="Logical Type" required error={errors.logicalType}>
              <div className="space-y-2">
                {LOGICAL_TYPES.map((type) => (
                  <label
                    key={type.value}
                    className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      formData.logicalType === type.value
                        ? 'border-primary-border bg-primary-50 dark:bg-primary-900/20'
                        : 'border-border-default hover:bg-bg-secondary'
                    }`}
                  >
                    <input
                      type="radio"
                      name="logicalType"
                      value={type.value}
                      checked={formData.logicalType === type.value}
                      onChange={(e) => updateFormData({ logicalType: e.target.value as SchemaLogicalType })}
                      className="mt-0.5"
                    />
                    <div>
                      <div className="font-medium text-text-primary">{type.label}</div>
                      <div className="text-xs text-text-tertiary">{type.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </FormField>

            <FormField label="Physical Type">
              <select
                value={formData.physicalType || 'table'}
                onChange={(e) => updateFormData({ physicalType: e.target.value })}
                className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
              >
                {PHYSICAL_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-text-tertiary mt-1">
                The type of data structure in your system
              </p>
            </FormField>
          </div>
        </div>
      </section>

      {/* Schema-Level Quality Rules Section */}
      <section className="border-t border-border-default pt-8">
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-semibold text-text-primary">Schema-Level Quality Rules</h2>
            <div className="group relative">
              <HelpCircle className="h-4 w-4 text-text-tertiary cursor-help" />
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-bg-primary border border-border-default rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                <p className="text-xs text-text-secondary">
                  Schema-level quality rules apply to the entire schema (table/dataset),
                  such as checking for duplicate records or monitoring record counts.
                </p>
              </div>
            </div>
          </div>
          <p className="text-sm text-text-secondary">
            Define quality checks that apply to the entire schema
          </p>
        </div>

        {/* Quality Rules Summary */}
        {qualityRules.length > 0 && (
          <div className="flex gap-4 p-4 bg-bg-secondary rounded-lg mb-4">
            <div className="text-center">
              <p className="text-2xl font-semibold text-text-primary">{qualityRules.length}</p>
              <p className="text-xs text-text-tertiary">Total Rules</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold text-primary-text">
                {qualityRules.filter((r) => r.type === 'library').length}
              </p>
              <p className="text-xs text-text-tertiary">Library</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold text-text-primary">
                {qualityRules.filter((r) => r.type === 'custom').length}
              </p>
              <p className="text-xs text-text-tertiary">Custom</p>
            </div>
          </div>
        )}

        {/* Quality Rules List */}
        {qualityRules.length > 0 && (
          <div className="space-y-4 mb-4">
            {qualityRules.map((rule) => {
              const metric = SCHEMA_QUALITY_METRICS.find((m) => m.value === rule.metric)
              return (
                <div
                  key={rule.id}
                  className="border border-border-default rounded-lg overflow-hidden"
                >
                  {/* Rule Header */}
                  <div className="flex items-center gap-3 p-4 bg-bg-secondary">
                    <div className="p-2 rounded-lg bg-info-bg text-info-text">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <Input
                        placeholder="Rule name"
                        value={rule.name}
                        onChange={(e) => updateQualityRule(rule.id, { name: e.target.value })}
                        className="font-medium"
                      />
                    </div>
                    <Badge variant="secondary" size="sm">
                      {rule.type === 'custom' ? 'Custom' : 'Library'}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeQualityRule(rule.id)}
                      className="text-error-text hover:bg-error-bg"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Rule Configuration */}
                  <div className="p-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          Metric
                        </label>
                        <select
                          value={rule.metric}
                          onChange={(e) => updateQualityRule(rule.id, {
                            metric: e.target.value,
                            type: e.target.value === 'custom' ? 'custom' : 'library'
                          })}
                          className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                        >
                          {SCHEMA_QUALITY_METRICS.map((m) => (
                            <option key={m.value} value={m.value}>
                              {m.label}
                            </option>
                          ))}
                        </select>
                        {metric && (
                          <p className="text-xs text-text-tertiary mt-1">
                            {metric.description}
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          Threshold
                        </label>
                        <div className="flex gap-2">
                          <select
                            value={rule.mustBe !== undefined ? 'mustBe' : rule.mustBeLessThan !== undefined ? 'mustBeLessThan' : 'mustBeGreaterThan'}
                            onChange={(e) => {
                              const val = rule.mustBe ?? rule.mustBeLessThan ?? rule.mustBeGreaterThan ?? 0
                              const updates: Partial<SchemaQualityRule> = {
                                mustBe: undefined,
                                mustBeLessThan: undefined,
                                mustBeGreaterThan: undefined,
                              }
                              updates[e.target.value as keyof typeof updates] = val
                              updateQualityRule(rule.id, updates)
                            }}
                            className="h-10 w-32 rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                          >
                            <option value="mustBe">Must be</option>
                            <option value="mustBeLessThan">Less than</option>
                            <option value="mustBeGreaterThan">Greater than</option>
                          </select>
                          <Input
                            type="number"
                            value={rule.mustBe ?? rule.mustBeLessThan ?? rule.mustBeGreaterThan ?? ''}
                            onChange={(e) => {
                              const key = rule.mustBe !== undefined ? 'mustBe' : rule.mustBeLessThan !== undefined ? 'mustBeLessThan' : 'mustBeGreaterThan'
                              updateQualityRule(rule.id, { [key]: parseFloat(e.target.value) || 0 })
                            }}
                            className="flex-1"
                          />
                          <select
                            value={rule.unit || 'rows'}
                            onChange={(e) => updateQualityRule(rule.id, { unit: e.target.value as 'rows' | 'percent' })}
                            className="h-10 w-24 rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                          >
                            <option value="rows">rows</option>
                            <option value="percent">%</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    {/* Arguments for specific metrics */}
                    {metric?.hasArguments && rule.metric !== 'custom' && (
                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          {metric.argumentsLabel}
                        </label>
                        <Input
                          placeholder={metric.argumentsLabel}
                          value={(rule.arguments?.properties as string[])?.join(', ') || (rule.arguments?.threshold as string) || ''}
                          onChange={(e) => {
                            if (rule.metric === 'duplicateValues') {
                              updateQualityRule(rule.id, {
                                arguments: { properties: e.target.value.split(',').map(s => s.trim()).filter(Boolean) }
                              })
                            } else {
                              updateQualityRule(rule.id, {
                                arguments: { threshold: e.target.value }
                              })
                            }
                          }}
                        />
                      </div>
                    )}

                    {/* Custom SQL expression */}
                    {rule.metric === 'custom' && (
                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          SQL Expression
                        </label>
                        <textarea
                          value={(rule.arguments?.sql as string) || ''}
                          onChange={(e) => updateQualityRule(rule.id, {
                            arguments: { sql: e.target.value }
                          })}
                          placeholder="SELECT COUNT(*) FROM {table} WHERE condition..."
                          className="w-full h-24 rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary font-mono placeholder:text-text-tertiary focus:outline-none focus:ring-1 focus:ring-primary-border"
                        />
                      </div>
                    )}

                    <div>
                      <label className="text-sm font-medium text-text-secondary mb-1 block">
                        Description
                      </label>
                      <Input
                        placeholder="Describe what this rule validates..."
                        value={rule.description || ''}
                        onChange={(e) => updateQualityRule(rule.id, { description: e.target.value })}
                      />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Add Rule Button */}
        <Button variant="secondary" onClick={addQualityRule}>
          <Plus className="h-4 w-4 mr-2" />
          Add Schema Quality Rule
        </Button>

        {/* Empty State */}
        {qualityRules.length === 0 && (
          <div className="mt-4 p-6 border-2 border-dashed border-border-default rounded-lg text-center">
            <AlertCircle className="h-10 w-10 text-text-tertiary mx-auto mb-3" />
            <p className="text-text-secondary mb-1">No schema-level quality rules defined</p>
            <p className="text-sm text-text-tertiary">
              Schema-level rules validate the entire dataset, such as checking for duplicates or record counts.
            </p>
          </div>
        )}
      </section>

      {/* Navigation */}
      <div className="flex justify-end pt-4 border-t border-border-default">
        <Button onClick={handleNext}>
          Next: Define Properties
        </Button>
      </div>
    </div>
  )
}
