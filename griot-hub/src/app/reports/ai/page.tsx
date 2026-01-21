'use client'

import { ReportLayout, ReportSection } from '@/components/reports/ReportLayout'
import { Brain, Sparkles, Target } from 'lucide-react'
import { Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo } from 'react'

interface AIReadiness {
  dataset: string
  featureCoverage: number
  labelQuality: number
  biasScore: number
  sampleSize: number
  readiness: 'ready' | 'partial' | 'not-ready'
  useCases: string[]
}

const mockAIData: AIReadiness[] = [
  {
    dataset: 'customer_360',
    featureCoverage: 92,
    labelQuality: 88,
    biasScore: 95,
    sampleSize: 1200000,
    readiness: 'ready',
    useCases: ['Churn Prediction', 'Segmentation'],
  },
  {
    dataset: 'transactions',
    featureCoverage: 85,
    labelQuality: 90,
    biasScore: 82,
    sampleSize: 5600000,
    readiness: 'ready',
    useCases: ['Fraud Detection', 'Recommendation'],
  },
  {
    dataset: 'user_behavior',
    featureCoverage: 72,
    labelQuality: 65,
    biasScore: 78,
    sampleSize: 890000,
    readiness: 'partial',
    useCases: ['Click Prediction'],
  },
  {
    dataset: 'product_catalog',
    featureCoverage: 58,
    labelQuality: 45,
    biasScore: 88,
    sampleSize: 45000,
    readiness: 'not-ready',
    useCases: [],
  },
]

export default function AIReadinessPage() {
  const columns: ColumnDef<AIReadiness>[] = useMemo(
    () => [
      {
        accessorKey: 'dataset',
        header: 'Dataset',
        cell: ({ row }) => <span className="font-medium">{row.original.dataset}</span>,
      },
      {
        accessorKey: 'featureCoverage',
        header: 'Features',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.featureCoverage}%</span>,
      },
      {
        accessorKey: 'labelQuality',
        header: 'Labels',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.labelQuality}%</span>,
      },
      {
        accessorKey: 'biasScore',
        header: 'Bias Score',
        cell: ({ row }) => {
          const score = row.original.biasScore
          const variant = score >= 85 ? 'success' : score >= 70 ? 'warning' : 'error'
          return <Badge variant={variant}>{score}%</Badge>
        },
      },
      {
        accessorKey: 'sampleSize',
        header: 'Samples',
        cell: ({ row }) => (
          <span className="text-text-secondary">{(row.original.sampleSize / 1000000).toFixed(1)}M</span>
        ),
      },
      {
        accessorKey: 'readiness',
        header: 'Status',
        cell: ({ row }) => {
          const status = row.original.readiness
          const variant = status === 'ready' ? 'success' : status === 'partial' ? 'warning' : 'error'
          return (
            <Badge variant={variant}>
              {status === 'ready' ? 'AI Ready' : status === 'partial' ? 'Partial' : 'Not Ready'}
            </Badge>
          )
        },
      },
    ],
    []
  )

  const readyCount = mockAIData.filter((d) => d.readiness === 'ready').length
  const partialCount = mockAIData.filter((d) => d.readiness === 'partial').length
  const avgFeatureCoverage = Math.round(
    mockAIData.reduce((sum, d) => sum + d.featureCoverage, 0) / mockAIData.length
  )

  return (
    <ReportLayout
      title="AI Readiness Report"
      icon={Brain}
      iconColor="text-purple-500 bg-purple-100 dark:bg-purple-900/30"
      description="Dataset suitability for ML, feature coverage, bias detection, and model training readiness."
      lastGenerated={new Date().toISOString()}
      metrics={[
        {
          label: 'AI-Ready Datasets',
          value: `${readyCount}/${mockAIData.length}`,
        },
        { label: 'Feature Coverage', value: `${avgFeatureCoverage}%` },
        { label: 'Partial Readiness', value: partialCount },
        { label: 'Total Use Cases', value: mockAIData.reduce((sum, d) => sum + d.useCases.length, 0) },
      ]}
      onGenerate={() => console.log('Regenerate report')}
      onDownload={() => console.log('Download PDF')}
      onShare={() => console.log('Share report')}
    >
      {/* Summary */}
      <ReportSection title="Executive Summary">
        <div className="prose prose-sm max-w-none text-text-secondary">
          <p>
            <strong>{readyCount}</strong> out of {mockAIData.length} datasets are fully ready for AI/ML initiatives.
            These datasets have sufficient feature coverage, high-quality labels, and acceptable bias scores.
          </p>
          {partialCount > 0 && (
            <p>
              <strong className="text-warning-text">{partialCount} dataset(s)</strong> are partially ready and require
              additional data engineering work before model training.
            </p>
          )}
          <p>
            Your platform supports{' '}
            <strong>{mockAIData.reduce((sum, d) => sum + d.useCases.length, 0)} identified use cases</strong> across
            customer analytics, fraud detection, and recommendation systems.
          </p>
        </div>
      </ReportSection>

      {/* Readiness by Dataset */}
      <ReportSection title="Dataset AI Readiness">
        <DataTable columns={columns} data={mockAIData} enableSorting enablePagination={false} />
      </ReportSection>

      {/* Use Cases */}
      <ReportSection title="Identified AI Use Cases">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockAIData
            .filter((d) => d.useCases.length > 0)
            .map((dataset) => (
              <div key={dataset.dataset} className="p-4 rounded-lg border border-border-default">
                <div className="flex items-start gap-3">
                  <div className="text-primary-500 mt-1">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-text-primary mb-2">{dataset.dataset}</div>
                    <div className="flex flex-wrap gap-1">
                      {dataset.useCases.map((useCase) => (
                        <Badge key={useCase} variant="secondary" size="sm">
                          {useCase}
                        </Badge>
                      ))}
                    </div>
                    <div className="mt-2 text-xs text-text-tertiary">
                      {dataset.sampleSize.toLocaleString()} samples available
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </ReportSection>

      {/* Recommendations */}
      <ReportSection title="Recommendations">
        <div className="space-y-3">
          {mockAIData
            .filter((d) => d.readiness !== 'ready')
            .map((dataset) => (
              <div key={dataset.dataset} className="p-4 rounded-lg border border-border-default">
                <div className="flex items-start gap-3">
                  <div className="text-primary-500 mt-1">
                    <Target className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-text-primary mb-1">{dataset.dataset}</div>
                    <ul className="text-sm text-text-secondary space-y-1 list-disc list-inside">
                      {dataset.featureCoverage < 70 && (
                        <li>Increase feature coverage by adding more relevant attributes</li>
                      )}
                      {dataset.labelQuality < 70 && <li>Improve label quality through manual review or active learning</li>}
                      {dataset.biasScore < 85 && <li>Address bias concerns to ensure fair model predictions</li>}
                      {dataset.sampleSize < 100000 && <li>Collect more samples to meet minimum training requirements</li>}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </ReportSection>
    </ReportLayout>
  )
}
