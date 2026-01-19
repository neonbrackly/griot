"""Evaluator for rowCount quality rule."""

from __future__ import annotations

from typing import Any

from .base import RuleEvaluator
from griot_core.validation_types import RuleResult
from ..adapters.base import DataFrameAdapter


class RowCountEvaluator(RuleEvaluator):
    """Evaluates ODCS rowCount quality rules.

    ODCS Definition:
        Checks the total number of rows in the dataset.

    Example Rules:
        # Exact count
        quality:
          - metric: rowCount
            mustBe: 1000

        # Minimum rows
        quality:
          - metric: rowCount
            mustBeGreaterThan: 0

        # Range
        quality:
          - metric: rowCount
            mustBeGreaterThanOrEqualTo: 100
            mustBeLessThanOrEqualTo: 10000
    """

    @property
    def metric_name(self) -> str:
        return "rowCount"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        # 1. MEASURE
        row_count = adapter.row_count()

        # 2. CALCULATE (row count is always in rows, not percent)
        metric_value = float(row_count)
        unit = "rows"

        # 3. COMPARE
        operator, threshold = self._get_operator_and_threshold(rule)
        passed = self._compare(operator, metric_value, threshold)

        # 4. REPORT
        message = self._build_message(
            passed, field, self.metric_name, metric_value, operator, threshold, unit
        )

        details: dict[str, Any] = {
            "row_count": row_count,
        }

        return RuleResult(
            passed=passed,
            field=field if field != "__schema__" else "__schema__",
            rule_type=self.metric_name,
            metric_value=metric_value,
            threshold=threshold,
            operator=operator,
            unit=unit,
            message=message,
            details=details,
        )
