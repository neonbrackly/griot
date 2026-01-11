/**
 * TypeScript types for Open Data Contract Standard (ODCS)
 * Generated from agents/specs/registry.yaml and griot-registry/schemas.py
 *
 * T-388: Complete ODCS type definitions for griot-hub
 *
 * NOTE: Do NOT import griot-core directly. All data comes through the Registry API.
 */

// =============================================================================
// ODCS Enums (matching griot-core/types.py and registry/schemas.py)
// =============================================================================

export type ContractStatus = 'draft' | 'active' | 'deprecated' | 'retired';
export type PhysicalType = 'table' | 'view' | 'file' | 'stream';
export type QualityRuleType = 'completeness' | 'accuracy' | 'freshness' | 'volume' | 'distribution';
export type CheckType = 'sql' | 'python' | 'great_expectations';
export type Severity = 'error' | 'warning' | 'info';
export type ExtractionMethod = 'full' | 'incremental' | 'cdc';
export type PartitioningStrategy = 'date' | 'hash' | 'range';
export type ReviewCadence = 'monthly' | 'quarterly' | 'annually';
export type AccessLevel = 'read' | 'write' | 'admin';
export type DistributionType = 'warehouse' | 'lake' | 'api' | 'stream' | 'file';
export type SourceType = 'system' | 'contract' | 'file' | 'api' | 'stream';
export type SensitivityLevel = 'public' | 'internal' | 'confidential' | 'restricted';
export type MaskingStrategy =
  | 'none'
  | 'redact'
  | 'hash_sha256'
  | 'hash_md5'
  | 'tokenize'
  | 'generalize'
  | 'k_anonymize'
  | 'differential_privacy'
  | 'encrypt';
export type LegalBasis =
  | 'consent'
  | 'contract'
  | 'legal_obligation'
  | 'vital_interest'
  | 'public_task'
  | 'legitimate_interest';
export type PIICategory =
  | 'email'
  | 'phone'
  | 'national_id'
  | 'name'
  | 'address'
  | 'dob'
  | 'financial'
  | 'health'
  | 'biometric'
  | 'location'
  | 'other';
export type BreakingChangeType =
  | 'field_removed'
  | 'type_changed_incompatible'
  | 'field_renamed'
  | 'required_field_added'
  | 'enum_value_removed'
  | 'constraint_tightened'
  | 'nullable_to_required';

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
// ODCS Description Section
// =============================================================================

export interface CustomProperty {
  name: string;
  value: string;
  description?: string;
}

export interface Description {
  purpose?: string;
  usage?: string;
  limitations?: string;
  customProperties?: CustomProperty[];
}

// =============================================================================
// ODCS Schema Property (Enhanced Field)
// =============================================================================

export interface ForeignKey {
  contract: string;
  field: string;
}

export interface SemanticInfo {
  description?: string;
  unit?: string;
  precision?: number;
  business_term?: string;
  glossary_uri?: string;
}

export interface PrivacyInfo {
  contains_pii: boolean;
  pii_category?: PIICategory;
  sensitivity_level: SensitivityLevel;
  masking: MaskingStrategy;
  retention_days?: number;
  legal_basis?: LegalBasis;
}

export interface FieldConstraints {
  min_length?: number;
  max_length?: number;
  pattern?: string;
  format?: FieldFormat;
  ge?: number;
  le?: number;
  gt?: number;
  lt?: number;
  multiple_of?: number;
  enum?: unknown[];
  unique?: boolean;
}

export interface SchemaProperty {
  name: string;
  description?: string;
  logicalType: string;
  physicalType?: string;
  nullable: boolean;
  examples?: unknown[];
  primary_key: boolean;
  foreign_key?: ForeignKey;
  constraints?: FieldConstraints;
  semantic?: SemanticInfo;
  privacy?: PrivacyInfo;
}

// =============================================================================
// ODCS Quality Rules
// =============================================================================

export interface CompletenessRule {
  rule: 'completeness';
  min_percent: number;
  critical_fields?: string[];
}

export interface AccuracyRule {
  rule: 'accuracy';
  max_error_rate: number;
  validation_method?: string;
}

export interface FreshnessRule {
  rule: 'freshness';
  max_age: string; // ISO 8601 duration
  timestamp_field?: string;
}

export interface VolumeRule {
  rule: 'volume';
  min_rows?: number;
  max_rows?: number;
}

export interface DistributionRule {
  rule: 'distribution';
  field: string;
  expected_distribution?: Record<string, unknown>;
}

export interface CustomCheck {
  name: string;
  type: CheckType;
  definition: string;
  severity: Severity;
}

export interface QualityRules {
  completeness?: CompletenessRule;
  accuracy?: AccuracyRule;
  freshness?: FreshnessRule;
  volume?: VolumeRule;
  distribution?: DistributionRule;
  custom_checks?: CustomCheck[];
}

// =============================================================================
// ODCS Schema Definition (Dataset/Table)
// =============================================================================

export interface SchemaDefinition {
  name: string;
  physicalType: PhysicalType;
  properties?: SchemaProperty[];
  quality?: QualityRules;
}

// =============================================================================
// ODCS Legal Section
// =============================================================================

export interface CrossBorder {
  restrictions?: string[];
  transfer_mechanisms?: string[];
  data_residency?: string;
}

export interface Legal {
  jurisdiction?: string[];
  basis?: LegalBasis;
  consent_id?: string;
  regulations?: string[];
  cross_border?: CrossBorder;
}

// =============================================================================
// ODCS Compliance Section
// =============================================================================

export interface AuditRequirements {
  logging: boolean;
  log_retention?: string; // ISO 8601 duration
}

export interface ExportRestrictions {
  allow_download: boolean;
  allow_external_transfer: boolean;
  allowed_destinations?: string[];
}

export interface Compliance {
  data_classification: SensitivityLevel;
  regulatory_scope?: string[];
  audit_requirements?: AuditRequirements;
  certification_requirements?: string[];
  export_restrictions?: ExportRestrictions;
}

// =============================================================================
// ODCS Lineage Section
// =============================================================================

export interface ExtractionConfig {
  method: ExtractionMethod;
  filter?: string;
}

export interface LineageSource {
  type: SourceType;
  identifier: string;
  description?: string;
  fields_used?: string[];
  extraction?: ExtractionConfig;
}

export interface Lineage {
  sources?: LineageSource[];
}

// =============================================================================
// ODCS SLA Section
// =============================================================================

export interface AvailabilitySLA {
  target_percent: number;
  measurement_window: string; // ISO 8601 duration
}

export interface FreshnessSLA {
  target: string; // ISO 8601 duration
  measurement_field?: string;
}

export interface CompletenessSLA {
  target_percent: number;
  critical_fields?: string[];
  critical_target_percent?: number;
}

export interface AccuracySLA {
  error_rate_target: number;
  validation_method?: string;
}

export interface ResponseTimeSLA {
  p50_ms?: number;
  p99_ms?: number;
}

export interface SLA {
  availability?: AvailabilitySLA;
  freshness?: FreshnessSLA;
  completeness?: CompletenessSLA;
  accuracy?: AccuracySLA;
  response_time?: ResponseTimeSLA;
}

// =============================================================================
// ODCS Access Section
// =============================================================================

export interface AccessGrant {
  principal: string;
  level: AccessLevel;
  fields?: string[];
  expiry?: string;
  conditions?: Record<string, unknown>;
}

export interface AccessApproval {
  required: boolean;
  approvers?: string[];
  workflow?: string;
}

export interface AccessAuthentication {
  methods?: string[];
  provider?: string;
}

export interface Access {
  default_level: AccessLevel;
  grants?: AccessGrant[];
  approval?: AccessApproval;
  authentication?: AccessAuthentication;
}

// =============================================================================
// ODCS Distribution Section
// =============================================================================

export interface PartitioningConfig {
  fields?: string[];
  strategy: PartitioningStrategy;
}

export interface DistributionChannel {
  type: DistributionType;
  identifier: string;
  format?: string;
  partitioning?: PartitioningConfig;
}

export interface Distribution {
  channels?: DistributionChannel[];
}

// =============================================================================
// ODCS Governance Section
// =============================================================================

export interface ProducerInfo {
  team: string;
  contact?: string;
  responsibilities?: string[];
}

export interface ConsumerInfo {
  team: string;
  contact?: string;
  use_case?: string;
  approved_date?: string;
  approved_by?: string;
}

export interface ApprovalEntry {
  role: string;
  approver?: string;
  approved_date?: string;
  comments?: string;
}

export interface ReviewConfig {
  cadence: ReviewCadence;
  last_review?: string;
  next_review?: string;
  reviewers?: string[];
}

export interface ChangeManagement {
  breaking_change_notice: string; // ISO 8601 duration
  deprecation_notice: string; // ISO 8601 duration
  communication_channels?: string[];
  migration_support: boolean;
}

export interface DisputeResolution {
  process?: string;
  escalation_path?: string[];
}

export interface DocumentationLinks {
  wiki?: string;
  runbook?: string;
  changelog?: string;
}

export interface Governance {
  producer?: ProducerInfo;
  consumers?: ConsumerInfo[];
  approval_chain?: ApprovalEntry[];
  review?: ReviewConfig;
  change_management?: ChangeManagement;
  dispute_resolution?: DisputeResolution;
  documentation?: DocumentationLinks;
}

// =============================================================================
// ODCS Team Section
// =============================================================================

export interface Steward {
  name: string;
  email?: string;
}

export interface Team {
  name: string;
  department?: string;
  steward?: Steward;
}

// =============================================================================
// ODCS Server Section
// =============================================================================

export interface Server {
  server: string;
  environment: 'development' | 'staging' | 'production';
  type: string;
  project: string;
  dataset: string;
}

// =============================================================================
// ODCS Role Section
// =============================================================================

export interface Role {
  role: string;
  access: AccessLevel;
}

// =============================================================================
// ODCS Timestamps Section
// =============================================================================

export interface Timestamps {
  created_at: string;
  updated_at: string;
  effective_from?: string;
  effective_until?: string;
}

// =============================================================================
// Legacy Field (for backwards compatibility)
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
// Contract (ODCS-aware)
// =============================================================================

export interface Contract {
  // Core identifiers
  id: string;
  name: string;
  api_version: string;
  kind: 'DataContract';

  // Basic metadata
  description?: string;
  owner?: string;
  version: string;
  status: ContractStatus;

  // ODCS sections
  description_odcs?: Description;
  schema?: SchemaDefinition[];
  legal?: Legal;
  compliance?: Compliance;
  lineage?: Lineage;
  sla?: SLA;
  access?: Access;
  distribution?: Distribution;
  governance?: Governance;
  team?: Team;
  servers?: Server[];
  roles?: Role[];

  // Timestamps
  created_at?: string;
  updated_at?: string;
  effective_from?: string;
  effective_until?: string;
}

export interface ContractCreate {
  id: string;
  name: string;
  description?: string;
  owner?: string;

  // ODCS sections
  description_odcs?: Description;
  schema?: SchemaDefinition[];
  legal?: Legal;
  compliance?: Compliance;
  lineage?: Lineage;
  sla?: SLA;
  access?: Access;
  distribution?: Distribution;
  governance?: Governance;
  team?: Team;
  servers?: Server[];
  roles?: Role[];
}

export type ChangeType = 'patch' | 'minor' | 'major';

export interface ContractUpdate {
  name?: string;
  description?: string;

  // ODCS sections
  description_odcs?: Description;
  schema?: SchemaDefinition[];
  legal?: Legal;
  compliance?: Compliance;
  lineage?: Lineage;
  sla?: SLA;
  access?: Access;
  distribution?: Distribution;
  governance?: Governance;
  team?: Team;
  servers?: Server[];
  roles?: Role[];

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
// Versions
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

export interface SectionChange {
  section: string;
  change_type: 'added' | 'removed' | 'modified';
  summary?: string;
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
  section_changes?: SectionChange[];
  added_schemas?: string[];
  removed_schemas?: string[];
  modified_schemas?: string[];
}

// =============================================================================
// Breaking Changes (T-305, T-384)
// =============================================================================

export interface BreakingChangeInfo {
  change_type: BreakingChangeType | string;
  field?: string;
  description: string;
  from_value?: unknown;
  to_value?: unknown;
  migration_hint?: string;
}

export interface BreakingChangesResponse {
  code: 'BREAKING_CHANGES_DETECTED';
  message: string;
  breaking_changes: BreakingChangeInfo[];
  allow_breaking_hint: string;
}

// =============================================================================
// Validations
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
// Search
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
// API Parameters
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
// PII & Privacy (Phase 2)
// =============================================================================

// Re-export for backwards compatibility
export type PIICategoryLegacy =
  | 'direct_identifier'
  | 'quasi_identifier'
  | 'sensitive'
  | 'non_pii';

export type MaskingStrategyLegacy =
  | 'none'
  | 'redact'
  | 'hash'
  | 'tokenize'
  | 'encrypt'
  | 'generalize'
  | 'pseudonymize';

export type LegalBasisLegacy =
  | 'consent'
  | 'contract'
  | 'legal_obligation'
  | 'vital_interests'
  | 'public_task'
  | 'legitimate_interests';

export interface PIIFieldInfo {
  field_name: string;
  contract_id: string;
  pii_category: PIICategory | PIICategoryLegacy;
  sensitivity_level: SensitivityLevel;
  masking_strategy: MaskingStrategy | MaskingStrategyLegacy;
  legal_basis?: LegalBasis | LegalBasisLegacy;
  retention_days?: number;
}

// =============================================================================
// Residency
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
// Reports
// =============================================================================

// Audit Report
export interface PIIInventoryItem {
  contract_id: string;
  contract_name: string;
  field_name: string;
  pii_category: PIICategory | PIICategoryLegacy;
  sensitivity_level: SensitivityLevel;
  masking_strategy: MaskingStrategy | MaskingStrategyLegacy;
  legal_basis?: LegalBasis | LegalBasisLegacy;
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
  pii_by_category: Record<string, number>;
  pii_by_sensitivity: Record<SensitivityLevel, number>;
  residency_checks: ResidencyCheck[];
  residency_compliance_rate: number;
  legal_basis_coverage: Record<string, number>;
  retention_policy_coverage: number;
}

// Analytics Report
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

// AI Readiness Report
export interface AIReadinessScore {
  overall_score: number;
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

// Combined Readiness Report
export interface ReadinessReport {
  generated_at: string;
  audit: AuditReport;
  analytics: AnalyticsReport;
  ai_readiness: AIReadinessReport;
  overall_health_score: number;
}

// =============================================================================
// Report Parameters
// =============================================================================

export interface ReportParams {
  contract_ids?: string[];
  from_date?: string;
  to_date?: string;
  include_details?: boolean;
}

// =============================================================================
// Data Governance AI (for UI - inspired by reference image)
// =============================================================================

export type PolicyCheckStatus = 'pass' | 'fail' | 'warning' | 'info';

export interface PolicyCheck {
  name: string;
  status: PolicyCheckStatus;
  issues?: PolicyIssue[];
}

export interface PolicyIssue {
  message: string;
  severity: 'error' | 'warning' | 'info';
  field?: string;
}

export interface DataGovernanceReport {
  ownership: PolicyCheck;
  data_classification: PolicyCheck;
  mandatory_fields: PolicyCheck;
  pii_compliance: PolicyCheck;
  sla_defined: PolicyCheck;
}

// =============================================================================
// Approval Workflow Types
// =============================================================================

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type ApprovalDecisionType = 'approve' | 'reject';

export interface ApproverInfo {
  user_id: string;
  email: string;
  name?: string;
  role?: string;
}

export interface Approval {
  id: string;
  approver: ApproverInfo;
  status: ApprovalStatus;
  decision_at?: string;
  comment?: string;
  order: number;
}

export interface ApprovalChain {
  id: string;
  contract_id: string;
  contract_version: string;
  approvals: Approval[];
  created_at: string;
  created_by: string;
  status: ApprovalStatus;
  completed_at?: string;
}

export interface ApprovalChainCreate {
  approvers: ApproverInfo[];
  require_all?: boolean;
  notify?: boolean;
}

export interface ApprovalDecision {
  decision: ApprovalDecisionType;
  comment?: string;
}

export interface ApprovalChainStatus {
  chain_id: string;
  contract_id: string;
  contract_version: string;
  status: ApprovalStatus;
  total_approvers: number;
  approved_count: number;
  pending_count: number;
  rejected_count: number;
  current_approver?: ApproverInfo;
  created_at: string;
  completed_at?: string;
}
