/**
 * Schema diff utility for detecting changes between contract schemas
 */

export interface SchemaField {
  name: string
  logicalType: string
  required?: boolean
  primaryKey?: boolean
  piiClassification?: string
  description?: string
}

export interface SchemaTable {
  name: string
  description?: string
  fields: SchemaField[]
}

export interface SchemaDiff {
  hasChanges: boolean
  summary: string
  changes: {
    addedTables: string[]
    removedTables: string[]
    modifiedTables: string[]
    addedFields: { table: string; field: string }[]
    removedFields: { table: string; field: string }[]
    modifiedFields: { table: string; field: string; changes: string[] }[]
  }
}

/**
 * Compare two schemas and return the differences
 */
export function compareSchemas(
  oldSchema: { tables: SchemaTable[] } | undefined,
  newSchema: { tables: SchemaTable[] } | undefined
): SchemaDiff {
  const oldTables = oldSchema?.tables || []
  const newTables = newSchema?.tables || []

  const oldTableNames = new Set(oldTables.map((t) => t.name))
  const newTableNames = new Set(newTables.map((t) => t.name))

  const addedTables: string[] = []
  const removedTables: string[] = []
  const modifiedTables: string[] = []
  const addedFields: { table: string; field: string }[] = []
  const removedFields: { table: string; field: string }[] = []
  const modifiedFields: { table: string; field: string; changes: string[] }[] = []

  // Find added tables
  for (const tableName of newTableNames) {
    if (!oldTableNames.has(tableName)) {
      addedTables.push(tableName)
    }
  }

  // Find removed tables
  for (const tableName of oldTableNames) {
    if (!newTableNames.has(tableName)) {
      removedTables.push(tableName)
    }
  }

  // Compare existing tables
  for (const newTable of newTables) {
    if (!oldTableNames.has(newTable.name)) continue

    const oldTable = oldTables.find((t) => t.name === newTable.name)
    if (!oldTable) continue

    const oldFieldNames = new Set(oldTable.fields.map((f) => f.name))
    const newFieldNames = new Set(newTable.fields.map((f) => f.name))

    let tableModified = false

    // Find added fields
    for (const fieldName of newFieldNames) {
      if (!oldFieldNames.has(fieldName)) {
        addedFields.push({ table: newTable.name, field: fieldName })
        tableModified = true
      }
    }

    // Find removed fields
    for (const fieldName of oldFieldNames) {
      if (!newFieldNames.has(fieldName)) {
        removedFields.push({ table: newTable.name, field: fieldName })
        tableModified = true
      }
    }

    // Compare existing fields
    for (const newField of newTable.fields) {
      if (!oldFieldNames.has(newField.name)) continue

      const oldField = oldTable.fields.find((f) => f.name === newField.name)
      if (!oldField) continue

      const changes: string[] = []

      if (oldField.logicalType !== newField.logicalType) {
        changes.push(`type changed from ${oldField.logicalType} to ${newField.logicalType}`)
      }
      if (oldField.required !== newField.required) {
        changes.push(newField.required ? 'made required' : 'made optional')
      }
      if (oldField.primaryKey !== newField.primaryKey) {
        changes.push(newField.primaryKey ? 'added as primary key' : 'removed from primary key')
      }
      if (oldField.piiClassification !== newField.piiClassification) {
        if (!oldField.piiClassification && newField.piiClassification) {
          changes.push(`marked as PII (${newField.piiClassification})`)
        } else if (oldField.piiClassification && !newField.piiClassification) {
          changes.push('PII classification removed')
        } else {
          changes.push(`PII changed from ${oldField.piiClassification} to ${newField.piiClassification}`)
        }
      }

      if (changes.length > 0) {
        modifiedFields.push({ table: newTable.name, field: newField.name, changes })
        tableModified = true
      }
    }

    if (tableModified) {
      modifiedTables.push(newTable.name)
    }
  }

  const hasChanges =
    addedTables.length > 0 ||
    removedTables.length > 0 ||
    addedFields.length > 0 ||
    removedFields.length > 0 ||
    modifiedFields.length > 0

  // Generate summary
  const summaryParts: string[] = []
  if (addedTables.length > 0) {
    summaryParts.push(`${addedTables.length} table(s) added`)
  }
  if (removedTables.length > 0) {
    summaryParts.push(`${removedTables.length} table(s) removed`)
  }
  if (addedFields.length > 0) {
    summaryParts.push(`${addedFields.length} field(s) added`)
  }
  if (removedFields.length > 0) {
    summaryParts.push(`${removedFields.length} field(s) removed`)
  }
  if (modifiedFields.length > 0) {
    summaryParts.push(`${modifiedFields.length} field(s) modified`)
  }

  const summary = hasChanges ? summaryParts.join(', ') : 'No schema changes'

  return {
    hasChanges,
    summary,
    changes: {
      addedTables,
      removedTables,
      modifiedTables,
      addedFields,
      removedFields,
      modifiedFields,
    },
  }
}

/**
 * Determine if schema changes are breaking (require major version)
 */
export function hasBreakingChanges(diff: SchemaDiff): boolean {
  const { removedTables, removedFields, modifiedFields } = diff.changes

  // Removed tables are breaking
  if (removedTables.length > 0) return true

  // Removed fields are breaking
  if (removedFields.length > 0) return true

  // Type changes or making fields required are breaking
  for (const mod of modifiedFields) {
    if (mod.changes.some((c) => c.includes('type changed') || c === 'made required')) {
      return true
    }
  }

  return false
}
