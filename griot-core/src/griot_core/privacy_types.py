"""Privacy types and enums for data protection compliance.

Supports Kenya Data Protection Act 2019 and EU GDPR requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Sensitivity(Enum):
    """Data sensitivity classification levels.

    Based on common enterprise data classification schemes
    aligned with Kenya DPA and GDPR requirements.
    """

    PUBLIC = "public"
    """Data that can be freely shared."""

    INTERNAL = "internal"
    """Data for internal use only, not public."""

    CONFIDENTIAL = "confidential"
    """Sensitive data requiring protection."""

    RESTRICTED = "restricted"
    """Highly sensitive data with strict access controls."""


class PIIType(Enum):
    """Types of Personally Identifiable Information.

    Categories based on common PII classifications.
    """

    # Direct identifiers
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"

    # Government IDs
    NATIONAL_ID = "national_id"  # Kenya National ID
    PASSPORT = "passport"
    TAX_ID = "tax_id"  # KRA PIN (Kenya)
    SSN = "ssn"  # Social Security Number

    # Financial
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    IBAN = "iban"

    # Health
    HEALTH_DATA = "health_data"
    MEDICAL_RECORD = "medical_record"

    # Biometric
    BIOMETRIC = "biometric"
    FINGERPRINT = "fingerprint"
    FACIAL_DATA = "facial_data"

    # Digital identifiers
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"
    DEVICE_ID = "device_id"
    USERNAME = "username"

    # Other
    DATE_OF_BIRTH = "date_of_birth"
    GENDER = "gender"
    ETHNICITY = "ethnicity"
    RELIGION = "religion"
    POLITICAL_OPINION = "political_opinion"
    SEXUAL_ORIENTATION = "sexual_orientation"

    # Generic
    OTHER = "other"
    UNKNOWN = "unknown"


class MaskingStrategy(Enum):
    """Strategies for masking PII data.

    Different masking approaches for different data types.
    """

    # Complete masking
    REDACT = "redact"
    """Replace with [REDACTED] or similar."""

    HASH = "hash"
    """Replace with cryptographic hash."""

    # Partial masking
    PARTIAL = "partial"
    """Show first/last few characters (e.g., J***n for John)."""

    TRUNCATE = "truncate"
    """Show only first N characters."""

    ASTERISK = "asterisk"
    """Replace characters with asterisks."""

    # Value transformation
    GENERALIZE = "generalize"
    """Generalize to category (e.g., exact age -> age range)."""

    PSEUDONYMIZE = "pseudonymize"
    """Replace with consistent fake value."""

    TOKENIZE = "tokenize"
    """Replace with reversible token."""

    # Null/remove
    NULL = "null"
    """Replace with null/None."""

    REMOVE = "remove"
    """Remove the field entirely."""

    # No masking
    NONE = "none"
    """No masking applied."""


class ComplianceFramework(Enum):
    """Data protection compliance frameworks."""

    KENYA_DPA = "kenya_dpa"
    """Kenya Data Protection Act 2019."""

    GDPR = "gdpr"
    """EU General Data Protection Regulation."""

    CCPA = "ccpa"
    """California Consumer Privacy Act."""

    HIPAA = "hipaa"
    """US Health Insurance Portability and Accountability Act."""

    PCI_DSS = "pci_dss"
    """Payment Card Industry Data Security Standard."""

    CUSTOM = "custom"
    """Custom/internal privacy policy."""


@dataclass
class PrivacyInfo:
    """Privacy metadata for a schema field.

    Attributes:
        is_pii (bool): Whether this field contains PII.
        pii_type (PIIType | None): Type of PII if is_pii is True.
        sensitivity (Sensitivity): Data sensitivity classification.
        requires_masking (bool): Whether this field requires masking in outputs.
        masking_strategy (MaskingStrategy): Strategy to use when masking is required.
        requires_encryption (bool): Whether this field requires encryption at rest.
        requires_consent (bool): Whether processing requires explicit consent.
        retention_days (int | None): Data retention period in days (None = indefinite).
        purpose_limitation (list[str]): Allowed purposes for processing this data.
        compliance_frameworks (list[ComplianceFramework]): Applicable compliance frameworks.
        custom_properties (dict[str, Any]): Additional custom privacy properties.

    """

    is_pii: bool = False
    """Whether this field contains PII."""

    pii_type: PIIType | None = None
    """Type of PII if is_pii is True."""

    sensitivity: Sensitivity = Sensitivity.INTERNAL
    """Data sensitivity classification."""

    requires_masking: bool = False
    """Whether this field requires masking in outputs."""

    masking_strategy: MaskingStrategy = MaskingStrategy.NONE
    """Strategy to use when masking is required."""

    requires_encryption: bool = False
    """Whether this field requires encryption at rest."""

    requires_consent: bool = False
    """Whether processing requires explicit consent."""

    retention_days: int | None = None
    """Data retention period in days (None = indefinite)."""

    purpose_limitation: list[str] = field(default_factory=list)
    """Allowed purposes for processing this data."""

    compliance_frameworks: list[ComplianceFramework] = field(default_factory=list)
    """Applicable compliance frameworks."""

    custom_properties: dict[str, Any] = field(default_factory=dict)
    """Additional custom privacy properties."""

    def __post_init__(self):
        """Validate privacy info consistency."""
        # If is_pii but no type, set to UNKNOWN
        if self.is_pii and self.pii_type is None:
            self.pii_type = PIIType.UNKNOWN

        # If PII, should at least be INTERNAL sensitivity
        if self.is_pii and self.sensitivity == Sensitivity.PUBLIC:
            # PII should not be public - upgrade to INTERNAL
            self.sensitivity = Sensitivity.INTERNAL

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "is_pii": self.is_pii,
            "sensitivity": self.sensitivity.value,
        }

        if self.pii_type:
            result["pii_type"] = self.pii_type.value

        if self.requires_masking:
            result["requires_masking"] = True
            result["masking_strategy"] = self.masking_strategy.value

        if self.requires_encryption:
            result["requires_encryption"] = True

        if self.requires_consent:
            result["requires_consent"] = True

        if self.retention_days is not None:
            result["retention_days"] = self.retention_days

        if self.purpose_limitation:
            result["purpose_limitation"] = self.purpose_limitation

        if self.compliance_frameworks:
            result["compliance_frameworks"] = [f.value for f in self.compliance_frameworks]

        if self.custom_properties:
            result["custom_properties"] = self.custom_properties

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrivacyInfo:
        """Create PrivacyInfo from dictionary."""
        pii_type = None
        if "pii_type" in data:
            pii_type = PIIType(data["pii_type"])

        sensitivity = Sensitivity.INTERNAL
        if "sensitivity" in data:
            sensitivity = Sensitivity(data["sensitivity"])

        masking_strategy = MaskingStrategy.NONE
        if "masking_strategy" in data:
            masking_strategy = MaskingStrategy(data["masking_strategy"])

        compliance_frameworks = []
        if "compliance_frameworks" in data:
            compliance_frameworks = [
                ComplianceFramework(f) for f in data["compliance_frameworks"]
            ]

        return cls(
            is_pii=data.get("is_pii", False),
            pii_type=pii_type,
            sensitivity=sensitivity,
            requires_masking=data.get("requires_masking", False),
            masking_strategy=masking_strategy,
            requires_encryption=data.get("requires_encryption", False),
            requires_consent=data.get("requires_consent", False),
            retention_days=data.get("retention_days"),
            purpose_limitation=data.get("purpose_limitation", []),
            compliance_frameworks=compliance_frameworks,
            custom_properties=data.get("custom_properties", {}),
        )


@dataclass
class PrivacyViolation:
    """Represents a privacy rule violation."""

    field: str
    """Field that has the violation."""

    violation_type: str
    """Type of violation (e.g., 'undeclared_pii', 'missing_masking')."""

    message: str
    """Human-readable description of the violation."""

    severity: ErrorSeverity
    """Severity level of the violation."""

    detected_pii_type: PIIType | None = None
    """PII type that was detected (for undeclared PII)."""

    sample_values: list[Any] = field(default_factory=list)
    """Sample values that triggered the violation."""

    recommendation: str | None = None
    """Recommended action to resolve the violation."""

    compliance_impact: list[ComplianceFramework] = field(default_factory=list)
    """Compliance frameworks affected by this violation."""

    details: dict[str, Any] = field(default_factory=dict)
    """Additional violation details."""


# Import ErrorSeverity from parent types
from griot_core.validation_types import ErrorSeverity


# Convenience constants for common privacy configurations
PII_EMAIL = PrivacyInfo(
    is_pii=True,
    pii_type=PIIType.EMAIL,
    sensitivity=Sensitivity.CONFIDENTIAL,
    requires_masking=True,
    masking_strategy=MaskingStrategy.PARTIAL,
)

PII_PHONE = PrivacyInfo(
    is_pii=True,
    pii_type=PIIType.PHONE,
    sensitivity=Sensitivity.CONFIDENTIAL,
    requires_masking=True,
    masking_strategy=MaskingStrategy.PARTIAL,
)

PII_NATIONAL_ID = PrivacyInfo(
    is_pii=True,
    pii_type=PIIType.NATIONAL_ID,
    sensitivity=Sensitivity.RESTRICTED,
    requires_masking=True,
    masking_strategy=MaskingStrategy.HASH,
    requires_encryption=True,
    compliance_frameworks=[ComplianceFramework.KENYA_DPA],
)

PII_CREDIT_CARD = PrivacyInfo(
    is_pii=True,
    pii_type=PIIType.CREDIT_CARD,
    sensitivity=Sensitivity.RESTRICTED,
    requires_masking=True,
    masking_strategy=MaskingStrategy.PARTIAL,
    requires_encryption=True,
    compliance_frameworks=[ComplianceFramework.PCI_DSS],
)

NON_PII_INTERNAL = PrivacyInfo(
    is_pii=False,
    sensitivity=Sensitivity.INTERNAL,
)

NON_PII_PUBLIC = PrivacyInfo(
    is_pii=False,
    sensitivity=Sensitivity.PUBLIC,
)
