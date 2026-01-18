"""Privacy framework for data protection compliance.

Supports automatic PII detection and validation against declared privacy
metadata. Aligned with Kenya Data Protection Act 2019 and EU GDPR.

Quick Start:
    from griot_core.validation.privacy import (
        PrivacyInfo,
        detect_pii,
        PIIType,
        Sensitivity,
    )

    # Declare privacy in schema
    field = Field(
        name="email",
        type=str,
        privacy=PrivacyInfo(
            is_pii=True,
            pii_type=PIIType.EMAIL,
            sensitivity=Sensitivity.CONFIDENTIAL,
        )
    )

    # Detect undeclared PII
    matches = detect_pii("user@example.com")
"""

from __future__ import annotations

# Types and enums
from .types import (
    Sensitivity,
    PIIType,
    MaskingStrategy,
    ComplianceFramework,
    PrivacyInfo,
    PrivacyViolation,
    # Convenience constants
    PII_EMAIL,
    PII_PHONE,
    PII_NATIONAL_ID,
    PII_CREDIT_CARD,
    NON_PII_INTERNAL,
    NON_PII_PUBLIC,
)

# PII detection patterns
from .patterns import (
    PIIPattern,
    PIIPatternRegistry,
    detect_pii,
    detect_pii_in_column,
    create_default_registry,
    DEFAULT_REGISTRY,
    # Pattern collections
    KENYA_PATTERNS,
    EU_PATTERNS,
    UNIVERSAL_PATTERNS,
    # Validation functions
    luhn_check,
    kenya_id_check,
    kra_pin_check,
    iban_check,
)

# Evaluators
from .evaluators import (
    PrivacyEvaluator,
    PrivacyEvaluatorRegistry,
    UndeclaredPIIEvaluator,
    MaskingEvaluator,
    SensitivityEvaluator,
    evaluate_privacy,
)


__all__ = [
    # Types
    "Sensitivity",
    "PIIType",
    "MaskingStrategy",
    "ComplianceFramework",
    "PrivacyInfo",
    "PrivacyViolation",
    # Convenience constants
    "PII_EMAIL",
    "PII_PHONE",
    "PII_NATIONAL_ID",
    "PII_CREDIT_CARD",
    "NON_PII_INTERNAL",
    "NON_PII_PUBLIC",
    # Patterns
    "PIIPattern",
    "PIIPatternRegistry",
    "detect_pii",
    "detect_pii_in_column",
    "create_default_registry",
    "DEFAULT_REGISTRY",
    "KENYA_PATTERNS",
    "EU_PATTERNS",
    "UNIVERSAL_PATTERNS",
    # Validators
    "luhn_check",
    "kenya_id_check",
    "kra_pin_check",
    "iban_check",
    # Evaluators
    "PrivacyEvaluator",
    "PrivacyEvaluatorRegistry",
    "UndeclaredPIIEvaluator",
    "MaskingEvaluator",
    "SensitivityEvaluator",
    "evaluate_privacy",
]
