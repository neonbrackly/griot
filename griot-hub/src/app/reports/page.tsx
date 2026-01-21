'use client'

import { PageShell, PageContainer, PageHeader, Card } from '@/components/layout'
import { Shield, DollarSign, BarChart3, Brain, FileText, Download, Calendar } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui'

const reports = [
  {
    id: 'audit',
    title: 'Audit Readiness Report',
    description: 'Compliance status, access controls, data lineage coverage, and audit trail completeness.',
    icon: Shield,
    href: '/reports/audit',
    color: 'text-success-500 bg-success-bg',
    metrics: [
      { label: 'Compliance Score', value: '87%' },
      { label: 'Controls Passed', value: '142/163' },
    ],
  },
  {
    id: 'cost',
    title: 'Cost Readiness Report',
    description: 'Storage costs by domain, compute usage, optimization opportunities, and cost attribution.',
    icon: DollarSign,
    href: '/reports/cost',
    color: 'text-info-500 bg-info-bg',
    metrics: [
      { label: 'Monthly Spend', value: '$42K' },
      { label: 'Optimization Opp.', value: '8' },
    ],
  },
  {
    id: 'analytics',
    title: 'Analytics Readiness Report',
    description: 'Data quality scores, completeness rates, freshness metrics, and schema health.',
    icon: BarChart3,
    href: '/reports/analytics',
    color: 'text-primary-500 bg-primary-100 dark:bg-primary-900/30',
    metrics: [
      { label: 'Quality Score', value: '91%' },
      { label: 'Avg Null Rate', value: '4.2%' },
    ],
  },
  {
    id: 'ai',
    title: 'AI Readiness Report',
    description: 'Dataset suitability for ML, feature coverage, bias detection, and model training readiness.',
    icon: Brain,
    href: '/reports/ai',
    color: 'text-purple-500 bg-purple-100 dark:bg-purple-900/30',
    metrics: [
      { label: 'AI-Ready Datasets', value: '12/23' },
      { label: 'Feature Coverage', value: '78%' },
    ],
  },
]

export default function ReportsPage() {
  return (
    <PageShell>
      <PageContainer>
        <PageHeader
          title="Reports Center"
          description="Generate comprehensive readiness reports for audit, cost, analytics, and AI initiatives."
          actions={
            <div className="flex gap-2">
              <Button variant="secondary">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule Report
              </Button>
              <Button variant="secondary">
                <FileText className="w-4 h-4 mr-2" />
                View History
              </Button>
            </div>
          }
        />

        {/* Report Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reports.map((report) => {
            const Icon = report.icon
            return (
              <Link key={report.id} href={report.href} className="block group">
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                  <div className="p-6">
                    {/* Icon and Title */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-3 rounded-lg ${report.color}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.preventDefault()
                          // TODO: Trigger download
                        }}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Content */}
                    <h3 className="text-lg font-semibold text-text-primary mb-2 group-hover:text-primary-500 transition-colors">
                      {report.title}
                    </h3>
                    <p className="text-sm text-text-secondary mb-4">{report.description}</p>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border-default">
                      {report.metrics.map((metric) => (
                        <div key={metric.label}>
                          <div className="text-xs text-text-tertiary mb-1">{metric.label}</div>
                          <div className="text-lg font-semibold text-text-primary">{metric.value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              </Link>
            )
          })}
        </div>

        {/* Recent Reports Section */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Recent Reports</h2>
          <Card>
            <div className="p-6 text-center text-text-tertiary">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No recent reports</p>
              <p className="text-xs mt-1">Generate a report to get started</p>
            </div>
          </Card>
        </div>
      </PageContainer>
    </PageShell>
  )
}
