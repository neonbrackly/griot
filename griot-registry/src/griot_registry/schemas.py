"""Pydantic schemas for API request/response models.

Updated for Open Data Contract Standard (ODCS) - T-370.
"""

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# ODCS Enums as Literals (T-370)
# =============================================================================
ContractStatusType = Literal["draft", "active", "deprecated", "retired"]
PhysicalTypeValue = Literal["table", "view", "file", "stream"]
QualityRuleTypeValue = Literal["completeness", "accuracy", "freshness", "volume", "distribution"]
CheckTypeValue = Literal["sql", "python", "great_expectations"]
SeverityValue = Literal["error", "warning", "info"]
ExtractionMethodValue = Literal["full", "incremental", "cdc"]
PartitioningStrategyValue = Literal["date", "hash", "range"]
ReviewCadenceValue = Literal["monthly", "quarterly", "annually"]
AccessLevelValue = Literal["read", "write", "admin"]
DistributionTypeValue = Literal["warehouse", "lake", "api", "stream", "file"]
SourceTypeValue = Literal["system", "contract", "file", "api", "stream"]
SensitivityLevelValue = Literal["public", "internal", "confidential", "restricted"]
MaskingStrategyValue = Literal[
    "none", "redact", "hash_sha256", "hash_md5", "tokenize",
    "generalize", "k_anonymize", "differential_privacy", "encrypt"
]
LegalBasisValue = Literal[
    "consent", "contract", "legal_obligation", "vital_interest",
    "public_task", "legitimate_interest"
]
PIICategoryValue = Literal[
    "email", "phone", "national_id", "name", "address", "dob",
    "financial", "health", "biometric", "location", "other"
]


# =============================================================================
# Common
# =============================================================================
class ErrorResponse(BaseModel):
    """Standard error response."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class PaginatedResponse(BaseModel):
    """Base for paginated responses."""

    total: int
    limit: int
    offset: int


# =============================================================================
# Field Schemas
# =============================================================================
class FieldConstraints(BaseModel):
    """Constraints applied to a field."""

    model_config = ConfigDict(extra="allow")

    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: Literal[
        "email", "uri", "uuid", "date", "datetime", "ipv4", "ipv6", "hostname"
    ] | None = None
    ge: float | None = None
    le: float | None = None
    gt: float | None = None
    lt: float | None = None
    multiple_of: float | None = None
    enum: list[Any] | None = None


class FieldMetadata(BaseModel):
    """Additional metadata for a field."""

    model_config = ConfigDict(extra="allow")

    unit: str | None = None
    aggregation: Literal["sum", "avg", "count", "min", "max", "none"] | None = None
    glossary_term: str | None = None


class FieldDefinition(BaseModel):
    """Schema for a single field in a contract."""

    name: str
    type: Literal["string", "integer", "float", "boolean", "date", "datetime", "array", "object"]
    description: str
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    constraints: FieldConstraints | None = None
    metadata: FieldMetadata | None = None


# =============================================================================
# ODCS Schema Sections (T-370)
# =============================================================================

# --- Description Section ---
class CustomProperty(BaseModel):
    """Custom property for description section."""

    name: str
    value: str
    description: str | None = None


class Description(BaseModel):
    """Contract description section (ODCS)."""

    purpose: str | None = None
    usage: str | None = None
    limitations: str | None = None
    custom_properties: list[CustomProperty] | None = Field(default=None, alias="customProperties")

    model_config = ConfigDict(populate_by_name=True)


# --- Schema Property Section (Enhanced Field) ---
class ForeignKey(BaseModel):
    """Foreign key reference to another contract."""

    contract: str = Field(..., description="Referenced contract ID")
    field: str = Field(..., description="Referenced field name")


class SemanticInfo(BaseModel):
    """Semantic metadata for a field."""

    description: str | None = None
    unit: str | None = None
    precision: int | None = None
    business_term: str | None = None
    glossary_uri: str | None = None


class PrivacyInfo(BaseModel):
    """Privacy metadata for a field."""

    contains_pii: bool = False
    pii_category: PIICategoryValue | None = None
    sensitivity_level: SensitivityLevelValue = "internal"
    masking: MaskingStrategyValue = "none"
    retention_days: int | None = None
    legal_basis: LegalBasisValue | None = None


class SchemaProperty(BaseModel):
    """Enhanced field definition with ODCS structure."""

    name: str
    description: str | None = None
    logical_type: str = Field(default="string", alias="logicalType")
    physical_type: str | None = Field(default=None, alias="physicalType")
    nullable: bool = True
    examples: list[Any] | None = None
    primary_key: bool = False
    foreign_key: ForeignKey | None = None
    constraints: FieldConstraints | None = None
    semantic: SemanticInfo | None = None
    privacy: PrivacyInfo | None = None

    model_config = ConfigDict(populate_by_name=True)


# --- Quality Rules Section ---
class CompletenessRule(BaseModel):
    """Completeness quality rule."""

    rule: Literal["completeness"] = "completeness"
    min_percent: float = Field(..., ge=0, le=100)
    critical_fields: list[str] | None = None


class AccuracyRule(BaseModel):
    """Accuracy quality rule."""

    rule: Literal["accuracy"] = "accuracy"
    max_error_rate: float = Field(..., ge=0, le=1)
    validation_method: str | None = None


class FreshnessRule(BaseModel):
    """Freshness quality rule."""

    rule: Literal["freshness"] = "freshness"
    max_age: str = Field(..., description="ISO 8601 duration (e.g., PT24H)")
    timestamp_field: str | None = None


class VolumeRule(BaseModel):
    """Volume quality rule."""

    rule: Literal["volume"] = "volume"
    min_rows: int | None = None
    max_rows: int | None = None


class DistributionRule(BaseModel):
    """Distribution quality rule."""

    rule: Literal["distribution"] = "distribution"
    field: str
    expected_distribution: dict[str, Any] | None = None


class CustomCheck(BaseModel):
    """Custom quality check."""

    name: str
    type: CheckTypeValue
    definition: str
    severity: SeverityValue = "error"


class QualityRules(BaseModel):
    """Quality rules for a schema."""

    completeness: CompletenessRule | None = None
    accuracy: AccuracyRule | None = None
    freshness: FreshnessRule | None = None
    volume: VolumeRule | None = None
    distribution: DistributionRule | None = None
    custom_checks: list[CustomCheck] | None = None


# --- Schema Section (Dataset/Table) ---
class SchemaDefinition(BaseModel):
    """Schema definition for a dataset/table."""

    name: str
    physical_type: PhysicalTypeValue = Field(default="table", alias="physicalType")
    properties: list[SchemaProperty] | None = None
    quality: QualityRules | None = None

    model_config = ConfigDict(populate_by_name=True)


# --- Legal Section ---
class CrossBorder(BaseModel):
    """Cross-border data transfer rules."""

    restrictions: list[str] | None = None
    transfer_mechanisms: list[str] | None = None
    data_residency: str | None = None


class Legal(BaseModel):
    """Legal requirements section."""

    jurisdiction: list[str] | None = None
    basis: LegalBasisValue | None = None
    consent_id: str | None = None
    regulations: list[str] | None = None
    cross_border: CrossBorder | None = None


# --- Compliance Section ---
class AuditRequirements(BaseModel):
    """Audit requirements for compliance."""

    logging: bool = True
    log_retention: str | None = Field(default="P365D", description="ISO 8601 duration")


class ExportRestrictions(BaseModel):
    """Export restrictions for compliance."""

    allow_download: bool = True
    allow_external_transfer: bool = False
    allowed_destinations: list[str] | None = None


class Compliance(BaseModel):
    """Compliance requirements section."""

    data_classification: SensitivityLevelValue = "internal"
    regulatory_scope: list[str] | None = None
    audit_requirements: AuditRequirements | None = None
    certification_requirements: list[str] | None = None
    export_restrictions: ExportRestrictions | None = None


# --- Lineage Section ---
class ExtractionConfig(BaseModel):
    """Extraction configuration for a source."""

    method: ExtractionMethodValue = "full"
    filter: str | None = None


class LineageSource(BaseModel):
    """Source in data lineage."""

    type: SourceTypeValue
    identifier: str
    description: str | None = None
    fields_used: list[str] | None = None
    extraction: ExtractionConfig | None = None


class Lineage(BaseModel):
    """Data lineage section."""

    sources: list[LineageSource] | None = None


# --- SLA Section ---
class AvailabilitySLA(BaseModel):
    """Availability SLA."""

    target_percent: float = Field(default=99.0, ge=0, le=100)
    measurement_window: str = Field(default="P30D", description="ISO 8601 duration")


class FreshnessSLA(BaseModel):
    """Freshness SLA."""

    target: str = Field(..., description="ISO 8601 duration (e.g., PT4H)")
    measurement_field: str | None = None


class CompletenessSLA(BaseModel):
    """Completeness SLA."""

    target_percent: float = Field(default=99.5, ge=0, le=100)
    critical_fields: list[str] | None = None
    critical_target_percent: float | None = Field(default=None, ge=0, le=100)


class AccuracySLA(BaseModel):
    """Accuracy SLA."""

    error_rate_target: float = Field(default=0.001, ge=0, le=1)
    validation_method: str | None = None


class ResponseTimeSLA(BaseModel):
    """Response time SLA for API access."""

    p50_ms: int | None = None
    p99_ms: int | None = None


class SLA(BaseModel):
    """Service Level Agreement section."""

    availability: AvailabilitySLA | None = None
    freshness: FreshnessSLA | None = None
    completeness: CompletenessSLA | None = None
    accuracy: AccuracySLA | None = None
    response_time: ResponseTimeSLA | None = None


# --- Access Section ---
class AccessGrant(BaseModel):
    """Access grant for a principal."""

    principal: str = Field(..., description="team://, role://, user://, service://")
    level: AccessLevelValue
    fields: list[str] | None = None
    expiry: date | None = None
    conditions: dict[str, Any] | None = None


class AccessApproval(BaseModel):
    """Access approval configuration."""

    required: bool = False
    approvers: list[str] | None = None
    workflow: str | None = None


class AccessAuthentication(BaseModel):
    """Authentication configuration."""

    methods: list[str] | None = None
    provider: str | None = None


class Access(BaseModel):
    """Access control section."""

    default_level: AccessLevelValue = "read"
    grants: list[AccessGrant] | None = None
    approval: AccessApproval | None = None
    authentication: AccessAuthentication | None = None


# --- Distribution Section ---
class PartitioningConfig(BaseModel):
    """Partitioning configuration for distribution."""

    fields: list[str] | None = None
    strategy: PartitioningStrategyValue = "date"


class DistributionChannel(BaseModel):
    """Distribution channel configuration."""

    type: DistributionTypeValue
    identifier: str
    format: str | None = None
    partitioning: PartitioningConfig | None = None


class Distribution(BaseModel):
    """Distribution section."""

    channels: list[DistributionChannel] | None = None


# --- Governance Section ---
class ProducerInfo(BaseModel):
    """Producer team information."""

    team: str
    contact: str | None = None
    responsibilities: list[str] | None = None


class ConsumerInfo(BaseModel):
    """Consumer team information."""

    team: str
    contact: str | None = None
    use_case: str | None = None
    approved_date: date | None = None
    approved_by: str | None = None


class ApprovalEntry(BaseModel):
    """Approval chain entry."""

    role: str
    approver: str | None = None
    approved_date: datetime | None = None
    comments: str | None = None


class ReviewConfig(BaseModel):
    """Review configuration."""

    cadence: ReviewCadenceValue = "quarterly"
    last_review: date | None = None
    next_review: date | None = None
    reviewers: list[str] | None = None


class ChangeManagement(BaseModel):
    """Change management configuration."""

    breaking_change_notice: str = Field(default="P30D", description="ISO 8601 duration")
    deprecation_notice: str = Field(default="P90D", description="ISO 8601 duration")
    communication_channels: list[str] | None = None
    migration_support: bool = True


class DisputeResolution(BaseModel):
    """Dispute resolution configuration."""

    process: str | None = None
    escalation_path: list[str] | None = None


class Documentation(BaseModel):
    """Documentation links."""

    wiki: str | None = None
    runbook: str | None = None
    changelog: str | None = None


class Governance(BaseModel):
    """Governance section."""

    producer: ProducerInfo | None = None
    consumers: list[ConsumerInfo] | None = None
    approval_chain: list[ApprovalEntry] | None = None
    review: ReviewConfig | None = None
    change_management: ChangeManagement | None = None
    dispute_resolution: DisputeResolution | None = None
    documentation: Documentation | None = None


# --- Team Section ---
class Steward(BaseModel):
    """Data steward contact."""

    name: str
    email: str | None = None


class Team(BaseModel):
    """Team information section."""

    name: str
    department: str | None = None
    steward: Steward | None = None


# --- Server Section ---
class Server(BaseModel):
    """Server/environment configuration."""

    server: str = Field(..., description="Unique server name")
    environment: str = Field(..., description="development | staging | production")
    type: str = Field(..., description="bigquery | redshift | snowflake | s3 | kafka")
    project: str = Field(..., description="Cloud project or account")
    dataset: str = Field(..., description="Dataset, database, or bucket name")


# --- Role Section ---
class Role(BaseModel):
    """Role configuration."""

    role: str = Field(..., description="Role name")
    access: AccessLevelValue


# --- Timestamps Section ---
class Timestamps(BaseModel):
    """Timestamp metadata."""

    created_at: datetime
    updated_at: datetime
    effective_from: date | None = None
    effective_until: date | None = None


# =============================================================================
# Contract Schemas (Updated for ODCS - T-370)
# =============================================================================
class ContractBase(BaseModel):
    """Base contract fields with ODCS support."""

    # Core identifiers
    id: str = Field(..., examples=["customer-profile"])
    name: str = Field(..., examples=["Customer Profile"])
    api_version: str = Field(default="v1.0.0", description="Griot Contract Schema version")
    kind: Literal["DataContract"] = "DataContract"

    # Legacy simple description (for backwards compatibility)
    description: str | None = None
    owner: str | None = None


class ContractCreate(ContractBase):
    """Schema for creating a new contract (ODCS-aware)."""

    # Legacy field list (for backwards compatibility)
    fields: list[FieldDefinition] | None = None

    # ODCS sections
    description_section: Description | None = Field(default=None, alias="description_odcs")
    schema: list[SchemaDefinition] | None = None
    legal: Legal | None = None
    compliance: Compliance | None = None
    lineage: Lineage | None = None
    sla: SLA | None = None
    access: Access | None = None
    distribution: Distribution | None = None
    governance: Governance | None = None
    team: Team | None = None
    servers: list[Server] | None = None
    roles: list[Role] | None = None

    model_config = ConfigDict(populate_by_name=True)


class ContractUpdate(BaseModel):
    """Schema for updating a contract (creates new version)."""

    # Basic updates
    name: str | None = None
    description: str | None = None

    # Legacy field list (for backwards compatibility)
    fields: list[FieldDefinition] | None = None

    # ODCS section updates
    description_section: Description | None = Field(default=None, alias="description_odcs")
    schema: list[SchemaDefinition] | None = None
    legal: Legal | None = None
    compliance: Compliance | None = None
    lineage: Lineage | None = None
    sla: SLA | None = None
    access: Access | None = None
    distribution: Distribution | None = None
    governance: Governance | None = None
    team: Team | None = None
    servers: list[Server] | None = None
    roles: list[Role] | None = None

    # Version control
    change_type: Literal["patch", "minor", "major"] = "minor"
    change_notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class Contract(ContractBase):
    """Full contract response schema with ODCS support."""

    # Version info
    version: str = Field(..., examples=["1.2.0"])
    status: ContractStatusType = "draft"

    # Legacy field list (for backwards compatibility)
    fields: list[FieldDefinition] = Field(default_factory=list)

    # ODCS sections
    description_section: Description | None = Field(default=None, alias="description_odcs")
    schema: list[SchemaDefinition] | None = None
    legal: Legal | None = None
    compliance: Compliance | None = None
    lineage: Lineage | None = None
    sla: SLA | None = None
    access: Access | None = None
    distribution: Distribution | None = None
    governance: Governance | None = None
    team: Team | None = None
    servers: list[Server] | None = None
    roles: list[Role] | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    effective_from: date | None = None
    effective_until: date | None = None

    model_config = ConfigDict(populate_by_name=True)


class ContractList(PaginatedResponse):
    """Paginated list of contracts."""

    items: list[Contract]


# =============================================================================
# ODCS Contract (Full Schema) - T-370
# =============================================================================
class ODCSContract(BaseModel):
    """Full Open Data Contract Standard contract schema.

    This represents the complete ODCS specification for contracts.
    Use this when you need the full ODCS structure without legacy fields.
    """

    # Required metadata
    api_version: str = Field(default="v1.0.0", alias="apiVersion")
    kind: Literal["DataContract"] = "DataContract"
    id: str
    name: str
    version: str
    status: ContractStatusType = "draft"

    # Description section
    description: Description | None = None

    # Schema section (datasets/tables with fields)
    schema: list[SchemaDefinition] | None = None

    # Legal and compliance
    legal: Legal | None = None
    compliance: Compliance | None = None

    # Data lineage
    lineage: Lineage | None = None

    # Service level agreements
    sla: SLA | None = None

    # Access control
    access: Access | None = None

    # Distribution channels
    distribution: Distribution | None = None

    # Governance
    governance: Governance | None = None

    # Team ownership
    team: Team | None = None

    # Infrastructure
    servers: list[Server] | None = None
    roles: list[Role] | None = None

    # Timestamps
    timestamps: Timestamps | None = None

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# Version Schemas
# =============================================================================
class VersionSummary(BaseModel):
    """Summary of a contract version."""

    version: str
    created_at: datetime
    created_by: str | None = None
    change_type: Literal["patch", "minor", "major"] | None = None
    change_notes: str | None = None
    is_breaking: bool = False


class VersionList(BaseModel):
    """List of version summaries."""

    items: list[VersionSummary]
    total: int


class TypeChange(BaseModel):
    """Represents a field type change between versions."""

    field: str
    from_type: str
    to_type: str
    is_breaking: bool


class ConstraintChange(BaseModel):
    """Represents a constraint change between versions."""

    field: str
    constraint: str
    from_value: Any
    to_value: Any
    is_breaking: bool


class SectionChange(BaseModel):
    """Represents a change to an ODCS section (T-374)."""

    section: str = Field(..., description="ODCS section name (legal, compliance, sla, etc.)")
    change_type: Literal["added", "removed", "modified"] = "modified"
    summary: str | None = Field(None, description="Human-readable summary of changes")
    is_breaking: bool = False


class ContractDiff(BaseModel):
    """Diff between two contract versions (T-374 enhanced for ODCS)."""

    from_version: str
    to_version: str
    has_breaking_changes: bool

    # Legacy field changes (backwards compatible)
    added_fields: list[str]
    removed_fields: list[str]
    type_changes: list[TypeChange]
    constraint_changes: list[ConstraintChange]

    # ODCS section changes (T-374)
    section_changes: list[SectionChange] = Field(default_factory=list)
    added_schemas: list[str] = Field(default_factory=list, description="Schema definitions added")
    removed_schemas: list[str] = Field(default_factory=list, description="Schema definitions removed")
    modified_schemas: list[str] = Field(default_factory=list, description="Schema definitions modified")


# =============================================================================
# Validation Schemas
# =============================================================================
class ValidationError(BaseModel):
    """A single validation error."""

    field: str
    row: int | None = None
    value: Any = None
    constraint: str
    message: str


class ValidationReport(BaseModel):
    """Report of a validation run (from griot-enforce)."""

    contract_id: str
    contract_version: str | None = None
    passed: bool
    row_count: int
    error_count: int = 0
    error_rate: float = 0.0
    duration_ms: float | None = None
    environment: Literal["development", "staging", "production"] | None = None
    pipeline_id: str | None = None
    run_id: str | None = None
    sample_errors: list[ValidationError] = Field(default_factory=list, max_length=100)


class ValidationRecord(BaseModel):
    """Stored validation record."""

    id: UUID
    contract_id: str
    contract_version: str | None = None
    passed: bool
    row_count: int
    error_count: int
    recorded_at: datetime


class ValidationList(PaginatedResponse):
    """Paginated list of validation records."""

    items: list[ValidationRecord]


# =============================================================================
# Breaking Change Schemas (T-304, T-371, T-372)
# =============================================================================
class BreakingChangeInfo(BaseModel):
    """Information about a single breaking change."""

    change_type: str = Field(
        ...,
        description="Type of breaking change (field_removed, type_changed_incompatible, etc.)",
    )
    field: str | None = Field(None, description="Affected field name")
    description: str = Field(..., description="Human-readable description")
    from_value: Any = None
    to_value: Any = None
    migration_hint: str | None = Field(None, description="Suggested migration approach")


class BreakingChangesResponse(BaseModel):
    """Response when breaking changes are detected and blocked."""

    code: str = "BREAKING_CHANGES_DETECTED"
    message: str = "Update contains breaking changes that require explicit acknowledgment"
    breaking_changes: list[BreakingChangeInfo]
    allow_breaking_hint: str = Field(
        default="Add ?allow_breaking=true to force the update",
        description="Hint for how to proceed with breaking changes",
    )


# =============================================================================
# Search Schemas
# =============================================================================
class SearchHit(BaseModel):
    """A single search result."""

    contract_id: str
    contract_name: str
    field_name: str | None = None
    match_type: Literal["name", "description", "field"]
    snippet: str | None = None


class SearchResults(BaseModel):
    """Search results response."""

    query: str
    items: list[SearchHit]
    total: int
