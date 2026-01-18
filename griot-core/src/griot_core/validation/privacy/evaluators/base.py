"""Base class for privacy rule evaluators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..types import PrivacyInfo, PrivacyViolation
from ...adapters.base import DataFrameAdapter


class PrivacyEvaluator(ABC):
    """Abstract base class for privacy rule evaluators.

    Privacy evaluators check data against privacy metadata declared
    in the schema. They detect violations like:
    - Undeclared PII
    - Missing masking
    - Sensitivity mismatches
    - Compliance violations
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this evaluator."""
        ...

    @abstractmethod
    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        privacy_info: PrivacyInfo | None,
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Evaluate privacy rules for a field.

        Args:
            adapter: DataFrame adapter
            field: Field name to evaluate
            privacy_info: Declared privacy metadata (None if not declared)
            **kwargs: Additional configuration

        Returns:
            List of privacy violations found
        """
        ...

    def evaluate_all_fields(
        self,
        adapter: DataFrameAdapter,
        privacy_metadata: dict[str, PrivacyInfo | None],
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Evaluate privacy rules for all fields.

        Args:
            adapter: DataFrame adapter
            privacy_metadata: Dict mapping field names to privacy info
            **kwargs: Additional configuration

        Returns:
            List of all privacy violations found
        """
        violations = []
        for field in adapter.get_columns():
            privacy_info = privacy_metadata.get(field)
            field_violations = self.evaluate(adapter, field, privacy_info, **kwargs)
            violations.extend(field_violations)
        return violations
