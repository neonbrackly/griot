'use client'

import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Button, Badge } from '@/components/ui'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import type { SchemaDiff } from '@/lib/utils/schema-diff'

interface SchemaChangeDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (reason: string) => void
  isSubmitting?: boolean
  diff: SchemaDiff
  approverName?: string
}

export function SchemaChangeDialog({
  isOpen,
  onClose,
  onConfirm,
  isSubmitting = false,
  diff,
  approverName,
}: SchemaChangeDialogProps) {
  const [reason, setReason] = useState('')

  const handleConfirm = () => {
    if (reason.trim()) {
      onConfirm(reason)
      setReason('')
    }
  }

  const handleClose = () => {
    setReason('')
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-warning-text" />
            <DialogTitle>Schema Change Requires Re-approval</DialogTitle>
          </div>
          <DialogDescription>
            This contract is active and has been approved. Changing the schema will trigger a re-approval workflow.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          {/* What will happen */}
          <div className="p-4 rounded-lg border border-warning-border bg-warning-bg/10">
            <p className="text-sm font-medium text-warning-text mb-2">
              This action will:
            </p>
            <ul className="text-sm text-text-secondary space-y-1">
              <li>• Invalidate the current approval</li>
              <li>• Change status to &quot;Pending Review&quot;</li>
              <li>
                • Create a re-approval task for{' '}
                {approverName ? (
                  <span className="font-medium">{approverName}</span>
                ) : (
                  'the assigned reviewer'
                )}
              </li>
            </ul>
          </div>

          {/* Schema changes summary */}
          <div>
            <p className="text-sm font-medium text-text-primary mb-2">Schema Changes:</p>
            <div className="p-3 rounded-lg bg-bg-secondary text-sm">
              <p className="text-text-secondary">{diff.summary}</p>

              {/* Detailed changes */}
              <div className="mt-2 space-y-1">
                {diff.changes.addedTables.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="success" size="xs">+</Badge>
                    <span className="text-text-tertiary">
                      Tables: {diff.changes.addedTables.join(', ')}
                    </span>
                  </div>
                )}
                {diff.changes.removedTables.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="destructive" size="xs">-</Badge>
                    <span className="text-text-tertiary">
                      Tables: {diff.changes.removedTables.join(', ')}
                    </span>
                  </div>
                )}
                {diff.changes.addedFields.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="success" size="xs">+</Badge>
                    <span className="text-text-tertiary">
                      Fields: {diff.changes.addedFields.map((f) => `${f.table}.${f.field}`).join(', ')}
                    </span>
                  </div>
                )}
                {diff.changes.removedFields.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="destructive" size="xs">-</Badge>
                    <span className="text-text-tertiary">
                      Fields: {diff.changes.removedFields.map((f) => `${f.table}.${f.field}`).join(', ')}
                    </span>
                  </div>
                )}
                {diff.changes.modifiedFields.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Badge variant="warning" size="xs">~</Badge>
                    <span className="text-text-tertiary">
                      Modified: {diff.changes.modifiedFields.map((f) => `${f.table}.${f.field}`).join(', ')}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Reason input */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Reason for change <span className="text-error-text">*</span>
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 border border-border-default rounded-md bg-bg-primary text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
              placeholder="Explain why this schema change is needed..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isSubmitting || !reason.trim()}
          >
            {isSubmitting ? 'Processing...' : 'Proceed with Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
