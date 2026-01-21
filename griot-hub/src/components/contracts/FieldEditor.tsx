'use client'

import { useState, useEffect } from 'react'
import { Button, Input } from '@/components/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { FormField } from '@/components/forms/FormField'

// Field types supported by the system
const FIELD_TYPES = [
  { value: 'string', label: 'String' },
  { value: 'integer', label: 'Integer' },
  { value: 'number', label: 'Number' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'date', label: 'Date' },
  { value: 'timestamp', label: 'Timestamp' },
  { value: 'array', label: 'Array' },
  { value: 'object', label: 'Object' },
]

// PII categories
const PII_CATEGORIES = [
  { value: '', label: 'None' },
  { value: 'personal', label: 'Personal (name, email, phone)' },
  { value: 'financial', label: 'Financial (account numbers)' },
  { value: 'health', label: 'Health (medical records)' },
  { value: 'sensitive', label: 'Sensitive (SSN, passport)' },
  { value: 'behavioral', label: 'Behavioral (usage patterns)' },
]

export interface FieldData {
  name: string
  logicalType: string
  physicalType?: string
  description?: string
  required: boolean
  unique?: boolean
  primaryKey: boolean
  piiClassification?: string
}

interface FieldEditorProps {
  isOpen: boolean
  onClose: () => void
  onSave: (field: FieldData) => void
  field?: FieldData | null
  existingFieldNames: string[]
  mode: 'add' | 'edit'
}

export function FieldEditor({
  isOpen,
  onClose,
  onSave,
  field,
  existingFieldNames,
  mode,
}: FieldEditorProps) {
  const [formData, setFormData] = useState<FieldData>({
    name: '',
    logicalType: 'string',
    description: '',
    required: false,
    primaryKey: false,
    piiClassification: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (field && mode === 'edit') {
      setFormData({
        name: field.name,
        logicalType: field.logicalType || 'string',
        physicalType: field.physicalType,
        description: field.description || '',
        required: field.required,
        unique: field.unique,
        primaryKey: field.primaryKey,
        piiClassification: field.piiClassification || '',
      })
    } else {
      setFormData({
        name: '',
        logicalType: 'string',
        description: '',
        required: false,
        primaryKey: false,
        piiClassification: '',
      })
    }
    setErrors({})
  }, [field, mode, isOpen])

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name || formData.name.length < 1) {
      newErrors.name = 'Field name is required'
    } else if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(formData.name)) {
      newErrors.name = 'Field name must start with letter or underscore and contain only letters, numbers, underscores'
    } else if (
      mode === 'add' &&
      existingFieldNames.includes(formData.name.toLowerCase())
    ) {
      newErrors.name = 'A field with this name already exists'
    } else if (
      mode === 'edit' &&
      field &&
      formData.name.toLowerCase() !== field.name.toLowerCase() &&
      existingFieldNames.includes(formData.name.toLowerCase())
    ) {
      newErrors.name = 'A field with this name already exists'
    }

    if (!formData.logicalType) {
      newErrors.logicalType = 'Field type is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSave = () => {
    if (validate()) {
      onSave({
        ...formData,
        physicalType: formData.physicalType || formData.logicalType,
      })
    }
  }

  const updateField = <K extends keyof FieldData>(key: K, value: FieldData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: '' }))
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{mode === 'add' ? 'Add Field' : 'Edit Field'}</DialogTitle>
          <DialogDescription>
            {mode === 'add'
              ? 'Add a new field to the table schema.'
              : 'Edit the field properties.'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <FormField name="name" label="Field Name" error={errors.name} required>
            <Input
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="e.g. customer_id"
            />
          </FormField>

          <FormField name="logicalType" label="Type" error={errors.logicalType} required>
            <Select
              value={formData.logicalType}
              onValueChange={(value) => updateField('logicalType', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {FIELD_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>

          <FormField name="description" label="Description">
            <Input
              value={formData.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Describe this field..."
            />
          </FormField>

          <div className="grid grid-cols-2 gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.required}
                onChange={(e) => updateField('required', e.target.checked)}
                className="h-4 w-4 rounded border-border-default text-primary-500 focus:ring-primary-500"
              />
              <span className="text-sm text-text-primary">Required</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.primaryKey}
                onChange={(e) => updateField('primaryKey', e.target.checked)}
                className="h-4 w-4 rounded border-border-default text-primary-500 focus:ring-primary-500"
              />
              <span className="text-sm text-text-primary">Primary Key</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.unique || false}
                onChange={(e) => updateField('unique', e.target.checked)}
                className="h-4 w-4 rounded border-border-default text-primary-500 focus:ring-primary-500"
              />
              <span className="text-sm text-text-primary">Unique</span>
            </label>
          </div>

          <FormField
            name="piiClassification"
            label="PII Classification"
            description="Mark if this field contains personally identifiable information"
          >
            <Select
              value={formData.piiClassification || ''}
              onValueChange={(value) => updateField('piiClassification', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select PII category" />
              </SelectTrigger>
              <SelectContent>
                {PII_CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            {mode === 'add' ? 'Add Field' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
