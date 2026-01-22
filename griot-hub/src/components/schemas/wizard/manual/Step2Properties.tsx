'use client'

import { useState, useMemo } from 'react'
import {
  Plus,
  Trash2,
  ChevronDown,
  ChevronUp,
  Key,
  Shield,
  AlertCircle,
  CheckCircle,
  GripVertical,
  Copy,
  MoreVertical,
} from 'lucide-react'
import { Button, Input, Badge } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/DropdownMenu'
import type { SchemaFormData, SchemaProperty, PropertyQualityRule, PropertyConstraint } from '@/types'

interface Props {
  formData: SchemaFormData
  updateFormData: (data: Partial<SchemaFormData>) => void
  onNext: () => void
  onBack: () => void
}

const LOGICAL_TYPES = [
  { value: 'string', label: 'String', description: 'Text data' },
  { value: 'integer', label: 'Integer', description: 'Whole numbers' },
  { value: 'number', label: 'Number', description: 'Decimal numbers' },
  { value: 'boolean', label: 'Boolean', description: 'True/false values' },
  { value: 'date', label: 'Date', description: 'Date values' },
  { value: 'datetime', label: 'DateTime', description: 'Date and time values' },
  { value: 'timestamp', label: 'Timestamp', description: 'Unix timestamp' },
  { value: 'array', label: 'Array', description: 'List of values' },
  { value: 'object', label: 'Object', description: 'Nested structure' },
  { value: 'binary', label: 'Binary', description: 'Binary data' },
]

const PII_TYPES = [
  { value: '', label: 'Not PII' },
  { value: 'email', label: 'Email Address' },
  { value: 'name', label: 'Personal Name' },
  { value: 'phone', label: 'Phone Number' },
  { value: 'address', label: 'Physical Address' },
  { value: 'ssn', label: 'SSN / National ID' },
  { value: 'dob', label: 'Date of Birth' },
  { value: 'financial', label: 'Financial Data' },
  { value: 'health', label: 'Health Data' },
  { value: 'biometric', label: 'Biometric Data' },
  { value: 'location', label: 'Location Data' },
  { value: 'other', label: 'Other PII' },
]

const SENSITIVITY_LEVELS = [
  { value: 'public', label: 'Public' },
  { value: 'internal', label: 'Internal' },
  { value: 'confidential', label: 'Confidential' },
  { value: 'restricted', label: 'Restricted' },
]

const CONSTRAINT_TYPES = [
  { value: 'minLength', label: 'Min Length', inputType: 'number' },
  { value: 'maxLength', label: 'Max Length', inputType: 'number' },
  { value: 'min', label: 'Min Value', inputType: 'number' },
  { value: 'max', label: 'Max Value', inputType: 'number' },
  { value: 'pattern', label: 'Regex Pattern', inputType: 'text' },
  { value: 'enum', label: 'Allowed Values', inputType: 'text' },
  { value: 'format', label: 'Format', inputType: 'select', options: ['email', 'uri', 'uuid', 'date', 'date-time', 'ipv4', 'ipv6'] },
]

const PROPERTY_QUALITY_METRICS = [
  { value: 'nullValues', label: 'Null Values', description: 'Check for null/missing values' },
  { value: 'missingValues', label: 'Missing Values', description: 'Check for empty or placeholder values' },
  { value: 'invalidValues', label: 'Invalid Values', description: 'Check for values not matching pattern' },
  { value: 'uniqueValues', label: 'Unique Values', description: 'Check value uniqueness' },
  { value: 'rangeCheck', label: 'Range Check', description: 'Validate values within range' },
  { value: 'formatCheck', label: 'Format Check', description: 'Validate value format' },
]

const generateId = () => `prop-${Math.random().toString(36).substring(2, 9)}`
const generateQualityId = () => `pqr-${Math.random().toString(36).substring(2, 9)}`

export function Step2Properties({ formData, updateFormData, onBack, onNext }: Props) {
  const [properties, setProperties] = useState<SchemaProperty[]>(formData.properties || [])
  const [expandedProperty, setExpandedProperty] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Calculate statistics
  const stats = useMemo(() => ({
    total: properties.length,
    primaryKeys: properties.filter(p => p.primaryKey).length,
    required: properties.filter(p => p.required).length,
    pii: properties.filter(p => p.customProperties?.privacy?.is_pii).length,
    withQuality: properties.filter(p => p.quality && p.quality.length > 0).length,
  }), [properties])

  const syncToFormData = (newProps: SchemaProperty[]) => {
    setProperties(newProps)
    updateFormData({ properties: newProps })
  }

  const addProperty = () => {
    const newProp: SchemaProperty = {
      id: generateId(),
      name: '',
      logicalType: 'string',
      physicalType: '',
      description: '',
      primaryKey: false,
      required: false,
      nullable: true,
      unique: false,
      customProperties: {
        constraints: [],
        privacy: { is_pii: false },
      },
      quality: [],
    }
    const newProps = [...properties, newProp]
    syncToFormData(newProps)
    setExpandedProperty(newProp.id!)
  }

  const duplicateProperty = (id: string) => {
    const original = properties.find(p => p.id === id)
    if (!original) return

    const newProp: SchemaProperty = {
      ...JSON.parse(JSON.stringify(original)),
      id: generateId(),
      name: `${original.name}_copy`,
    }
    const index = properties.findIndex(p => p.id === id)
    const newProps = [...properties.slice(0, index + 1), newProp, ...properties.slice(index + 1)]
    syncToFormData(newProps)
    setExpandedProperty(newProp.id!)
  }

  const removeProperty = (id: string) => {
    const newProps = properties.filter(p => p.id !== id)
    syncToFormData(newProps)
    if (expandedProperty === id) {
      setExpandedProperty(null)
    }
  }

  const updateProperty = (id: string, updates: Partial<SchemaProperty>) => {
    const newProps = properties.map(p => p.id === id ? { ...p, ...updates } : p)
    syncToFormData(newProps)
  }

  const addConstraint = (propId: string) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newConstraint: PropertyConstraint = {
      type: 'minLength',
      value: '',
    }
    const newConstraints = [...(prop.customProperties?.constraints || []), newConstraint]
    updateProperty(propId, {
      customProperties: {
        ...prop.customProperties,
        constraints: newConstraints,
      }
    })
  }

  const updateConstraint = (propId: string, index: number, updates: Partial<PropertyConstraint>) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newConstraints = (prop.customProperties?.constraints || []).map((c, i) =>
      i === index ? { ...c, ...updates } : c
    )
    updateProperty(propId, {
      customProperties: {
        ...prop.customProperties,
        constraints: newConstraints,
      }
    })
  }

  const removeConstraint = (propId: string, index: number) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newConstraints = (prop.customProperties?.constraints || []).filter((_, i) => i !== index)
    updateProperty(propId, {
      customProperties: {
        ...prop.customProperties,
        constraints: newConstraints,
      }
    })
  }

  const addQualityRule = (propId: string) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newRule: PropertyQualityRule = {
      id: generateQualityId(),
      name: '',
      type: 'library',
      metric: 'nullValues',
      mustBe: 0,
    }
    const newRules = [...(prop.quality || []), newRule]
    updateProperty(propId, { quality: newRules })
  }

  const updateQualityRule = (propId: string, ruleId: string, updates: Partial<PropertyQualityRule>) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newRules = (prop.quality || []).map(r => r.id === ruleId ? { ...r, ...updates } : r)
    updateProperty(propId, { quality: newRules })
  }

  const removeQualityRule = (propId: string, ruleId: string) => {
    const prop = properties.find(p => p.id === propId)
    if (!prop) return

    const newRules = (prop.quality || []).filter(r => r.id !== ruleId)
    updateProperty(propId, { quality: newRules })
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (properties.length === 0) {
      newErrors.properties = 'At least one property is required'
    }

    properties.forEach((prop) => {
      if (!prop.name || prop.name.length < 1) {
        newErrors[`${prop.id}_name`] = 'Property name is required'
      }
      if (!/^[a-z][a-z0-9_]*$/.test(prop.name || '')) {
        newErrors[`${prop.id}_name`] = 'Must be lowercase, start with a letter'
      }
    })

    // Check for duplicate names
    const names = properties.map(p => p.name)
    const duplicates = names.filter((name, index) => names.indexOf(name) !== index)
    if (duplicates.length > 0) {
      newErrors.duplicates = `Duplicate property names: ${duplicates.join(', ')}`
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validate()) {
      onNext()
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Define Properties</h2>
        <p className="text-sm text-text-secondary">
          Add properties (fields/columns) to your schema. For each property, define its type, constraints, and quality rules.
        </p>
      </div>

      {/* Statistics */}
      <div className="flex gap-4 p-4 bg-bg-secondary rounded-lg">
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{stats.total}</p>
          <p className="text-xs text-text-tertiary">Properties</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-warning-text">{stats.primaryKeys}</p>
          <p className="text-xs text-text-tertiary">Primary Keys</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{stats.required}</p>
          <p className="text-xs text-text-tertiary">Required</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-error-text">{stats.pii}</p>
          <p className="text-xs text-text-tertiary">PII Fields</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-success-text">{stats.withQuality}</p>
          <p className="text-xs text-text-tertiary">With Quality Rules</p>
        </div>
      </div>

      {/* Error Messages */}
      {(errors.properties || errors.duplicates) && (
        <div className="p-3 bg-error-bg border border-error-border rounded-lg">
          <p className="text-sm text-error-text">{errors.properties || errors.duplicates}</p>
        </div>
      )}

      {/* Properties List */}
      <div className="space-y-3">
        {properties.map((prop, index) => {
          const isExpanded = expandedProperty === prop.id
          const hasPii = prop.customProperties?.privacy?.is_pii
          const hasQuality = prop.quality && prop.quality.length > 0
          const hasConstraints = prop.customProperties?.constraints && prop.customProperties.constraints.length > 0

          return (
            <div
              key={prop.id}
              className="border border-border-default rounded-lg overflow-hidden"
            >
              {/* Property Header */}
              <div
                className="flex items-center gap-3 p-4 bg-bg-secondary cursor-pointer hover:bg-bg-tertiary transition-colors"
                onClick={() => setExpandedProperty(isExpanded ? null : prop.id!)}
              >
                <GripVertical className="h-4 w-4 text-text-tertiary" />

                <span className="text-sm text-text-tertiary w-6">{index + 1}.</span>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-text-primary truncate">
                      {prop.name || '(unnamed)'}
                    </span>
                    {prop.primaryKey && (
                      <Key className="h-4 w-4 text-warning-text" title="Primary Key" />
                    )}
                    {hasPii && (
                      <Shield className="h-4 w-4 text-error-text" title="PII" />
                    )}
                  </div>
                  <div className="text-xs text-text-tertiary">
                    {prop.logicalType}
                    {prop.physicalType && ` · ${prop.physicalType}`}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {prop.required && <Badge variant="secondary" size="sm">Required</Badge>}
                  {prop.unique && <Badge variant="outline" size="sm">Unique</Badge>}
                  {hasConstraints && (
                    <Badge variant="outline" size="sm">
                      {prop.customProperties?.constraints?.length} constraints
                    </Badge>
                  )}
                  {hasQuality && (
                    <Badge variant="success" size="sm">
                      {prop.quality?.length} rules
                    </Badge>
                  )}
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => duplicateProperty(prop.id!)}>
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-error-text"
                      onClick={() => removeProperty(prop.id!)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-text-tertiary" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-text-tertiary" />
                )}
              </div>

              {/* Property Details (Expanded) */}
              {isExpanded && (
                <div className="p-4 space-y-6 border-t border-border-default">
                  {/* Basic Info */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <FormField label="Property Name" required error={errors[`${prop.id}_name`]}>
                      <Input
                        placeholder="e.g., customer_id"
                        value={prop.name}
                        onChange={(e) => updateProperty(prop.id!, {
                          name: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_')
                        })}
                      />
                    </FormField>

                    <FormField label="Logical Type" required>
                      <select
                        value={prop.logicalType}
                        onChange={(e) => updateProperty(prop.id!, { logicalType: e.target.value })}
                        className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary"
                      >
                        {LOGICAL_TYPES.map((t) => (
                          <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                      </select>
                    </FormField>

                    <FormField label="Physical Type">
                      <Input
                        placeholder="e.g., VARCHAR(50)"
                        value={prop.physicalType || ''}
                        onChange={(e) => updateProperty(prop.id!, { physicalType: e.target.value })}
                      />
                    </FormField>

                    <FormField label="Business Name">
                      <Input
                        placeholder="e.g., Customer ID"
                        value={prop.businessName || ''}
                        onChange={(e) => updateProperty(prop.id!, { businessName: e.target.value })}
                      />
                    </FormField>
                  </div>

                  <FormField label="Description">
                    <Input
                      placeholder="Describe this property..."
                      value={prop.description || ''}
                      onChange={(e) => updateProperty(prop.id!, { description: e.target.value })}
                    />
                  </FormField>

                  {/* Flags */}
                  <div className="flex flex-wrap gap-4">
                    {[
                      { key: 'primaryKey', label: 'Primary Key' },
                      { key: 'required', label: 'Required' },
                      { key: 'unique', label: 'Unique' },
                      { key: 'nullable', label: 'Nullable' },
                      { key: 'partitioned', label: 'Partitioned' },
                      { key: 'criticalDataElement', label: 'Critical Data Element' },
                    ].map(({ key, label }) => (
                      <label key={key} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={prop[key as keyof SchemaProperty] as boolean || false}
                          onChange={(e) => {
                            const updates: Partial<SchemaProperty> = { [key]: e.target.checked }
                            // If marking as required, set nullable to false
                            if (key === 'required' && e.target.checked) {
                              updates.nullable = false
                            }
                            // If marking as nullable, set required to false
                            if (key === 'nullable' && e.target.checked) {
                              updates.required = false
                            }
                            updateProperty(prop.id!, updates)
                          }}
                          className="rounded"
                        />
                        <span className="text-sm text-text-secondary">{label}</span>
                      </label>
                    ))}
                  </div>

                  {/* Privacy / PII Settings */}
                  <div className="p-4 bg-bg-secondary rounded-lg">
                    <h4 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Privacy Classification
                    </h4>
                    <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs text-text-secondary mb-1 block">PII Type</label>
                        <select
                          value={prop.customProperties?.privacy?.pii_type || ''}
                          onChange={(e) => updateProperty(prop.id!, {
                            customProperties: {
                              ...prop.customProperties,
                              privacy: {
                                ...prop.customProperties?.privacy,
                                is_pii: !!e.target.value,
                                pii_type: e.target.value || undefined,
                              }
                            }
                          })}
                          className="h-9 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary"
                        >
                          {PII_TYPES.map((t) => (
                            <option key={t.value} value={t.value}>{t.label}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="text-xs text-text-secondary mb-1 block">Sensitivity Level</label>
                        <select
                          value={prop.customProperties?.privacy?.sensitivity || 'internal'}
                          onChange={(e) => updateProperty(prop.id!, {
                            customProperties: {
                              ...prop.customProperties,
                              privacy: {
                                ...prop.customProperties?.privacy,
                                sensitivity: e.target.value as any,
                              }
                            }
                          })}
                          className="h-9 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary"
                        >
                          {SENSITIVITY_LEVELS.map((l) => (
                            <option key={l.value} value={l.value}>{l.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Constraints */}
                  <div className="p-4 bg-bg-secondary rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-text-primary">Constraints</h4>
                      <Button variant="ghost" size="sm" onClick={() => addConstraint(prop.id!)}>
                        <Plus className="h-4 w-4 mr-1" />
                        Add Constraint
                      </Button>
                    </div>

                    {(!prop.customProperties?.constraints || prop.customProperties.constraints.length === 0) ? (
                      <p className="text-sm text-text-tertiary">No constraints defined</p>
                    ) : (
                      <div className="space-y-2">
                        {prop.customProperties.constraints.map((constraint, idx) => {
                          const constraintType = CONSTRAINT_TYPES.find(c => c.value === constraint.type)
                          return (
                            <div key={idx} className="flex items-center gap-2">
                              <select
                                value={constraint.type}
                                onChange={(e) => updateConstraint(prop.id!, idx, { type: e.target.value as any })}
                                className="h-9 w-36 rounded-md border border-border-default bg-bg-primary px-2 text-sm text-text-primary"
                              >
                                {CONSTRAINT_TYPES.map((c) => (
                                  <option key={c.value} value={c.value}>{c.label}</option>
                                ))}
                              </select>

                              {constraintType?.inputType === 'select' ? (
                                <select
                                  value={constraint.value as string}
                                  onChange={(e) => updateConstraint(prop.id!, idx, { value: e.target.value })}
                                  className="h-9 flex-1 rounded-md border border-border-default bg-bg-primary px-2 text-sm text-text-primary"
                                >
                                  <option value="">Select format...</option>
                                  {constraintType.options?.map((opt) => (
                                    <option key={opt} value={opt}>{opt}</option>
                                  ))}
                                </select>
                              ) : (
                                <Input
                                  type={constraintType?.inputType || 'text'}
                                  placeholder={constraint.type === 'enum' ? 'value1, value2, value3' : 'Value'}
                                  value={Array.isArray(constraint.value) ? constraint.value.join(', ') : constraint.value}
                                  onChange={(e) => updateConstraint(prop.id!, idx, {
                                    value: constraint.type === 'enum'
                                      ? e.target.value.split(',').map(s => s.trim())
                                      : constraintType?.inputType === 'number'
                                        ? parseFloat(e.target.value) || 0
                                        : e.target.value
                                  })}
                                  className="h-9 flex-1"
                                />
                              )}

                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeConstraint(prop.id!, idx)}
                                className="text-error-text hover:bg-error-bg"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>

                  {/* Property-Level Quality Rules */}
                  <div className="p-4 bg-bg-secondary rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-text-primary flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-success-text" />
                        Property Quality Rules
                      </h4>
                      <Button variant="ghost" size="sm" onClick={() => addQualityRule(prop.id!)}>
                        <Plus className="h-4 w-4 mr-1" />
                        Add Quality Rule
                      </Button>
                    </div>

                    {(!prop.quality || prop.quality.length === 0) ? (
                      <p className="text-sm text-text-tertiary">No quality rules defined for this property</p>
                    ) : (
                      <div className="space-y-3">
                        {prop.quality.map((rule) => (
                          <div key={rule.id} className="p-3 bg-bg-primary rounded border border-border-default">
                            <div className="flex items-center gap-2 mb-2">
                              <Input
                                placeholder="Rule name"
                                value={rule.name}
                                onChange={(e) => updateQualityRule(prop.id!, rule.id!, { name: e.target.value })}
                                className="flex-1 h-8"
                              />
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeQualityRule(prop.id!, rule.id!)}
                                className="text-error-text hover:bg-error-bg"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>

                            <div className="grid grid-cols-3 gap-2">
                              <select
                                value={rule.metric}
                                onChange={(e) => updateQualityRule(prop.id!, rule.id!, { metric: e.target.value })}
                                className="h-8 w-full rounded-md border border-border-default bg-bg-primary px-2 text-xs text-text-primary"
                              >
                                {PROPERTY_QUALITY_METRICS.map((m) => (
                                  <option key={m.value} value={m.value}>{m.label}</option>
                                ))}
                              </select>

                              <div className="flex gap-1">
                                <select
                                  value={rule.mustBe !== undefined ? 'mustBe' : rule.mustBeLessThan !== undefined ? 'mustBeLessThan' : 'mustBeGreaterThan'}
                                  onChange={(e) => {
                                    const val = rule.mustBe ?? rule.mustBeLessThan ?? rule.mustBeGreaterThan ?? 0
                                    const updates: Partial<PropertyQualityRule> = {
                                      mustBe: undefined,
                                      mustBeLessThan: undefined,
                                      mustBeGreaterThan: undefined,
                                    }
                                    updates[e.target.value as keyof typeof updates] = val
                                    updateQualityRule(prop.id!, rule.id!, updates)
                                  }}
                                  className="h-8 w-20 rounded-md border border-border-default bg-bg-primary px-1 text-xs text-text-primary"
                                >
                                  <option value="mustBe">=</option>
                                  <option value="mustBeLessThan">&lt;</option>
                                  <option value="mustBeGreaterThan">&gt;</option>
                                </select>
                                <Input
                                  type="number"
                                  value={rule.mustBe ?? rule.mustBeLessThan ?? rule.mustBeGreaterThan ?? ''}
                                  onChange={(e) => {
                                    const key = rule.mustBe !== undefined ? 'mustBe' : rule.mustBeLessThan !== undefined ? 'mustBeLessThan' : 'mustBeGreaterThan'
                                    updateQualityRule(prop.id!, rule.id!, { [key]: parseFloat(e.target.value) || 0 })
                                  }}
                                  className="h-8 flex-1"
                                />
                              </div>

                              {rule.metric === 'invalidValues' && (
                                <Input
                                  placeholder="Regex pattern"
                                  value={rule.pattern || ''}
                                  onChange={(e) => updateQualityRule(prop.id!, rule.id!, { pattern: e.target.value })}
                                  className="h-8"
                                />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Add Property Button */}
      <Button variant="secondary" onClick={addProperty} className="w-full">
        <Plus className="h-4 w-4 mr-2" />
        Add Property
      </Button>

      {/* Empty State */}
      {properties.length === 0 && (
        <div className="p-8 border-2 border-dashed border-border-default rounded-lg text-center">
          <AlertCircle className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
          <p className="text-text-secondary mb-2">No properties defined yet</p>
          <p className="text-sm text-text-tertiary mb-4">
            Add properties to define the structure of your schema. Each property represents a field or column.
          </p>
          <Button onClick={addProperty}>
            <Plus className="h-4 w-4 mr-2" />
            Add First Property
          </Button>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-4 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={handleNext}>
          Next: Ownership
        </Button>
      </div>
    </div>
  )
}
