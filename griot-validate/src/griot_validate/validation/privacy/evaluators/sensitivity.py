"""Evaluator for validating data sensitivity levels."""

from __future__ import annotations

from typing import Any

from .base import PrivacyEvaluator
from griot_core.types import ErrorSeverity, Sensitivity, PIIType, PrivacyInfo, PrivacyViolation
from ...adapters.base import DataFrameAdapter


class SensitivityEvaluator(PrivacyEvaluator):
    """Validates that sensitivity levels are appropriate for data content.

    This evaluator checks:
    1. PII fields have at least INTERNAL sensitivity
    2. High-risk PII types have appropriate sensitivity levels
    3. Public sensitivity is only used for non-PII data

    Usage:
        evaluator = SensitivityEvaluator()
        violations = evaluator.evaluate(
            adapter, "credit_card",
            privacy_info=PrivacyInfo(
                is_pii=True,
                pii_type=PIIType.CREDIT_CARD,
                sensitivity=Sensitivity.INTERNAL,  # Too low!
            )
        )
    """

    # Minimum required sensitivity for PII types
    MIN_SENSITIVITY_BY_TYPE: dict[PIIType, Sensitivity] = {
        # Restricted (highest)
        PIIType.NATIONAL_ID: Sensitivity.RESTRICTED,
        PIIType.PASSPORT: Sensitivity.RESTRICTED,
        PIIType.SSN: Sensitivity.RESTRICTED,
        PIIType.CREDIT_CARD: Sensitivity.RESTRICTED,
        PIIType.BANK_ACCOUNT: Sensitivity.RESTRICTED,
        PIIType.IBAN: Sensitivity.RESTRICTED,
        PIIType.HEALTH_DATA: Sensitivity.RESTRICTED,
        PIIType.MEDICAL_RECORD: Sensitivity.RESTRICTED,
        PIIType.BIOMETRIC: Sensitivity.RESTRICTED,
        PIIType.FINGERPRINT: Sensitivity.RESTRICTED,
        PIIType.FACIAL_DATA: Sensitivity.RESTRICTED,
        PIIType.TAX_ID: Sensitivity.RESTRICTED,
        # Sensitive categories under GDPR Article 9
        PIIType.ETHNICITY: Sensitivity.RESTRICTED,
        PIIType.RELIGION: Sensitivity.RESTRICTED,
        PIIType.POLITICAL_OPINION: Sensitivity.RESTRICTED,
        PIIType.SEXUAL_ORIENTATION: Sensitivity.RESTRICTED,
        # Confidential
        PIIType.EMAIL: Sensitivity.CONFIDENTIAL,
        PIIType.PHONE: Sensitivity.CONFIDENTIAL,
        PIIType.ADDRESS: Sensitivity.CONFIDENTIAL,
        PIIType.DATE_OF_BIRTH: Sensitivity.CONFIDENTIAL,
        PIIType.NAME: Sensitivity.CONFIDENTIAL,
        PIIType.IP_ADDRESS: Sensitivity.CONFIDENTIAL,
        PIIType.DEVICE_ID: Sensitivity.CONFIDENTIAL,
        PIIType.MAC_ADDRESS: Sensitivity.CONFIDENTIAL,
        # Internal (minimum for any PII)
        PIIType.GENDER: Sensitivity.INTERNAL,
        PIIType.USERNAME: Sensitivity.INTERNAL,
    }

    # Sensitivity level ordering (for comparison)
    SENSITIVITY_ORDER = {
        Sensitivity.PUBLIC: 0,
        Sensitivity.INTERNAL: 1,
        Sensitivity.CONFIDENTIAL: 2,
        Sensitivity.RESTRICTED: 3,
    }

    @property
    def name(self) -> str:
        return "sensitivity"

    def evaluate(
        self,
        adapter: DataFrameAdapter,
        field: str,
        privacy_info: PrivacyInfo | None,
        **kwargs: Any,
    ) -> list[PrivacyViolation]:
        """Evaluate sensitivity level for a field.

        Args:
            adapter: DataFrame adapter
            field: Field name to check
            privacy_info: Declared privacy metadata

        Returns:
            List of violations for sensitivity issues
        """
        violations = []

        # Skip if no privacy info
        if not privacy_info:
            return violations

        # Check 1: PII should not be PUBLIC
        if privacy_info.is_pii and privacy_info.sensitivity == Sensitivity.PUBLIC:
            violations.append(
                PrivacyViolation(
                    field=field,
                    violation_type="pii_public_sensitivity",
                    message=(
                        f"Field '{field}' is marked as PII but has PUBLIC sensitivity. "
                        f"PII must be at least INTERNAL sensitivity."
                    ),
                    severity=ErrorSeverity.ERROR,
                    detected_pii_type=privacy_info.pii_type,
                    recommendation=(
                        f"Update sensitivity to at least Sensitivity.INTERNAL "
                        f"for field '{field}'"
                    ),
                    details={
                        "current_sensitivity": privacy_info.sensitivity.value,
                        "minimum_required": Sensitivity.INTERNAL.value,
                    },
                )
            )

        # Check 2: PII type-specific sensitivity requirements
        if privacy_info.is_pii and privacy_info.pii_type:
            min_sensitivity = self.MIN_SENSITIVITY_BY_TYPE.get(
                privacy_info.pii_type, Sensitivity.INTERNAL
            )

            if self._sensitivity_below(privacy_info.sensitivity, min_sensitivity):
                violations.append(
                    PrivacyViolation(
                        field=field,
                        violation_type="insufficient_sensitivity",
                        message=(
                            f"Field '{field}' contains {privacy_info.pii_type.value} "
                            f"but has {privacy_info.sensitivity.value} sensitivity. "
                            f"Minimum required: {min_sensitivity.value}"
                        ),
                        severity=ErrorSeverity.WARNING,
                        detected_pii_type=privacy_info.pii_type,
                        recommendation=(
                            f"Upgrade sensitivity to Sensitivity.{min_sensitivity.name} "
                            f"for field '{field}'"
                        ),
                        details={
                            "current_sensitivity": privacy_info.sensitivity.value,
                            "minimum_required": min_sensitivity.value,
                            "pii_type": privacy_info.pii_type.value,
                        },
                    )
                )

        # Check 3: RESTRICTED data should require encryption
        if (
            privacy_info.sensitivity == Sensitivity.RESTRICTED
            and not privacy_info.requires_encryption
        ):
            violations.append(
                PrivacyViolation(
                    field=field,
                    violation_type="restricted_without_encryption",
                    message=(
                        f"Field '{field}' has RESTRICTED sensitivity "
                        f"but requires_encryption is not set"
                    ),
                    severity=ErrorSeverity.WARNING,
                    detected_pii_type=privacy_info.pii_type,
                    recommendation=(
                        f"Set requires_encryption=True for RESTRICTED field '{field}'"
                    ),
                    details={
                        "sensitivity": privacy_info.sensitivity.value,
                    },
                )
            )

        # Check 4: High-risk PII should require consent
        high_consent_types = {
            PIIType.HEALTH_DATA,
            PIIType.MEDICAL_RECORD,
            PIIType.BIOMETRIC,
            PIIType.ETHNICITY,
            PIIType.RELIGION,
            PIIType.POLITICAL_OPINION,
            PIIType.SEXUAL_ORIENTATION,
        }

        if (
            privacy_info.pii_type in high_consent_types
            and not privacy_info.requires_consent
        ):
            violations.append(
                PrivacyViolation(
                    field=field,
                    violation_type="special_category_without_consent",
                    message=(
                        f"Field '{field}' contains special category data "
                        f"({privacy_info.pii_type.value}) but requires_consent is not set"
                    ),
                    severity=ErrorSeverity.WARNING,
                    detected_pii_type=privacy_info.pii_type,
                    recommendation=(
                        f"Set requires_consent=True for special category "
                        f"field '{field}' (GDPR Article 9)"
                    ),
                    details={
                        "pii_type": privacy_info.pii_type.value,
                        "gdpr_article": "Article 9",
                    },
                )
            )

        return violations

    def _sensitivity_below(
        self, actual: Sensitivity, minimum: Sensitivity
    ) -> bool:
        """Check if actual sensitivity is below minimum required."""
        return self.SENSITIVITY_ORDER[actual] < self.SENSITIVITY_ORDER[minimum]
