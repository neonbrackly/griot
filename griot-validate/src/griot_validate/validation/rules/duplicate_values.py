"""Evaluator for duplicateValues quality rule."""

from __future__ import annotations

from typing import Any

from .base import RuleEvaluator
from griot_validate.validation.types import RuleResult
from ..adapters.base import DataFrameAdapter


class DuplicateValuesEvaluator(RuleEvaluator):
    """Evaluates ODCS duplicateValues quality rules.

    ODCS Definition:
        Counts duplicate values in a field.

    Example Rule:
        quality:
          - metric: duplicateValues
            mustBe: 0
            unit: rows
    """

    @property
    def metric_name(self) -> str:
        return "duplicateValues"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        # 1. MEASURE
        duplicate_count = adapter.count_duplicates(field)
        total_rows = adapter.row_count()

        # 2. CALCULATE
        unit = self._get_unit(rule)
        metric_value = self._calculate_metric(duplicate_count, total_rows, unit)

        # 3. COMPARE
        operator, threshold = self._get_operator_and_threshold(rule)
        passed = self._compare(operator, metric_value, threshold)

        # 4. REPORT
        message = self._build_message(
            passed, field, self.metric_name, metric_value, operator, threshold, unit
        )

        # Get details
        details: dict[str, Any] = {
            "duplicate_count": duplicate_count,
            "total_rows": total_rows,
            "unique_count": adapter.count_unique(field),
        }

        if not passed and duplicate_count > 0:
            details["sample_duplicates"] = adapter.sample_invalid_values(
                field, "duplicate", limit=5
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
