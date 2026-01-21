'use client'

import { useState } from 'react'
import { Plus, Edit, Trash2, ChevronDown, ChevronRight, Shield, AlertCircle, Lock } from 'lucide-react'
import { Button, Badge } from '@/components/ui'
import { TableEditor, type TableData } from './TableEditor'
import { FieldEditor, type FieldData } from './FieldEditor'
import { ConfirmDialog } from './ReviewDialog'
import type { ContractStatus } from '@/types'

export interface SchemaTable {
  name: string
  physicalName?: string
  description?: string
  fields: FieldData[]
}

interface SchemaEditorProps {
  tables: SchemaTable[]
  onChange: (tables: SchemaTable[]) => void
  status: ContractStatus
  isReadOnly?: boolean
  onSchemaChange?: () => void // Called when schema changes on active contracts
}

export function SchemaEditor({
  tables,
  onChange,
  status,
  isReadOnly = false,
  onSchemaChange,
}: SchemaEditorProps) {
  const [expandedTables, setExpandedTables] = useState<Set<string>>(
    new Set(tables.map((t) => t.name))
  )
  const [showTableEditor, setShowTableEditor] = useState(false)
  const [showFieldEditor, setShowFieldEditor] = useState(false)
  const [editingTable, setEditingTable] = useState<SchemaTable | null>(null)
  const [editingField, setEditingField] = useState<{ table: string; field: FieldData | null } | null>(null)
  const [tableEditorMode, setTableEditorMode] = useState<'add' | 'edit'>('add')
  const [fieldEditorMode, setFieldEditorMode] = useState<'add' | 'edit'>('add')
  const [deleteConfirm, setDeleteConfirm] = useState<{ type: 'table' | 'field'; table: string; field?: string } | null>(null)

  // Determine if editing is allowed based on status
  const canEdit = !isReadOnly && (status === 'draft' || status === 'pending_review' || status === 'active')
  const isLocked = status === 'deprecated' || (status as string) === 'retired'
  const requiresReapproval = status === 'active'

  const toggleTable = (tableName: string) => {
    setExpandedTables((prev) => {
      const next = new Set(prev)
      if (next.has(tableName)) {
        next.delete(tableName)
      } else {
        next.add(tableName)
      }
      return next
    })
  }

  // Table operations
  const handleAddTable = () => {
    setEditingTable(null)
    setTableEditorMode('add')
    setShowTableEditor(true)
  }

  const handleEditTable = (table: SchemaTable) => {
    setEditingTable(table)
    setTableEditorMode('edit')
    setShowTableEditor(true)
  }

  const handleSaveTable = (tableData: TableData) => {
    if (tableEditorMode === 'add') {
      const newTable: SchemaTable = {
        ...tableData,
        fields: [],
      }
      onChange([...tables, newTable])
      setExpandedTables((prev) => new Set(prev).add(tableData.name))
    } else if (editingTable) {
      const updatedTables = tables.map((t) =>
        t.name === editingTable.name
          ? { ...t, ...tableData }
          : t
      )
      onChange(updatedTables)
    }
    setShowTableEditor(false)
    if (requiresReapproval && onSchemaChange) {
      onSchemaChange()
    }
  }

  const handleDeleteTable = (tableName: string) => {
    setDeleteConfirm({ type: 'table', table: tableName })
  }

  const confirmDeleteTable = () => {
    if (deleteConfirm?.type === 'table') {
      const updatedTables = tables.filter((t) => t.name !== deleteConfirm.table)
      onChange(updatedTables)
      if (requiresReapproval && onSchemaChange) {
        onSchemaChange()
      }
    }
    setDeleteConfirm(null)
  }

  // Field operations
  const handleAddField = (tableName: string) => {
    setEditingField({ table: tableName, field: null })
    setFieldEditorMode('add')
    setShowFieldEditor(true)
  }

  const handleEditField = (tableName: string, field: FieldData) => {
    setEditingField({ table: tableName, field })
    setFieldEditorMode('edit')
    setShowFieldEditor(true)
  }

  const handleSaveField = (fieldData: FieldData) => {
    if (!editingField) return

    const updatedTables = tables.map((table) => {
      if (table.name !== editingField.table) return table

      if (fieldEditorMode === 'add') {
        return {
          ...table,
          fields: [...table.fields, fieldData],
        }
      } else if (editingField.field) {
        return {
          ...table,
          fields: table.fields.map((f) =>
            f.name === editingField.field!.name ? fieldData : f
          ),
        }
      }
      return table
    })

    onChange(updatedTables)
    setShowFieldEditor(false)
    if (requiresReapproval && onSchemaChange) {
      onSchemaChange()
    }
  }

  const handleDeleteField = (tableName: string, fieldName: string) => {
    setDeleteConfirm({ type: 'field', table: tableName, field: fieldName })
  }

  const confirmDeleteField = () => {
    if (deleteConfirm?.type === 'field' && deleteConfirm.field) {
      const updatedTables = tables.map((table) => {
        if (table.name !== deleteConfirm.table) return table
        return {
          ...table,
          fields: table.fields.filter((f) => f.name !== deleteConfirm.field),
        }
      })
      onChange(updatedTables)
      if (requiresReapproval && onSchemaChange) {
        onSchemaChange()
      }
    }
    setDeleteConfirm(null)
  }

  const existingTableNames = tables.map((t) => t.name.toLowerCase())

  return (
    <div className="space-y-4">
      {/* Status Banner */}
      {isLocked && (
        <div className="p-4 rounded-lg border border-border-default bg-bg-secondary">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-text-tertiary" />
            <span className="text-sm font-medium text-text-secondary">
              Schema is read-only
            </span>
          </div>
          <p className="text-xs text-text-tertiary mt-1">
            This contract is {status}. Schema cannot be modified.
            {status === 'deprecated' && ' Consider creating a replacement contract.'}
          </p>
        </div>
      )}

      {status === 'pending_review' && canEdit && (
        <div className="p-4 rounded-lg border border-info-border bg-info-bg/10">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-info-text" />
            <span className="text-sm font-medium text-info-text">Under Review</span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            This contract is under review. Schema changes will be visible to the reviewer.
          </p>
        </div>
      )}

      {requiresReapproval && canEdit && (
        <div className="p-4 rounded-lg border border-warning-border bg-warning-bg/10">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-warning-text" />
            <span className="text-sm font-medium text-warning-text">Re-approval Required</span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            This contract is active. Schema changes will require re-approval.
          </p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-text-primary">Schema</h3>
        {canEdit && (
          <Button size="sm" onClick={handleAddTable}>
            <Plus className="h-4 w-4 mr-1" />
            Add Table
          </Button>
        )}
      </div>

      {/* Tables */}
      <div className="space-y-3">
        {tables.length === 0 ? (
          <div className="text-center py-8 text-text-tertiary">
            <p>No tables defined.</p>
            {canEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleAddTable}
                className="mt-2"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add your first table
              </Button>
            )}
          </div>
        ) : (
          tables.map((table) => (
            <div
              key={table.name}
              className="border border-border-default rounded-lg overflow-hidden"
            >
              {/* Table Header */}
              <div
                className="flex items-center justify-between p-3 bg-bg-secondary cursor-pointer"
                onClick={() => toggleTable(table.name)}
              >
                <div className="flex items-center gap-2">
                  {expandedTables.has(table.name) ? (
                    <ChevronDown className="h-4 w-4 text-text-tertiary" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-text-tertiary" />
                  )}
                  <span className="font-medium text-text-primary">{table.name}</span>
                  <Badge variant="secondary" size="xs">
                    {table.fields.length} fields
                  </Badge>
                  {table.fields.some((f) => f.piiClassification) && (
                    <Badge variant="warning" size="xs" className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      PII
                    </Badge>
                  )}
                </div>
                {canEdit && (
                  <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditTable(table)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteTable(table.name)}
                    >
                      <Trash2 className="h-4 w-4 text-error-text" />
                    </Button>
                  </div>
                )}
              </div>

              {/* Fields */}
              {expandedTables.has(table.name) && (
                <div className="p-3 space-y-2">
                  {table.fields.length === 0 ? (
                    <p className="text-sm text-text-tertiary text-center py-2">
                      No fields defined.
                    </p>
                  ) : (
                    table.fields.map((field) => (
                      <div
                        key={field.name}
                        className="flex items-center justify-between p-2 rounded bg-bg-primary border border-border-default"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm text-text-primary">
                            {field.name}
                          </span>
                          {field.primaryKey && (
                            <Badge variant="primary" size="xs">PK</Badge>
                          )}
                          {field.required && (
                            <Badge variant="secondary" size="xs">Required</Badge>
                          )}
                          {field.piiClassification && (
                            <Badge variant="warning" size="xs">
                              PII: {field.piiClassification}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-text-tertiary">
                            {field.logicalType}
                          </span>
                          {canEdit && (
                            <div className="flex items-center gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEditField(table.name, field)}
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteField(table.name, field.name)}
                              >
                                <Trash2 className="h-3 w-3 text-error-text" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                  {canEdit && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAddField(table.name)}
                      className="w-full mt-2"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Add Field
                    </Button>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Table Editor Dialog */}
      <TableEditor
        isOpen={showTableEditor}
        onClose={() => setShowTableEditor(false)}
        onSave={handleSaveTable}
        table={editingTable}
        existingTableNames={
          tableEditorMode === 'add'
            ? existingTableNames
            : existingTableNames.filter((n) => n !== editingTable?.name.toLowerCase())
        }
        mode={tableEditorMode}
      />

      {/* Field Editor Dialog */}
      {editingField && (
        <FieldEditor
          isOpen={showFieldEditor}
          onClose={() => setShowFieldEditor(false)}
          onSave={handleSaveField}
          field={editingField.field}
          existingFieldNames={
            tables
              .find((t) => t.name === editingField.table)
              ?.fields.map((f) => f.name.toLowerCase())
              .filter((n) =>
                fieldEditorMode === 'edit' && editingField.field
                  ? n !== editingField.field.name.toLowerCase()
                  : true
              ) || []
          }
          mode={fieldEditorMode}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm !== null}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={deleteConfirm?.type === 'table' ? confirmDeleteTable : confirmDeleteField}
        title={`Delete ${deleteConfirm?.type === 'table' ? 'Table' : 'Field'}`}
        description={
          deleteConfirm?.type === 'table'
            ? `Are you sure you want to delete the table "${deleteConfirm.table}"? This will also delete all its fields.`
            : `Are you sure you want to delete the field "${deleteConfirm?.field}"?`
        }
        confirmLabel="Delete"
        variant="destructive"
      />
    </div>
  )
}
