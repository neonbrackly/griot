'use client'

import { useState, useMemo } from 'react'
import { Plus, Trash2, CheckCircle, AlertCircle, AlertTriangle, Code, Info } from 'lucide-react'
import { Button, Input, Badge } from '@/components/ui'
import { FormField } from '@/components/forms/FormField'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'
import type { QualityRule } from '@/types'

interface Props {
  formData: ContractFormData
  updateFormData: (data: Partial<ContractFormData>) => void
  onNext: () => void
  onBack: () => void
}

type RuleType = 'completeness' | 'uniqueness' | 'validity' | 'custom'

interface RuleTemplate {
  type: RuleType
  label: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  defaultThreshold?: number
}

const RULE_TEMPLATES: RuleTemplate[] = [
  {
    type: 'completeness',
    label: 'Completeness',
    description: 'Check that fields are not null/empty',
    icon: CheckCircle,
    color: 'bg-success-bg text-success-text',
    defaultThreshold: 99,
  },
  {
    type: 'uniqueness',
    label: 'Uniqueness',
    description: 'Check that values are unique',
    icon: AlertTriangle,
    color: 'bg-warning-bg text-warning-text',
    defaultThreshold: 100,
  },
  {
    type: 'validity',
    label: 'Validity',
    description: 'Check values against format/range',
    icon: Info,
    color: 'bg-info-bg text-info-text',
    defaultThreshold: 95,
  },
  {
    type: 'custom',
    label: 'Custom SQL',
    description: 'Write a custom validation expression',
    icon: Code,
    color: 'bg-primary-bg text-primary-text',
  },
]

const generateId = () => Math.random().toString(36).substring(2, 9)

export function Step4Quality({ formData, updateFormData, onNext, onBack }: Props) {
  const [rules, setRules] = useState<(QualityRule & { tempId: string })[]>(() => {
    if (formData.qualityRules && formData.qualityRules.length > 0) {
      return formData.qualityRules.map((r) => ({ ...r, tempId: r.id || generateId() }))
    }
    return []
  })

  // Get all tables and fields from schema
  const tableOptions = useMemo(() => {
    if (!formData.tables) return []
    return formData.tables.map((t: any) => ({
      name: t.name,
      fields: t.fields?.map((f: any) => f.name) || [],
    }))
  }, [formData.tables])

  const syncToFormData = (newRules: (QualityRule & { tempId: string })[]) => {
    const cleanedRules = newRules.map(({ tempId, ...rule }) => ({
      ...rule,
      id: rule.id || tempId,
    }))
    updateFormData({ qualityRules: cleanedRules })
  }

  const addRule = (type: RuleType) => {
    const template = RULE_TEMPLATES.find((t) => t.type === type)
    const newRule: QualityRule & { tempId: string } = {
      tempId: generateId(),
      id: generateId(),
      name: '',
      type,
      enabled: true,
      threshold: template?.defaultThreshold,
    }
    const newRules = [...rules, newRule]
    setRules(newRules)
    syncToFormData(newRules)
  }

  const removeRule = (tempId: string) => {
    const newRules = rules.filter((r) => r.tempId !== tempId)
    setRules(newRules)
    syncToFormData(newRules)
  }

  const updateRule = (tempId: string, updates: Partial<QualityRule>) => {
    const newRules = rules.map((r) =>
      r.tempId === tempId ? { ...r, ...updates } : r
    )
    setRules(newRules)
    syncToFormData(newRules)
  }

  const toggleRuleEnabled = (tempId: string) => {
    const rule = rules.find((r) => r.tempId === tempId)
    if (rule) {
      updateRule(tempId, { enabled: !rule.enabled })
    }
  }

  const getRuleTemplate = (type: RuleType) => RULE_TEMPLATES.find((t) => t.type === type)

  const enabledCount = rules.filter((r) => r.enabled).length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Quality Rules</h2>
        <p className="text-sm text-text-secondary">
          Define validation rules to ensure data quality. Rules are executed during contract runs.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="flex gap-4 p-4 bg-bg-secondary rounded-lg">
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">{rules.length}</p>
          <p className="text-xs text-text-tertiary">Total Rules</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-success-text">{enabledCount}</p>
          <p className="text-xs text-text-tertiary">Enabled</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-tertiary">{rules.length - enabledCount}</p>
          <p className="text-xs text-text-tertiary">Disabled</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-semibold text-text-primary">
            {rules.filter((r) => r.type === 'custom').length}
          </p>
          <p className="text-xs text-text-tertiary">Custom</p>
        </div>
      </div>

      {/* Add Rule Buttons */}
      <div>
        <p className="text-sm font-medium text-text-secondary mb-3">Add a new rule:</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {RULE_TEMPLATES.map((template) => {
            const Icon = template.icon
            return (
              <button
                key={template.type}
                type="button"
                onClick={() => addRule(template.type)}
                className="flex flex-col items-center gap-2 p-4 border border-border-default rounded-lg hover:border-primary-border hover:bg-bg-secondary transition-colors"
              >
                <div className={`p-2 rounded-lg ${template.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-sm font-medium text-text-primary">{template.label}</span>
                <span className="text-xs text-text-tertiary text-center">{template.description}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Rules List */}
      {rules.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-text-secondary">Configured Rules</h3>
          {rules.map((rule) => {
            const template = getRuleTemplate(rule.type)
            const Icon = template?.icon || AlertCircle
            return (
              <div
                key={rule.tempId}
                className={`border rounded-lg overflow-hidden ${
                  rule.enabled ? 'border-border-default' : 'border-border-default/50 opacity-60'
                }`}
              >
                {/* Rule Header */}
                <div className="flex items-center gap-3 p-4 bg-bg-secondary">
                  <div className={`p-2 rounded-lg ${template?.color || 'bg-bg-primary text-text-secondary'}`}>
                    <Icon className="h-4 w-4" />
                  </div>

                  <div className="flex-1">
                    <Input
                      placeholder={`${template?.label} rule name`}
                      value={rule.name}
                      onChange={(e) => updateRule(rule.tempId, { name: e.target.value })}
                      className="font-medium"
                    />
                  </div>

                  <Badge variant={rule.enabled ? 'success' : 'secondary'} size="sm">
                    {rule.enabled ? 'Enabled' : 'Disabled'}
                  </Badge>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleRuleEnabled(rule.tempId)}
                  >
                    {rule.enabled ? 'Disable' : 'Enable'}
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeRule(rule.tempId)}
                    className="text-error-text hover:bg-error-bg"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {/* Rule Configuration */}
                <div className="p-4 space-y-4">
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Table Selection */}
                    <div>
                      <label className="text-sm font-medium text-text-secondary mb-1 block">
                        Apply to Table
                      </label>
                      <select
                        value={rule.table || ''}
                        onChange={(e) => {
                          updateRule(rule.tempId, { table: e.target.value || undefined, field: undefined })
                        }}
                        className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                      >
                        <option value="">All tables</option>
                        {tableOptions.map((table) => (
                          <option key={table.name} value={table.name}>{table.name}</option>
                        ))}
                      </select>
                    </div>

                    {/* Field Selection (if table is selected) */}
                    {rule.table && (
                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          Apply to Field
                        </label>
                        <select
                          value={rule.field || ''}
                          onChange={(e) => updateRule(rule.tempId, { field: e.target.value || undefined })}
                          className="h-10 w-full rounded-md border border-border-default bg-bg-primary px-3 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-primary-border"
                        >
                          <option value="">All fields</option>
                          {tableOptions
                            .find((t) => t.name === rule.table)
                            ?.fields.map((field: string) => (
                              <option key={field} value={field}>{field}</option>
                            ))}
                        </select>
                      </div>
                    )}

                    {/* Threshold (for non-custom rules) */}
                    {rule.type !== 'custom' && (
                      <div>
                        <label className="text-sm font-medium text-text-secondary mb-1 block">
                          Threshold (%)
                        </label>
                        <Input
                          type="number"
                          value={rule.threshold || ''}
                          onChange={(e) => updateRule(rule.tempId, { threshold: parseFloat(e.target.value) || undefined })}
                          min={0}
                          max={100}
                          placeholder="e.g., 99"
                        />
                      </div>
                    )}
                  </div>

                  {/* Custom SQL Expression */}
                  {rule.type === 'custom' && (
                    <div>
                      <label className="text-sm font-medium text-text-secondary mb-1 block">
                        SQL Expression
                      </label>
                      <textarea
                        value={rule.expression || ''}
                        onChange={(e) => updateRule(rule.tempId, { expression: e.target.value })}
                        placeholder="e.g., COUNT(*) WHERE status IS NOT NULL > 0"
                        className="w-full h-24 rounded-md border border-border-default bg-bg-primary px-3 py-2 text-sm text-text-primary font-mono placeholder:text-text-tertiary focus:outline-none focus:ring-1 focus:ring-primary-border"
                      />
                      <p className="text-xs text-text-tertiary mt-1">
                        Write a SQL expression that returns true for valid data.
                      </p>
                    </div>
                  )}

                  {/* Rule Type Description */}
                  <div className="p-3 bg-bg-secondary rounded-lg text-sm text-text-tertiary">
                    {rule.type === 'completeness' && (
                      <p>
                        <strong>Completeness check:</strong> Validates that the specified percentage of records have non-null values.
                        {rule.threshold && ` At least ${rule.threshold}% of values must be present.`}
                      </p>
                    )}
                    {rule.type === 'uniqueness' && (
                      <p>
                        <strong>Uniqueness check:</strong> Validates that values are unique across records.
                        {rule.threshold && ` At least ${rule.threshold}% of values must be unique.`}
                      </p>
                    )}
                    {rule.type === 'validity' && (
                      <p>
                        <strong>Validity check:</strong> Validates that values conform to expected format or range.
                        {rule.threshold && ` At least ${rule.threshold}% of values must be valid.`}
                      </p>
                    )}
                    {rule.type === 'custom' && (
                      <p>
                        <strong>Custom check:</strong> Runs your SQL expression to validate data.
                        The expression should return a boolean value indicating validity.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Empty State */}
      {rules.length === 0 && (
        <div className="p-8 border-2 border-dashed border-border-default rounded-lg text-center">
          <AlertCircle className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
          <p className="text-text-secondary mb-2">No quality rules defined yet</p>
          <p className="text-sm text-text-tertiary">
            Add rules above to validate data quality during contract runs.
          </p>
        </div>
      )}

      {/* Tips */}
      <div className="p-4 bg-bg-secondary rounded-lg">
        <h4 className="text-sm font-medium text-text-primary mb-2">Tips for Quality Rules</h4>
        <ul className="text-sm text-text-tertiary space-y-1">
          <li>• <strong>Completeness</strong> - Great for required fields that should never be null</li>
          <li>• <strong>Uniqueness</strong> - Use on primary keys and fields like email or user_id</li>
          <li>• <strong>Validity</strong> - Good for dates, enums, and fields with known formats</li>
          <li>• <strong>Custom</strong> - Write complex validation logic with SQL</li>
        </ul>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack}>Back</Button>
        <Button onClick={onNext}>
          Next: SLA
        </Button>
      </div>
    </div>
  )
}
