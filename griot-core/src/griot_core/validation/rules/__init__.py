"""Quality rule evaluator registry."""

from __future__ import annotations

from typing import Any

from .base import RuleEvaluator
from .null_values import NullValuesEvaluator
from .duplicate_values import DuplicateValuesEvaluator
from .invalid_values import InvalidValuesEvaluator
from .row_count import RowCountEvaluator
from .freshness import FreshnessEvaluator


class RuleEvaluatorRegistry:
    """Registry for quality rule evaluators.

    Maps ODCS metric names to evaluator classes.
    Extensible - register custom evaluators at runtime.

    Usage:
        evaluator = RuleEvaluatorRegistry.get("nullValues")
        result = evaluator.evaluate(adapter, field, rule)
    """

    _evaluators: dict[str, type[RuleEvaluator]] = {}
    _instances: dict[str, RuleEvaluator] = {}  # Singleton instances

    @classmethod
    def register(cls, metric_name: str, evaluator_class: type[RuleEvaluator]) -> None:
        """Register an evaluator for a metric type.

        Args:
            metric_name: The ODCS metric name (e.g., "nullValues")
            evaluator_class: The evaluator class to use
        """
        cls._evaluators[metric_name] = evaluator_class
        # Clear cached instance if exists
        if metric_name in cls._instances:
            del cls._instances[metric_name]

    @classmethod
    def get(cls, metric_name: str) -> RuleEvaluator:
        """Get evaluator instance for metric type.

        Args:
            metric_name: The ODCS metric name

        Returns:
            RuleEvaluator instance

        Raises:
            ValueError: If no evaluator is registered for the metric
        """
        if metric_name not in cls._instances:
            if metric_name not in cls._evaluators:
                raise ValueError(f"No evaluator registered for metric: {metric_name}")
            cls._instances[metric_name] = cls._evaluators[metric_name]()
        return cls._instances[metric_name]

    @classmethod
    def has(cls, metric_name: str) -> bool:
        """Check if evaluator exists for metric.

        Args:
            metric_name: The ODCS metric name

        Returns:
            True if an evaluator is registered
        """
        return metric_name in cls._evaluators

    @classmethod
    def list_metrics(cls) -> list[str]:
        """List all registered metric types.

        Returns:
            List of registered metric names
        """
        return list(cls._evaluators.keys())


# Register built-in evaluators (camelCase - ODCS standard)
RuleEvaluatorRegistry.register("nullValues", NullValuesEvaluator)
RuleEvaluatorRegistry.register("duplicateValues", DuplicateValuesEvaluator)
RuleEvaluatorRegistry.register("invalidValues", InvalidValuesEvaluator)
RuleEvaluatorRegistry.register("rowCount", RowCountEvaluator)
RuleEvaluatorRegistry.register("freshness", FreshnessEvaluator)

# Also register snake_case aliases for convenience
RuleEvaluatorRegistry.register("null_values", NullValuesEvaluator)
RuleEvaluatorRegistry.register("duplicate_values", DuplicateValuesEvaluator)
RuleEvaluatorRegistry.register("invalid_values", InvalidValuesEvaluator)
RuleEvaluatorRegistry.register("row_count", RowCountEvaluator)


# Convenience function
def get_evaluator(metric_name: str) -> RuleEvaluator:
    """Get evaluator for a metric type.

    Args:
        metric_name: The ODCS metric name

    Returns:
        RuleEvaluator instance
    """
    return RuleEvaluatorRegistry.get(metric_name)


__all__ = [
    "RuleEvaluator",
    "RuleEvaluatorRegistry",
    "get_evaluator",
    "NullValuesEvaluator",
    "DuplicateValuesEvaluator",
    "InvalidValuesEvaluator",
    "RowCountEvaluator",
    "FreshnessEvaluator",
]
