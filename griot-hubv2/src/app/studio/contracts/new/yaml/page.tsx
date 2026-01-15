'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FileCode, Upload, Check, AlertCircle, Save, Eye } from 'lucide-react'

import { PageContainer, Card } from '@/components/layout'
import { Button, Textarea } from '@/components/ui'
import { BackLink } from '@/components/navigation/Breadcrumbs'
import { Skeleton } from '@/components/feedback'
import { toast } from '@/lib/hooks'
import { api, queryKeys } from '@/lib/api/client'

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
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [isValidating, setIsValidating] = useState(false)

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
      setYamlContent(content)
      toast.success('File loaded', 'YAML file has been loaded successfully')
    }
    reader.readAsText(file)
  }

  // Validation function
  const validateYAML = () => {
    setIsValidating(true)
    const errors: string[] = []

    try {
      // Basic YAML structure validation
      if (!yamlContent.includes('version:')) {
        errors.push('Missing required field: version')
      }
      if (!yamlContent.includes('name:')) {
        errors.push('Missing required field: name')
      }
      if (!yamlContent.includes('dataset:')) {
        errors.push('Missing required field: dataset')
      }

      // Check for common YAML syntax errors
      const lines = yamlContent.split('\n')
      lines.forEach((line, index) => {
        if (line.trim() && !line.startsWith('#')) {
          const colonCount = (line.match(/:/g) || []).length
          if (colonCount > 1 && !line.includes('"') && !line.includes("'")) {
            errors.push(`Line ${index + 1}: Multiple colons detected, may need quotes`)
          }
        }
      })

      setValidationErrors(errors)

      if (errors.length === 0) {
        toast.success('Validation passed', 'Your YAML contract is valid')
      } else {
        toast.error('Validation failed', `Found ${errors.length} errors`)
      }
    } catch (error) {
      errors.push('Invalid YAML syntax')
      setValidationErrors(errors)
      toast.error('Validation failed', 'Invalid YAML syntax')
    } finally {
      setIsValidating(false)
    }
  }

  // Create contract mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      // Parse YAML and create contract
      const response = await api.post('/contracts', {
        yaml: yamlContent,
        source: 'yaml_import',
      })
      return response
    },
    onSuccess: (data: any) => {
      toast.success('Contract created', 'Your contract has been created successfully')
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all })
      router.push(`/studio/contracts/${data.id}`)
    },
    onError: () => {
      toast.error('Failed to create contract', 'Please check your YAML and try again')
    },
  })

  const handleSave = () => {
    if (validationErrors.length > 0) {
      toast.error('Please fix validation errors first', '')
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
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={validateYAML}
                  disabled={isValidating}
                >
                  <Check className="h-4 w-4" />
                  Validate
                </Button>
              </div>
            </div>

            <Textarea
              value={yamlContent}
              onChange={(e) => setYamlContent(e.target.value)}
              className="font-mono text-sm min-h-[500px] resize-y"
              placeholder="Paste your YAML contract here..."
            />

            <div className="flex items-center justify-between mt-4">
              <p className="text-xs text-text-tertiary">
                {yamlContent.split('\n').length} lines
              </p>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => router.push('/studio/contracts/new')}>
                  Cancel
                </Button>
                <Button
                  onClick={handleSave}
                  disabled={createMutation.isPending || validationErrors.length > 0}
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
              {validationErrors.length === 0 ? (
                <>
                  <Check className="h-5 w-5 text-success-text" />
                  Validation
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-error-text" />
                  Validation Errors
                </>
              )}
            </h3>
            {validationErrors.length === 0 ? (
              <p className="text-sm text-text-secondary">
                No errors found. Ready to create contract.
              </p>
            ) : (
              <ul className="space-y-2">
                {validationErrors.map((error, index) => (
                  <li key={index} className="text-sm text-error-text flex items-start gap-2">
                    <span>•</span>
                    <span>{error}</span>
                  </li>
                ))}
              </ul>
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
