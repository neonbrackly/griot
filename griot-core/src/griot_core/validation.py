"""
Griot Core Validation Engine

Data validation engine for Griot contracts.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

from griot_core.exceptions import ValidationError
from griot_core.types import (
    DataType,
    FieldFormat,
    QualityRuleType,
    Severity,
)

if TYPE_CHECKING:
    from griot_core.models import FieldInfo, GriotModel
    from griot_core.types import CustomCheck, QualityRule

__all__ = [
    "FieldValidationError",
    "FieldStats",
    "ValidationResult",
    "QualityRuleResult",
    "QualityValidationResult",
    "validate_data",
    "validate_single_row",
    "validate_value",
    "validate_quality_rules",
    "validate_completeness",
    "validate_volume",
    "validate_freshness",
]


@dataclass
class FieldValidationError:
    """Single field validation error."""

    field: str
    row: int | None
    value: Any
    constraint: str
    message: str
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field,
            "row": self.row,
            "value": _serialize_value(self.value),
            "constraint": self.constraint,
            "message": self.message,
            "severity": self.severity.value,
        }

    def __str__(self) -> str:
        loc = f"[row {self.row}]" if self.row is not None else ""
        return f"{self.field}{loc}: {self.message}"


@dataclass
class FieldStats:
    """Per-field validation statistics."""

    field: str
    total: int = 0
    valid: int = 0
    invalid: int = 0
    null_count: int = 0

    @property
    def valid_rate(self) -> float:
        """Return the proportion of valid values."""
        if self.total == 0:
            return 1.0
        return self.valid / self.total

    @property
    def invalid_rate(self) -> float:
        """Return the proportion of invalid values."""
        if self.total == 0:
            return 0.0
        return self.invalid / self.total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field,
            "total": self.total,
            "valid": self.valid,
            "invalid": self.invalid,
            "null_count": self.null_count,
            "valid_rate": self.valid_rate,
        }


@dataclass
class ValidationResult:
    """Contains validation results and statistics."""

    passed: bool
    row_count: int
    error_count: int
    errors: list[FieldValidationError] = dataclass_field(default_factory=list)
    field_stats: dict[str, FieldStats] = dataclass_field(default_factory=dict)
    duration_ms: float = 0.0

    @property
    def error_rate(self) -> float:
        """Return the proportion of rows with errors."""
        if self.row_count == 0:
            return 0.0
        # Count unique rows with errors
        error_rows = set(e.row for e in self.errors if e.row is not None)
        return len(error_rows) / self.row_count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "passed": self.passed,
            "row_count": self.row_count,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "duration_ms": self.duration_ms,
            "errors": [e.to_dict() for e in self.errors],
            "field_stats": {k: v.to_dict() for k, v in self.field_stats.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def raise_on_failure(self) -> None:
        """Raise ValidationError if validation failed."""
        if not self.passed:
            raise ValidationError(
                f"Validation failed with {self.error_count} errors",
                errors=self.errors,
            )

    def summary(self) -> str:
        """Return a human-readable summary."""
        status = "PASSED" if self.passed else "FAILED"
        lines = [
            f"Validation {status}",
            f"  Rows validated: {self.row_count:,}",
            f"  Total errors: {self.error_count:,}",
            f"  Error rate: {self.error_rate:.2%}",
            f"  Duration: {self.duration_ms:.2f}ms",
        ]

        if not self.passed and self.errors:
            lines.append("")
            lines.append("Sample errors:")
            for error in self.errors[:5]:
                lines.append(f"  - {error}")
            if len(self.errors) > 5:
                lines.append(f"  ... and {len(self.errors) - 5} more")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()


# Format validators
_FORMAT_VALIDATORS: dict[FieldFormat, Callable[[str], bool]] = {}


def _validate_email(value: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def _validate_uri(value: str) -> bool:
    """Validate URI format."""
    pattern = r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+$"
    return bool(re.match(pattern, value))


def _validate_uuid(value: str) -> bool:
    """Validate UUID format."""
    try:
        UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def _validate_date(value: str) -> bool:
    """Validate ISO date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def _validate_datetime(value: str) -> bool:
    """Validate ISO datetime format."""
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            datetime.strptime(value.replace("+00:00", "Z").rstrip("Z") + "Z" if "+" in value else value, fmt)
            return True
        except ValueError:
            continue
    # Try with timezone offset
    try:
        # Handle +HH:MM timezone
        if "+" in value or (value.count("-") > 2):
            base = value[:19]  # YYYY-MM-DDTHH:MM:SS
            datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
            return True
    except ValueError:
        pass
    return False


def _validate_ipv4(value: str) -> bool:
    """Validate IPv4 format."""
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def _validate_ipv6(value: str) -> bool:
    """Validate IPv6 format."""
    # Basic IPv6 validation
    parts = value.split(":")
    if len(parts) < 3 or len(parts) > 8:
        return False
    try:
        for part in parts:
            if part == "":
                continue  # Allow :: shorthand
            if len(part) > 4:
                return False
            int(part, 16)
        return True
    except ValueError:
        return False


def _validate_hostname(value: str) -> bool:
    """Validate hostname format."""
    if len(value) > 253:
        return False
    pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    return bool(re.match(pattern, value))


_FORMAT_VALIDATORS = {
    FieldFormat.EMAIL: _validate_email,
    FieldFormat.URI: _validate_uri,
    FieldFormat.UUID: _validate_uuid,
    FieldFormat.DATE: _validate_date,
    FieldFormat.DATETIME: _validate_datetime,
    FieldFormat.IPV4: _validate_ipv4,
    FieldFormat.IPV6: _validate_ipv6,
    FieldFormat.HOSTNAME: _validate_hostname,
}


def validate_value(
    value: Any,
    field_info: FieldInfo,
    row: int | None = None,
) -> list[FieldValidationError]:
    """
    Validate a single value against field constraints.

    Args:
        value: The value to validate.
        field_info: Field metadata and constraints.
        row: Optional row index for error reporting.

    Returns:
        List of validation errors (empty if valid).
    """
    errors: list[FieldValidationError] = []
    field_name = field_info.name

    # Handle null values
    if value is None:
        if not field_info.nullable:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="nullable",
                    message=f"Field '{field_name}' does not allow null values",
                )
            )
        return errors

    # Type validation
    expected_type = field_info.python_type
    if expected_type is not object and not _is_type_compatible(value, expected_type):
        errors.append(
            FieldValidationError(
                field=field_name,
                row=row,
                value=value,
                constraint="type",
                message=f"Expected {expected_type.__name__}, got {type(value).__name__}",
            )
        )
        # Don't continue with other validations if type is wrong
        return errors

    # String constraints
    if isinstance(value, str):
        if field_info.min_length is not None and len(value) < field_info.min_length:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="min_length",
                    message=f"Length {len(value)} < minimum {field_info.min_length}",
                )
            )

        if field_info.max_length is not None and len(value) > field_info.max_length:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="max_length",
                    message=f"Length {len(value)} > maximum {field_info.max_length}",
                )
            )

        if field_info.pattern is not None:
            if not re.match(field_info.pattern, value):
                errors.append(
                    FieldValidationError(
                        field=field_name,
                        row=row,
                        value=value,
                        constraint="pattern",
                        message=f"Value does not match pattern '{field_info.pattern}'",
                    )
                )

        if field_info.format is not None:
            validator = _FORMAT_VALIDATORS.get(field_info.format)
            if validator and not validator(value):
                errors.append(
                    FieldValidationError(
                        field=field_name,
                        row=row,
                        value=value,
                        constraint="format",
                        message=f"Value is not a valid {field_info.format.value}",
                    )
                )

    # Numeric constraints
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if field_info.ge is not None and value < field_info.ge:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="ge",
                    message=f"Value {value} < minimum {field_info.ge}",
                )
            )

        if field_info.le is not None and value > field_info.le:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="le",
                    message=f"Value {value} > maximum {field_info.le}",
                )
            )

        if field_info.gt is not None and value <= field_info.gt:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="gt",
                    message=f"Value {value} must be > {field_info.gt}",
                )
            )

        if field_info.lt is not None and value >= field_info.lt:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="lt",
                    message=f"Value {value} must be < {field_info.lt}",
                )
            )

        if field_info.multiple_of is not None:
            if value % field_info.multiple_of != 0:
                errors.append(
                    FieldValidationError(
                        field=field_name,
                        row=row,
                        value=value,
                        constraint="multiple_of",
                        message=f"Value {value} is not a multiple of {field_info.multiple_of}",
                    )
                )

    # Enum constraint
    if field_info.enum is not None:
        if value not in field_info.enum:
            errors.append(
                FieldValidationError(
                    field=field_name,
                    row=row,
                    value=value,
                    constraint="enum",
                    message=f"Value must be one of: {field_info.enum}",
                )
            )

    return errors


def _is_type_compatible(value: Any, expected: type) -> bool:
    """Check if a value is compatible with the expected type."""
    if expected is object:
        return True

    # Handle numeric types
    if expected is float and isinstance(value, (int, float)):
        return True
    if expected is int and isinstance(value, int) and not isinstance(value, bool):
        return True

    # Handle string types
    if expected is str and isinstance(value, str):
        return True

    # Handle bool
    if expected is bool and isinstance(value, bool):
        return True

    # Handle collections
    if expected is list and isinstance(value, (list, tuple)):
        return True
    if expected is dict and isinstance(value, dict):
        return True

    return isinstance(value, expected)


def validate_single_row(
    model: type[GriotModel],
    row: dict[str, Any],
    row_index: int | None = None,
) -> list[FieldValidationError]:
    """
    Validate a single row of data against a contract.

    Args:
        model: The GriotModel class defining the contract.
        row: Dictionary representing one data row.
        row_index: Optional row index for error reporting.

    Returns:
        List of FieldValidationError for any validation failures.
    """
    errors: list[FieldValidationError] = []

    # Check for missing required fields
    for field_name, field_info in model._griot_fields.items():
        if field_name not in row:
            if not field_info.nullable and not field_info.has_default:
                errors.append(
                    FieldValidationError(
                        field=field_name,
                        row=row_index,
                        value=None,
                        constraint="required",
                        message=f"Required field '{field_name}' is missing",
                    )
                )
            continue

        value = row[field_name]
        field_errors = validate_value(value, field_info, row=row_index)
        errors.extend(field_errors)

    return errors


def validate_data(
    model: type[GriotModel],
    data: list[dict[str, Any]] | dict[str, Any],
) -> ValidationResult:
    """
    Validate data against a contract.

    Args:
        model: The GriotModel class defining the contract.
        data: Either a single row (dict) or multiple rows (list of dicts).
              Can also accept objects with to_dict() method.

    Returns:
        ValidationResult containing pass/fail status and any errors.
    """
    start_time = time.perf_counter()

    # Handle DataFrame-like objects
    if hasattr(data, "to_dict"):
        data = data.to_dict("records")

    # Normalize to list
    if isinstance(data, dict):
        rows = [data]
    else:
        rows = list(data)

    row_count = len(rows)
    all_errors: list[FieldValidationError] = []
    field_stats: dict[str, FieldStats] = {
        name: FieldStats(field=name) for name in model._griot_fields
    }

    # Track unique values for uniqueness validation
    unique_values: dict[str, set[Any]] = {
        name: set()
        for name, info in model._griot_fields.items()
        if info.unique or info.primary_key
    }

    # Validate each row
    for row_idx, row in enumerate(rows):
        row_errors = validate_single_row(model, row, row_index=row_idx)
        all_errors.extend(row_errors)

        # Update field stats
        error_fields = {e.field for e in row_errors}
        for field_name, stats in field_stats.items():
            stats.total += 1
            value = row.get(field_name)

            if value is None:
                stats.null_count += 1

            if field_name in error_fields:
                stats.invalid += 1
            else:
                stats.valid += 1

        # Check uniqueness constraints
        for field_name, seen in unique_values.items():
            value = row.get(field_name)
            if value is not None:
                if value in seen:
                    all_errors.append(
                        FieldValidationError(
                            field=field_name,
                            row=row_idx,
                            value=value,
                            constraint="unique",
                            message=f"Duplicate value for unique field '{field_name}'",
                        )
                    )
                else:
                    seen.add(value)

    duration_ms = (time.perf_counter() - start_time) * 1000

    return ValidationResult(
        passed=len(all_errors) == 0,
        row_count=row_count,
        error_count=len(all_errors),
        errors=all_errors,
        field_stats=field_stats,
        duration_ms=duration_ms,
    )


def _serialize_value(value: Any) -> Any:
    """Convert a value to a JSON-serializable format."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    return str(value)


# ============================================================================
# ODCS Quality Rule Validation (Phase 6 - T-331)
# ============================================================================


@dataclass
class QualityRuleResult:
    """
    Result of a single quality rule validation.

    Attributes:
        rule_type: Type of quality rule validated.
        passed: Whether the rule passed.
        actual_value: The actual measured value.
        threshold: The threshold that was checked against.
        message: Human-readable result message.
        severity: Severity level if rule failed.
        field: Optional field name for field-specific rules.
    """

    rule_type: QualityRuleType
    passed: bool
    actual_value: float | int | None
    threshold: float | int | None
    message: str
    severity: Severity = Severity.ERROR
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_type": self.rule_type.value,
            "passed": self.passed,
            "actual_value": self.actual_value,
            "threshold": self.threshold,
            "message": self.message,
            "severity": self.severity.value,
            "field": self.field,
        }


@dataclass
class QualityValidationResult:
    """
    Result of quality rules validation against a dataset.

    Attributes:
        passed: Whether all quality rules passed.
        rule_results: Individual results for each quality rule.
        row_count: Number of rows validated.
        duration_ms: Time taken for validation in milliseconds.
    """

    passed: bool
    rule_results: list[QualityRuleResult] = dataclass_field(default_factory=list)
    row_count: int = 0
    duration_ms: float = 0.0

    @property
    def failed_rules(self) -> list[QualityRuleResult]:
        """Return list of failed rule results."""
        return [r for r in self.rule_results if not r.passed]

    @property
    def passed_rules(self) -> list[QualityRuleResult]:
        """Return list of passed rule results."""
        return [r for r in self.rule_results if r.passed]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "passed": self.passed,
            "row_count": self.row_count,
            "duration_ms": self.duration_ms,
            "rule_results": [r.to_dict() for r in self.rule_results],
            "failed_count": len(self.failed_rules),
            "passed_count": len(self.passed_rules),
        }

    def summary(self) -> str:
        """Return a human-readable summary."""
        status = "PASSED" if self.passed else "FAILED"
        lines = [
            f"Quality Validation {status}",
            f"  Rows analyzed: {self.row_count:,}",
            f"  Rules passed: {len(self.passed_rules)}/{len(self.rule_results)}",
            f"  Duration: {self.duration_ms:.2f}ms",
        ]

        if self.failed_rules:
            lines.append("")
            lines.append("Failed rules:")
            for result in self.failed_rules:
                lines.append(f"  - [{result.rule_type.value}] {result.message}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()


def validate_completeness(
    data: list[dict[str, Any]],
    fields: list[str] | None = None,
    min_percent: float = 99.0,
) -> QualityRuleResult:
    """
    Validate data completeness (non-null percentage).

    Args:
        data: List of row dictionaries.
        fields: Optional list of fields to check. If None, checks all fields.
        min_percent: Minimum required completeness percentage (default: 99.0).

    Returns:
        QualityRuleResult with completeness validation result.
    """
    if not data:
        return QualityRuleResult(
            rule_type=QualityRuleType.COMPLETENESS,
            passed=True,
            actual_value=100.0,
            threshold=min_percent,
            message="No data to validate",
        )

    # Determine fields to check
    if fields is None:
        fields = list(data[0].keys()) if data else []

    total_cells = len(data) * len(fields)
    if total_cells == 0:
        return QualityRuleResult(
            rule_type=QualityRuleType.COMPLETENESS,
            passed=True,
            actual_value=100.0,
            threshold=min_percent,
            message="No fields to validate",
        )

    # Count non-null values
    non_null_count = sum(
        1 for row in data for field in fields if row.get(field) is not None
    )

    completeness_percent = (non_null_count / total_cells) * 100
    passed = completeness_percent >= min_percent

    return QualityRuleResult(
        rule_type=QualityRuleType.COMPLETENESS,
        passed=passed,
        actual_value=round(completeness_percent, 2),
        threshold=min_percent,
        message=(
            f"Completeness: {completeness_percent:.2f}% "
            f"({'meets' if passed else 'below'} threshold of {min_percent}%)"
        ),
        severity=Severity.ERROR if not passed else Severity.INFO,
    )


def validate_volume(
    data: list[dict[str, Any]],
    min_rows: int | None = None,
    max_rows: int | None = None,
) -> QualityRuleResult:
    """
    Validate data volume (row count).

    Args:
        data: List of row dictionaries.
        min_rows: Minimum expected row count (optional).
        max_rows: Maximum expected row count (optional).

    Returns:
        QualityRuleResult with volume validation result.
    """
    row_count = len(data)
    passed = True
    messages = []

    if min_rows is not None and row_count < min_rows:
        passed = False
        messages.append(f"Row count {row_count} below minimum {min_rows}")

    if max_rows is not None and row_count > max_rows:
        passed = False
        messages.append(f"Row count {row_count} exceeds maximum {max_rows}")

    if not messages:
        threshold_desc = []
        if min_rows is not None:
            threshold_desc.append(f"min={min_rows}")
        if max_rows is not None:
            threshold_desc.append(f"max={max_rows}")
        threshold_str = ", ".join(threshold_desc) if threshold_desc else "none"
        messages.append(f"Row count {row_count} within expected range ({threshold_str})")

    return QualityRuleResult(
        rule_type=QualityRuleType.VOLUME,
        passed=passed,
        actual_value=row_count,
        threshold=min_rows,  # Use min_rows as primary threshold
        message="; ".join(messages),
        severity=Severity.ERROR if not passed else Severity.INFO,
    )


def validate_freshness(
    data: list[dict[str, Any]],
    timestamp_field: str,
    max_age_seconds: int,
    reference_time: datetime | None = None,
) -> QualityRuleResult:
    """
    Validate data freshness based on a timestamp field.

    Args:
        data: List of row dictionaries.
        timestamp_field: Name of the field containing timestamps.
        max_age_seconds: Maximum allowed age in seconds.
        reference_time: Reference time to compare against (default: now).

    Returns:
        QualityRuleResult with freshness validation result.
    """
    if not data:
        return QualityRuleResult(
            rule_type=QualityRuleType.FRESHNESS,
            passed=True,
            actual_value=0,
            threshold=max_age_seconds,
            message="No data to validate freshness",
            field=timestamp_field,
        )

    if reference_time is None:
        reference_time = datetime.utcnow()

    # Find the most recent timestamp
    latest_timestamp: datetime | None = None
    for row in data:
        ts_value = row.get(timestamp_field)
        if ts_value is None:
            continue

        # Parse timestamp
        if isinstance(ts_value, datetime):
            ts = ts_value
        elif isinstance(ts_value, str):
            try:
                # Try common formats
                for fmt in [
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S",
                ]:
                    try:
                        ts = datetime.strptime(ts_value.replace("+00:00", "").rstrip("Z"), fmt.rstrip("Z"))
                        break
                    except ValueError:
                        continue
                else:
                    continue
            except (ValueError, TypeError):
                continue
        else:
            continue

        if latest_timestamp is None or ts > latest_timestamp:
            latest_timestamp = ts

    if latest_timestamp is None:
        return QualityRuleResult(
            rule_type=QualityRuleType.FRESHNESS,
            passed=False,
            actual_value=None,
            threshold=max_age_seconds,
            message=f"No valid timestamps found in field '{timestamp_field}'",
            severity=Severity.WARNING,
            field=timestamp_field,
        )

    # Calculate age in seconds
    age_seconds = (reference_time - latest_timestamp).total_seconds()
    passed = age_seconds <= max_age_seconds

    # Format age for human readability
    if age_seconds < 60:
        age_str = f"{age_seconds:.0f} seconds"
    elif age_seconds < 3600:
        age_str = f"{age_seconds / 60:.1f} minutes"
    elif age_seconds < 86400:
        age_str = f"{age_seconds / 3600:.1f} hours"
    else:
        age_str = f"{age_seconds / 86400:.1f} days"

    return QualityRuleResult(
        rule_type=QualityRuleType.FRESHNESS,
        passed=passed,
        actual_value=int(age_seconds),
        threshold=max_age_seconds,
        message=(
            f"Data age: {age_str} "
            f"({'within' if passed else 'exceeds'} max age of {max_age_seconds}s)"
        ),
        severity=Severity.ERROR if not passed else Severity.INFO,
        field=timestamp_field,
    )


def validate_quality_rules(
    model: type[GriotModel],
    data: list[dict[str, Any]],
) -> QualityValidationResult:
    """
    Validate data against ODCS quality rules defined on the model.

    Args:
        model: The GriotModel class with quality rules defined.
        data: List of row dictionaries to validate.

    Returns:
        QualityValidationResult with all rule results.
    """
    start_time = time.perf_counter()

    # Handle DataFrame-like objects
    if hasattr(data, "to_dict"):
        data = data.to_dict("records")

    if isinstance(data, dict):
        data = [data]

    rule_results: list[QualityRuleResult] = []
    row_count = len(data)

    # Get quality rules from model
    quality_rules = model.get_quality_rules() if hasattr(model, "get_quality_rules") else []

    for rule in quality_rules:
        rule_type = rule.rule_type if hasattr(rule, "rule_type") else None

        if rule_type == QualityRuleType.COMPLETENESS:
            threshold = rule.threshold if hasattr(rule, "threshold") else 99.0
            fields = rule.fields if hasattr(rule, "fields") else None
            result = validate_completeness(data, fields=fields, min_percent=threshold)
            rule_results.append(result)

        elif rule_type == QualityRuleType.VOLUME:
            min_rows = rule.min_value if hasattr(rule, "min_value") else None
            max_rows = rule.max_value if hasattr(rule, "max_value") else None
            result = validate_volume(data, min_rows=min_rows, max_rows=max_rows)
            rule_results.append(result)

        elif rule_type == QualityRuleType.FRESHNESS:
            field = rule.field if hasattr(rule, "field") else None
            max_age = rule.max_value if hasattr(rule, "max_value") else 86400  # Default 24h
            if field:
                result = validate_freshness(data, field, int(max_age))
                rule_results.append(result)

        elif rule_type == QualityRuleType.ACCURACY:
            # Accuracy requires external validation - mark as skipped
            rule_results.append(
                QualityRuleResult(
                    rule_type=QualityRuleType.ACCURACY,
                    passed=True,
                    actual_value=None,
                    threshold=None,
                    message="Accuracy validation requires external reference data",
                    severity=Severity.INFO,
                )
            )

        elif rule_type == QualityRuleType.DISTRIBUTION:
            # Distribution validation requires statistical analysis - mark as skipped
            rule_results.append(
                QualityRuleResult(
                    rule_type=QualityRuleType.DISTRIBUTION,
                    passed=True,
                    actual_value=None,
                    threshold=None,
                    message="Distribution validation requires baseline statistics",
                    severity=Severity.INFO,
                )
            )

    duration_ms = (time.perf_counter() - start_time) * 1000
    passed = all(r.passed for r in rule_results)

    return QualityValidationResult(
        passed=passed,
        rule_results=rule_results,
        row_count=row_count,
        duration_ms=duration_ms,
    )
