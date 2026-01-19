"""Shared types for the validation module.

This module contains all enums, dataclasses, and type definitions used
across the validation framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from griot_core.privacy_types import PrivacyViolation


class ValidationMode(Enum):
    """Validation behavior mode."""

    EAGER = "eager"  # Stop at first error
    LAZY = "lazy"  # Collect all errors


class ErrorSeverity(Enum):
    """Severity level for validation issues."""

    ERROR = "error"  # Validation failure
    WARNING = "warning"  # Non-blocking issue
    INFO = "info"  # Informational


class ErrorType(Enum):
    """Classification of validation errors."""

    # Pre-validation errors
    MISSING_COLUMN = "missing_column"
    EXTRA_COLUMN = "extra_column"
    TYPE_MISMATCH = "type_mismatch"

    # Quality rule errors
    NULL_VALUES = "null_values"
    DUPLICATE_VALUES = "duplicate_values"
    INVALID_VALUES = "invalid_values"
    ROW_COUNT = "row_count"
    FRESHNESS = "freshness"
    DISTRIBUTION = "distribution"
    CUSTOM_CHECK = "custom_check"
    UNSUPPORTED_BACKEND = "unsupported_backend"


@dataclass
class ValidationError:
    """A single validation error with full context.

    Attributes:
        field: Column/field name (None for schema-level errors)
        error_type: Classification of the error
        message: Human-readable description
        severity: Error severity level
        actual_value: The measured/found value
        expected_value: The threshold/expected value
        operator: The comparison operator used (mustBe, mustBeLessThan, etc.)
        unit: The unit of measurement (rows, percent)
        details: Additional context (e.g., sample invalid values)
    """

    field: str | None
    error_type: ErrorType
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    actual_value: Any = None
    expected_value: Any = None
    operator: str | None = None
    unit: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "field": self.field,
            "error_type": self.error_type.value,
            "message": self.message,
            "severity": self.severity.value,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "operator": self.operator,
            "unit": self.unit,
            "details": self.details,
        }


@dataclass
class RuleResult:
    """Result of evaluating a single quality rule.

    This is the output from a RuleEvaluator, capturing all context
    needed for reporting.
    """

    passed: bool
    field: str
    rule_type: str  # "nullValues", "duplicateValues", etc.
    metric_value: Any  # The measured value
    threshold: Any  # The comparison threshold
    operator: str  # "mustBe", "mustBeLessThan", etc.
    unit: str  # "rows" or "percent"
    message: str  # Human-readable result
    details: dict[str, Any] = field(default_factory=dict)

    def to_error(self) -> ValidationError:
        """Convert failed result to ValidationError."""
        # Map rule_type to ErrorType
        error_type_map = {
            "nullValues": ErrorType.NULL_VALUES,
            "duplicateValues": ErrorType.DUPLICATE_VALUES,
            "invalidValues": ErrorType.INVALID_VALUES,
            "rowCount": ErrorType.ROW_COUNT,
            "freshness": ErrorType.FRESHNESS,
            "distribution": ErrorType.DISTRIBUTION,
        }
        error_type = error_type_map.get(self.rule_type, ErrorType.CUSTOM_CHECK)

        return ValidationError(
            field=self.field if self.field != "__schema__" else None,
            error_type=error_type,
            message=self.message,
            severity=ErrorSeverity.ERROR,
            actual_value=self.metric_value,
            expected_value=self.threshold,
            operator=self.operator,
            unit=self.unit,
            details=self.details,
        )


@dataclass
class ValidationResult:
    """Complete result of validating a DataFrame against a schema.

    Attributes:
        is_valid: True if all checks passed
        errors: List of validation errors
        warnings: List of non-blocking warnings
        schema_name: Name of the validated schema
        row_count: Number of rows validated
        column_count: Number of columns in DataFrame
        duration_ms: Validation duration in milliseconds
    """

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    privacy_violations: list[PrivacyViolation] = field(default_factory=list)
    schema_name: str | None = None
    row_count: int = 0
    column_count: int = 0
    duration_ms: float = 0.0

    def summary(self) -> str:
        """Generate human-readable summary."""
        if self.is_valid:
            return f"Validation passed ({self.row_count} rows, {self.column_count} columns)"

        lines = [
            f"Validation failed: {len(self.errors)} error(s)",
            f"  Schema: {self.schema_name or 'Unknown'}",
            f"  Rows: {self.row_count}, Columns: {self.column_count}",
            "",
            "Errors:",
        ]
        for err in self.errors:
            field_name = err.field or "schema"
            lines.append(f"  [{err.error_type.value}] {field_name}: {err.message}")
            if err.actual_value is not None and err.expected_value is not None:
                lines.append(
                    f"    Actual: {err.actual_value} | "
                    f"Expected: {err.operator} {err.expected_value} ({err.unit})"
                )

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warn in self.warnings:
                field_name = warn.field or "schema"
                lines.append(f"  [{warn.error_type.value}] {field_name}: {warn.message}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "schema_name": self.schema_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duration_ms": self.duration_ms,
        }
