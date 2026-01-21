'use client'

import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-bg-tertiary text-text-secondary',
        primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
        secondary: 'bg-bg-tertiary text-text-secondary',
        success: 'bg-success-bg text-success-text',
        warning: 'bg-warning-bg text-warning-text',
        error: 'bg-error-bg text-error-text',
        info: 'bg-info-bg text-info-text',
        outline: 'border border-border-default bg-transparent text-text-secondary',
      },
      size: {
        xs: 'h-5 px-1.5 text-xs rounded',
        sm: 'h-6 px-2 text-xs rounded-md',
        md: 'h-7 px-2.5 text-sm rounded-md',
        lg: 'h-8 px-3 text-sm rounded-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'sm',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  icon?: React.ReactNode
}

function Badge({ className, variant, size, icon, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {icon && <span className="mr-1 shrink-0">{icon}</span>}
      {children}
    </div>
  )
}

export { Badge, badgeVariants }
