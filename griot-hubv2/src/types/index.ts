// Core Entity Types for Griot Data Contract Management System

// Base entity interface
export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
}

// User types
export interface User extends BaseEntity {
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'manager' | 'member' | 'viewer'
  teamId: string
  lastLoginAt?: string
  status: 'active' | 'inactive' | 'pending'
}

// Team types
export interface Team extends BaseEntity {
  name: string
  description?: string
  memberCount: number
  domains: string[]
}

// Database Connection types
export type ConnectionType = 'snowflake' | 'bigquery' | 'databricks' | 'postgres' | 'redshift'

export interface Connection extends BaseEntity {
  name: string
  type: ConnectionType
  status: 'active' | 'inactive' | 'error'
  config: ConnectionConfig
  lastTestedAt?: string
  lastTestStatus?: 'success' | 'error' | 'pending'
}

export interface ConnectionConfig {
  // Common fields
  host?: string
  port?: number
  database?: string
  schema?: string
  // Snowflake specific
  account?: string
  warehouse?: string
  // BigQuery specific
  projectId?: string
  dataset?: string
  // Databricks specific
  workspace?: string
  cluster?: string
}

// Data Asset types
export type AssetStatus = 'active' | 'draft' | 'deprecated'

export interface DataAsset extends BaseEntity {
  name: string
  description?: string
  status: AssetStatus
  domain: string
  connectionId: string
  ownerTeamId: string
  tags: string[]
  tables: DataTable[]
  sla: AssetSLA
  lastSyncedAt?: string
}

export interface DataTable {
  id: string
  name: string
  physicalName: string
  description?: string
  fields: DataField[]
  rowCount?: number
}

export interface DataField {
  name: string
  type: string
  description?: string
  isPrimaryKey: boolean
  isNullable: boolean
  piiType?: 'email' | 'name' | 'phone' | 'address' | 'ssn' | 'other'
  businessName?: string
}

export interface AssetSLA {
  freshnessHours: number
  availabilityPercent: number
}

// Contract types
export type ContractStatus = 'draft' | 'proposed' | 'pending_review' | 'active' | 'deprecated'

export interface Contract extends BaseEntity {
  name: string
  version: string
  status: ContractStatus
  description?: string
  domain: string
  assetId?: string // Optional - proposed contracts may not have an asset
  asset?: DataAsset
  ownerTeamId: string
  tags: string[]
  odcsVersion: string
  schema: ContractSchema
  qualityRules: QualityRule[]
  sla: ContractSLA
  lastRunAt?: string
  lastRunStatus?: 'passed' | 'failed' | 'warning'
  issueCount?: number
}

export interface ContractSchema {
  tables: ContractTable[]
}

export interface ContractTable {
  name: string
  physicalName?: string
  description?: string
  fields: ContractField[]
}

export interface ContractField {
  name: string
  logicalType: string
  physicalType?: string
  description?: string
  required: boolean
  unique: boolean
  primaryKey: boolean
  piiClassification?: string
  businessName?: string
  example?: string
}

export interface QualityRule {
  id: string
  name: string
  type: 'completeness' | 'uniqueness' | 'validity' | 'custom'
  field?: string
  table?: string
  expression?: string
  threshold?: number
  enabled: boolean
}

export interface ContractSLA {
  freshnessHours: number
  availabilityPercent: number
  responseTimeMs?: number
}

// Issue types
export type IssueSeverity = 'critical' | 'warning' | 'info'
export type IssueStatus = 'open' | 'in_progress' | 'resolved' | 'ignored'
export type IssueCategory = 'pii_exposure' | 'schema_drift' | 'sla_breach' | 'quality_failure' | 'other'

export interface Issue extends BaseEntity {
  title: string
  description: string
  severity: IssueSeverity
  status: IssueStatus
  category: IssueCategory
  contractId: string
  contractName?: string
  contractVersion?: string
  field?: string
  table?: string
  assignedTeamId?: string
  detectedAt: string
  resolvedAt?: string
}

// Run types
export type RunStatus = 'running' | 'passed' | 'failed' | 'warning'

export interface ContractRun extends BaseEntity {
  contractId: string
  status: RunStatus
  startedAt: string
  completedAt?: string
  duration?: number
  ruleResults: RuleResult[]
  summary: RunSummary
}

export interface RuleResult {
  ruleId: string
  ruleName: string
  passed: boolean
  actualValue?: number
  expectedValue?: number
  message?: string
}

export interface RunSummary {
  totalRules: number
  passed: number
  failed: number
  warnings: number
}

// Dashboard types
export interface DashboardMetrics {
  complianceHealth: HealthScore
  costHealth: HealthScore
  analyticsHealth: HealthScore
  activeIssues: number
  criticalIssues: number
  contractsRun: number
  contractsPassed: number
}

export interface HealthScore {
  score: number
  trend: number
  details: string
}

export interface TimelineDay {
  date: string
  status: 'passed' | 'failed' | 'warning' | 'running' | 'none'
  runsCount: number
  passedCount: number
  failedCount: number
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    page: number
    pageSize: number
    totalPages: number
  }
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}
