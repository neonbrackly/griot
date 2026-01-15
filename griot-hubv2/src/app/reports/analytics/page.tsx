'use client'

import { ReportLayout, ReportSection } from '@/components/reports/ReportLayout'
import { BarChart3, CheckCircle2, AlertCircle } from 'lucide-react'
import { Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo } from 'react'

interface DataQuality {
  dataset: string
  completeness: number
  uniqueness: number
  validity: number
  freshness: number
  overall: number
  status: 'excellent' | 'good' | 'warning' | 'poor'
}

const mockQuality: DataQuality[] = [
  {
    dataset: 'customer_360',
    completeness: 98,
    uniqueness: 100,
    validity: 95,
    freshness: 92,
    overall: 96,
    status: 'excellent',
  },
  {
    dataset: 'transactions',
    completeness: 89,
    uniqueness: 98,
    validity: 91,
    freshness: 88,
    overall: 92,
    status: 'good',
  },
  {
    dataset: 'customer_events',
    completeness: 68,
    uniqueness: 95,
    validity: 72,
    freshness: 85,
    overall: 80,
    status: 'warning',
  },
  {
    dataset: 'user_profiles',
    completeness: 92,
    uniqueness: 88,
    validity: 94,
    freshness: 90,
    overall: 91,
    status: 'good',
  },
]

export default function AnalyticsReadinessPage() {
  const columns: ColumnDef<DataQuality>[] = useMemo(
    () => [
      {
        accessorKey: 'dataset',
        header: 'Dataset',
        cell: ({ row }) => <span className="font-medium">{row.original.dataset}</span>,
      },
      {
        accessorKey: 'completeness',
        header: 'Completeness',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.completeness}%</span>,
      },
      {
        accessorKey: 'uniqueness',
        header: 'Uniqueness',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.uniqueness}%</span>,
      },
      {
        accessorKey: 'validity',
        header: 'Validity',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.validity}%</span>,
      },
      {
        accessorKey: 'freshness',
        header: 'Freshness',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.freshness}%</span>,
      },
      {
        accessorKey: 'overall',
        header: 'Overall',
        cell: ({ row }) => {
          const score = row.original.overall
          const variant = score >= 95 ? 'success' : score >= 85 ? 'secondary' : score >= 70 ? 'warning' : 'error'
          return (
            <Badge variant={variant}>
              {score}%
            </Badge>
          )
        },
      },
    ],
    []
  )

  const avgQuality = Math.round(mockQuality.reduce((sum, q) => sum + q.overall, 0) / mockQuality.length)
  const excellentCount = mockQuality.filter((q) => q.status === 'excellent').length
  const warningCount = mockQuality.filter((q) => q.status === 'warning' || q.status === 'poor').length

  return (
    <ReportLayout
      title="Analytics Readiness Report"
      icon={BarChart3}
      iconColor="text-primary-500 bg-primary-100 dark:bg-primary-900/30"
      description="Data quality scores, completeness rates, freshness metrics, and schema health across all datasets."
      lastGenerated={new Date().toISOString()}
      metrics={[
        { label: 'Overall Quality', value: `${avgQuality}%`, trend: 2 },
        { label: 'Excellent Datasets', value: excellentCount },
        { label: 'Needs Attention', value: warningCount },
        { label: 'Total Datasets', value: mockQuality.length },
      ]}
      onGenerate={() => console.log('Regenerate report')}
      onDownload={() => console.log('Download PDF')}
      onShare={() => console.log('Share report')}
    >
      {/* Summary */}
      <ReportSection title="Executive Summary">
        <div className="prose prose-sm max-w-none text-text-secondary">
          <p>
            Your data platform maintains an average quality score of <strong>{avgQuality}%</strong> across all
            monitored datasets. {excellentCount} dataset(s) are performing excellently with scores above 95%.
          </p>
          {warningCount > 0 && (
            <p className="text-warning-text">
              <strong>Attention Required:</strong> {warningCount} dataset(s) have quality scores below 85% and should
              be reviewed for data integrity issues.
            </p>
          )}
        </div>
      </ReportSection>

      {/* Quality Dimensions */}
      <ReportSection title="Quality by Dimension">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {['Completeness', 'Uniqueness', 'Validity', 'Freshness'].map((dimension) => {
            const key = dimension.toLowerCase() as keyof DataQuality
            const avg = Math.round(mockQuality.reduce((sum, q) => sum + (q[key] as number), 0) / mockQuality.length)
            return (
              <div key={dimension} className="p-4 rounded-lg border border-border-default">
                <div className="text-sm text-text-tertiary mb-1">{dimension}</div>
                <div className="text-3xl font-bold text-text-primary">{avg}%</div>
                <div className="mt-2 h-2 bg-bg-secondary rounded-full overflow-hidden">
                  <div
                    className={`h-full ${avg >= 90 ? 'bg-success-500' : avg >= 70 ? 'bg-warning-500' : 'bg-error-500'}`}
                    style={{ width: `${avg}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </ReportSection>

      {/* Dataset Quality Table */}
      <ReportSection title="Dataset Quality Scores">
        <DataTable columns={columns} data={mockQuality} enableSorting enablePagination={false} />
      </ReportSection>

      {/* Issues & Recommendations */}
      <ReportSection title="Quality Issues">
        <div className="space-y-3">
          {mockQuality
            .filter((q) => q.status === 'warning' || q.status === 'poor')
            .map((dataset) => (
              <div key={dataset.dataset} className="p-4 rounded-lg border border-border-default">
                <div className="flex items-start gap-3">
                  <div className="text-warning-500 mt-1">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-text-primary mb-1">{dataset.dataset}</div>
                    <div className="text-sm text-text-secondary">
                      {dataset.completeness < 80 && 'Low completeness: High percentage of null values detected. '}
                      {dataset.validity < 80 && 'Validity issues: Data format and constraint violations found. '}
                      {dataset.freshness < 80 && 'Freshness concerns: Data is not being updated frequently enough.'}
                    </div>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="secondary" size="sm">
                        Completeness: {dataset.completeness}%
                      </Badge>
                      <Badge variant="secondary" size="sm">
                        Validity: {dataset.validity}%
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </ReportSection>
    </ReportLayout>
  )
}
