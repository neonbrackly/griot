'use client'

import { PageShell, PageContainer, PageHeader, Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Button, Input, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation'
import { Search, GitBranch, Database, FileCode, ArrowRight, Info } from 'lucide-react'
import { useState } from 'react'

interface LineageNode {
  id: string
  name: string
  type: 'source' | 'asset' | 'contract' | 'report'
  status: 'active' | 'deprecated'
}

const mockLineage: LineageNode[] = [
  { id: 'src-1', name: 'Production DB', type: 'source', status: 'active' },
  { id: 'asset-1', name: 'customer_360', type: 'asset', status: 'active' },
  { id: 'contract-1', name: 'Customer Analytics', type: 'contract', status: 'active' },
  { id: 'report-1', name: 'Churn Analysis', type: 'report', status: 'active' },
]

export default function DataLineagePage() {
  const [searchQuery, setSearchQuery] = useState('')

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'source':
        return 'text-info-500 bg-info-bg'
      case 'asset':
        return 'text-success-500 bg-success-bg'
      case 'contract':
        return 'text-primary-500 bg-primary-100 dark:bg-primary-900/30'
      case 'report':
        return 'text-purple-500 bg-purple-100 dark:bg-purple-900/30'
      default:
        return 'text-text-tertiary bg-bg-secondary'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'source':
        return Database
      case 'asset':
        return Database
      case 'contract':
        return FileCode
      case 'report':
        return FileCode
      default:
        return FileCode
    }
  }

  return (
    <PageShell>
      <PageContainer>
        <BackLink href="/marketplace" />

        <PageHeader
          title="Data Lineage"
          description="Visualize data flow from sources to reports"
          actions={
            <div className="flex gap-2">
              <Button variant="secondary">
                <GitBranch className="w-4 h-4 mr-2" />
                Full Graph
              </Button>
              <Button variant="secondary">
                <Info className="w-4 h-4 mr-2" />
                Guide
              </Button>
            </div>
          }
        />

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-tertiary" />
            <Input
              placeholder="Search for assets, contracts, or reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Lineage Visualization Placeholder */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Lineage Flow</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Simple Linear Lineage Visualization */}
            <div className="flex items-center justify-between py-8 px-4 overflow-x-auto">
              {mockLineage.map((node, index) => {
                const Icon = getTypeIcon(node.type)
                return (
                  <div key={node.id} className="flex items-center">
                    {/* Node */}
                    <div className="flex flex-col items-center min-w-[120px]">
                      <div className={`p-4 rounded-lg ${getTypeColor(node.type)}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div className="mt-2 text-center">
                        <div className="text-sm font-medium text-text-primary">{node.name}</div>
                        <Badge variant="secondary" size="sm" className="mt-1">
                          {node.type}
                        </Badge>
                      </div>
                    </div>

                    {/* Arrow */}
                    {index < mockLineage.length - 1 && (
                      <div className="mx-4">
                        <ArrowRight className="w-8 h-8 text-text-tertiary" />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Legend */}
            <div className="mt-6 pt-6 border-t border-border-default">
              <div className="flex items-center gap-4 text-sm">
                <span className="text-text-tertiary">Legend:</span>
                {['source', 'asset', 'contract', 'report'].map((type) => {
                  const Icon = getTypeIcon(type)
                  return (
                    <div key={type} className="flex items-center gap-2">
                      <div className={`p-1 rounded ${getTypeColor(type)}`}>
                        <Icon className="w-3 h-3" />
                      </div>
                      <span className="text-text-secondary capitalize">{type}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Impact Analysis */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Upstream Dependencies</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockLineage
                  .filter((n) => n.type === 'source' || n.type === 'asset')
                  .map((node) => {
                    const Icon = getTypeIcon(node.type)
                    return (
                      <div
                        key={node.id}
                        className="flex items-center gap-3 p-3 rounded-lg border border-border-default"
                      >
                        <div className={`p-2 rounded ${getTypeColor(node.type)}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-text-primary">{node.name}</div>
                          <div className="text-xs text-text-tertiary capitalize">{node.type}</div>
                        </div>
                        <Badge variant="success" size="sm">
                          {node.status}
                        </Badge>
                      </div>
                    )
                  })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Downstream Impacts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockLineage
                  .filter((n) => n.type === 'contract' || n.type === 'report')
                  .map((node) => {
                    const Icon = getTypeIcon(node.type)
                    return (
                      <div
                        key={node.id}
                        className="flex items-center gap-3 p-3 rounded-lg border border-border-default"
                      >
                        <div className={`p-2 rounded ${getTypeColor(node.type)}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-text-primary">{node.name}</div>
                          <div className="text-xs text-text-tertiary capitalize">{node.type}</div>
                        </div>
                        <Badge variant="warning" size="sm">
                          Impacted
                        </Badge>
                      </div>
                    )
                  })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Info Box */}
        <Card className="mt-6">
          <CardContent>
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-info-500 mt-0.5" />
              <div>
                <div className="font-medium text-text-primary mb-1">Data Lineage Visualization</div>
                <p className="text-sm text-text-secondary">
                  This is a simplified lineage view. For full interactive graph visualization with column-level lineage,
                  use the <strong>Full Graph</strong> button above. You can trace data from its source through
                  transformations to final consumption in reports and dashboards.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </PageContainer>
    </PageShell>
  )
}
