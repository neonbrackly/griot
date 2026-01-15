'use client'

import { ReportLayout, ReportSection } from '@/components/reports/ReportLayout'
import { DollarSign, TrendingDown, Database } from 'lucide-react'
import { Badge } from '@/components/ui'
import { DataTable } from '@/components/data-display'
import { ColumnDef } from '@tanstack/react-table'
import { useMemo } from 'react'

interface CostBreakdown {
  domain: string
  storage: number
  compute: number
  total: number
  trend: number
  opportunities: number
}

const mockCosts: CostBreakdown[] = [
  { domain: 'Customer', storage: 12500, compute: 8200, total: 20700, trend: -5, opportunities: 2 },
  { domain: 'Finance', storage: 8900, compute: 4300, total: 13200, trend: 12, opportunities: 3 },
  { domain: 'Marketing', storage: 3400, compute: 2100, total: 5500, trend: -8, opportunities: 1 },
  { domain: 'Operations', storage: 2100, compute: 900, total: 3000, trend: 3, opportunities: 2 },
]

export default function CostReadinessPage() {
  const columns: ColumnDef<CostBreakdown>[] = useMemo(
    () => [
      {
        accessorKey: 'domain',
        header: 'Domain',
        cell: ({ row }) => <span className="font-medium">{row.original.domain}</span>,
      },
      {
        accessorKey: 'storage',
        header: 'Storage',
        cell: ({ row }) => <span className="text-text-secondary">${(row.original.storage / 1000).toFixed(1)}K</span>,
      },
      {
        accessorKey: 'compute',
        header: 'Compute',
        cell: ({ row }) => <span className="text-text-secondary">${(row.original.compute / 1000).toFixed(1)}K</span>,
      },
      {
        accessorKey: 'total',
        header: 'Total',
        cell: ({ row }) => <span className="font-semibold">${(row.original.total / 1000).toFixed(1)}K</span>,
      },
      {
        accessorKey: 'trend',
        header: 'Trend',
        cell: ({ row }) => {
          const trend = row.original.trend
          return (
            <Badge variant={trend < 0 ? 'success' : trend > 10 ? 'error' : 'warning'}>
              {trend > 0 ? '+' : ''}
              {trend}%
            </Badge>
          )
        },
      },
      {
        accessorKey: 'opportunities',
        header: 'Optimizations',
        cell: ({ row }) => <Badge variant="secondary">{row.original.opportunities}</Badge>,
      },
    ],
    []
  )

  const totalCost = mockCosts.reduce((sum, c) => sum + c.total, 0)
  const totalOpportunities = mockCosts.reduce((sum, c) => sum + c.opportunities, 0)
  const avgTrend = mockCosts.reduce((sum, c) => sum + c.trend, 0) / mockCosts.length

  return (
    <ReportLayout
      title="Cost Readiness Report"
      icon={DollarSign}
      iconColor="text-info-500 bg-info-bg"
      description="Storage and compute costs by domain, optimization opportunities, and cost attribution analysis."
      lastGenerated={new Date().toISOString()}
      metrics={[
        { label: 'Monthly Total', value: `$${(totalCost / 1000).toFixed(1)}K`, trend: Math.round(avgTrend) },
        { label: 'Storage Costs', value: `$${(mockCosts.reduce((s, c) => s + c.storage, 0) / 1000).toFixed(1)}K` },
        { label: 'Compute Costs', value: `$${(mockCosts.reduce((s, c) => s + c.compute, 0) / 1000).toFixed(1)}K` },
        { label: 'Optimization Opp.', value: totalOpportunities },
      ]}
      onGenerate={() => console.log('Regenerate report')}
      onDownload={() => console.log('Download PDF')}
      onShare={() => console.log('Share report')}
    >
      {/* Summary */}
      <ReportSection title="Executive Summary">
        <div className="prose prose-sm max-w-none text-text-secondary">
          <p>
            Your total monthly data platform spend is <strong>${(totalCost / 1000).toFixed(1)}K</strong>, with a{' '}
            {avgTrend < 0 ? 'decrease' : 'increase'} of <strong>{Math.abs(avgTrend).toFixed(1)}%</strong> from last
            month.
          </p>
          <p>
            We've identified <strong className="text-primary-text">{totalOpportunities} optimization opportunities</strong>{' '}
            that could reduce your monthly spend by an estimated 15-20%.
          </p>
        </div>
      </ReportSection>

      {/* Cost Breakdown */}
      <ReportSection title="Cost by Domain">
        <DataTable columns={columns} data={mockCosts} enableSorting enablePagination={false} />
      </ReportSection>

      {/* Optimization Opportunities */}
      <ReportSection title="Optimization Opportunities">
        <div className="space-y-3">
          <div className="p-4 rounded-lg border border-border-default">
            <div className="flex items-start gap-3">
              <div className="text-primary-500 mt-1">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="font-medium text-text-primary mb-1">Archival Storage Tier Migration</div>
                <div className="text-sm text-text-secondary">
                  3 datasets haven't been accessed in 90+ days. Moving to cold storage could save $4.2K/month.
                </div>
                <Badge variant="success" className="mt-2">
                  Potential savings: $4.2K/mo
                </Badge>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg border border-border-default">
            <div className="flex items-start gap-3">
              <div className="text-primary-500 mt-1">
                <Database className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="font-medium text-text-primary mb-1">Duplicate Data Cleanup</div>
                <div className="text-sm text-text-secondary">
                  2 twin assets (customer_data and Customer360) are consuming redundant storage.
                </div>
                <Badge variant="success" className="mt-2">
                  Potential savings: $1.8K/mo
                </Badge>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg border border-border-default">
            <div className="flex items-start gap-3">
              <div className="text-primary-500 mt-1">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="font-medium text-text-primary mb-1">Compute Cluster Right-Sizing</div>
                <div className="text-sm text-text-secondary">
                  Finance domain clusters are over-provisioned by 40% based on actual usage patterns.
                </div>
                <Badge variant="success" className="mt-2">
                  Potential savings: $2.6K/mo
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </ReportSection>
    </ReportLayout>
  )
}
