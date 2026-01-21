'use client'

import { Card } from '@/components/layout'
import { ArrowUp, ArrowDown, LucideIcon } from 'lucide-react'
import { Skeleton } from '@/components/feedback'

interface HealthScoreCardProps {
  title: string
  icon: LucideIcon
  score: number
  trend: number
  details: string
  color: 'green' | 'blue' | 'purple'
  isLoading?: boolean
  onClick?: () => void
}

export function HealthScoreCard({
  title,
  icon: Icon,
  score,
  trend,
  details,
  color,
  isLoading,
  onClick,
}: HealthScoreCardProps) {
  const colorClasses = {
    green: 'bg-success-bg text-success-text',
    blue: 'bg-info-bg text-info-text',
    purple: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
  }

  if (isLoading) {
    return (
      <Card padding="lg">
        <div className="flex items-start justify-between">
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-12 h-5" />
        </div>
        <div className="mt-4 space-y-2">
          <Skeleton className="w-20 h-9" />
          <Skeleton className="w-32 h-4" />
          <Skeleton className="w-24 h-3" />
        </div>
      </Card>
    )
  }

  return (
    <Card
      padding="lg"
      className={onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1 text-sm">
          {trend > 0 ? (
            <ArrowUp className="w-4 h-4 text-success-text" />
          ) : trend < 0 ? (
            <ArrowDown className="w-4 h-4 text-error-text" />
          ) : null}
          <span className={trend > 0 ? 'text-success-text' : trend < 0 ? 'text-error-text' : 'text-text-tertiary'}>
            {Math.abs(trend)}%
          </span>
        </div>
      </div>
      <div className="mt-4">
        <div className="text-3xl font-bold text-text-primary">{score}%</div>
        <div className="text-sm text-text-secondary mt-1">{title}</div>
        <div className="text-xs text-text-tertiary mt-0.5">{details}</div>
      </div>
    </Card>
  )
}
