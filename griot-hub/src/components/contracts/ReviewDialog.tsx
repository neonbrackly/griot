'use client'

import { useState } from 'react'
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

  const getDialogContent = () => {
    switch (type) {
      case 'request_changes':
        return {
          title: 'Request Changes',
          description:
            'Please provide feedback on what changes are needed for this contract.',
          placeholder: 'Describe the changes needed...',
          submitLabel: 'Request Changes',
          variant: 'destructive' as const,
        }
      case 'deprecate':
        return {
          title: 'Deprecate Contract',
          description:
            'This contract will be marked as deprecated. Please provide a reason.',
          placeholder: 'Reason for deprecation...',
          submitLabel: 'Deprecate Contract',
          variant: 'destructive' as const,
        }
      case 'submit_for_review':
        return {
          title: 'Submit for Review',
          description:
            'This contract will be submitted for review. Add any notes for the reviewer (optional).',
          placeholder: 'Optional notes for reviewer...',
          submitLabel: 'Submit for Review',
          variant: 'default' as const,
        }
    }
  }

  const content = getDialogContent()

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{content.title}</DialogTitle>
          <DialogDescription>{content.description}</DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <textarea
            className="w-full min-h-[100px] px-3 py-2 border border-border-default rounded-md bg-bg-primary text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
            placeholder={content.placeholder}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant={content.variant}
            onClick={handleSubmit}
            disabled={isSubmitting || (type === 'request_changes' && !feedback.trim())}
          >
            {isSubmitting ? 'Processing...' : content.submitLabel}
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
  variant?: 'default' | 'destructive'
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  isSubmitting = false,
  title,
  description,
  confirmLabel,
  variant = 'default',
}: ConfirmDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button variant={variant} onClick={onConfirm} disabled={isSubmitting}>
            {isSubmitting ? 'Processing...' : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
