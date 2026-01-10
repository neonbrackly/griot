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

__version__ = "0.3.0"
__all__ = [
    # Core classes
    "GriotModel",
    "Field",
    "FieldInfo",
    # Type definitions
    "ConstraintType",
    "Severity",
    "FieldFormat",
    "AggregationType",
    "DataType",
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
]

# Core classes
from griot_core.models import Field, FieldInfo, GriotModel

# Type definitions
from griot_core.types import (
    AggregationType,
    ConstraintType,
    DataType,
    FieldFormat,
    Severity,
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
