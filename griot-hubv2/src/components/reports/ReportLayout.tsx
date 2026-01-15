'use client'

import { PageShell, PageContainer, PageHeader, Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Button, Badge } from '@/components/ui'
import { BackLink } from '@/components/navigation'
import { Download, Share2, RefreshCw, LucideIcon } from 'lucide-react'
import { ReactNode } from 'react'

interface Metric {
  label: string
  value: string | number
  trend?: number
  variant?: 'default' | 'success' | 'warning' | 'error'
}

interface ReportLayoutProps {
  title: string
  icon: LucideIcon
  iconColor: string
  description: string
  lastGenerated?: string
  children: ReactNode
  metrics: Metric[]
  onGenerate?: () => void
  onDownload?: () => void
  onShare?: () => void
}

export function ReportLayout({
  title,
  icon: Icon,
  iconColor,
  description,
  lastGenerated,
  children,
  metrics,
  onGenerate,
  onDownload,
  onShare,
}: ReportLayoutProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <PageShell>
      <PageContainer>
        <BackLink href="/reports" />

        <div className="mb-6">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className={`p-2 rounded-lg ${iconColor}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h1 className="text-3xl font-bold text-text-primary">{title}</h1>
              </div>
              {description && (
                <p className="text-text-secondary mt-1">{description}</p>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={onShare}>
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="secondary" onClick={onDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </Button>
              <Button onClick={onGenerate}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        </div>

        {/* Last Generated */}
        {lastGenerated && (
          <div className="mb-4">
            <span className="text-sm text-text-tertiary">
              Last generated: <span className="text-text-secondary">{formatDate(lastGenerated)}</span>
            </span>
          </div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {metrics.map((metric) => (
            <Card key={metric.label} padding="lg">
              <div className="text-xs text-text-tertiary mb-1">{metric.label}</div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-text-primary">{metric.value}</span>
                {metric.trend !== undefined && (
                  <Badge variant={metric.trend > 0 ? 'success' : metric.trend < 0 ? 'error' : 'secondary'} size="sm">
                    {metric.trend > 0 ? '+' : ''}
                    {metric.trend}%
                  </Badge>
                )}
              </div>
            </Card>
          ))}
        </div>

        {/* Report Content */}
        {children}
      </PageContainer>
    </PageShell>
  )
}

interface ReportSectionProps {
  title: string
  children: ReactNode
  action?: ReactNode
}

export function ReportSection({ title, children, action }: ReportSectionProps) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          {action}
        </div>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}
