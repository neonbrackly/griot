'use client'

import { Button, Badge } from '@/components/ui'
import { Card } from '@/components/layout'
import { CheckCircle, AlertCircle, AlertTriangle, Loader2 } from 'lucide-react'
import type { ContractFormData } from '@/app/studio/contracts/new/wizard/page'

// Validation result type from the API
interface ValidationResult {
  is_valid: boolean
  has_errors: boolean
  has_warnings: boolean
  error_count: number
  warning_count: number
  issues: Array<{
    code: string
    field: string | null
    message: string
    severity: 'error' | 'warning'
    suggestion: string | null
  }>
}

interface Props {
  formData: ContractFormData
  onSubmit: () => void
  onBack: () => void
  isSubmitting: boolean
  isValidating?: boolean
  validationResult?: ValidationResult | null
}

export function Step7Review({
  formData,
  onSubmit,
  onBack,
  isSubmitting,
  isValidating = false,
  validationResult = null,
}: Props) {
  // Required validations (must pass to create)
  const requiredValidations = [
    { label: 'Contract name provided (min 3 chars)', valid: !!formData.name && formData.name.length >= 3 },
    { label: 'Description provided (min 10 chars)', valid: !!formData.description && formData.description.length >= 10 },
    { label: 'Domain selected', valid: !!formData.domain },
    { label: 'At least one schema table defined', valid: !!(formData.tables && formData.tables.length > 0) },
    { label: 'SLA configured', valid: !!formData.sla },
  ]

  // Check for primary key in tables
  const hasPrimaryKey = formData.tables?.some((table) =>
    table.fields?.some((field: { primaryKey?: boolean }) => field.primaryKey === true)
  ) ?? false

  // Add primary key check to required validations
  const allRequiredValidations = [
    ...requiredValidations,
    { label: 'At least one field marked as primary key', valid: hasPrimaryKey },
  ]

  // Optional validations (warnings, not blockers)
  const optionalValidations = [
    { label: 'Owner team assigned', valid: !!formData.ownerTeamId },
    { label: 'Tags added', valid: !!(formData.tags && formData.tags.length > 0) },
    { label: 'Quality rules defined', valid: !!(formData.qualityRules && formData.qualityRules.length > 0) },
  ]

  const allRequiredValid = allRequiredValidations.every((v) => v.valid)
  const isWorking = isSubmitting || isValidating

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-2">Review & Create</h2>
        <p className="text-sm text-text-secondary">
          Review your contract before creating. The contract will be validated before creation.
        </p>
      </div>

      {/* Required Validation Checklist */}
      <Card className="p-4">
        <h3 className="font-medium text-text-primary mb-3">Required Fields</h3>
        <div className="space-y-2">
          {allRequiredValidations.map((validation) => (
            <div key={validation.label} className="flex items-center gap-2">
              {validation.valid ? (
                <CheckCircle className="h-4 w-4 text-success-text" />
              ) : (
                <AlertCircle className="h-4 w-4 text-error-text" />
              )}
              <span
                className={`text-sm ${
                  validation.valid ? 'text-text-primary' : 'text-error-text'
                }`}
              >
                {validation.label}
              </span>
            </div>
          ))}
        </div>

        {/* Optional fields */}
        <h3 className="font-medium text-text-primary mb-3 mt-4">Optional (Recommended)</h3>
        <div className="space-y-2">
          {optionalValidations.map((validation) => (
            <div key={validation.label} className="flex items-center gap-2">
              {validation.valid ? (
                <CheckCircle className="h-4 w-4 text-success-text" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-warning-text" />
              )}
              <span
                className={`text-sm ${
                  validation.valid ? 'text-text-primary' : 'text-text-tertiary'
                }`}
              >
                {validation.label}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* API Validation Results */}
      {validationResult && !validationResult.is_valid && (
        <Card className="p-4 border-error-border bg-error-bg/10">
          <h3 className="font-medium text-error-text mb-3 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            API Validation Failed
          </h3>
          <p className="text-sm text-text-secondary mb-3">
            {validationResult.error_count} error{validationResult.error_count !== 1 ? 's' : ''}
            {validationResult.warning_count > 0 && (
              <>, {validationResult.warning_count} warning{validationResult.warning_count !== 1 ? 's' : ''}</>
            )}
          </p>
          <ul className="space-y-2 max-h-48 overflow-y-auto">
            {validationResult.issues.map((issue, index) => (
              <li
                key={index}
                className={`text-sm flex items-start gap-2 p-2 rounded ${
                  issue.severity === 'error'
                    ? 'bg-error-bg/20 text-error-text'
                    : 'bg-warning-bg/20 text-warning-text'
                }`}
              >
                {issue.severity === 'error' ? (
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                )}
                <div>
                  <span className="font-medium">{issue.code}</span>
                  {issue.field && <span className="text-text-tertiary"> ({issue.field})</span>}
                  <p className="text-xs mt-0.5">{issue.message}</p>
                  {issue.suggestion && (
                    <p className="text-xs mt-1 italic text-text-tertiary">
                      Tip: {issue.suggestion}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Contract Summary */}
      <Card className="p-4">
        <h3 className="font-medium text-text-primary mb-3">Contract Summary</h3>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-text-tertiary">Name</p>
            <p className="text-sm font-medium text-text-primary">{formData.name || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-text-tertiary">Description</p>
            <p className="text-sm text-text-secondary">{formData.description || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-text-tertiary mb-1">Domain & Status</p>
            <div className="flex gap-2">
              {formData.domain && <Badge variant="secondary" size="sm">{formData.domain}</Badge>}
              {formData.status && <Badge variant="secondary" size="sm">{formData.status}</Badge>}
            </div>
          </div>
          <div>
            <p className="text-xs text-text-tertiary">SLA</p>
            <p className="text-sm text-text-secondary">
              Freshness: {formData.sla?.freshnessHours || '-'}h • Availability: {formData.sla?.availabilityPercent || '-'}%
            </p>
          </div>
          <div>
            <p className="text-xs text-text-tertiary">Schema Tables</p>
            <p className="text-sm text-text-secondary">
              {formData.tables?.length || 0} table{formData.tables?.length !== 1 ? 's' : ''} defined
              {formData.tables?.map((t) => t.fields?.length || 0).reduce((a, b) => a + b, 0) || 0} total fields
            </p>
          </div>
          {formData.tags && formData.tags.length > 0 && (
            <div>
              <p className="text-xs text-text-tertiary mb-1">Tags</p>
              <div className="flex flex-wrap gap-1">
                {formData.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" size="xs">{tag}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Validation error message */}
      {!allRequiredValid && (
        <Card className="p-4 border-error-border bg-error-bg/10">
          <div className="flex items-center gap-2 text-error-text">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Please complete all required fields before creating the contract.</span>
          </div>
        </Card>
      )}

      <div className="flex justify-between">
        <Button variant="secondary" onClick={onBack} disabled={isWorking}>
          Back
        </Button>
        <div className="flex gap-2">
          <Button
            onClick={onSubmit}
            disabled={!allRequiredValid || isWorking}
          >
            {isValidating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Validating...
              </>
            ) : isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Creating...
              </>
            ) : (
              'Create Contract'
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
