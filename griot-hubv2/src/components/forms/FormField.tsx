'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Label } from '@/components/ui/Label'

interface FormFieldProps {
  name: string
  label?: string
  description?: string
  required?: boolean
  error?: string
  className?: string
  children: React.ReactNode
}

export function FormField({
  name,
  label,
  description,
  required,
  error,
  className,
  children,
}: FormFieldProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <div className="flex items-center gap-1">
          <Label htmlFor={name}>
            {label}
            {required && <span className="text-error-text ml-1">*</span>}
          </Label>
        </div>
      )}
      {description && (
        <p className="text-sm text-text-tertiary">{description}</p>
      )}
      {children}
      {error && (
        <p className="text-sm text-error-text" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

// Form section grouping
interface FormSectionProps {
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function FormSection({ title, description, children, className }: FormSectionProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && (
            <h3 className="text-sm font-medium text-text-primary">{title}</h3>
          )}
          {description && (
            <p className="text-sm text-text-tertiary">{description}</p>
          )}
        </div>
      )}
      <div className="space-y-4">{children}</div>
    </div>
  )
}

// Form actions wrapper
interface FormActionsProps {
  children: React.ReactNode
  className?: string
  align?: 'left' | 'right' | 'center' | 'between'
}

export function FormActions({ children, className, align = 'right' }: FormActionsProps) {
  const alignClasses = {
    left: 'justify-start',
    right: 'justify-end',
    center: 'justify-center',
    between: 'justify-between',
  }

  return (
    <div
      className={cn(
        'flex items-center gap-3 pt-6 border-t border-border-default',
        alignClasses[align],
        className
      )}
    >
      {children}
    </div>
  )
}
