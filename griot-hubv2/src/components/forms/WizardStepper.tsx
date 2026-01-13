'use client'

import * as React from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Step {
  id: string
  label: string
  description?: string
}

interface WizardStepperProps {
  steps: Step[]
  currentStep: number
  onStepClick?: (stepIndex: number) => void
  allowNavigation?: boolean
  orientation?: 'horizontal' | 'vertical'
  className?: string
}

export function WizardStepper({
  steps,
  currentStep,
  onStepClick,
  allowNavigation = false,
  orientation = 'horizontal',
  className,
}: WizardStepperProps) {
  const isHorizontal = orientation === 'horizontal'

  const getStepStatus = (index: number) => {
    if (index < currentStep) return 'completed'
    if (index === currentStep) return 'current'
    return 'upcoming'
  }

  const handleStepClick = (index: number) => {
    if (!allowNavigation || !onStepClick) return
    // Only allow clicking on completed steps or current step
    if (index <= currentStep) {
      onStepClick(index)
    }
  }

  return (
    <nav aria-label="Progress" className={className}>
      <ol
        className={cn(
          'flex',
          isHorizontal ? 'items-center' : 'flex-col space-y-4'
        )}
      >
        {steps.map((step, index) => {
          const status = getStepStatus(index)
          const isLast = index === steps.length - 1
          const isClickable = allowNavigation && index <= currentStep

          return (
            <li
              key={step.id}
              className={cn(
                isHorizontal && !isLast && 'flex-1',
                isHorizontal ? 'flex items-center' : 'relative'
              )}
            >
              <div
                className={cn(
                  'flex items-center',
                  isHorizontal ? 'gap-3' : 'gap-4',
                  isClickable && 'cursor-pointer group'
                )}
                onClick={() => handleStepClick(index)}
                role={isClickable ? 'button' : undefined}
                tabIndex={isClickable ? 0 : undefined}
                onKeyDown={(e) => {
                  if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
                    handleStepClick(index)
                  }
                }}
              >
                {/* Step indicator */}
                <div
                  className={cn(
                    'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors',
                    status === 'completed' &&
                      'bg-primary-600 border-primary-600 text-white',
                    status === 'current' &&
                      'border-primary-600 bg-primary-50 text-primary-600 dark:bg-primary-900/30',
                    status === 'upcoming' &&
                      'border-border-default bg-bg-secondary text-text-tertiary',
                    isClickable &&
                      'group-hover:border-primary-400 group-hover:bg-primary-50 dark:group-hover:bg-primary-900/20'
                  )}
                >
                  {status === 'completed' ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    index + 1
                  )}
                </div>

                {/* Step text */}
                <div className={cn('min-w-0', isHorizontal && 'hidden sm:block')}>
                  <p
                    className={cn(
                      'text-sm font-medium',
                      status === 'current'
                        ? 'text-primary-600'
                        : status === 'completed'
                        ? 'text-text-primary'
                        : 'text-text-tertiary'
                    )}
                  >
                    {step.label}
                  </p>
                  {step.description && (
                    <p className="text-xs text-text-tertiary mt-0.5 truncate">
                      {step.description}
                    </p>
                  )}
                </div>
              </div>

              {/* Connector line (horizontal) */}
              {isHorizontal && !isLast && (
                <div
                  className={cn(
                    'flex-1 h-0.5 mx-4',
                    status === 'completed' || index < currentStep
                      ? 'bg-primary-600'
                      : 'bg-border-default'
                  )}
                />
              )}

              {/* Connector line (vertical) */}
              {!isHorizontal && !isLast && (
                <div
                  className={cn(
                    'absolute left-4 top-8 -translate-x-1/2 w-0.5 h-8',
                    status === 'completed' ? 'bg-primary-600' : 'bg-border-default'
                  )}
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

// Compact version for mobile or narrow spaces
export function WizardStepperCompact({
  steps,
  currentStep,
  className,
}: Omit<WizardStepperProps, 'orientation'>) {
  return (
    <div className={cn('flex items-center justify-center gap-2', className)}>
      {steps.map((step, index) => {
        const status =
          index < currentStep
            ? 'completed'
            : index === currentStep
            ? 'current'
            : 'upcoming'

        return (
          <React.Fragment key={step.id}>
            <div
              className={cn(
                'h-2 w-2 rounded-full transition-colors',
                status === 'completed' && 'bg-primary-600',
                status === 'current' && 'bg-primary-600 ring-4 ring-primary-100 dark:ring-primary-900/30',
                status === 'upcoming' && 'bg-border-strong'
              )}
            />
          </React.Fragment>
        )
      })}
      <span className="ml-3 text-sm text-text-secondary">
        Step {currentStep + 1} of {steps.length}
      </span>
    </div>
  )
}
