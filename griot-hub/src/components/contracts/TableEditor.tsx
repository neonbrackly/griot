'use client'

import { useState, useEffect } from 'react'
import { Button, Input } from '@/components/ui'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { FormField } from '@/components/forms/FormField'

export interface TableData {
  name: string
  physicalName?: string
  description?: string
}

interface TableEditorProps {
  isOpen: boolean
  onClose: () => void
  onSave: (table: TableData) => void
  table?: TableData | null
  existingTableNames: string[]
  mode: 'add' | 'edit'
}

export function TableEditor({
  isOpen,
  onClose,
  onSave,
  table,
  existingTableNames,
  mode,
}: TableEditorProps) {
  const [formData, setFormData] = useState<TableData>({
    name: '',
    description: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (table && mode === 'edit') {
      setFormData({
        name: table.name,
        physicalName: table.physicalName,
        description: table.description || '',
      })
    } else {
      setFormData({
        name: '',
        description: '',
      })
    }
    setErrors({})
  }, [table, mode, isOpen])

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name || formData.name.length < 1) {
      newErrors.name = 'Table name is required'
    } else if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(formData.name)) {
      newErrors.name = 'Table name must start with letter or underscore and contain only letters, numbers, underscores'
    } else if (
      mode === 'add' &&
      existingTableNames.includes(formData.name.toLowerCase())
    ) {
      newErrors.name = 'A table with this name already exists'
    } else if (
      mode === 'edit' &&
      table &&
      formData.name.toLowerCase() !== table.name.toLowerCase() &&
      existingTableNames.includes(formData.name.toLowerCase())
    ) {
      newErrors.name = 'A table with this name already exists'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSave = () => {
    if (validate()) {
      onSave({
        ...formData,
        physicalName: formData.physicalName || formData.name,
      })
    }
  }

  const updateField = <K extends keyof TableData>(key: K, value: TableData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: '' }))
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{mode === 'add' ? 'Add Table' : 'Edit Table'}</DialogTitle>
          <DialogDescription>
            {mode === 'add'
              ? 'Add a new table to the contract schema.'
              : 'Edit the table properties.'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <FormField name="name" label="Table Name" error={errors.name} required>
            <Input
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="e.g. customers"
            />
          </FormField>

          <FormField name="physicalName" label="Physical Name" description="Database table name (defaults to table name)">
            <Input
              value={formData.physicalName || ''}
              onChange={(e) => updateField('physicalName', e.target.value)}
              placeholder="e.g. tbl_customers"
            />
          </FormField>

          <FormField name="description" label="Description">
            <textarea
              className="w-full min-h-[80px] px-3 py-2 border border-border-default rounded-md bg-bg-primary text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-border focus:border-transparent"
              value={formData.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Describe this table..."
            />
          </FormField>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            {mode === 'add' ? 'Add Table' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
