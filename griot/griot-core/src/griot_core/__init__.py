"""
Griot Core - Data Contract Definition Library

A Python library for defining, validating, and managing data contracts
with full AI/LLM readiness support. Uses Python stdlib only (no external
dependencies in core modules).

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

__version__ = "0.4.0"
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
    # Validation
    "ValidationResult",
    "FieldValidationError",
    "FieldStats",
    "validate_data",
    "validate_value",
    # Contract operations
    "ContractDiff",
    "TypeChange",
    "ConstraintChange",
    "LintIssue",
    "load_contract",
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
    "generate_analytics_report",
    "generate_ai_readiness_report",
    "generate_audit_report",
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

# Validation
from griot_core.validation import (
    FieldStats,
    FieldValidationError,
    ValidationResult,
    validate_data,
    validate_value,
)

# Contract operations
from griot_core.contract import (
    ConstraintChange,
    ContractDiff,
    LintIssue,
    TypeChange,
    load_contract,
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
    generate_ai_readiness_report,
    generate_analytics_report,
    generate_audit_report,
)
