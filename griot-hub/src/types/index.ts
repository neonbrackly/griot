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

// Schema types (ODCS-compliant standalone schemas)
export type SchemaStatus = 'draft' | 'active' | 'deprecated'
export type SchemaSource = 'manual' | 'connection' | 'import'
export type SchemaLogicalType = 'object' | 'array' | 'primitive'

export interface Schema extends BaseEntity {
  name: string
  physicalName?: string
  logicalType: SchemaLogicalType
  physicalType?: string
  description?: string
  businessName?: string
  domain?: string
  status: SchemaStatus
  source: SchemaSource
  connectionId?: string
  ownerTeamId?: string
  ownerId?: string
  tags: string[]
  properties: SchemaProperty[]
  quality?: SchemaQualityRule[]
  hasPii: boolean
  propertyCount: number
  version: string
}

export interface SchemaProperty {
  id?: string
  name: string
  logicalType: string
  physicalType?: string
  description?: string
  businessName?: string
  primaryKey: boolean
  required: boolean
  nullable: boolean
  unique: boolean
  partitioned?: boolean
  partitionKeyPosition?: number
  criticalDataElement?: boolean
  defaultValue?: string
  customProperties?: {
    constraints?: PropertyConstraint[]
    semantic?: {
      logicalType?: string
      description?: string
      businessName?: string
    }
    privacy?: {
      is_pii: boolean
      pii_type?: string
      sensitivity?: 'public' | 'internal' | 'confidential' | 'restricted'
    }
  }
  quality?: PropertyQualityRule[]
  relationships?: PropertyRelationship[]
  tags?: string[]
}

export interface PropertyConstraint {
  type: 'minLength' | 'maxLength' | 'min' | 'max' | 'pattern' | 'enum' | 'format'
  value: string | number | string[]
  description?: string
}

export interface PropertyRelationship {
  to: string
  type: 'foreignKey' | 'reference'
  customProperties?: Array<{ property: string; value: string }>
}

// Quality Rules - Schema Level
export interface SchemaQualityRule {
  id: string
  name: string
  description?: string
  type: 'library' | 'custom'
  engine?: string
  metric: string
  mustBe?: number
  mustBeLessThan?: number
  mustBeGreaterThan?: number
  unit?: 'rows' | 'percent'
  arguments?: Record<string, unknown>
}

// Quality Rules - Property Level
export interface PropertyQualityRule {
  id?: string
  name: string
  description?: string
  type: 'library' | 'custom'
  metric: string
  mustBe?: number
  mustBeLessThan?: number
  mustBeGreaterThan?: number
  pattern?: string
  unit?: 'rows' | 'percent'
  arguments?: Record<string, unknown>
}

// Schema Form Data (for manual wizard)
export interface SchemaFormData {
  // Basic info
  name: string
  physicalName?: string
  logicalType: SchemaLogicalType
  physicalType?: string
  description?: string
  businessName?: string
  domain?: string
  // Schema-level quality rules
  quality?: SchemaQualityRule[]
  // Properties
  properties: SchemaProperty[]
  // Ownership
  ownerTeamId?: string
  tags?: string[]
}

// Schema Form Data (for connection-based wizard)
export interface ConnectionSchemaFormData {
  connectionId?: string
  connection?: Connection
  selectedTables?: SelectedTable[]
  name?: string
  description?: string
  domain?: string
  ownerTeamId?: string
  tags?: string[]
}

export interface SelectedTable {
  id: string
  schema: string
  name: string
  columns: TableColumn[]
  rowCount?: number
}

export interface TableColumn {
  name: string
  type: string
  nullable: boolean
  primaryKey?: boolean
}

// Legacy type aliases for backward compatibility during migration
export type AssetStatus = SchemaStatus
export type DataAsset = Schema
export type AssetFormData = ConnectionSchemaFormData
export interface AssetSLA {
  freshnessHours: number
  availabilityPercent: number
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

// Database Browse types (for connection browsing)
export interface DatabaseStructure {
  schemas: DatabaseSchema[]
}

export interface DatabaseSchema {
  name: string
  tables: DatabaseTable[]
}

export interface DatabaseTable {
  name: string
  columns: TableColumn[]
  rowCount?: number
  sizeBytes?: number
  lastUpdated?: string
}

export interface TablePreview {
  columns: TableColumn[]
  sampleData: Record<string, unknown>[]
  rowCount: number
  sizeBytes?: number
  lastUpdated?: string
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
  ownerTeamName?: string // Team name for display
  tags: string[]
  odcsVersion: string
  schema: ContractSchema
  qualityRules: QualityRule[]
  sla: ContractSLA
  lastRunAt?: string
  lastRunStatus?: 'passed' | 'failed' | 'warning'
  issueCount?: number
  // Reviewer fields
  reviewerId?: string
  reviewerType?: 'user' | 'team'
  reviewerName?: string
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

// Task types
export interface PendingAuthorization {
  id: string
  contractId: string
  contractName: string
  requestedBy: string
  requestedByEmail: string
  requestedAt: string
  domain: string
  priority: 'high' | 'medium' | 'low'
  description?: string
}

export interface CommentToReview {
  id: string
  contractId: string
  contractName: string
  commentBy: string
  commentByAvatar?: string
  commentAt: string
  comment: string
  type: 'feedback' | 'question' | 'approval'
}

export interface Draft {
  id: string
  type: 'contract' | 'asset'
  name?: string
  updatedAt: string
  completionPercent?: number
  domain?: string
}

export interface MyTasks {
  authorizations: PendingAuthorization[]
  comments: CommentToReview[]
  drafts: Draft[]
}

// Notification types
export type NotificationType =
  | 'contract_approved'
  | 'contract_rejected'
  | 'issue_detected'
  | 'sla_breach'
  | 'schema_drift'
  | 'comment_added'
  | 'task_assigned'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  description: string
  href?: string
  read: boolean
  createdAt: string
}

// Search result types
export interface SearchResult {
  id: string
  name: string
  type: 'contract' | 'asset' | 'issue' | 'team'
  href: string
  description?: string
  domain?: string
}

export interface GlobalSearchResults {
  contracts: SearchResult[]
  assets: SearchResult[]
  issues: SearchResult[]
  teams: SearchResult[]
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
