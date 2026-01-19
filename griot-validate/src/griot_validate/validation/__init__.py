"""Griot validation module - DataFrame validation against ODCS schemas.

This module provides a unified, framework-agnostic validation system
that works consistently across pandas, polars, pyspark, and dask.

Quick Start:
    from griot_core.validation import validate_dataframe

    result = validate_dataframe(df, schema)
    if result.is_valid:
        print("All checks passed!")
    else:
        for error in result.errors:
            print(f"{error.field}: {error.message}")

Components:
    - ValidationEngine: Core orchestrator for validation
    - validate_dataframe: Main entry point function
    - DataFrameAdapter: Framework-specific adapters
    - RuleEvaluator: Quality rule evaluators
"""

from __future__ import annotations

# Core types
from griot_core.validation_types import (
    ValidationMode,
    ErrorType,
    ErrorSeverity,
    ValidationError,
    RuleResult,
    ValidationResult,
)

# Engine and public API
from .engine import ValidationEngine, validate_dataframe

# Adapters (for advanced usage)
from .adapters import AdapterRegistry, get_adapter

# Rule evaluators (for advanced usage)
from .rules import (
    RuleEvaluatorRegistry,
    get_evaluator,
    RuleEvaluator,
    NullValuesEvaluator,
    DuplicateValuesEvaluator,
    InvalidValuesEvaluator,
    RowCountEvaluator,
    FreshnessEvaluator,
)

# Privacy framework (for data protection compliance)
from .privacy import (
    Sensitivity,
    PIIType,
    MaskingStrategy,
    ComplianceFramework,
    PrivacyInfo,
    PrivacyViolation,
    detect_pii,
    detect_pii_in_column,
    evaluate_privacy,
    PrivacyEvaluatorRegistry,
    # Convenience constants
    PII_EMAIL,
    PII_PHONE,
    PII_NATIONAL_ID,
    PII_CREDIT_CARD,
)


__all__ = [
    # Main API
    "validate_dataframe",
    "ValidationEngine",
    # Types
    "ValidationMode",
    "ErrorType",
    "ErrorSeverity",
    "ValidationError",
    "RuleResult",
    "ValidationResult",
    # Adapters
    "AdapterRegistry",
    "get_adapter",
    # Evaluators
    "RuleEvaluatorRegistry",
    "get_evaluator",
    "RuleEvaluator",
    "NullValuesEvaluator",
    "DuplicateValuesEvaluator",
    "InvalidValuesEvaluator",
    "RowCountEvaluator",
    "FreshnessEvaluator",
    # Privacy
    "Sensitivity",
    "PIIType",
    "MaskingStrategy",
    "ComplianceFramework",
    "PrivacyInfo",
    "PrivacyViolation",
    "detect_pii",
    "detect_pii_in_column",
    "evaluate_privacy",
    "PrivacyEvaluatorRegistry",
    "PII_EMAIL",
    "PII_PHONE",
    "PII_NATIONAL_ID",
    "PII_CREDIT_CARD",
]


# Version
__version__ = "0.1.0"
