'use client'

import { CheckCircle, XCircle, AlertCircle, Percent, Database, BarChart } from 'lucide-react'
import { Card } from '@/components/layout'
import { Badge, Button } from '@/components/ui'
import { useState } from 'react'

// Rule type icons
const RULE_TYPE_ICONS: Record<string, React.ElementType> = {
  completeness: CheckCircle,
  uniqueness: Database,
  validity: AlertCircle,
  accuracy: BarChart,
  consistency: CheckCircle,
  timeliness: AlertCircle,
}

// Rule type colors
const RULE_TYPE_COLORS: Record<string, string> = {
  completeness: 'text-green-600',
  uniqueness: 'text-blue-600',
  validity: 'text-yellow-600',
  accuracy: 'text-purple-600',
  consistency: 'text-teal-600',
  timeliness: 'text-orange-600',
}

interface QualityRule {
  id: string
  name: string
  type: string
  field?: string
  table?: string
  threshold?: number
  expression?: string
  enabled: boolean
}

interface QualityRulesCardProps {
  rules: QualityRule[]
  onViewAll?: () => void
}

export function QualityRulesCard({ rules, onViewAll }: QualityRulesCardProps) {
  const [showAll, setShowAll] = useState(false)

  if (!rules || rules.length === 0) return null

  const enabledRules = rules.filter((r) => r.enabled)
  const disabledRules = rules.filter((r) => !r.enabled)

  // Group rules by level (schema vs field)
  const schemaRules = rules.filter((r) => !r.field)
  const fieldRules = rules.filter((r) => r.field)

  // Group field rules by table
  const rulesByTable = fieldRules.reduce((acc, rule) => {
    const table = rule.table || 'Unknown'
    if (!acc[table]) {
      acc[table] = []
    }
    acc[table].push(rule)
    return acc
  }, {} as Record<string, QualityRule[]>)

  const displayedRules = showAll ? rules : rules.slice(0, 5)

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-text-secondary">Quality Rules</h3>
          <Badge variant="secondary" size="sm">{rules.length}</Badge>
        </div>
        {onViewAll && (
          <Button variant="ghost" size="sm" onClick={onViewAll}>
            Manage Rules
          </Button>
        )}
      </div>

      {/* Summary */}
      <div className="flex gap-4 mb-4 pb-4 border-b border-border-default">
        <div className="flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-success-text" />
          <span className="text-sm text-text-secondary">
            {enabledRules.length} enabled
          </span>
        </div>
        <div className="flex items-center gap-2">
          <XCircle className="h-4 w-4 text-text-tertiary" />
          <span className="text-sm text-text-secondary">
            {disabledRules.length} disabled
          </span>
        </div>
        {schemaRules.length > 0 && (
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-text-tertiary" />
            <span className="text-sm text-text-secondary">
              {schemaRules.length} schema-level
            </span>
          </div>
        )}
        {fieldRules.length > 0 && (
          <div className="flex items-center gap-2">
            <BarChart className="h-4 w-4 text-text-tertiary" />
            <span className="text-sm text-text-secondary">
              {fieldRules.length} field-level
            </span>
          </div>
        )}
      </div>

      {/* Rules list */}
      <div className="space-y-3">
        {displayedRules.map((rule) => {
          const Icon = RULE_TYPE_ICONS[rule.type] || AlertCircle
          const iconColor = RULE_TYPE_COLORS[rule.type] || 'text-text-tertiary'

          return (
            <div
              key={rule.id}
              className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary"
            >
              <div className="flex items-center gap-3">
                <Icon className={`h-5 w-5 ${iconColor}`} />
                <div>
                  <p className="font-medium text-text-primary text-sm">{rule.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" size="xs">{rule.type}</Badge>
                    {rule.field && (
                      <span className="text-xs text-text-tertiary">
                        {rule.table ? `${rule.table}.` : ''}{rule.field}
                      </span>
                    )}
                    {!rule.field && rule.table && (
                      <span className="text-xs text-text-tertiary">
                        Table: {rule.table}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {rule.threshold != null && (
                  <div className="flex items-center gap-1 text-sm">
                    <Percent className="h-3 w-3 text-text-tertiary" />
                    <span className="text-text-primary font-mono">{rule.threshold}%</span>
                  </div>
                )}
                <Badge variant={rule.enabled ? 'success' : 'secondary'} size="sm">
                  {rule.enabled ? 'On' : 'Off'}
                </Badge>
              </div>
            </div>
          )
        })}
      </div>

      {/* Show more/less toggle */}
      {rules.length > 5 && (
        <Button
          variant="ghost"
          size="sm"
          className="w-full mt-3"
          onClick={() => setShowAll(!showAll)}
        >
          {showAll ? 'Show Less' : `Show ${rules.length - 5} More`}
        </Button>
      )}

      {/* Rules by table (collapsed by default) */}
      {Object.keys(rulesByTable).length > 0 && (
        <div className="mt-4 pt-4 border-t border-border-default">
          <p className="text-xs font-medium text-text-tertiary mb-2">Rules by Table</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(rulesByTable).map(([table, tableRules]) => (
              <Badge key={table} variant="secondary" size="xs">
                {table}: {tableRules.length}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}
