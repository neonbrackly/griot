'use client'

import * as React from 'react'
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ChevronRight,
  ChevronDown,
  Table as TableIcon,
  Database as DatabaseIcon,
  Search,
  Eye,
  X,
} from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/feedback/Skeleton'
import { cn, formatNumber } from '@/lib/utils'
import { api, queryKeys } from '@/lib/api/client'
import type {
  AssetFormData,
  DatabaseStructure,
  DatabaseSchema,
  SelectedTable,
} from '@/types'

interface Step2Props {
  data: AssetFormData
  onUpdate: (data: Partial<AssetFormData>) => void
  onBack: () => void
  onNext: () => void
}

// Schema Tree Node Component
function SchemaNode({
  schema,
  expanded,
  onToggle,
  selectedTables,
  onToggleTable,
  onPreview,
}: {
  schema: DatabaseSchema
  expanded: boolean
  onToggle: () => void
  selectedTables: SelectedTable[]
  onToggleTable: (schemaName: string, tableName: string) => void
  onPreview: (tableId: string) => void
}) {
  const selectedInSchema = selectedTables.filter((t) => t.schema === schema.name).length

  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-bg-hover transition-colors"
      >
        <div className="flex items-center gap-2">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-text-tertiary" />
          ) : (
            <ChevronRight className="w-4 h-4 text-text-tertiary" />
          )}
          <DatabaseIcon className="w-4 h-4 text-text-secondary" />
          <span className="font-medium text-text-primary">{schema.name}</span>
          <Badge variant="secondary" className="text-xs">
            {schema.tables.length} tables
          </Badge>
        </div>
        {selectedInSchema > 0 && (
          <Badge variant="default" className="text-xs bg-primary-500 text-white">
            {selectedInSchema} selected
          </Badge>
        )}
      </button>

      {expanded && (
        <div className="pl-8 py-1 space-y-1">
          {schema.tables.map((table) => {
            const tableId = `${schema.name}.${table.name}`
            const isSelected = selectedTables.some((t) => t.id === tableId)

            return (
              <div
                key={table.name}
                className={cn(
                  'flex items-center justify-between px-3 py-2 rounded-md',
                  'hover:bg-bg-hover transition-colors',
                  isSelected && 'bg-primary-50 dark:bg-primary-900/20'
                )}
              >
                <label className="flex items-center gap-3 cursor-pointer flex-1">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() => onToggleTable(schema.name, table.name)}
                  />
                  <TableIcon className="w-4 h-4 text-text-tertiary" />
                  <span className="text-sm text-text-primary">{table.name}</span>
                  <span className="text-xs text-text-tertiary">
                    {table.columns?.length || 0} cols
                  </span>
                </label>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onPreview(tableId)}
                  className="h-7 w-7"
                >
                  <Eye className="w-4 h-4" />
                </Button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Selected Table Card Component
function SelectedTableCard({
  table,
  onRemove,
}: {
  table: SelectedTable
  onRemove: () => void
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
      <div className="flex items-center gap-2">
        <TableIcon className="w-4 h-4 text-text-secondary" />
        <div>
          <div className="text-sm font-medium text-text-primary">
            {table.schema}.{table.name}
          </div>
          <div className="text-xs text-text-tertiary">
            {table.columns?.length || 0} columns
            {table.rowCount && ` • ${formatNumber(table.rowCount)} rows`}
          </div>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={onRemove}
        className="h-7 w-7 text-text-tertiary hover:text-error-text"
      >
        <X className="w-4 h-4" />
      </Button>
    </div>
  )
}

// Database Browser Skeleton
function DatabaseBrowserSkeleton() {
  return (
    <div className="space-y-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="px-4 py-3">
          <Skeleton className="h-5 w-full" />
        </div>
      ))}
    </div>
  )
}

export function Step2Tables({ data, onUpdate, onBack, onNext }: Step2Props) {
  const [search, setSearch] = useState('')
  const [expandedSchemas, setExpandedSchemas] = useState<Set<string>>(new Set())
  const [previewTable, setPreviewTable] = useState<string | null>(null)

  // Fetch database structure
  const { data: dbStructure, isLoading } = useQuery({
    queryKey: queryKeys.connections.browse(data.connectionId!),
    queryFn: () => api.get<DatabaseStructure>(`/connections/${data.connectionId}/browse`),
    enabled: !!data.connectionId,
  })

  // Filter tables by search
  const filteredStructure = useMemo(() => {
    if (!search || !dbStructure) return dbStructure

    const searchLower = search.toLowerCase()
    return {
      schemas: dbStructure.schemas
        .map((schema) => ({
          ...schema,
          tables: schema.tables.filter((table) =>
            table.name.toLowerCase().includes(searchLower)
          ),
        }))
        .filter((schema) => schema.tables.length > 0),
    }
  }, [dbStructure, search])

  const selectedTables = data.selectedTables || []

  const toggleTable = (schemaName: string, tableName: string) => {
    const tableId = `${schemaName}.${tableName}`
    const isSelected = selectedTables.some((t) => t.id === tableId)

    if (isSelected) {
      onUpdate({
        selectedTables: selectedTables.filter((t) => t.id !== tableId),
      })
    } else {
      const schema = dbStructure?.schemas.find((s) => s.name === schemaName)
      const table = schema?.tables.find((t) => t.name === tableName)
      if (table) {
        const newTable: SelectedTable = {
          id: tableId,
          schema: schemaName,
          name: tableName,
          columns: table.columns,
          rowCount: table.rowCount,
        }
        onUpdate({
          selectedTables: [...selectedTables, newTable],
        })
      }
    }
  }

  const toggleSchema = (schemaName: string) => {
    const newExpanded = new Set(expandedSchemas)
    if (newExpanded.has(schemaName)) {
      newExpanded.delete(schemaName)
    } else {
      newExpanded.add(schemaName)
    }
    setExpandedSchemas(newExpanded)
  }

  const canProceed = selectedTables.length > 0

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-text-primary">
          Step 2: Select Tables
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Browse your database and select tables to include in this asset
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left: Database Browser */}
        <div className="space-y-4">
          <Input
            placeholder="Search tables..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />

          <div className="border border-border-default rounded-lg overflow-hidden max-h-[500px] overflow-y-auto">
            {isLoading ? (
              <DatabaseBrowserSkeleton />
            ) : !filteredStructure || filteredStructure.schemas.length === 0 ? (
              <div className="p-6 text-center">
                <DatabaseIcon className="w-12 h-12 mx-auto mb-3 text-text-tertiary" />
                <p className="text-text-secondary">No tables found</p>
                <p className="text-sm text-text-tertiary mt-1">
                  {search ? 'Try a different search term' : 'No schemas available'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-border-default">
                {filteredStructure.schemas.map((schema) => (
                  <SchemaNode
                    key={schema.name}
                    schema={schema}
                    expanded={expandedSchemas.has(schema.name)}
                    onToggle={() => toggleSchema(schema.name)}
                    selectedTables={selectedTables}
                    onToggleTable={toggleTable}
                    onPreview={setPreviewTable}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Selected Tables */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-text-primary">
              Selected Tables ({selectedTables.length})
            </h3>
            {selectedTables.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onUpdate({ selectedTables: [] })}
              >
                Clear All
              </Button>
            )}
          </div>

          <div className="border border-border-default rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
            {selectedTables.length === 0 ? (
              <div className="text-center py-8">
                <TableIcon className="w-8 h-8 mx-auto mb-2 text-text-tertiary" />
                <p className="text-text-secondary">No tables selected</p>
                <p className="text-sm text-text-tertiary mt-1">
                  Click tables on the left to add them
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {selectedTables.map((table) => (
                  <SelectedTableCard
                    key={table.id}
                    table={table}
                    onRemove={() => toggleTable(table.schema, table.name)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Summary Stats */}
          {selectedTables.length > 0 && (
            <div className="bg-bg-tertiary rounded-lg p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {selectedTables.length}
                  </div>
                  <div className="text-xs text-text-secondary">Tables</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {selectedTables.reduce((acc, t) => acc + (t.columns?.length || 0), 0)}
                  </div>
                  <div className="text-xs text-text-secondary">Columns</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-text-primary">
                    {formatNumber(
                      selectedTables.reduce((acc, t) => acc + (t.rowCount || 0), 0)
                    )}
                  </div>
                  <div className="text-xs text-text-secondary">Est. Rows</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* TODO: Table Preview Modal */}
      {/* <TablePreviewModal
        open={!!previewTable}
        onClose={() => setPreviewTable(null)}
        connectionId={data.connectionId!}
        tableId={previewTable}
      /> */}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-border-default">
        <Button variant="secondary" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onNext} disabled={!canProceed}>
          Next: Configure Asset
        </Button>
      </div>
    </div>
  )
}
