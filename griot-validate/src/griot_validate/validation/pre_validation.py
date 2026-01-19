"""Pre-validation checks for column existence and structure."""

from __future__ import annotations

from typing import Any

from griot_core.validation_types import ValidationError, ErrorType, ErrorSeverity
from .adapters.base import DataFrameAdapter


def check_columns(
    adapter: DataFrameAdapter,
    schema_fields: dict[str, Any],
) -> list[ValidationError]:
    """Check that all required schema columns exist in DataFrame.

    Args:
        adapter: DataFrame adapter
        schema_fields: Dict mapping field names to field info

    Returns:
        List of errors for missing columns
    """
    errors = []
    df_columns = set(adapter.get_columns())

    for field_name, field_info in schema_fields.items():
        if field_name not in df_columns:
            # Build helpful message with available columns
            available = sorted(df_columns)

            errors.append(
                ValidationError(
                    field=field_name,
                    error_type=ErrorType.MISSING_COLUMN,
                    message=(
                        f"Required column '{field_name}' not found in DataFrame. "
                        f"Available columns: {available}"
                    ),
                    severity=ErrorSeverity.ERROR,
                    details={"available_columns": available},
                )
            )

    return errors


def check_types(
    adapter: DataFrameAdapter,
    schema_fields: dict[str, Any],
) -> list[ValidationError]:
    """Check column types match schema expectations.

    Args:
        adapter: DataFrame adapter
        schema_fields: Dict mapping field names to field info

    Returns:
        List of warnings for type mismatches
    """
    warnings = []
    df_columns = set(adapter.get_columns())

    for field_name, field_info in schema_fields.items():
        if field_name not in df_columns:
            continue  # Missing column already reported

        expected_type = _get_expected_type(field_info)
        actual_type = adapter.get_column_dtype(field_name)

        if expected_type and not _types_compatible(expected_type, actual_type):
            warnings.append(
                ValidationError(
                    field=field_name,
                    error_type=ErrorType.TYPE_MISMATCH,
                    message=(
                        f"Column '{field_name}' has type '{actual_type}', "
                        f"expected '{expected_type}'"
                    ),
                    severity=ErrorSeverity.WARNING,
                    actual_value=actual_type,
                    expected_value=expected_type,
                )
            )

    return warnings


def _get_expected_type(field_info: Any) -> str | None:
    """Extract expected type from field info."""
    # Try different attribute names
    if hasattr(field_info, "logical_type"):
        return field_info.logical_type
    if hasattr(field_info, "type"):
        t = field_info.type
        if isinstance(t, str):
            return t
        # Handle Python type annotations
        if hasattr(t, "__name__"):
            return _python_type_to_logical(t.__name__)
    if hasattr(field_info, "python_type"):
        return _python_type_to_logical(field_info.python_type.__name__)
    return None


def _python_type_to_logical(type_name: str) -> str:
    """Convert Python type name to logical type."""
    mapping = {
        "str": "string",
        "int": "integer",
        "float": "float",
        "bool": "boolean",
        "datetime": "datetime",
        "date": "date",
    }
    return mapping.get(type_name.lower(), "object")


def _types_compatible(expected: str, actual: str) -> bool:
    """Check if actual type is compatible with expected type."""
    # Normalize types
    expected = expected.lower()
    actual = actual.lower()

    # Direct match
    if expected == actual:
        return True

    # Compatibility mappings
    compatible = {
        "string": ["string", "object", "str"],
        "integer": ["integer", "int", "int64", "int32"],
        "float": ["float", "float64", "float32", "double", "number"],
        "boolean": ["boolean", "bool"],
        "datetime": ["datetime", "datetime64", "timestamp"],
        "date": ["date", "datetime"],
    }

    for canonical, variants in compatible.items():
        if expected in variants and actual in variants:
            return True

    return False
