'use client'

import { TimelineDay } from '@/types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/layout'
import { Badge } from '@/components/ui'
import { Skeleton } from '@/components/feedback'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

interface TimelineChartProps {
  data: TimelineDay[]
  isLoading?: boolean
  period?: string
}

export function TimelineChart({ data, isLoading, period = 'Past 30 days' }: TimelineChartProps) {
  const router = useRouter()
  const [hoveredDay, setHoveredDay] = useState<TimelineDay | null>(null)
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Contract Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    )
  }

  // Calculate max runs for scaling
  const maxRuns = Math.max(...data.map((d) => d.runsCount || 0), 1)

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  // Get color based on status
  const getStatusColor = (status: TimelineDay['status']) => {
    switch (status) {
      case 'passed':
        return 'bg-success-500 hover:bg-success-600'
      case 'warning':
        return 'bg-warning-500 hover:bg-warning-600'
      case 'failed':
        return 'bg-error-500 hover:bg-error-600'
      case 'none':
        return 'bg-border-default hover:bg-bg-hover'
      default:
        return 'bg-border-default'
    }
  }

  const handleDayClick = (day: TimelineDay) => {
    if (day.runsCount > 0) {
      router.push(`/runs/${day.date}`)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Contract Runs</CardTitle>
          <Badge variant="secondary">{period}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Timeline visualization */}
        <div className="relative">
          {/* Bars */}
          <div className="flex items-end gap-1 h-32 mb-2">
            {data.map((day, index) => {
              const height = day.runsCount ? (day.runsCount / maxRuns) * 100 : 2
              return (
                <button
                  key={day.date}
                  className={`flex-1 rounded-t transition-all cursor-pointer relative group ${getStatusColor(
                    day.status
                  )}`}
                  style={{ height: `${height}%`, minHeight: '4px' }}
                  onClick={() => handleDayClick(day)}
                  onMouseEnter={() => {
                    setHoveredDay(day)
                    setHoveredIndex(index)
                  }}
                  onMouseLeave={() => {
                    setHoveredDay(null)
                    setHoveredIndex(null)
                  }}
                  aria-label={`${formatDate(day.date)}: ${day.runsCount} runs`}
                />
              )
            })}
          </div>

          {/* Tooltip */}
          {hoveredDay && hoveredIndex !== null && (
            <div
              className="absolute bottom-full mb-2 transform -translate-x-1/2 z-10 pointer-events-none"
              style={{
                left: `${(hoveredIndex / data.length) * 100}%`,
              }}
            >
              <div className="bg-bg-primary border border-border-default rounded-lg shadow-lg p-3 min-w-[200px]">
                <div className="text-sm font-medium text-text-primary mb-1">
                  {formatDate(hoveredDay.date)}
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Total Runs:</span>
                    <span className="text-text-primary font-medium">{hoveredDay.runsCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Passed:</span>
                    <span className="text-success-text font-medium">{hoveredDay.passedCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Failed:</span>
                    <span className="text-error-text font-medium">{hoveredDay.failedCount}</span>
                  </div>
                  {hoveredDay.status === 'warning' && (
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Warnings:</span>
                      <span className="text-warning-text font-medium">
                        {hoveredDay.runsCount - hoveredDay.passedCount - hoveredDay.failedCount}
                      </span>
                    </div>
                  )}
                </div>
                <div className="text-xs text-text-tertiary mt-2 pt-2 border-t border-border-default">
                  Click to view details
                </div>
              </div>
              {/* Arrow */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
                <div className="border-8 border-transparent border-t-border-default" />
                <div className="border-8 border-transparent border-t-bg-primary absolute top-0 left-1/2 transform -translate-x-1/2 -mt-px" />
              </div>
            </div>
          )}

          {/* Date labels */}
          <div className="flex justify-between text-xs text-text-tertiary mt-2">
            <span>{data.length > 0 ? formatDate(data[0].date) : ''}</span>
            <span>{data.length > 0 ? formatDate(data[data.length - 1].date) : ''}</span>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-border-default text-xs text-text-secondary">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-success-500" />
              <span>Passed</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-warning-500" />
              <span>Warnings</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-error-500" />
              <span>Failed</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-border-default" />
              <span>No Runs</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
