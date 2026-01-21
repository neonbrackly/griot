'use client'

import { ReportLayout, ReportSection } from '@/components/reports/ReportLayout'
import { Shield, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react'
import { Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo } from 'react'

interface ComplianceControl {
  id: string
  category: string
  control: string
  status: 'passed' | 'failed' | 'warning'
  coverage: number
  lastChecked: string
}

const mockControls: ComplianceControl[] = [
  {
    id: 'AC-001',
    category: 'Access Control',
    control: 'Role-Based Access Control (RBAC)',
    status: 'passed',
    coverage: 100,
    lastChecked: '2025-01-13',
  },
  {
    id: 'AC-002',
    category: 'Access Control',
    control: 'Multi-Factor Authentication',
    status: 'passed',
    coverage: 95,
    lastChecked: '2025-01-13',
  },
  {
    id: 'DL-001',
    category: 'Data Lineage',
    control: 'End-to-End Lineage Tracking',
    status: 'warning',
    coverage: 78,
    lastChecked: '2025-01-12',
  },
  {
    id: 'AT-001',
    category: 'Audit Trail',
    control: 'Immutable Audit Logs',
    status: 'passed',
    coverage: 100,
    lastChecked: '2025-01-13',
  },
  {
    id: 'PII-001',
    category: 'Data Privacy',
    control: 'PII Identification & Classification',
    status: 'failed',
    coverage: 62,
    lastChecked: '2025-01-10',
  },
]

export default function AuditReadinessPage() {
  const columns: ColumnDef<ComplianceControl>[] = useMemo(
    () => [
      {
        accessorKey: 'id',
        header: 'Control ID',
        cell: ({ row }) => <span className="font-mono text-sm">{row.original.id}</span>,
      },
      {
        accessorKey: 'category',
        header: 'Category',
        cell: ({ row }) => <Badge variant="secondary">{row.original.category}</Badge>,
      },
      {
        accessorKey: 'control',
        header: 'Control',
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => {
          const status = row.original.status
          const variant = status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warning'
          const Icon = status === 'passed' ? CheckCircle2 : status === 'failed' ? XCircle : AlertTriangle
          return (
            <Badge variant={variant} className="gap-1">
              <Icon className="w-3 h-3" />
              {status}
            </Badge>
          )
        },
      },
      {
        accessorKey: 'coverage',
        header: 'Coverage',
        cell: ({ row }) => <span className="text-text-secondary">{row.original.coverage}%</span>,
      },
    ],
    []
  )

  const passedCount = mockControls.filter((c) => c.status === 'passed').length
  const failedCount = mockControls.filter((c) => c.status === 'failed').length
  const warningCount = mockControls.filter((c) => c.status === 'warning').length
  const totalCount = mockControls.length

  const complianceScore = Math.round((passedCount / totalCount) * 100)

  return (
    <ReportLayout
      title="Audit Readiness Report"
      icon={Shield}
      iconColor="text-success-500 bg-success-bg"
      description="Comprehensive overview of compliance controls, data lineage coverage, and audit trail completeness."
      lastGenerated={new Date().toISOString()}
      metrics={[
        { label: 'Compliance Score', value: `${complianceScore}%`, trend: 3 },
        { label: 'Controls Passed', value: `${passedCount}/${totalCount}` },
        { label: 'Failed Controls', value: failedCount },
        { label: 'Warnings', value: warningCount },
      ]}
      onGenerate={() => console.log('Regenerate report')}
      onDownload={() => console.log('Download PDF')}
      onShare={() => console.log('Share report')}
    >
      {/* Summary */}
      <ReportSection title="Executive Summary">
        <div className="prose prose-sm max-w-none text-text-secondary">
          <p>
            Your data governance program is <strong className="text-success-text">{complianceScore}% compliant</strong>{' '}
            with industry standards. {passedCount} out of {totalCount} controls are fully implemented and passing
            automated checks.
          </p>
          {failedCount > 0 && (
            <p className="text-error-text">
              <strong>Critical Issues:</strong> {failedCount} control(s) are currently failing and require immediate
              attention. See details below.
            </p>
          )}
          {warningCount > 0 && (
            <p className="text-warning-text">
              <strong>Warnings:</strong> {warningCount} control(s) are partially compliant but have room for
              improvement.
            </p>
          )}
        </div>
      </ReportSection>

      {/* Controls by Category */}
      <ReportSection title="Controls by Category">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {['Access Control', 'Data Lineage', 'Audit Trail', 'Data Privacy'].map((category) => {
            const controls = mockControls.filter((c) => c.category === category)
            const passed = controls.filter((c) => c.status === 'passed').length
            return (
              <div key={category} className="p-4 rounded-lg border border-border-default">
                <div className="text-sm font-medium text-text-primary mb-2">{category}</div>
                <div className="text-2xl font-bold text-text-primary">
                  {passed}/{controls.length}
                </div>
                <div className="text-xs text-text-tertiary">passed</div>
              </div>
            )
          })}
        </div>
      </ReportSection>

      {/* Detailed Controls Table */}
      <ReportSection title="Control Details">
        <DataTable columns={columns} data={mockControls} enableSorting enablePagination={false} />
      </ReportSection>

      {/* Recommendations */}
      <ReportSection title="Recommendations">
        <div className="space-y-3">
          {mockControls
            .filter((c) => c.status !== 'passed')
            .map((control) => (
              <div key={control.id} className="p-4 rounded-lg border border-border-default">
                <div className="flex items-start gap-3">
                  <div className={`mt-1 ${control.status === 'failed' ? 'text-error-500' : 'text-warning-500'}`}>
                    {control.status === 'failed' ? <XCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-text-primary mb-1">
                      {control.id}: {control.control}
                    </div>
                    <div className="text-sm text-text-secondary">
                      {control.status === 'failed'
                        ? 'Immediate action required to meet compliance requirements.'
                        : 'Improve coverage to reduce audit risk.'}
                    </div>
                    <div className="text-xs text-text-tertiary mt-2">Coverage: {control.coverage}%</div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </ReportSection>
    </ReportLayout>
  )
}
