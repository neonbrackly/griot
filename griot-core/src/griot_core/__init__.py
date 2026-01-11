"""
Griot Core - Data Contract Definition Library

A Python library for defining, validating, and managing data contracts
with full AI/LLM readiness support.

Example:
    from griot_core import GriotModel, Field

    class Customer(GriotModel):
        customer_id: str = Field(
            description="Unique customer identifier",
            primary_key=True,
            pattern=r"^CUST-\\d{6}$"
        )
        email: str = Field(
            description="Customer email address",
            format="email",
            max_length=255
        )
        age: int = Field(
            description="Customer age in years",
            ge=0,
            le=150,
            unit="years"
        )

    # Validate data
    result = Customer.validate(data)
    if not result.passed:
        for error in result.errors:
            print(f"{error.field}: {error.message}")

    # Generate mock data
    mock_data = Customer.mock(rows=100)

    # Export for AI/LLM
    manifest = Customer.to_manifest(format="llm_context")
"""
from __future__ import annotations

__version__ = "0.5.0"  # Phase 6 - ODCS Overhaul
__all__ = [
    # Core classes
    "GriotModel",
    "Field",
    "FieldInfo",
    # Type definitions (Phase 1)
    "ConstraintType",
    "Severity",
    "FieldFormat",
    "AggregationType",
    "DataType",
    # PII/Privacy types (Phase 2 - FR-SDK-008)
    "PIICategory",
    "SensitivityLevel",
    "MaskingStrategy",
    "LegalBasis",
    # Data Residency types (Phase 2 - FR-SDK-011)
    "DataRegion",
    "ResidencyConfig",
    "ResidencyRule",
    # Data Lineage types (Phase 2 - FR-SDK-012)
    "LineageConfig",
    "Source",
    "Transformation",
    "Consumer",
    # Phase 6 - ODCS types (Open Data Contract Standard)
    "ContractStatus",
    "PhysicalType",
    "QualityRuleType",
    "CheckType",
    "ExtractionMethod",
    "PartitioningStrategy",
    "ReviewCadence",
    "AccessLevel",
    "DistributionType",
    "SourceType",
    # Phase 6 - ODCS dataclasses
    "CustomProperty",
    "Description",
    "SemanticInfo",
    "PrivacyInfo",
    "FieldConstraints",
    "ForeignKey",
    "SchemaProperty",
    "QualityRule",
    "CustomCheck",
    "Legal",
    "CrossBorder",
    "Compliance",
    "AuditRequirements",
    "SLA",
    "AvailabilitySLA",
    "FreshnessSLA",
    "CompletenessSLA",
    "AccuracySLA",
    "ResponseTimeSLA",
    "AccessGrant",
    "AccessApproval",
    "AccessConfig",
    "DistributionChannel",
    "Distribution",
    "GovernanceProducer",
    "GovernanceConsumer",
    "ApprovalRecord",
    "ReviewConfig",
    "ChangeManagement",
    "Governance",
    "Team",
    "Steward",
    "Server",
    "Role",
    "Timestamps",
    # Validation
    "ValidationResult",
    "FieldValidationError",
    "FieldStats",
    "validate_data",
    "validate_value",
    # Quality validation (Phase 6 - T-331)
    "QualityRuleResult",
    "QualityValidationResult",
    "validate_quality_rules",
    "validate_completeness",
    "validate_volume",
    "validate_freshness",
    # Contract operations
    "ContractDiff",
    "TypeChange",
    "ConstraintChange",
    "LintIssue",
    "load_contract",
    "load_contract_from_string",
    "load_contract_from_dict",
    "model_to_yaml",
    "model_to_dict",
    # Breaking change detection (Phase 6 - T-300, T-301, T-302)
    "BreakingChange",
    "BreakingChangeType",
    "detect_breaking_changes",
    # Schema migration (Phase 6 - T-330)
    "MigrationResult",
    "detect_schema_version",
    "migrate_contract",
    "migrate_v0_to_v1",
    # Exceptions
    "GriotError",
    "ValidationError",
    "ContractNotFoundError",
    "ContractParseError",
    "BreakingChangeError",
    "ConstraintError",
    # Mock generation
    "generate_mock_data",
    # Manifest export
    "export_manifest",
    # Reports (Phase 2 - FR-SDK-013, FR-SDK-014, FR-SDK-016)
    "AnalyticsReport",
    "AIReadinessReport",
    "AuditReport",
    "ReadinessReport",
    "generate_analytics_report",
    "generate_ai_readiness_report",
    "generate_audit_report",
    "generate_readiness_report",
]

# Core classes
from griot_core.models import Field, FieldInfo, GriotModel

# Type definitions (Phase 1)
from griot_core.types import (
    AggregationType,
    ConstraintType,
    DataType,
    FieldFormat,
    Severity,
)

# PII/Privacy types (Phase 2)
from griot_core.types import (
    LegalBasis,
    MaskingStrategy,
    PIICategory,
    SensitivityLevel,
)

# Data Residency types (Phase 2)
from griot_core.types import (
    DataRegion,
    ResidencyConfig,
    ResidencyRule,
)

# Data Lineage types (Phase 2)
from griot_core.types import (
    Consumer,
    LineageConfig,
    Source,
    Transformation,
)

# Phase 6 - ODCS types (Open Data Contract Standard)
from griot_core.types import (
    AccessLevel,
    CheckType,
    ContractStatus,
    DistributionType,
    ExtractionMethod,
    PartitioningStrategy,
    PhysicalType,
    QualityRuleType,
    ReviewCadence,
    SourceType,
)

# Phase 6 - ODCS dataclasses (T-311 through T-326)
from griot_core.types import (
    AccuracySLA,
    AccessApproval,
    AccessConfig,
    AccessGrant,
    ApprovalRecord,
    AuditRequirements,
    AvailabilitySLA,
    ChangeManagement,
    Compliance,
    CompletenessSLA,
    CrossBorder,
    CustomCheck,
    CustomProperty,
    Description,
    Distribution,
    DistributionChannel,
    FieldConstraints,
    ForeignKey,
    FreshnessSLA,
    Governance,
    GovernanceConsumer,
    GovernanceProducer,
    Legal,
    PrivacyInfo,
    QualityRule,
    ResponseTimeSLA,
    ReviewConfig,
    Role,
    SchemaProperty,
    SemanticInfo,
    Server,
    SLA,
    Steward,
    Team,
    Timestamps,
)

# Validation
from griot_core.validation import (
    FieldStats,
    FieldValidationError,
    ValidationResult,
    validate_data,
    validate_value,
)

# Quality validation (Phase 6 - T-331)
from griot_core.validation import (
    QualityRuleResult,
    QualityValidationResult,
    validate_completeness,
    validate_freshness,
    validate_quality_rules,
    validate_volume,
)

# Contract operations
from griot_core.contract import (
    ConstraintChange,
    ContractDiff,
    LintIssue,
    TypeChange,
    load_contract,
    load_contract_from_dict,
    load_contract_from_string,
    model_to_dict,
    model_to_yaml,
)

# Breaking change detection (Phase 6 - T-300, T-301, T-302)
from griot_core.contract import (
    BreakingChange,
    BreakingChangeType,
    detect_breaking_changes,
)

# Schema migration (Phase 6 - T-330)
from griot_core.migration import (
    MigrationResult,
    detect_schema_version,
    migrate_contract,
    migrate_v0_to_v1,
)

# Exceptions
from griot_core.exceptions import (
    BreakingChangeError,
    ConstraintError,
    ContractNotFoundError,
    ContractParseError,
    GriotError,
    ValidationError,
)

# Mock generation
from griot_core.mock import generate_mock_data

# Manifest export
from griot_core.manifest import export_manifest

# Reports (Phase 2)
from griot_core.reports import (
    AIReadinessReport,
    AnalyticsReport,
    AuditReport,
    ReadinessReport,
    generate_ai_readiness_report,
    generate_analytics_report,
    generate_audit_report,
    generate_readiness_report,
)
