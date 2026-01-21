/**
 * API Adapters - Transform real API responses to hub's expected format
 *
 * The griot-registry API uses ODCS format while the hub UI expects a different structure.
 * These adapters handle the transformation.
 */

import type {
  Contract,
  ContractStatus,
  Issue,
  IssueStatus,
  IssueSeverity,
  PaginatedResponse,
} from '@/types'

// ============================================================================
// Registry API Response Types (from griot-registry)
// ============================================================================

export interface RegistryContractResponse {
  apiVersion: string
  kind: string
  id: string
  name: string
  version: string
  status: string
  description?: string | { logicalType: string }
  schema: RegistrySchemaDefinition[]
  owner?: string
  created_at?: string
  updated_at?: string
}

export interface RegistrySchemaDefinition {
  name: string
  id: string
  logicalType: string
  description?: string
  properties?: RegistrySchemaProperty[]
}

export interface RegistrySchemaProperty {
  name: string
  logicalType: string
  description?: string
  nullable?: boolean
  primary_key?: boolean
  primaryKey?: boolean
  customProperties?: {
    privacy?: {
      is_pii: boolean
      sensitivity: string
    }
  }
}

export interface RegistryListResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface RegistryIssueResponse {
  id: string
  contract_id: string
  run_id: string | null
  title: string
  description: string
  severity: string
  category: string
  status: string
  affected_field: string | null
  affected_schema: string | null
  assignee: string | null
  resolution: string | null
  resolved_by: string | null
  resolved_at: string | null
  created_at: string
  updated_at: string
  created_by: string
}

export interface RegistryRunResponse {
  id: string
  contract_id: string
  contract_version: string | null
  schema_name: string | null
  pipeline_id: string | null
  environment: string | null
  trigger: string | null
  status: string
  result: Record<string, unknown> | null
  created_at: string
  updated_at: string
  completed_at: string | null
  created_by: string
}

export interface RegistryValidationResponse {
  id: string
  contract_id: string
  contract_version: string | null
  schema_name: string | null
  passed: boolean
  row_count: number
  error_count: number
  error_rate: number
  duration_ms: number
  environment: string | null
  pipeline_id: string | null
  run_id: string | null
  recorded_at: string
}

// ============================================================================
// Adapters
// ============================================================================

/**
 * Map registry contract status to hub contract status
 */
function mapContractStatus(status: string): ContractStatus {
  const statusMap: Record<string, ContractStatus> = {
    draft: 'draft',
    active: 'active',
    deprecated: 'deprecated',
    retired: 'deprecated',
    proposed: 'proposed',
    pending_review: 'pending_review',
  }
  return statusMap[status.toLowerCase()] || 'draft'
}

/**
 * Map registry issue severity to hub issue severity
 */
function mapIssueSeverity(severity: string): IssueSeverity {
  const severityMap: Record<string, IssueSeverity> = {
    error: 'critical',
    warning: 'warning',
    info: 'info',
    critical: 'critical',
  }
  return severityMap[severity.toLowerCase()] || 'info'
}

/**
 * Map registry issue status to hub issue status
 */
function mapIssueStatus(status: string): IssueStatus {
  const statusMap: Record<string, IssueStatus> = {
    open: 'open',
    resolved: 'resolved',
    in_progress: 'in_progress',
    ignored: 'ignored',
  }
  return statusMap[status.toLowerCase()] || 'open'
}

/**
 * Transform a registry contract to hub contract format
 */
export function adaptContract(contract: RegistryContractResponse): Contract {
  // Extract description - it might be a string or an object
  let description = ''
  if (typeof contract.description === 'string') {
    description = contract.description
  } else if (contract.description && typeof contract.description === 'object') {
    description = ''
  }

  // Transform schema
  const tables = (contract.schema || []).map((schema) => ({
    name: schema.name,
    physicalName: schema.name,
    description: schema.description || '',
    fields: (schema.properties || []).map((prop) => ({
      name: prop.name,
      logicalType: prop.logicalType,
      physicalType: prop.logicalType,
      description: prop.description || '',
      required: prop.nullable === false,
      unique: false,
      primaryKey: prop.primary_key === true || prop.primaryKey === true,
      piiClassification: prop.customProperties?.privacy?.is_pii ? 'pii' : undefined,
    })),
  }))

  return {
    id: contract.id,
    name: contract.name,
    version: contract.version,
    status: mapContractStatus(contract.status),
    description,
    domain: 'default', // Registry API doesn't have domain field
    ownerTeamId: contract.owner || 'default-team',
    tags: [],
    odcsVersion: contract.apiVersion,
    schema: { tables },
    qualityRules: [],
    sla: {
      freshnessHours: 24,
      availabilityPercent: 99.9,
    },
    createdAt: contract.created_at || new Date().toISOString(),
    updatedAt: contract.updated_at || new Date().toISOString(),
  }
}

/**
 * Transform registry contracts list to hub paginated format
 */
export function adaptContractsList(
  response: RegistryListResponse<RegistryContractResponse>,
  page: number = 1,
  pageSize: number = 20
): PaginatedResponse<Contract> {
  const contracts = response.items.map(adaptContract)

  return {
    data: contracts,
    meta: {
      total: response.total,
      page,
      pageSize,
      totalPages: Math.ceil(response.total / pageSize),
    },
  }
}

/**
 * Transform a registry issue to hub issue format
 */
export function adaptIssue(issue: RegistryIssueResponse): Issue {
  return {
    id: issue.id,
    title: issue.title,
    description: issue.description || '',
    severity: mapIssueSeverity(issue.severity),
    status: mapIssueStatus(issue.status),
    category: (issue.category as Issue['category']) || 'other',
    contractId: issue.contract_id,
    contractName: undefined,
    contractVersion: undefined,
    field: issue.affected_field || undefined,
    table: issue.affected_schema || undefined,
    assignedTeamId: issue.assignee || undefined,
    detectedAt: issue.created_at,
    resolvedAt: issue.resolved_at || undefined,
    createdAt: issue.created_at,
    updatedAt: issue.updated_at,
  }
}

/**
 * Transform registry issues list to hub paginated format
 */
export function adaptIssuesList(
  response: RegistryListResponse<RegistryIssueResponse>,
  page: number = 1,
  pageSize: number = 20
): PaginatedResponse<Issue> {
  const issues = response.items.map(adaptIssue)

  return {
    data: issues,
    meta: {
      total: response.total,
      page,
      pageSize,
      totalPages: Math.ceil(response.total / pageSize),
    },
  }
}

/**
 * Transform registry run to hub format
 */
export function adaptRun(run: RegistryRunResponse) {
  let status: 'running' | 'passed' | 'failed' | 'warning' = 'running'
  if (run.status === 'completed') {
    status = 'passed'
  } else if (run.status === 'failed') {
    status = 'failed'
  } else if (run.status === 'running' || run.status === 'pending') {
    status = 'running'
  }

  return {
    id: run.id,
    contractId: run.contract_id,
    status,
    startedAt: run.created_at,
    completedAt: run.completed_at || undefined,
    duration: run.completed_at
      ? new Date(run.completed_at).getTime() - new Date(run.created_at).getTime()
      : undefined,
    ruleResults: [],
    summary: {
      totalRules: 0,
      passed: status === 'passed' ? 1 : 0,
      failed: status === 'failed' ? 1 : 0,
      warnings: 0,
    },
    createdAt: run.created_at,
    updatedAt: run.updated_at,
  }
}

/**
 * Transform registry runs list to hub paginated format
 */
export function adaptRunsList(
  response: RegistryListResponse<RegistryRunResponse>,
  page: number = 1,
  pageSize: number = 20
) {
  const runs = response.items.map(adaptRun)

  return {
    data: runs,
    meta: {
      total: response.total,
      page,
      pageSize,
      totalPages: Math.ceil(response.total / pageSize),
    },
  }
}

/**
 * Transform registry validation to hub format for dashboard metrics
 */
export function adaptValidation(validation: RegistryValidationResponse) {
  return {
    id: validation.id,
    contractId: validation.contract_id,
    passed: validation.passed,
    rowCount: validation.row_count,
    errorCount: validation.error_count,
    errorRate: validation.error_rate,
    durationMs: validation.duration_ms,
    environment: validation.environment,
    recordedAt: validation.recorded_at,
  }
}
