'use client'

import { PageShell, PageContainer, PageHeader } from '@/components/layout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Button } from '@/components/ui'
import { Badge } from '@/components/ui'
import {
  Shield,
  DollarSign,
  BarChart3,
  AlertTriangle,
  Lightbulb,
  ChevronRight,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import Link from 'next/link'

// Placeholder data - will be replaced with real API calls by Agent 3
const mockMetrics = {
  compliance: { score: 87, trend: 3, detail: '142/163 pass' },
  cost: { score: 78, trend: -12, detail: '$42K/mo' },
  analytics: { score: 91, trend: 2, detail: '4.2% nulls' },
}

const mockIssues = [
  { id: '1', title: 'PII Exposure Risk', severity: 'critical', contract: 'CONTRACT-045' },
  { id: '2', title: 'Schema Drift Detected', severity: 'warning', contract: 'CONTRACT-023' },
]

const mockRecommendations = [
  { id: '1', text: '3 contracts pending > 7 days' },
  { id: '2', text: 'customer_events: 32% nulls' },
  { id: '3', text: '2 twin assets detected' },
]

export default function DashboardPage() {
  return (
    <PageShell>
      <PageContainer>
        <PageHeader
          title="Good morning, Jane"
          actions={
            <Button variant="secondary">
              Generate Report
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          }
        />

        {/* Health Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <HealthCard
            title="Compliance Health"
            icon={Shield}
            score={mockMetrics.compliance.score}
            trend={mockMetrics.compliance.trend}
            detail={mockMetrics.compliance.detail}
            color="green"
          />
          <HealthCard
            title="Cost Health"
            icon={DollarSign}
            score={mockMetrics.cost.score}
            trend={mockMetrics.cost.trend}
            detail={mockMetrics.cost.detail}
            color="blue"
          />
          <HealthCard
            title="Analytics Health"
            icon={BarChart3}
            score={mockMetrics.analytics.score}
            trend={mockMetrics.analytics.trend}
            detail={mockMetrics.analytics.detail}
            color="purple"
          />
        </div>

        {/* Timeline Placeholder */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Contract Runs</CardTitle>
              <Badge variant="secondary">Past 30 days</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-24 flex items-end gap-1">
              {/* Placeholder timeline bars - Agent 3 will implement real chart */}
              {Array.from({ length: 30 }).map((_, i) => {
                const height = Math.random() * 80 + 20
                const status = Math.random() > 0.9 ? 'error' : Math.random() > 0.8 ? 'warning' : 'success'
                return (
                  <div
                    key={i}
                    className={`flex-1 rounded-t transition-all hover:opacity-80 cursor-pointer ${
                      status === 'success' ? 'bg-success-500' :
                      status === 'warning' ? 'bg-warning-500' :
                      'bg-error-500'
                    }`}
                    style={{ height: `${height}%` }}
                  />
                )
              })}
            </div>
            <div className="flex justify-between text-xs text-text-tertiary mt-2">
              <span>Dec 14</span>
              <span>Jan 13</span>
            </div>
          </CardContent>
        </Card>

        {/* Issues and Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Active Issues */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-error-500" />
                  Active Issues
                </CardTitle>
                <Badge variant="error">{mockIssues.length}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {mockIssues.map((issue) => (
                <Link
                  key={issue.id}
                  href={`/studio/issues/${issue.id}`}
                  className="block p-3 rounded-lg border border-border-default hover:bg-bg-hover transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-text-primary">{issue.title}</div>
                      <div className="text-sm text-text-secondary">{issue.contract}</div>
                    </div>
                    <Badge variant={issue.severity === 'critical' ? 'error' : 'warning'}>
                      {issue.severity}
                    </Badge>
                  </div>
                </Link>
              ))}
              <Button variant="ghost" className="w-full" asChild>
                <Link href="/studio/issues">View All Issues</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-primary-500" />
                Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {mockRecommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-bg-tertiary"
                >
                  <div className="w-2 h-2 rounded-full bg-primary-500" />
                  <span className="text-sm text-text-primary">{rec.text}</span>
                </div>
              ))}
              <Button variant="ghost" className="w-full">
                View All Recommendations
              </Button>
            </CardContent>
          </Card>
        </div>
      </PageContainer>
    </PageShell>
  )
}

// Health Card Component
function HealthCard({
  title,
  icon: Icon,
  score,
  trend,
  detail,
  color,
}: {
  title: string
  icon: React.ComponentType<{ className?: string }>
  score: number
  trend: number
  detail: string
  color: 'green' | 'blue' | 'purple'
}) {
  const colorClasses = {
    green: 'bg-success-bg text-success-text',
    blue: 'bg-info-bg text-info-text',
    purple: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
  }

  return (
    <Card padding="lg">
      <div className="flex items-start justify-between">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1 text-sm">
          {trend > 0 ? (
            <ArrowUp className="w-4 h-4 text-success-text" />
          ) : (
            <ArrowDown className="w-4 h-4 text-error-text" />
          )}
          <span className={trend > 0 ? 'text-success-text' : 'text-error-text'}>
            {Math.abs(trend)}%
          </span>
        </div>
      </div>
      <div className="mt-4">
        <div className="text-3xl font-bold text-text-primary">{score}%</div>
        <div className="text-sm text-text-secondary mt-1">{title}</div>
        <div className="text-xs text-text-tertiary mt-0.5">{detail}</div>
      </div>
    </Card>
  )
}
