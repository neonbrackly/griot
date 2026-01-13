'use client'

import * as React from 'react'
import {
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle,
  FileEdit,
  Archive,
  Lightbulb,
  Loader2,
} from 'lucide-react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

// Contract Status Types
export type ContractStatus =
  | 'draft'
  | 'proposed'
  | 'pending_review'
  | 'active'
  | 'deprecated'

// Issue Severity Types
export type IssueSeverity = 'critical' | 'warning' | 'info' | 'resolved'

// Generic Status Types
export type GenericStatus =
  | 'active'
  | 'inactive'
  | 'pending'
  | 'success'
  | 'error'
  | 'warning'
  | 'loading'

const statusBadgeVariants = cva(
  'inline-flex items-center gap-1.5 font-medium rounded-full',
  {
    variants: {
      size: {
        xs: 'h-5 px-2 text-xs',
        sm: 'h-6 px-2.5 text-xs',
        md: 'h-7 px-3 text-sm',
        lg: 'h-8 px-3.5 text-sm',
      },
    },
    defaultVariants: {
      size: 'sm',
    },
  }
)

interface StatusBadgeProps extends VariantProps<typeof statusBadgeVariants> {
  className?: string
}

// Contract Status Badge
interface ContractStatusBadgeProps extends StatusBadgeProps {
  status: ContractStatus
}

const contractStatusConfig: Record<
  ContractStatus,
  { label: string; icon: React.ComponentType<{ className?: string }>; className: string }
> = {
  draft: {
    label: 'Draft',
    icon: FileEdit,
    className: 'bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300',
  },
  proposed: {
    label: 'Proposed',
    icon: Lightbulb,
    className: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  },
  pending_review: {
    label: 'Pending Review',
    icon: Clock,
    className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  },
  active: {
    label: 'Active',
    icon: CheckCircle2,
    className: 'bg-success-bg text-success-text',
  },
  deprecated: {
    label: 'Deprecated',
    icon: Archive,
    className: 'bg-neutral-100 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400',
  },
}

export function ContractStatusBadge({ status, size, className }: ContractStatusBadgeProps) {
  const config = contractStatusConfig[status]
  const Icon = config.icon

  return (
    <span className={cn(statusBadgeVariants({ size }), config.className, className)}>
      <Icon className="h-3.5 w-3.5" />
      {config.label}
    </span>
  )
}

// Issue Severity Badge
interface IssueSeverityBadgeProps extends StatusBadgeProps {
  severity: IssueSeverity
}

const severityConfig: Record<
  IssueSeverity,
  { label: string; icon: React.ComponentType<{ className?: string }>; className: string }
> = {
  critical: {
    label: 'Critical',
    icon: XCircle,
    className: 'bg-error-bg text-error-text',
  },
  warning: {
    label: 'Warning',
    icon: AlertCircle,
    className: 'bg-warning-bg text-warning-text',
  },
  info: {
    label: 'Info',
    icon: AlertCircle,
    className: 'bg-info-bg text-info-text',
  },
  resolved: {
    label: 'Resolved',
    icon: CheckCircle2,
    className: 'bg-success-bg text-success-text',
  },
}

export function IssueSeverityBadge({ severity, size, className }: IssueSeverityBadgeProps) {
  const config = severityConfig[severity]
  const Icon = config.icon

  return (
    <span className={cn(statusBadgeVariants({ size }), config.className, className)}>
      <Icon className="h-3.5 w-3.5" />
      {config.label}
    </span>
  )
}

// Generic Status Badge
interface GenericStatusBadgeProps extends StatusBadgeProps {
  status: GenericStatus
  label?: string
}

const genericStatusConfig: Record<
  GenericStatus,
  { label: string; icon: React.ComponentType<{ className?: string }>; className: string }
> = {
  active: {
    label: 'Active',
    icon: CheckCircle2,
    className: 'bg-success-bg text-success-text',
  },
  inactive: {
    label: 'Inactive',
    icon: XCircle,
    className: 'bg-neutral-100 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400',
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-warning-bg text-warning-text',
  },
  success: {
    label: 'Success',
    icon: CheckCircle2,
    className: 'bg-success-bg text-success-text',
  },
  error: {
    label: 'Error',
    icon: XCircle,
    className: 'bg-error-bg text-error-text',
  },
  warning: {
    label: 'Warning',
    icon: AlertCircle,
    className: 'bg-warning-bg text-warning-text',
  },
  loading: {
    label: 'Loading',
    icon: Loader2,
    className: 'bg-info-bg text-info-text',
  },
}

export function StatusBadge({ status, label, size, className }: GenericStatusBadgeProps) {
  const config = genericStatusConfig[status]
  const Icon = config.icon

  return (
    <span className={cn(statusBadgeVariants({ size }), config.className, className)}>
      <Icon className={cn('h-3.5 w-3.5', status === 'loading' && 'animate-spin')} />
      {label || config.label}
    </span>
  )
}
