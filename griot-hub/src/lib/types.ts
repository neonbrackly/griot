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

// =============================================================================
// PII & PRIVACY (Phase 2)
// =============================================================================

export type PIICategory =
  | 'direct_identifier'
  | 'quasi_identifier'
  | 'sensitive'
  | 'non_pii';

export type SensitivityLevel = 'public' | 'internal' | 'confidential' | 'restricted';

export type MaskingStrategy =
  | 'none'
  | 'redact'
  | 'hash'
  | 'tokenize'
  | 'encrypt'
  | 'generalize'
  | 'pseudonymize';

export type LegalBasis =
  | 'consent'
  | 'contract'
  | 'legal_obligation'
  | 'vital_interests'
  | 'public_task'
  | 'legitimate_interests';

export interface PIIFieldInfo {
  field_name: string;
  contract_id: string;
  pii_category: PIICategory;
  sensitivity_level: SensitivityLevel;
  masking_strategy: MaskingStrategy;
  legal_basis?: LegalBasis;
  retention_days?: number;
}

// =============================================================================
// RESIDENCY
// =============================================================================

export type Region =
  | 'us'
  | 'eu'
  | 'uk'
  | 'apac'
  | 'latam'
  | 'mea'
  | 'global';

export interface ResidencyRequirement {
  region: Region;
  required: boolean;
  allowed_regions: Region[];
  restricted_regions: Region[];
}

export interface ResidencyStatus {
  contract_id: string;
  field_name?: string;
  current_region: Region;
  required_region: Region;
  compliant: boolean;
  violation_reason?: string;
}

// =============================================================================
// REPORTS
// =============================================================================

// Audit Report (T-050 / FR-SDK-013)
export interface PIIInventoryItem {
  contract_id: string;
  contract_name: string;
  field_name: string;
  pii_category: PIICategory;
  sensitivity_level: SensitivityLevel;
  masking_strategy: MaskingStrategy;
  legal_basis?: LegalBasis;
  retention_days?: number;
}

export interface ResidencyCheck {
  contract_id: string;
  region: Region;
  compliant: boolean;
  fields_checked: number;
  violations: ResidencyStatus[];
}

export interface AuditReport {
  generated_at: string;
  contract_count: number;
  field_count: number;
  pii_inventory: PIIInventoryItem[];
  pii_by_category: Record<PIICategory, number>;
  pii_by_sensitivity: Record<SensitivityLevel, number>;
  residency_checks: ResidencyCheck[];
  residency_compliance_rate: number;
  legal_basis_coverage: Record<LegalBasis, number>;
  retention_policy_coverage: number;
}

// Analytics Report (T-051 / FR-SDK-014)
export interface ContractMetrics {
  contract_id: string;
  contract_name: string;
  field_count: number;
  validation_count: number;
  pass_rate: number;
  avg_error_rate: number;
  last_validation?: string;
}

export interface FieldUsageMetrics {
  field_name: string;
  contract_count: number;
  avg_null_rate: number;
  type_distribution: Record<FieldType, number>;
}

export interface AnalyticsReport {
  generated_at: string;
  total_contracts: number;
  total_fields: number;
  total_validations: number;
  overall_pass_rate: number;
  contract_metrics: ContractMetrics[];
  field_usage: FieldUsageMetrics[];
  validations_by_day: { date: string; count: number; pass_rate: number }[];
  top_failing_contracts: { contract_id: string; fail_count: number }[];
  top_error_types: { constraint: string; count: number }[];
}

// AI Readiness Report (T-052 / FR-SDK-016)
export interface AIReadinessScore {
  overall_score: number; // 0-100
  documentation_score: number;
  semantic_coverage_score: number;
  data_quality_score: number;
  consistency_score: number;
}

export interface SemanticCoverage {
  fields_with_description: number;
  fields_with_unit: number;
  fields_with_aggregation: number;
  fields_with_glossary_term: number;
  total_fields: number;
}

export interface ContractAIReadiness {
  contract_id: string;
  contract_name: string;
  score: AIReadinessScore;
  semantic_coverage: SemanticCoverage;
  recommendations: string[];
}

export interface AIReadinessReport {
  generated_at: string;
  overall_score: AIReadinessScore;
  semantic_coverage: SemanticCoverage;
  contracts: ContractAIReadiness[];
  top_recommendations: string[];
  readiness_by_contract: { contract_id: string; score: number }[];
}

// Combined Readiness Report (T-053 / FR-SDK-017)
export interface ReadinessReport {
  generated_at: string;
  audit: AuditReport;
  analytics: AnalyticsReport;
  ai_readiness: AIReadinessReport;
  overall_health_score: number;
}

// =============================================================================
// REPORT PARAMETERS
// =============================================================================

export interface ReportParams {
  contract_ids?: string[];
  from_date?: string;
  to_date?: string;
  include_details?: boolean;
}
