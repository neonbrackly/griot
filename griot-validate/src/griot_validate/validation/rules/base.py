"""Abstract base class for quality rule evaluators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from griot_core.validation_types import RuleResult
from ..adapters.base import DataFrameAdapter


class RuleEvaluator(ABC):
    """Abstract base class for quality rule evaluators.

    Each evaluator handles one type of ODCS quality metric:
        - NullValuesEvaluator
        - DuplicateValuesEvaluator
        - InvalidValuesEvaluator
        - RowCountEvaluator
        - FreshnessEvaluator

    All evaluators follow the same pattern:
        1. MEASURE - Use adapter to count/measure
        2. CALCULATE - Convert to metric (rows or percent)
        3. COMPARE - Apply operator against threshold
        4. REPORT - Build RuleResult with context
    """

    @property
    @abstractmethod
    def metric_name(self) -> str:
        """The ODCS metric name (e.g., 'nullValues', 'duplicateValues')."""
        ...

    @abstractmethod
    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        rule: dict[str, Any],
    ) -> RuleResult:
        """Evaluate the quality rule against data.

        Args:
            adapter: DataFrame adapter for data access
            field: Column/field name to evaluate
            rule: Quality rule definition dict

        Returns:
            RuleResult with pass/fail and all context
        """
        ...

    # -------------------------------------------------------------------------
    # Shared Helpers
    # -------------------------------------------------------------------------

    def _get_operator_and_threshold(
        self, rule: dict[str, Any]
    ) -> tuple[str, Any]:
        """Extract operator and threshold from rule.

        ODCS operators:
            - mustBe: exact match
            - mustBeLessThan: strictly less
            - mustBeGreaterThan: strictly greater
            - mustBeLessThanOrEqualTo: less or equal
            - mustBeGreaterThanOrEqualTo: greater or equal
        """
        operators = [
            "mustBe",
            "mustBeLessThan",
            "mustBeGreaterThan",
            "mustBeLessThanOrEqualTo",
            "mustBeGreaterThanOrEqualTo",
        ]

        for op in operators:
            if op in rule:
                return op, rule[op]

        # Check for snake_case versions
        snake_operators = {
            "must_be": "mustBe",
            "must_be_less_than": "mustBeLessThan",
            "must_be_greater_than": "mustBeGreaterThan",
            "must_be_less_than_or_equal_to": "mustBeLessThanOrEqualTo",
            "must_be_greater_than_or_equal_to": "mustBeGreaterThanOrEqualTo",
        }

        for snake, camel in snake_operators.items():
            if snake in rule:
                return camel, rule[snake]

        # Default to mustBe if just a value is present
        if "value" in rule:
            return "mustBe", rule["value"]

        raise ValueError(f"No valid operator found in rule: {rule}")

    def _get_unit(self, rule: dict[str, Any]) -> str:
        """Get unit from rule (default: 'rows')."""
        return rule.get("unit", "rows")

    def _calculate_metric(self, count: int, total: int, unit: str) -> float:
        """Calculate metric value based on unit."""
        if unit == "percent":
            return (count / total * 100) if total > 0 else 0.0
        return float(count)

    def _compare(self, operator: str, actual: float, expected: float) -> bool:
        """Apply operator comparison."""
        comparisons = {
            "mustBe": lambda a, e: a == e,
            "mustBeLessThan": lambda a, e: a < e,
            "mustBeGreaterThan": lambda a, e: a > e,
            "mustBeLessThanOrEqualTo": lambda a, e: a <= e,
            "mustBeGreaterThanOrEqualTo": lambda a, e: a >= e,
        }
        return comparisons[operator](actual, expected)

    def _build_message(
        self,
        passed: bool,
        field: str,
        metric_name: str,
        actual: float,
        operator: str,
        expected: float,
        unit: str,
    ) -> str:
        """Build human-readable result message."""
        status = "passed" if passed else "failed"
        op_symbols = {
            "mustBe": "==",
            "mustBeLessThan": "<",
            "mustBeGreaterThan": ">",
            "mustBeLessThanOrEqualTo": "<=",
            "mustBeGreaterThanOrEqualTo": ">=",
        }
        symbol = op_symbols.get(operator, operator)

        if unit == "percent":
            return (
                f"{metric_name} check {status}: {actual:.2f}% "
                f"(expected {symbol} {expected}%)"
            )
        else:
            return (
                f"{metric_name} check {status}: {int(actual)} rows "
                f"(expected {symbol} {int(expected)})"
            )
