"""Evaluator for nullValues quality rule."""

from __future__ import annotations

from typing import Any

from .base import RuleEvaluator
from griot_validate.validation.types import RuleResult
from ..adapters.base import DataFrameAdapter


class NullValuesEvaluator(RuleEvaluator):
    """Evaluates ODCS nullValues quality rules.

    ODCS Definition:
        Counts null/missing values in a field.

    Example Rule:
        quality:
          - metric: nullValues
            mustBe: 0
            unit: rows
    """

    @property
    def metric_name(self) -> str:
        return "nullValues"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        # 1. MEASURE
        null_count = adapter.count_nulls(field)
        total_rows = adapter.row_count()

        # 2. CALCULATE
        unit = self._get_unit(rule)
        metric_value = self._calculate_metric(null_count, total_rows, unit)

        # 3. COMPARE
        operator, threshold = self._get_operator_and_threshold(rule)
        passed = self._compare(operator, metric_value, threshold)

        # 4. REPORT
        message = self._build_message(
            passed, field, self.metric_name, metric_value, operator, threshold, unit
        )

        # Get sample null positions for debugging
        details: dict[str, Any] = {
            "null_count": null_count,
            "total_rows": total_rows,
        }

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
