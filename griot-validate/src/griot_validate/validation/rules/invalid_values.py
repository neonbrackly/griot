"""Evaluator for invalidValues quality rule."""

from __future__ import annotations

from typing import Any

from .base import RuleEvaluator
from griot_validate.validation.types import RuleResult
from ..adapters.base import DataFrameAdapter


class InvalidValuesEvaluator(RuleEvaluator):
    """Evaluates ODCS invalidValues quality rules.

    Supports three types of invalid value checks:
        1. Enum: Values must be in a specified set
        2. Pattern: Values must match a regex pattern
        3. Range: Values must be within min/max bounds

    Example Rules:
        # Enum check
        quality:
          - metric: invalidValues
            mustBe: 0
            validValues: ['A', 'B', 'C']

        # Pattern check
        quality:
          - metric: invalidValues
            mustBe: 0
            pattern: '^[A-Z]{3}-\\d{4}$'

        # Range check
        quality:
          - metric: invalidValues
            mustBe: 0
            minValue: 0
            maxValue: 100
    """

    @property
    def metric_name(self) -> str:
        return "invalidValues"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        total_rows = adapter.row_count()
        unit = self._get_unit(rule)
        operator, threshold = self._get_operator_and_threshold(rule)

        # Determine check type and measure
        valid_values = rule.get("arguments").get("validValues") or rule.get("arguments").get("valid_values")
        pattern = rule.get("pattern")
        min_value = rule.get("arguments").get("minValue") or rule.get("arguments").get("min_value")
        max_value = rule.get("arguments").get("maxValue") or rule.get("arguments").get("max_value")

        details: dict[str, Any] = {"total_rows": total_rows}
        invalid_count = 0

        if valid_values is not None:
            # Enum check
            invalid_count = adapter.count_not_in_set(field, valid_values)
            details["check_type"] = "enum"
            details["valid_values"] = valid_values
            if invalid_count > 0:
                details["sample_invalid"] = adapter.sample_invalid_values(
                    field, "not_in_set", valid_values=valid_values, limit=5
                )

        elif pattern is not None:
            # Pattern check
            invalid_count = adapter.count_not_matching_pattern(field, pattern)
            details["check_type"] = "pattern"
            details["pattern"] = pattern
            if invalid_count > 0:
                details["sample_invalid"] = adapter.sample_invalid_values(
                    field, "not_matching_pattern", pattern=pattern, limit=5
                )

        elif min_value is not None or max_value is not None:
            # Range check
            invalid_count = adapter.count_outside_range(field, min_value, max_value)
            details["check_type"] = "range"
            details["min_value"] = min_value
            details["max_value"] = max_value
            if invalid_count > 0:
                details["sample_invalid"] = adapter.sample_invalid_values(
                    field,
                    "outside_range",
                    min_value=min_value,
                    max_value=max_value,
                    limit=5,
                )

        else:
            # No constraint specified - pass by default
            return RuleResult(
                passed=True,
                field=field,
                rule_type=self.metric_name,
                metric_value=0,
                threshold=threshold,
                operator=operator,
                unit=unit,
                message=f"invalidValues check passed: no constraints specified",
                details=details,
            )

        details["invalid_count"] = invalid_count

        # Calculate metric
        metric_value = self._calculate_metric(invalid_count, total_rows, unit)

        # Compare
        passed = self._compare(operator, metric_value, threshold)

        # Build message
        message = self._build_message(
            passed, field, self.metric_name, metric_value, operator, threshold, unit
        )

        return RuleResult(
            passed=passed,
            field=field,
            rule_type=self.metric_name,
            metric_value=metric_value,
            threshold=threshold,
            operator=operator,
            unit=unit,
            message=message,
            details=details,
        )
