"""Evaluator for validating masking requirements."""

from __future__ import annotations

from typing import Any

from .base import PrivacyEvaluator
from ..types import PrivacyInfo, PrivacyViolation, MaskingStrategy, PIIType
from ...types import ErrorSeverity
from ...adapters.base import DataFrameAdapter


class MaskingEvaluator(PrivacyEvaluator):
    """Validates that fields requiring masking are properly masked.

    This evaluator checks:
    1. Fields with requires_masking=True have appropriate masking applied
    2. PII fields that should be masked are not exposed in plain text

    Usage:
        evaluator = MaskingEvaluator()
        violations = evaluator.evaluate(
            adapter, "ssn_field",
            privacy_info=PrivacyInfo(
                is_pii=True,
                requires_masking=True,
                masking_strategy=MaskingStrategy.PARTIAL,
            )
        )
    """

    @property
    def name(self) -> str:
        return "masking"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        privacy_info: PrivacyInfo | None,
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Evaluate masking requirements for a field.

        Args:
            adapter: DataFrame adapter
            field: Field name to check
            privacy_info: Declared privacy metadata

        Returns:
            List of violations for masking issues
        """
        violations = []

        # Skip if no privacy info or masking not required
        if not privacy_info or not privacy_info.requires_masking:
            return violations

        # Skip if masking strategy is NONE
        if privacy_info.masking_strategy == MaskingStrategy.NONE:
            return violations

        # Get sample values to check
        try:
            values = adapter.get_column_values(field, drop_nulls=True)
        except Exception:
            return violations

        if not values:
            return violations

        # Check if values appear to be masked
        unmasked_values = self._find_unmasked_values(
            values, privacy_info.masking_strategy, privacy_info.pii_type
        )

        if unmasked_values:
            # Determine severity - PII without masking is an error
            severity = ErrorSeverity.ERROR if privacy_info.is_pii else ErrorSeverity.WARNING

            violations.append(
                PrivacyViolation(
                    field=field,
                    violation_type="missing_masking",
                    message=(
                        f"Field '{field}' requires masking "
                        f"(strategy: {privacy_info.masking_strategy.value}) "
                        f"but {len(unmasked_values)} unmasked values found"
                    ),
                    severity=severity,
                    detected_pii_type=privacy_info.pii_type,
                    sample_values=self._redact_samples(unmasked_values[:3]),
                    recommendation=(
                        f"Apply {privacy_info.masking_strategy.value} masking "
                        f"to field '{field}' before data export/sharing"
                    ),
                    details={
                        "unmasked_count": len(unmasked_values),
                        "total_values": len(values),
                        "masking_strategy": privacy_info.masking_strategy.value,
                    },
                )
            )

        return violations

    def _find_unmasked_values(
        self,
        values: list[Any],
        strategy: MaskingStrategy,
        pii_type: PIIType | None,
    ) -> list[Any]:
        """Find values that don't appear to be masked.

        Args:
            values: List of values to check
            strategy: Expected masking strategy
            pii_type: Type of PII (for type-specific checks)

        Returns:
            List of values that appear unmasked
        """
        unmasked = []

        for value in values[:100]:  # Sample first 100
            if value is None:
                continue

            str_value = str(value)

            if self._appears_unmasked(str_value, strategy, pii_type):
                unmasked.append(value)

        return unmasked

    def _appears_unmasked(
        self,
        value: str,
        strategy: MaskingStrategy,
        pii_type: PIIType | None,
    ) -> bool:
        """Check if a value appears to be unmasked.

        Args:
            value: String value to check
            strategy: Expected masking strategy
            pii_type: Type of PII

        Returns:
            True if value appears unmasked
        """
        # Empty or null-like values are considered masked
        if not value or value.lower() in ("null", "none", "nan", ""):
            return False

        # Check for common masking indicators
        masked_indicators = [
            "[REDACTED]",
            "[MASKED]",
            "***",
            "XXX",
            "###",
            "XXXX",
        ]

        value_upper = value.upper()
        for indicator in masked_indicators:
            if indicator in value_upper:
                return False  # Appears masked

        # Strategy-specific checks
        if strategy == MaskingStrategy.REDACT:
            # Should be completely redacted
            if value in ("[REDACTED]", "[MASKED]", "REDACTED", "MASKED"):
                return False
            return True

        elif strategy == MaskingStrategy.HASH:
            # Hashed values are typically hex strings of fixed length
            if self._looks_like_hash(value):
                return False
            return True

        elif strategy == MaskingStrategy.PARTIAL:
            # Partial masking should have asterisks
            if "*" in value or "X" in value:
                return False
            return True

        elif strategy == MaskingStrategy.ASTERISK:
            # Should be mostly asterisks
            asterisk_count = value.count("*")
            if asterisk_count >= len(value) // 2:
                return False
            return True

        elif strategy == MaskingStrategy.NULL:
            # Should be null
            if value.lower() in ("null", "none", "nan", ""):
                return False
            return True

        elif strategy == MaskingStrategy.TOKENIZE:
            # Tokens are typically UUIDs or random strings
            if self._looks_like_token(value):
                return False
            return True

        # For other strategies, use PII-type specific checks
        return self._pii_type_specific_check(value, pii_type)

    def _looks_like_hash(self, value: str) -> bool:
        """Check if value looks like a hash."""
        import re

        # Common hash lengths: MD5=32, SHA1=40, SHA256=64
        if len(value) in (32, 40, 64, 128):
            if re.match(r"^[a-fA-F0-9]+$", value):
                return True
        return False

    def _looks_like_token(self, value: str) -> bool:
        """Check if value looks like a token/UUID."""
        import re

        # UUID format
        uuid_pattern = r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
        if re.match(uuid_pattern, value):
            return True

        # Generic token (alphanumeric, 20+ chars)
        if len(value) >= 20 and re.match(r"^[a-zA-Z0-9_-]+$", value):
            return True

        return False

    def _pii_type_specific_check(self, value: str, pii_type: PIIType | None) -> bool:
        """Check if value looks like unmasked PII of the given type."""
        import re

        if pii_type == PIIType.EMAIL:
            # Unmasked email has @ and domain
            if "@" in value and "." in value.split("@")[-1]:
                if "*" not in value:  # Not partially masked
                    return True

        elif pii_type == PIIType.PHONE:
            # Unmasked phone is mostly digits
            digits = re.sub(r"\D", "", value)
            if len(digits) >= 10 and "*" not in value:
                return True

        elif pii_type == PIIType.CREDIT_CARD:
            # Unmasked CC is 13-19 digits
            digits = re.sub(r"\D", "", value)
            if 13 <= len(digits) <= 19 and "*" not in value:
                return True

        elif pii_type == PIIType.SSN:
            # US SSN format
            if re.match(r"^\d{3}-\d{2}-\d{4}$", value):
                return True

        elif pii_type == PIIType.NATIONAL_ID:
            # Kenya ID is 7-8 digits
            if re.match(r"^\d{7,8}$", value):
                return True

        # Default: assume unmasked if no asterisks or hash-like pattern
        if "*" not in value and not self._looks_like_hash(value):
            return True

        return False

    def _redact_samples(self, values: list[Any]) -> list[str]:
        """Redact sample values for safe display in violation message."""
        redacted = []
        for value in values:
            str_value = str(value)
            if len(str_value) <= 4:
                redacted.append("****")
            else:
                # Show first 2 and last 2 chars
                redacted.append(f"{str_value[:2]}...{str_value[-2:]}")
        return redacted
