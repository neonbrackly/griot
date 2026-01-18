"""Evaluator for detecting undeclared PII in data."""

from __future__ import annotations

from typing import Any

from .base import PrivacyEvaluator
from ..types import PrivacyInfo, PrivacyViolation, PIIType, Sensitivity
from ..patterns import DEFAULT_REGISTRY, PIIPatternRegistry
from ...types import ErrorSeverity
from ...adapters.base import DataFrameAdapter


class UndeclaredPIIEvaluator(PrivacyEvaluator):
    """Detects PII that wasn't declared in schema privacy metadata.

    This evaluator scans column values for PII patterns and reports
    any fields that contain PII but don't have is_pii=True in their
    privacy metadata.

    Usage:
        evaluator = UndeclaredPIIEvaluator()
        violations = evaluator.evaluate(
            adapter, "email_field",
            privacy_info=None,  # or PrivacyInfo(is_pii=False)
        )

    Configuration:
        - sample_size: Number of values to sample (default: 100)
        - detection_threshold: Min detection rate to report (default: 0.1)
        - pattern_registry: Custom PIIPatternRegistry (default: built-in)
    """

    @property
    def name(self) -> str:
        return "undeclared_pii"

    def __init__(
        self,
        pattern_registry: PIIPatternRegistry | None = None,
        sample_size: int = 100,
        detection_threshold: float = 0.1,
    ):
        """Initialize evaluator.

        Args:
            pattern_registry: Custom pattern registry (uses default if None)
            sample_size: Number of values to sample per column
            detection_threshold: Minimum detection rate to flag (0-1)
        """
        self.pattern_registry = pattern_registry or DEFAULT_REGISTRY
        self.sample_size = sample_size
        self.detection_threshold = detection_threshold

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        privacy_info: PrivacyInfo | None,
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Evaluate a field for undeclared PII.

        Args:
            adapter: DataFrame adapter
            field: Field name to check
            privacy_info: Declared privacy metadata

        Returns:
            List of violations for undeclared PII
        """
        violations = []

        # If already declared as PII, skip detection
        if privacy_info and privacy_info.is_pii:
            return violations

        # Get sample size from kwargs or use default
        sample_size = kwargs.get("sample_size", self.sample_size)
        threshold = kwargs.get("detection_threshold", self.detection_threshold)

        # Get column values
        try:
            values = adapter.get_column_values(field, drop_nulls=True)
        except Exception:
            return violations  # Can't read column, skip

        if not values:
            return violations

        # Convert to strings for pattern matching
        str_values = [str(v) for v in values if v is not None]
        if not str_values:
            return violations

        # Detect PII types in column
        detected_pii = self.pattern_registry.detect_in_column(str_values, sample_size)

        # Report violations for detected PII above threshold
        for pii_type, detection_rate in detected_pii.items():
            if detection_rate >= threshold:
                # Get sample values that matched
                sample_matches = []
                patterns = self.pattern_registry.get_patterns_by_type(pii_type)
                for value in str_values[:10]:  # Check first 10
                    for pattern in patterns:
                        if pattern.match(value):
                            sample_matches.append(value)
                            break
                    if len(sample_matches) >= 3:
                        break

                # Determine severity based on PII type
                severity = self._get_severity_for_pii_type(pii_type)

                # Build recommendation
                recommendation = (
                    f"Add privacy metadata to field '{field}': "
                    f"PrivacyInfo(is_pii=True, pii_type=PIIType.{pii_type.name})"
                )

                violations.append(
                    PrivacyViolation(
                        field=field,
                        violation_type="undeclared_pii",
                        message=(
                            f"Field '{field}' appears to contain {pii_type.value} "
                            f"({detection_rate:.0%} detection rate) but is not declared as PII"
                        ),
                        severity=severity,
                        detected_pii_type=pii_type,
                        sample_values=sample_matches[:3],  # Limit samples
                        recommendation=recommendation,
                        details={
                            "detection_rate": detection_rate,
                            "sample_size": min(sample_size, len(str_values)),
                            "total_values": len(str_values),
                        },
                    )
                )

        return violations

    def _get_severity_for_pii_type(self, pii_type: PIIType) -> ErrorSeverity:
        """Determine severity based on PII type."""
        # High sensitivity PII
        high_severity = {
            PIIType.NATIONAL_ID,
            PIIType.PASSPORT,
            PIIType.TAX_ID,
            PIIType.SSN,
            PIIType.CREDIT_CARD,
            PIIType.BANK_ACCOUNT,
            PIIType.IBAN,
            PIIType.HEALTH_DATA,
            PIIType.MEDICAL_RECORD,
            PIIType.BIOMETRIC,
        }

        if pii_type in high_severity:
            return ErrorSeverity.ERROR

        # Medium sensitivity
        medium_severity = {
            PIIType.EMAIL,
            PIIType.PHONE,
            PIIType.ADDRESS,
            PIIType.DATE_OF_BIRTH,
        }

        if pii_type in medium_severity:
            return ErrorSeverity.WARNING

        return ErrorSeverity.INFO
