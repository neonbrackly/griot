"""Privacy evaluators for data protection validation.

Evaluators check data against declared privacy metadata and detect:
- Undeclared PII in data
- Missing masking for PII fields
- Insufficient sensitivity levels
- Compliance violations
"""

from __future__ import annotations

from typing import Any

from .base import PrivacyEvaluator
from .undeclared_pii import UndeclaredPIIEvaluator
from .masking import MaskingEvaluator
from .sensitivity import SensitivityEvaluator
from griot_core.types import PrivacyInfo, PrivacyViolation
from ...adapters.base import DataFrameAdapter


class PrivacyEvaluatorRegistry:
    """Registry of privacy evaluators.

    Usage:
        registry = PrivacyEvaluatorRegistry()

        # Get single evaluator
        evaluator = registry.get("undeclared_pii")

        # Run all evaluators
        violations = registry.evaluate_all(adapter, field, privacy_info)
    """

    _evaluators: dict[str, type[PrivacyEvaluator]] = {}
    _instances: dict[str, PrivacyEvaluator] = {}

    @classmethod
    def register(cls, name: str, evaluator_class: type[PrivacyEvaluator]) -> None:
        """Register an evaluator."""
        cls._evaluators[name] = evaluator_class
        if name in cls._instances:
            del cls._instances[name]

    @classmethod
    def get(cls, name: str) -> PrivacyEvaluator:
        """Get evaluator instance by name."""
        if name not in cls._instances:
            if name not in cls._evaluators:
                raise ValueError(f"No privacy evaluator registered: {name}")
            cls._instances[name] = cls._evaluators[name]()
        return cls._instances[name]

    @classmethod
    def has(cls, name: str) -> bool:
        """Check if evaluator is registered."""
        return name in cls._evaluators

    @classmethod
    def list_evaluators(cls) -> list[str]:
        """List registered evaluator names."""
        return list(cls._evaluators.keys())

    @classmethod
    def evaluate_all(
        cls,
        adapter: DataFrameAdapter,
        field: str,
        privacy_info: PrivacyInfo | None,
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Run all registered evaluators on a field.

        Args:
            adapter: DataFrame adapter
            field: Field name to evaluate
            privacy_info: Declared privacy metadata
            **kwargs: Additional configuration

        Returns:
            Combined list of violations from all evaluators
        """
        violations = []
        for name in cls._evaluators:
            evaluator = cls.get(name)
            field_violations = evaluator.evaluate(adapter, field, privacy_info, **kwargs)
            violations.extend(field_violations)
        return violations


# Register built-in evaluators
PrivacyEvaluatorRegistry.register("undeclared_pii", UndeclaredPIIEvaluator)
PrivacyEvaluatorRegistry.register("masking", MaskingEvaluator)
PrivacyEvaluatorRegistry.register("sensitivity", SensitivityEvaluator)


def evaluate_privacy(
    adapter: DataFrameAdapter,
    privacy_metadata: dict[str, PrivacyInfo | None],
    **kwargs: Any,
) -> list[PrivacyViolation]:
    """Evaluate privacy for all fields using all evaluators.

    Args:
        adapter: DataFrame adapter
        privacy_metadata: Dict mapping field names to privacy info
        **kwargs: Additional configuration (sample_size, detection_threshold)

    Returns:
        List of all privacy violations found
    """
    violations = []

    for field in adapter.get_columns():
        privacy_info = privacy_metadata.get(field)
        field_violations = PrivacyEvaluatorRegistry.evaluate_all(
            adapter, field, privacy_info, **kwargs
        )
        violations.extend(field_violations)

    return violations


__all__ = [
    "PrivacyEvaluator",
    "PrivacyEvaluatorRegistry",
    "UndeclaredPIIEvaluator",
    "MaskingEvaluator",
    "SensitivityEvaluator",
    "evaluate_privacy",
]
