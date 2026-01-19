"""Validation engine - orchestrates DataFrame validation."""

from __future__ import annotations

import time
from typing import Any

from griot_core.privacy_types import PrivacyViolation
from griot_core.validation_types import (
    ValidationMode,
    ValidationResult,
    ValidationError,
    ErrorType,
    ErrorSeverity,
    RuleResult,
)
from .adapters import AdapterRegistry
from .adapters.base import DataFrameAdapter
from .rules import RuleEvaluatorRegistry
from .privacy import PrivacyEvaluatorRegistry
from .pre_validation import check_columns, check_types


class ValidationEngine:
    """Orchestrates DataFrame validation against ODCS schema.

    The validation process has three phases:
        1. Pre-validation: Check columns exist, types match
        2. Quality rules: Evaluate ODCS quality rules
        3. Aggregation: Combine results into ValidationResult

    Usage:
        engine = ValidationEngine()
        result = engine.validate(df, schema)

        # Or with options
        result = engine.validate(
            df, schema,
            mode=ValidationMode.LAZY,
            fail_fast=False
        )
    """

    def __init__(self, mode: ValidationMode = ValidationMode.LAZY):
        """Initialize validation engine.

        Args:
            mode: Validation mode (EAGER stops at first error, LAZY collects all)
        """
        self.mode = mode

    def validate(
        self,
        df: Any,
        schema: Any,
        *,
        mode: ValidationMode | None = None,
        fail_fast: bool = False,
        data_privacy_checks:list[str] | None = None,
    ) -> ValidationResult:
        """Validate DataFrame against schema.

        Args:
            df: DataFrame to validate (pandas, polars, pyspark, dask)
            schema: ODCS schema (dict or GriotSchema object)
            mode: Override default validation mode
            fail_fast: If True, stop at first error (overrides mode)
            data_privacy_checks: A list of Data privacy checks to conduct

        Returns:
            ValidationResult with validation outcome
        """
        start_time = time.perf_counter()
        validation_mode = mode or self.mode
        if fail_fast:
            validation_mode = ValidationMode.EAGER

        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        privacy_violations: list[Any] = []

        # Get adapter for DataFrame type
        try:
            adapter = AdapterRegistry.get_adapter(df)
        except ValueError as e:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        field=None,
                        error_type=ErrorType.UNSUPPORTED_BACKEND,
                        message=str(e),
                        severity=ErrorSeverity.ERROR,
                    )
                ],
                warnings=[],
                privacy_violations=[],
                schema_name=_get_schema_name(schema),
                row_count=0,
                column_count=0,
                duration_ms=_elapsed_ms(start_time),
            )

        # Extract schema information
        schema_fields = _extract_schema_fields(schema)
        quality_rules = _extract_quality_rules(schema)
        schema_level_rules = _extract_schema_level_rules(schema)

        # Phase 1: Pre-validation
        column_errors = check_columns(adapter, schema_fields)
        if column_errors:
            errors.extend(column_errors)
            if validation_mode == ValidationMode.EAGER:
                return self._build_result(
                    adapter, schema, errors, warnings,privacy_violations, start_time
                )

        type_warnings = check_types(adapter, schema_fields)
        warnings.extend(type_warnings)

        # Phase 2: Quality & Privacy rules evaluation
        for field_name, rules in quality_rules.items():
            if field_name not in adapter.get_columns():
                continue  # Skip missing columns (already reported)

            # data quality rules
            for rule in rules:
                result = self._evaluate_rule(adapter, field_name, rule)
                if result:
                    if not result.passed:
                        errors.append(self._rule_result_to_error(result))
                        if validation_mode == ValidationMode.EAGER:
                            return self._build_result(adapter, schema, errors, warnings,privacy_violations, start_time)
                    else:
                        # Optionally track passed rules as info
                        pass

            # privacy quality rules
            if data_privacy_checks is not None:
                for dp_check in data_privacy_checks:
                    evaluator = PrivacyEvaluatorRegistry.get(dp_check)
                    violations = evaluator.evaluate(adapter,field_name,schema.get_field(field_name).privacy)
                    privacy_violations.extend(violations)

        # Schema-level rules (e.g., rowCount)
        for rule in schema_level_rules:
            result = self._evaluate_rule(adapter, "__schema__", rule)
            if result:
                if not result.passed:
                    errors.append(self._rule_result_to_error(result))
                    if validation_mode == ValidationMode.EAGER:
                        return self._build_result(adapter, schema, errors, warnings, privacy_violations,start_time)

        # Phase 3: Build result
        return self._build_result(adapter, schema, errors, warnings,privacy_violations, start_time)

    def _evaluate_rule(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult | None:
        """Evaluate a single quality rule.

        Args:
            adapter: DataFrame adapter
            field: Field name or "__schema__" for schema-level
            rule: Rule configuration dict

        Returns:
            RuleResult or None if evaluator not found
        """
        metric = rule.get("metric") or rule.get("type")
        if not metric:
            return None

        if not RuleEvaluatorRegistry.has(metric):
            # Unknown metric - skip with warning
            return None

        evaluator = RuleEvaluatorRegistry.get(metric)
        return evaluator.evaluate(adapter, field, rule)

    def _rule_result_to_error(self, result: RuleResult) -> ValidationError:
        """Convert RuleResult to ValidationError."""
        error_type_map = {
            "nullValues": ErrorType.NULL_VALUES,
            "null_values": ErrorType.NULL_VALUES,
            "duplicateValues": ErrorType.DUPLICATE_VALUES,
            "duplicate_values": ErrorType.DUPLICATE_VALUES,
            "invalidValues": ErrorType.INVALID_VALUES,
            "invalid_values": ErrorType.INVALID_VALUES,
            "rowCount": ErrorType.ROW_COUNT,
            "row_count": ErrorType.ROW_COUNT,
            "freshness": ErrorType.FRESHNESS,
        }

        return ValidationError(
            field=result.field if result.field != "__schema__" else None,
            error_type=error_type_map.get(result.rule_type, ErrorType.INVALID_VALUES),
            message=result.message,
            severity=ErrorSeverity.ERROR,
            actual_value=result.metric_value,
            expected_value=result.threshold,
            operator=result.operator,
            unit=result.unit,
            details=result.details,
        )

    def _build_result(
        self,
        adapter: DataFrameAdapter,
        schema: Any,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        privacy_violations:list[PrivacyViolation],
        start_time: float,
    ) -> ValidationResult:
        """Build final ValidationResult."""
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            privacy_violations=privacy_violations,
            schema_name=_get_schema_name(schema),
            row_count=adapter.row_count(),
            column_count=len(adapter.get_columns()),
            duration_ms=_elapsed_ms(start_time),
        )


def _get_schema_name(schema: Any) -> str | None:
    """Extract schema name from schema object or dict."""
    if isinstance(schema, dict):
        return schema.get("name") or schema.get("schema_name")
    if hasattr(schema, "name"):
        return schema.name
    if hasattr(schema, "schema_name"):
        return schema.schema_name
    return None


def _extract_schema_fields(schema: Any) -> dict[str, Any]:
    """Extract field definitions from schema.

    Supports:
        - Dict with 'properties' or 'fields' key
        - GriotSchema with fields attribute
    """
    if isinstance(schema, dict):
        # ODCS format: properties at top level or under 'schema'
        if "properties" in schema:
            return schema["properties"]
        if "schema" in schema and "properties" in schema["schema"]:
            return schema["schema"]["properties"]
        if "fields" in schema:
            return schema["fields"]
        return {}

    # GriotSchema object
    if hasattr(schema, "fields"):
        return schema.fields
    if hasattr(schema, "properties"):
        return schema.properties

    return {}


def _extract_quality_rules(schema: Any) -> dict[str, list[dict[str, Any]]]:
    """Extract field-level quality rules from schema.

    Returns dict mapping field names to list of rules.
    """
    rules: dict[str, list[dict[str, Any]]] = {}

    if isinstance(schema, dict):
        # ODCS format: quality rules in properties or at schema level
        properties = _extract_schema_fields(schema)

        for field_name, field_info in properties.items():
            if isinstance(field_info, dict):
                field_rules = field_info.get("quality", [])
                if field_rules:
                    rules[field_name] = field_rules

        # Also check for quality at schema level that references fields
        schema_quality = schema.get("quality", [])
        for rule in schema_quality:
            field = rule.get("field")
            if field and field != "__schema__":
                if field not in rules:
                    rules[field] = []
                rules[field].append(rule)

    elif hasattr(schema, "fields"):
        # GriotSchema object
        for field_name, field_info in schema.fields.items():
            if hasattr(field_info, "quality"):
                rules[field_name] = field_info.quality
            elif isinstance(field_info, dict) and "quality" in field_info:
                rules[field_name] = field_info["quality"]

    return rules


def _extract_schema_level_rules(schema: Any) -> list[dict[str, Any]]:
    """Extract schema-level quality rules (e.g., rowCount).

    These are rules that apply to the entire dataset, not specific fields.
    """
    rules: list[dict[str, Any]] = []

    if isinstance(schema, dict):
        schema_quality = schema.get("quality", [])
        for rule in schema_quality:
            # Schema-level if no field or field is __schema__
            field = rule.get("field")
            if not field or field == "__schema__":
                rules.append(rule)

    elif hasattr(schema, "quality"):
        for rule in schema.quality:
            field = rule.get("field") if isinstance(rule, dict) else getattr(rule, "field", None)
            if not field or field == "__schema__":
                rules.append(rule if isinstance(rule, dict) else vars(rule))

    return rules


def _elapsed_ms(start_time: float) -> float:
    """Calculate elapsed time in milliseconds."""
    return (time.perf_counter() - start_time) * 1000


# Public API function
def validate_dataframe(
    df: Any,
    schema: Any,
    *,
    mode: ValidationMode = ValidationMode.LAZY,
    fail_fast: bool = False,
    data_privacy_checks:list[str] | None = None
) -> ValidationResult:
    """Validate DataFrame against ODCS schema.

    This is the main entry point for DataFrame validation.

    Args:
        df: DataFrame to validate (pandas, polars, pyspark, dask)
        schema: ODCS schema definition (dict or GriotSchema object)
        mode: Validation mode (EAGER or LAZY)
        fail_fast: If True, stop at first error
        data_privacy_checks: list of data privacy checks

    Returns:
        ValidationResult containing:
            - is_valid: Whether validation passed
            - errors: List of validation errors
            - warnings: List of validation warnings
            - schema_name: Name of the schema
            - row_count: Number of rows in DataFrame
            - column_count: Number of columns in DataFrame
            - duration_ms: Validation duration in milliseconds

    Example:
        import pandas as pd
        from griot_core.validation import validate_dataframe

        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        schema = {
            "name": "users",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "quality": [
                {"metric": "rowCount", "mustBeGreaterThan": 0}
            ]
        }

        result = validate_dataframe(df, schema)
        if result.is_valid:
            print("Validation passed!")
        else:
            for error in result.errors:
                print(f"Error: {error.message}")
    """
    engine = ValidationEngine(mode=mode)
    return engine.validate(df, schema, fail_fast=fail_fast,data_privacy_checks=data_privacy_checks)
