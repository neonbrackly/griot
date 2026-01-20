"""Evaluator for freshness quality rule."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .base import RuleEvaluator
from griot_validate.validation.types import RuleResult
from ..adapters.base import DataFrameAdapter


class FreshnessEvaluator(RuleEvaluator):
    """Evaluates ODCS freshness quality rules.

    ODCS Definition:
        Checks if data is fresh (recently updated) based on a timestamp field.

    Example Rules:
        # Data must be updated within last 24 hours
        quality:
          - metric: freshness
            field: updated_at
            mustBeLessThan: 24
            unit: hours

        # Data must be updated within last 7 days
        quality:
          - metric: freshness
            field: last_modified
            mustBeLessThan: 7
            unit: days
    """

    @property
    def metric_name(self) -> str:
        return "freshness"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        # Get the timestamp field (might be different from the field parameter)
        timestamp_field = rule.get("field", field)

        # 1. MEASURE
        max_timestamp = adapter.get_max_timestamp(timestamp_field)
        now = datetime.now()

        # Calculate age
        if max_timestamp is None:
            age_hours = float("inf")
        else:
            # Handle various timestamp formats
            if hasattr(max_timestamp, "to_pydatetime"):
                # pandas Timestamp
                max_timestamp = max_timestamp.to_pydatetime()
            elif isinstance(max_timestamp, str):
                # Try to parse string timestamp
                try:
                    max_timestamp = datetime.fromisoformat(max_timestamp)
                except ValueError:
                    age_hours = float("inf")
                    max_timestamp = None

            if max_timestamp is not None:
                delta = now - max_timestamp
                age_hours = delta.total_seconds() / 3600

        # 2. CALCULATE
        unit = rule.get("unit", "hours")
        if unit == "days":
            metric_value = age_hours / 24
        elif unit == "minutes":
            metric_value = age_hours * 60
        elif unit == "seconds":
            metric_value = age_hours * 3600
        else:  # hours
            metric_value = age_hours

        # 3. COMPARE
        operator, threshold = self._get_operator_and_threshold(rule)
        passed = self._compare(operator, metric_value, threshold)

        # 4. REPORT
        status = "passed" if passed else "failed"
        op_symbols = {
            "mustBe": "==",
            "mustBeLessThan": "<",
            "mustBeGreaterThan": ">",
            "mustBeLessThanOrEqualTo": "<=",
            "mustBeGreaterThanOrEqualTo": ">=",
        }
        symbol = op_symbols.get(operator, operator)

        if metric_value == float("inf"):
            message = f"freshness check {status}: no valid timestamps found"
        else:
            message = (
                f"freshness check {status}: {metric_value:.2f} {unit} old "
                f"(expected {symbol} {threshold} {unit})"
            )

        details: dict[str, Any] = {
            "timestamp_field": timestamp_field,
            "max_timestamp": str(max_timestamp) if max_timestamp else None,
            "current_time": str(now),
            "age_hours": age_hours if age_hours != float("inf") else None,
        }

        return RuleResult(
            passed=passed,
            field=timestamp_field,
            rule_type=self.metric_name,
            metric_value=metric_value,
            threshold=threshold,
            operator=operator,
            unit=unit,
            message=message,
            details=details,
        )
