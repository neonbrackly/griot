'use client'

import * as React from 'react'
import { LucideIcon, FileQuestion } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary'
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function EmptyState({
  icon: Icon = FileQuestion,
  title,
  description,
  action,
  secondaryAction,
  className,
  size = 'md',
}: EmptyStateProps) {
  const sizeConfig = {
    sm: {
      container: 'py-8',
      icon: 'w-10 h-10',
      title: 'text-base',
      description: 'text-sm',
    },
    md: {
      container: 'py-12',
      icon: 'w-12 h-12',
      title: 'text-lg',
      description: 'text-sm',
    },
    lg: {
      container: 'py-16',
      icon: 'w-16 h-16',
      title: 'text-xl',
      description: 'text-base',
    },
  }

  const config = sizeConfig[size]

  return (
    <div className={cn('flex flex-col items-center text-center', config.container, className)}>
      <div className="rounded-full bg-bg-tertiary p-4 mb-4">
        <Icon className={cn(config.icon, 'text-text-tertiary')} />
      </div>
      <h3 className={cn('font-semibold text-text-primary mb-1', config.title)}>
        {title}
      </h3>
      {description && (
        <p className={cn('text-text-secondary max-w-sm mb-4', config.description)}>
          {description}
        </p>
      )}
      {(action || secondaryAction) && (
        <div className="flex items-center gap-3 mt-2">
          {action && (
            <Button
              variant={action.variant || 'primary'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button variant="secondary" onClick={secondaryAction.onClick}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

// Pre-built empty states for common scenarios
export function NoResultsEmptyState({
  searchQuery,
  onClearSearch,
}: {
  searchQuery?: string
  onClearSearch?: () => void
}) {
  return (
    <EmptyState
      title="No results found"
      description={
        searchQuery
          ? `No results match "${searchQuery}". Try adjusting your search or filters.`
          : 'Try adjusting your search or filters.'
      }
      action={
        onClearSearch
          ? {
              label: 'Clear search',
              onClick: onClearSearch,
              variant: 'secondary',
            }
          : undefined
      }
    />
  )
}

export function ErrorEmptyState({
  title = 'Something went wrong',
  description = 'An error occurred while loading this data. Please try again.',
  onRetry,
}: {
  title?: string
  description?: string
  onRetry?: () => void
}) {
  return (
    <EmptyState
      title={title}
      description={description}
      action={
        onRetry
          ? {
              label: 'Try again',
              onClick: onRetry,
            }
          : undefined
      }
    />
  )
}
