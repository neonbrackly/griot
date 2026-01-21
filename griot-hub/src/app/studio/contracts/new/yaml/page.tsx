'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FileCode, Upload, Check, AlertCircle, AlertTriangle, Save, Shield, Loader2 } from 'lucide-react'
import YAML from 'yaml'

import { PageContainer, Card } from '@/components/layout'
import { Button, Textarea } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { Skeleton } from '@/components/feedback'
import { toast } from '@/lib/hooks'
import { api, queryKeys } from '@/lib/api/client'

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

const DEFAULT_YAML = `# ODCS v3.3 Data Contract
# https://github.com/bitol-io/open-data-contract-standard

version: "3.3.0"
name: "customer_analytics"
status: "draft"
description: "Customer analytics contract for reporting"

dataset:
  - table: customers
    physicalName: ANALYTICS_DB.CUSTOMER.customers
    description: "Customer master data"

    fields:
      - column: customer_id
        logicalType: string
        physicalType: VARCHAR(50)
        required: true
        unique: true
        primaryKey: true
        description: "Unique customer identifier"

      - column: email
        logicalType: string
        physicalType: VARCHAR(255)
        required: true
        unique: true
        piiClassification: email
        description: "Customer email address"

      - column: created_at
        logicalType: timestamp
        physicalType: TIMESTAMP
        required: true
        description: "Account creation timestamp"

sla:
  freshnessHours: 24
  availabilityPercent: 99.5

tags:
  - analytics
  - customer

quality:
  - type: completeness
    field: email
    threshold: 99
    enabled: true

  - type: uniqueness
    field: email
    enabled: true
`

function YAMLContractPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const mode = searchParams.get('mode') || 'paste'

  const [yamlContent, setYamlContent] = useState(DEFAULT_YAML)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [hasBeenValidated, setHasBeenValidated] = useState(false)

  // Reset validation when content changes
  const handleContentChange = (newContent: string) => {
    setYamlContent(newContent)
    setHasBeenValidated(false)
    setValidationResult(null)
  }

  // File upload handler
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
      toast.error('Invalid file type', 'Please upload a .yaml or .yml file')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      handleContentChange(content)
      toast.success('File loaded', 'YAML file has been loaded successfully. Please validate before creating.')
    }
    reader.readAsText(file)
  }

  // Parse YAML string to JSON object
  const parseYamlToJson = (yamlString: string): Record<string, unknown> => {
    try {
      const parsed = YAML.parse(yamlString)
      return parsed || {}
    } catch (error) {
      console.error('YAML parse error:', error)
      throw new Error('Invalid YAML syntax')
    }
  }

  // Transform parsed YAML to ODCS contract format expected by the API
  const transformToODCSContract = (parsed: Record<string, unknown>): Record<string, unknown> => {
    // If already in ODCS format (has schema array), return with defaults
    if (Array.isArray(parsed.schema)) {
      return {
        apiVersion: parsed.apiVersion || 'v1.0.0',
        kind: parsed.kind || 'DataContract',
        id: parsed.id || `yaml-import-${Date.now().toString(36)}`,
        name: parsed.name,
        version: parsed.version || '1.0.0',
        status: parsed.status || 'draft',
        description: typeof parsed.description === 'object'
          ? parsed.description
          : parsed.description
            ? { logicalType: 'string', value: String(parsed.description) }
            : { logicalType: 'string' },
        schema: parsed.schema,
        ...(parsed.tags && { tags: parsed.tags }),
        ...(parsed.sla && { sla: parsed.sla }),
        ...(parsed.quality && { quality: parsed.quality }),
      }
    }

    // Transform ODCS v3.3 YAML format (dataset/fields) to API format (schema/properties)
    const dataset = parsed.dataset as Array<Record<string, unknown>> | undefined
    const schema = dataset?.map((table, index) => {
      const fields = table.fields as Array<Record<string, unknown>> | undefined
      return {
        name: table.table || table.name || `table_${index + 1}`,
        id: `schema-${Date.now().toString(36)}-${index}`,
        logicalType: 'object',
        description: table.description,
        physicalName: table.physicalName,
        properties: fields?.map((field) => ({
          name: field.column || field.name,
          logicalType: field.logicalType || 'string',
          physicalType: field.physicalType,
          description: field.description,
          nullable: field.required === true ? false : true,
          primary_key: field.primaryKey === true,
          unique: field.unique === true,
          ...(field.piiClassification && {
            customProperties: {
              privacy: {
                is_pii: true,
                sensitivity: field.piiClassification === 'ssn' || field.piiClassification === 'financial'
                  ? 'restricted'
                  : field.piiClassification === 'email' || field.piiClassification === 'phone'
                    ? 'confidential'
                    : 'internal',
              },
            },
          }),
        })) || [],
      }
    }) || []

    // Transform SLA if present
    const slaInput = parsed.sla as Record<string, unknown> | undefined
    const sla = slaInput ? {
      freshness: slaInput.freshnessHours ? `PT${slaInput.freshnessHours}H` : undefined,
      availability: slaInput.availabilityPercent,
      responseTime: slaInput.responseTimeMs,
    } : undefined

    // Transform quality rules if present
    const qualityInput = parsed.quality as Array<Record<string, unknown>> | undefined
    const quality = qualityInput?.map((rule) => ({
      type: rule.type,
      field: rule.field,
      table: rule.table,
      threshold: rule.threshold,
      enabled: rule.enabled,
      expression: rule.expression,
    }))

    return {
      apiVersion: parsed.apiVersion || 'v1.0.0',
      kind: parsed.kind || 'DataContract',
      id: parsed.id || `yaml-import-${Date.now().toString(36)}`,
      name: parsed.name,
      version: parsed.version || '1.0.0',
      status: parsed.status || 'draft',
      description: typeof parsed.description === 'object'
        ? parsed.description
        : parsed.description
          ? { logicalType: 'string', value: String(parsed.description) }
          : { logicalType: 'string' },
      schema,
      ...(parsed.tags && { tags: parsed.tags }),
      ...(sla && { sla }),
      ...(quality && { quality }),
    }
  }

  // Validation using the API endpoint
  const validateYAML = async () => {
    setIsValidating(true)

    try {
      // Parse YAML to JSON
      const parsed = parseYamlToJson(yamlContent)
      // Transform to ODCS format
      const payload = transformToODCSContract(parsed)

      // Call validation endpoint
      const result = await api.post<ValidationResult>('/contracts/validate', payload)
      setValidationResult(result)
      setHasBeenValidated(true)

      if (result.is_valid) {
        toast.success('Validation passed', 'Your contract is valid and ready to create')
      } else {
        toast.error(
          'Validation failed',
          `Found ${result.error_count} error${result.error_count !== 1 ? 's' : ''}${
            result.warning_count > 0 ? ` and ${result.warning_count} warning${result.warning_count !== 1 ? 's' : ''}` : ''
          }`
        )
      }
    } catch (error: unknown) {
      // Handle YAML parse errors or API errors
      const errorMessage = error instanceof Error
        ? error.message
        : (error as Record<string, unknown>)?.detail as string || 'Failed to validate contract'
      setValidationResult({
        is_valid: false,
        has_errors: true,
        has_warnings: false,
        error_count: 1,
        warning_count: 0,
        issues: [{
          code: 'PARSE_ERROR',
          field: null,
          message: errorMessage,
          severity: 'error',
          suggestion: 'Check your YAML syntax and try again',
        }],
      })
      setHasBeenValidated(true)
      toast.error('Validation failed', errorMessage)
    } finally {
      setIsValidating(false)
    }
  }

  // Create contract mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      // Parse YAML and transform to ODCS format
      const parsed = parseYamlToJson(yamlContent)
      const payload = transformToODCSContract(parsed)

      const response = await api.post('/contracts', payload)
      return response
    },
    onSuccess: (data: any) => {
      toast.success('Contract created', 'Your contract has been created successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${data.id}`)
    },
    onError: (error: any) => {
      const message = error?.message || error?.detail || 'Please check your YAML and try again'
      toast.error('Failed to create contract', message)
    },
  })

  // Can only create if validated and valid
  const canCreate = hasBeenValidated && validationResult?.is_valid === true

  const handleSave = () => {
    if (!canCreate) {
      toast.error('Please validate your contract first', 'Click the Validate button to check your YAML')
      return
    }
    createMutation.mutate()
  }

  return (
    <PageContainer>
      <BackLink href="/studio/contracts/new" label="Back to Method Selection" />

      <div className="mt-6 mb-6">
        <h1 className="text-2xl font-semibold text-text-primary">
          {mode === 'import' ? 'Import YAML Contract' : 'Create Contract from YAML'}
        </h1>
        <p className="mt-2 text-text-secondary">
          {mode === 'import'
            ? 'Upload a YAML file or paste your contract definition below'
            : 'Write or paste your ODCS v3.3 contract definition in YAML format'}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Editor */}
        <div className="lg:col-span-2 space-y-4">
          {mode === 'import' && (
            <Card className="p-6">
              <label htmlFor="file-upload" className="block">
                <div className="border-2 border-dashed border-border-default rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-bg-secondary transition-colors">
                  <Upload className="h-12 w-12 text-text-tertiary mx-auto mb-4" />
                  <p className="text-text-primary font-medium mb-1">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-text-secondary">YAML files (.yaml, .yml)</p>
                </div>
                <input
                  id="file-upload"
                  type="file"
                  accept=".yaml,.yml"
                  className="hidden"
                  onChange={handleFileUpload}
                />
              </label>
            </Card>
          )}

          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileCode className="h-5 w-5 text-text-secondary" />
                <span className="font-medium text-text-primary">YAML Editor</span>
              </div>
              <div className="flex items-center gap-2">
                {/* Prominent Validate Button */}
                <Button
                  variant={hasBeenValidated && validationResult?.is_valid ? 'secondary' : 'primary'}
                  size="sm"
                  onClick={validateYAML}
                  disabled={isValidating}
                  className="gap-2"
                >
                  {isValidating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Validating...
                    </>
                  ) : hasBeenValidated && validationResult?.is_valid ? (
                    <>
                      <Check className="h-4 w-4" />
                      Valid
                    </>
                  ) : (
                    <>
                      <Shield className="h-4 w-4" />
                      Validate Contract
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Validation required notice */}
            {!hasBeenValidated && (
              <div className="mb-3 p-3 bg-info-bg/20 border border-info-border rounded-md">
                <div className="flex items-center gap-2 text-sm text-info-text">
                  <Shield className="h-4 w-4" />
                  <span>Click <strong>Validate Contract</strong> to check your YAML before creating</span>
                </div>
              </div>
            )}

            <Textarea
              value={yamlContent}
              onChange={(e) => handleContentChange(e.target.value)}
              className="font-mono text-sm min-h-[500px] resize-y bg-bg-primary"
              placeholder="Paste your YAML contract here..."
            />

            <div className="flex items-center justify-between mt-4">
              <p className="text-xs text-text-tertiary">
                {yamlContent.split('\n').length} lines
                {hasBeenValidated && (
                  <span className={validationResult?.is_valid ? 'text-success-text ml-2' : 'text-error-text ml-2'}>
                    • {validationResult?.is_valid ? 'Valid' : 'Invalid'}
                  </span>
                )}
              </p>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => router.push('/studio/contracts/new')}>
                  Cancel
                </Button>
                <Button
                  onClick={handleSave}
                  disabled={!canCreate || createMutation.isPending}
                  title={!canCreate ? 'Validate your contract first' : 'Create contract'}
                >
                  <Save className="h-4 w-4" />
                  {createMutation.isPending ? 'Creating...' : 'Create Contract'}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar - Validation & Help */}
        <div className="space-y-4">
          {/* Validation Status */}
          <Card className="p-4">
            <h3 className="font-medium text-text-primary mb-3 flex items-center gap-2">
              {!hasBeenValidated ? (
                <>
                  <Shield className="h-5 w-5 text-text-tertiary" />
                  Validation Required
                </>
              ) : validationResult?.is_valid ? (
                <>
                  <Check className="h-5 w-5 text-success-text" />
                  Validation Passed
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-error-text" />
                  Validation Failed
                </>
              )}
            </h3>

            {!hasBeenValidated ? (
              <p className="text-sm text-text-secondary">
                Click &quot;Validate Contract&quot; to check your YAML before creating.
              </p>
            ) : validationResult?.is_valid ? (
              <p className="text-sm text-success-text">
                Your contract is valid and ready to create.
              </p>
            ) : (
              <div className="space-y-3">
                {/* Error count summary */}
                <p className="text-sm text-text-secondary">
                  {validationResult?.error_count || 0} error{validationResult?.error_count !== 1 ? 's' : ''}
                  {(validationResult?.warning_count || 0) > 0 && (
                    <>, {validationResult?.warning_count} warning{validationResult?.warning_count !== 1 ? 's' : ''}</>
                  )}
                </p>

                {/* Issues list */}
                <ul className="space-y-2 max-h-60 overflow-y-auto">
                  {validationResult?.issues.map((issue, index) => (
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
              </div>
            )}
          </Card>

          {/* Help */}
          <Card className="p-4">
            <h3 className="font-medium text-text-primary mb-3">Quick Reference</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="font-medium text-text-secondary">Required Fields:</p>
                <ul className="mt-1 text-text-tertiary space-y-1">
                  <li>• version</li>
                  <li>• name</li>
                  <li>• dataset (with tables)</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-text-secondary">Optional Fields:</p>
                <ul className="mt-1 text-text-tertiary space-y-1">
                  <li>• description</li>
                  <li>• status</li>
                  <li>• sla</li>
                  <li>• quality rules</li>
                  <li>• tags</li>
                </ul>
              </div>
            </div>
          </Card>

          {/* Documentation Link */}
          <Card className="p-4 bg-info-bg/20 border-info-border">
            <p className="text-sm text-text-secondary">
              📖 Need help? Check out the{' '}
              <a
                href="https://github.com/bitol-io/open-data-contract-standard"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline"
              >
                ODCS v3.3 documentation
              </a>
            </p>
          </Card>
        </div>
      </div>
    </PageContainer>
  )
}

export default function YAMLContractPage() {
  return (
    <Suspense
      fallback={
        <PageContainer>
          <Skeleton className="h-96 w-full" />
        </PageContainer>
      }
    >
      <YAMLContractPageContent />
    </Suspense>
  )
}
