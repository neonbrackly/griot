'use client'

import React, { useState } from 'react'
import { Send, AlertTriangle, Archive, MessageSquare, Loader2, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'

interface ReviewDialogProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (feedback: string) => void
  isSubmitting?: boolean
  type: 'request_changes' | 'deprecate' | 'submit_for_review'
}

export function ReviewDialog({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  type,
}: ReviewDialogProps) {
  const [feedback, setFeedback] = useState('')

  const handleSubmit = () => {
    onSubmit(feedback)
    setFeedback('')
  }

  const handleClose = () => {
    setFeedback('')
    onClose()
  }

  const getDialogContent = () => {
    switch (type) {
      case 'request_changes':
        return {
          title: 'Request Changes',
          description:
            'Please provide feedback on what changes are needed for this contract.',
          placeholder: 'Describe the changes needed...\n\nFor example:\n- Missing field descriptions\n- Quality rules need adjustment\n- SLA values are too strict',
          submitLabel: 'Request Changes',
          variant: 'danger' as const,
          icon: AlertTriangle,
          iconBg: 'bg-status-error/10',
          iconColor: 'text-status-error',
          borderColor: 'border-l-status-error',
          required: true,
        }
      case 'deprecate':
        return {
          title: 'Deprecate Contract',
          description:
            'This contract will be marked as deprecated and will no longer be active.',
          placeholder: 'Reason for deprecation...\n\nFor example:\n- Replaced by a newer contract\n- Data source no longer available\n- Business requirements changed',
          submitLabel: 'Deprecate Contract',
          variant: 'danger' as const,
          icon: Archive,
          iconBg: 'bg-status-warning/10',
          iconColor: 'text-status-warning',
          borderColor: 'border-l-status-warning',
          required: true,
        }
      case 'submit_for_review':
        return {
          title: 'Submit for Review',
          description:
            'This contract will be submitted for review by the assigned reviewer.',
          placeholder: 'Add any notes for the reviewer (optional)...\n\nFor example:\n- Please review the PII classifications\n- Quality rules based on last quarter metrics\n- Ready for production use',
          submitLabel: 'Submit for Review',
          variant: 'primary' as const,
          icon: Send,
          iconBg: 'bg-primary-500/10',
          iconColor: 'text-primary-500',
          borderColor: 'border-l-primary-500',
          required: false,
        }
    }
  }

  const content = getDialogContent()
  const Icon = content.icon

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className={`sm:max-w-[480px] border-l-4 ${content.borderColor} p-0 overflow-hidden`}>
        <div className="p-6">
          <DialogHeader className="p-0 pb-4">
            <div className="flex items-start gap-4">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full ${content.iconBg} flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${content.iconColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                <DialogTitle className="text-xl font-semibold">{content.title}</DialogTitle>
                <DialogDescription className="mt-1">{content.description}</DialogDescription>
              </div>
            </div>
          </DialogHeader>

          <div className="mt-4">
            <label className="block text-sm font-medium text-text-primary mb-2">
              <span className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-text-tertiary" />
                {content.required ? 'Feedback (required)' : 'Notes for reviewer'}
              </span>
            </label>
            <textarea
              className="w-full min-h-[140px] px-4 py-3 border border-border-default rounded-lg bg-bg-primary text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent resize-none transition-colors"
              placeholder={content.placeholder}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              autoFocus
            />
            {content.required && !feedback.trim() && (
              <p className="mt-2 text-xs text-text-tertiary">
                Please provide a reason to continue
              </p>
            )}
          </div>
        </div>

        <DialogFooter className="bg-bg-tertiary border-t border-border-subtle p-4 mt-0">
          <Button variant="ghost" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant={content.variant}
            onClick={handleSubmit}
            disabled={isSubmitting || (content.required && !feedback.trim())}
            className="min-w-[140px]"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Icon className="w-4 h-4 mr-2" />
                {content.submitLabel}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Confirmation dialog for approve action
interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  isSubmitting?: boolean
  title: string
  description: string
  confirmLabel: string
  variant?: 'primary' | 'danger'
  icon?: React.ComponentType<{ className?: string }>
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  isSubmitting = false,
  title,
  description,
  confirmLabel,
  variant = 'primary',
  icon: CustomIcon,
}: ConfirmDialogProps) {
  // Default icon based on variant
  const Icon = CustomIcon || (variant === 'danger' ? AlertTriangle : Send)

  // Check if this is an approve/success action (CheckCircle icon)
  const isSuccess = CustomIcon === CheckCircle

  const iconBg = variant === 'danger'
    ? 'bg-status-error/10'
    : isSuccess
      ? 'bg-status-success/10'
      : 'bg-primary-500/10'
  const iconColor = variant === 'danger'
    ? 'text-status-error'
    : isSuccess
      ? 'text-status-success'
      : 'text-primary-500'
  const borderColor = variant === 'danger'
    ? 'border-l-status-error'
    : isSuccess
      ? 'border-l-status-success'
      : 'border-l-primary-500'

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-[420px] border-l-4 ${borderColor} p-0 overflow-hidden`}>
        <div className="p-6">
          <DialogHeader className="p-0">
            <div className="flex items-start gap-4">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full ${iconBg} flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${iconColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                <DialogTitle className="text-xl font-semibold">{title}</DialogTitle>
                <DialogDescription className="mt-1">{description}</DialogDescription>
              </div>
            </div>
          </DialogHeader>
        </div>

        <DialogFooter className="bg-bg-tertiary border-t border-border-subtle p-4 mt-0">
          <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant={variant}
            onClick={onConfirm}
            disabled={isSubmitting}
            className="min-w-[120px]"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Icon className="w-4 h-4 mr-2" />
                {confirmLabel}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
