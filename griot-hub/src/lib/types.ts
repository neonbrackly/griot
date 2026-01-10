/**
 * TypeScript types generated from agents/specs/registry.yaml
 * These types match the Registry API schemas.
 *
 * NOTE: Do NOT import griot-core directly. All data comes through the Registry API.
 */

// =============================================================================
// HEALTH
// =============================================================================

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';

export interface HealthResponse {
  status: HealthStatus;
  version: string;
  timestamp?: string;
}

// =============================================================================
// ERROR
// =============================================================================

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// CONTRACT
// =============================================================================

export type ContractStatus = 'draft' | 'active' | 'deprecated';

export interface Contract {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: ContractStatus;
  owner?: string;
  fields: FieldDefinition[];
  created_at?: string;
  updated_at?: string;
}

export interface ContractCreate {
  id: string;
  name: string;
  description?: string;
  owner?: string;
  fields: FieldDefinition[];
}

export type ChangeType = 'patch' | 'minor' | 'major';

export interface ContractUpdate {
  name?: string;
  description?: string;
  fields?: FieldDefinition[];
  change_type?: ChangeType;
  change_notes?: string;
}

export interface ContractList {
  items: Contract[];
  total: number;
  limit: number;
  offset: number;
}

// =============================================================================
// FIELD
// =============================================================================

export type FieldType =
  | 'string'
  | 'integer'
  | 'float'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'array'
  | 'object';

export type FieldFormat =
  | 'email'
  | 'uri'
  | 'uuid'
  | 'date'
  | 'datetime'
  | 'ipv4'
  | 'ipv6'
  | 'hostname';

export type AggregationType = 'sum' | 'avg' | 'count' | 'min' | 'max' | 'none';

export interface FieldConstraints {
  min_length?: number;
  max_length?: number;
  pattern?: string;
  format?: FieldFormat;
  ge?: number; // greater than or equal
  le?: number; // less than or equal
  gt?: number; // greater than
  lt?: number; // less than
  multiple_of?: number;
  enum?: unknown[];
}

export interface FieldMetadata {
  unit?: string;
  aggregation?: AggregationType;
  glossary_term?: string;
}

export interface FieldDefinition {
  name: string;
  type: FieldType;
  description: string;
  nullable?: boolean;
  primary_key?: boolean;
  unique?: boolean;
  constraints?: FieldConstraints;
  metadata?: FieldMetadata;
}

// =============================================================================
// VERSIONS
// =============================================================================

export interface VersionSummary {
  version: string;
  created_at?: string;
  created_by?: string;
  change_type?: ChangeType;
  change_notes?: string;
  is_breaking?: boolean;
}

export interface VersionList {
  items: VersionSummary[];
  total: number;
}

export interface TypeChange {
  field: string;
  from_type: string;
  to_type: string;
  is_breaking: boolean;
}

export interface ConstraintChange {
  field: string;
  constraint: string;
  from_value: unknown;
  to_value: unknown;
  is_breaking: boolean;
}

export interface ContractDiff {
  from_version: string;
  to_version: string;
  has_breaking_changes: boolean;
  added_fields: string[];
  removed_fields: string[];
  type_changes: TypeChange[];
  constraint_changes: ConstraintChange[];
}

// =============================================================================
// VALIDATIONS
// =============================================================================

export type Environment = 'development' | 'staging' | 'production';

export interface ValidationError {
  field: string;
  row?: number;
  value?: unknown;
  constraint: string;
  message: string;
}

export interface ValidationReport {
  contract_id: string;
  contract_version?: string;
  passed: boolean;
  row_count: number;
  error_count?: number;
  error_rate?: number;
  duration_ms?: number;
  environment?: Environment;
  pipeline_id?: string;
  run_id?: string;
  sample_errors?: ValidationError[];
}

export interface ValidationRecord {
  id: string;
  contract_id: string;
  contract_version?: string;
  passed: boolean;
  row_count: number;
  error_count?: number;
  recorded_at: string;
}

export interface ValidationList {
  items: ValidationRecord[];
  total: number;
}

// =============================================================================
// SEARCH
// =============================================================================

export type MatchType = 'name' | 'description' | 'field';

export interface SearchHit {
  contract_id: string;
  contract_name: string;
  field_name?: string;
  match_type: MatchType;
  snippet?: string;
}

export interface SearchResults {
  query: string;
  items: SearchHit[];
  total: number;
}

// =============================================================================
// API PARAMETERS
// =============================================================================

export interface ListParams {
  limit?: number;
  offset?: number;
}

export interface ContractListParams extends ListParams {
  status?: ContractStatus;
  owner?: string;
}

export interface ValidationListParams extends ListParams {
  contract_id?: string;
  passed?: boolean;
  from_date?: string;
  to_date?: string;
}

export interface SearchParams extends ListParams {
  q: string;
  field?: string;
}
