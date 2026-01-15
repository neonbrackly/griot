'use client'

import { PageShell, PageContainer, PageHeader } from '@/components/layout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import {
  Button,
  Badge,
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui'
import { TimelineChart } from '@/components/dashboard/TimelineChart'
import { HealthScoreCard } from '@/components/dashboard/HealthScoreCard'
import { Skeleton } from '@/components/feedback'
import {
  Shield,
  DollarSign,
  BarChart3,
  AlertTriangle,
  Lightbulb,
  ChevronDown,
  FileText,
  Brain,
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { api, queryKeys } from '@/lib/api/client'
import type { DashboardMetrics, Issue, TimelineDay } from '@/types'

interface Recommendation {
  id: string
  type: 'action' | 'warning' | 'info'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  actionLabel: string
  actionHref: string
}

export default function DashboardPage() {
  const router = useRouter()

  // Fetch dashboard metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery<DashboardMetrics>({
    queryKey: queryKeys.dashboard.metrics,
    queryFn: () => api.get('/dashboard/metrics'),
  })

  // Fetch timeline data
  const {
    data: timeline,
    isLoading: timelineLoading,
    error: timelineError,
  } = useQuery<TimelineDay[]>({
    queryKey: queryKeys.dashboard.timeline({ days: 30 }),
    queryFn: () => api.get('/dashboard/timeline?days=30'),
  })

  // Fetch recommendations
  const {
    data: recommendations,
    isLoading: recommendationsLoading,
  } = useQuery<Recommendation[]>({
    queryKey: queryKeys.dashboard.recommendations,
    queryFn: () => api.get('/dashboard/recommendations'),
  })

  // Fetch active issues
  const {
    data: issuesData,
    isLoading: issuesLoading,
  } = useQuery<{ data: Issue[] }>({
    queryKey: queryKeys.issues.list({ status: 'open', limit: 5 }),
    queryFn: () => api.get<{ data: Issue[] }>('/issues?status=open&limit=5'),
  })

  const issues = issuesData?.data || []

  // Get user name from query or default
  const userName = 'Jane'
  const greeting = `Good morning, ${userName}`

  return (
    <PageShell>
      <PageContainer>
        <PageHeader
          title={greeting}
          actions={
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary">
                  Generate Report
                  <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem onClick={() => router.push('/reports/audit')}>
                  <Shield className="w-4 h-4 mr-2" />
                  Audit Readiness
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/reports/cost')}>
                  <DollarSign className="w-4 h-4 mr-2" />
                  Cost Readiness
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/reports/analytics')}>
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Analytics Readiness
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/reports/ai')}>
                  <Brain className="w-4 h-4 mr-2" />
                  AI Readiness
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/reports')}>
                  <FileText className="w-4 h-4 mr-2" />
                  View All Reports
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          }
        />

        {/* Health Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <HealthScoreCard
            title="Compliance Health"
            icon={Shield}
            score={metrics?.complianceHealth.score || 0}
            trend={metrics?.complianceHealth.trend || 0}
            details={metrics?.complianceHealth.details || ''}
            color="green"
            isLoading={metricsLoading}
          />
          <HealthScoreCard
            title="Cost Health"
            icon={DollarSign}
            score={metrics?.costHealth.score || 0}
            trend={metrics?.costHealth.trend || 0}
            details={metrics?.costHealth.details || ''}
            color="blue"
            isLoading={metricsLoading}
          />
          <HealthScoreCard
            title="Analytics Health"
            icon={BarChart3}
            score={metrics?.analyticsHealth.score || 0}
            trend={metrics?.analyticsHealth.trend || 0}
            details={metrics?.analyticsHealth.details || ''}
            color="purple"
            isLoading={metricsLoading}
          />
        </div>

        {/* Timeline Chart */}
        <div className="mb-6">
          <TimelineChart data={timeline || []} isLoading={timelineLoading} period="Past 30 days" />
        </div>

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
                <Badge variant="error">{metrics?.activeIssues || 0}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {issuesLoading ? (
                <>
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </>
              ) : issues.length > 0 ? (
                <>
                  {issues.map((issue) => (
                    <Link
                      key={issue.id}
                      href={`/studio/issues/${issue.id}`}
                      className="block p-3 rounded-lg border border-border-default hover:bg-bg-hover transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-text-primary">{issue.title}</div>
                          <div className="text-sm text-text-secondary">{issue.contractId}</div>
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
                </>
              ) : (
                <div className="text-center py-8 text-text-tertiary">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No active issues</p>
                </div>
              )}
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
              {recommendationsLoading ? (
                <>
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </>
              ) : recommendations && recommendations.length > 0 ? (
                <>
                  {recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      className="p-3 rounded-lg border border-border-default hover:bg-bg-hover transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={`w-2 h-2 rounded-full mt-1.5 ${
                            rec.priority === 'high'
                              ? 'bg-error-500'
                              : rec.priority === 'medium'
                              ? 'bg-warning-500'
                              : 'bg-primary-500'
                          }`}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-text-primary">{rec.title}</div>
                          <div className="text-xs text-text-secondary mt-0.5">{rec.description}</div>
                          <Button variant="ghost" size="sm" className="mt-2 h-auto py-1 px-2" asChild>
                            <Link href={rec.actionHref}>{rec.actionLabel} →</Link>
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <div className="text-center py-8 text-text-tertiary">
                  <Lightbulb className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No recommendations at this time</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </PageContainer>
    </PageShell>
  )
}
