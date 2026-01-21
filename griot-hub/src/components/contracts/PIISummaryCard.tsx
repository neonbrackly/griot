'use client'

import { Shield, AlertTriangle, Eye, Lock, CreditCard, Heart, Fingerprint } from 'lucide-react'
import { Card } from '@/components/layout'
import { Badge } from '@/components/ui'

// PII categories with their metadata
const PII_CATEGORIES: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  personal: { label: 'Personal', icon: Eye, color: 'text-blue-600' },
  financial: { label: 'Financial', icon: CreditCard, color: 'text-yellow-600' },
  health: { label: 'Health', icon: Heart, color: 'text-red-600' },
  sensitive: { label: 'Sensitive', icon: Fingerprint, color: 'text-purple-600' },
  behavioral: { label: 'Behavioral', icon: Lock, color: 'text-green-600' },
}

interface PIIField {
  name: string
  table: string
  classification: string
}

interface PIISummaryCardProps {
  piiFields: PIIField[]
}

export function PIISummaryCard({ piiFields }: PIISummaryCardProps) {
  if (piiFields.length === 0) return null

  // Group fields by classification
  const groupedByCategory = piiFields.reduce((acc, field) => {
    const category = field.classification || 'personal'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(field)
    return acc
  }, {} as Record<string, PIIField[]>)

  const categories = Object.keys(groupedByCategory)

  return (
    <Card className="p-6 border-warning-border bg-warning-bg/10">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="h-5 w-5 text-warning-text" />
        <h3 className="text-sm font-semibold text-warning-text">Privacy Information</h3>
        <Badge variant="warning" size="sm">{piiFields.length} PII Fields</Badge>
      </div>

      <p className="text-sm text-text-secondary mb-4">
        This contract contains personally identifiable information (PII) that requires special handling
        and compliance measures.
      </p>

      {/* Category breakdown */}
      <div className="space-y-3">
        {categories.map((category) => {
          const fields = groupedByCategory[category]
          const categoryInfo = PII_CATEGORIES[category] || PII_CATEGORIES.personal
          const Icon = categoryInfo.icon

          return (
            <div key={category} className="p-3 rounded-lg bg-bg-primary border border-border-default">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`h-4 w-4 ${categoryInfo.color}`} />
                <span className="text-sm font-medium text-text-primary">
                  {categoryInfo.label}
                </span>
                <Badge variant="secondary" size="xs">{fields.length}</Badge>
              </div>
              <div className="flex flex-wrap gap-1">
                {fields.slice(0, 6).map((field) => (
                  <Badge key={`${field.table}.${field.name}`} variant="secondary" size="xs">
                    {field.table}.{field.name}
                  </Badge>
                ))}
                {fields.length > 6 && (
                  <Badge variant="secondary" size="xs">
                    +{fields.length - 6} more
                  </Badge>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Compliance warning */}
      <div className="mt-4 p-3 rounded-lg bg-warning-bg/20 border border-warning-border">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-warning-text mt-0.5" />
          <div>
            <p className="text-sm font-medium text-warning-text">Compliance Notice</p>
            <p className="text-xs text-text-secondary mt-1">
              Ensure proper data handling procedures are in place for PII. Consult your organization&apos;s
              privacy policy and applicable regulations (GDPR, CCPA, HIPAA, etc.).
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
}

// Helper function to extract PII fields from contract schema
export function extractPIIFields(schema: { tables?: Array<{ name: string; fields?: Array<{ name: string; piiClassification?: string }> }> } | undefined): PIIField[] {
  if (!schema?.tables) return []

  return schema.tables.flatMap((table) =>
    (table.fields || [])
      .filter((field) => field.piiClassification)
      .map((field) => ({
        name: field.name,
        table: table.name,
        classification: field.piiClassification || 'personal',
      }))
  )
}
