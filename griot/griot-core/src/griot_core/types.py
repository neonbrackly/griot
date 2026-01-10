"""
Griot Core Type Definitions

Enums and type definitions for the Griot data contract system.
All types use Python stdlib only (no external dependencies).
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum, auto
from typing import Any, Callable, TypeVar, Union

__all__ = [
    # Phase 1 - Core types
    "ConstraintType",
    "Severity",
    "FieldFormat",
    "AggregationType",
    "DataType",
    # Phase 2 - PII/Privacy types (FR-SDK-008)
    "PIICategory",
    "SensitivityLevel",
    "MaskingStrategy",
    "LegalBasis",
    # Phase 2 - Residency types (FR-SDK-011)
    "ResidencyConfig",
    "ResidencyRule",
    "DataRegion",
    # Phase 2 - Lineage types (FR-SDK-012)
    "LineageConfig",
    "Source",
    "Transformation",
    "Consumer",
]


class ConstraintType(str, Enum):
    """Types of field constraints that can be applied to values."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    FORMAT = "format"
    GE = "ge"  # Greater than or equal
    LE = "le"  # Less than or equal
    GT = "gt"  # Greater than
    LT = "lt"  # Less than
    MULTIPLE_OF = "multiple_of"
    ENUM = "enum"
    UNIQUE = "unique"


class Severity(str, Enum):
    """Error/issue severity levels for validation and linting."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class FieldFormat(str, Enum):
    """Built-in field format validators for common patterns."""

    EMAIL = "email"
    URI = "uri"
    UUID = "uuid"
    DATE = "date"
    DATETIME = "datetime"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    HOSTNAME = "hostname"


class AggregationType(str, Enum):
    """Recommended aggregation methods for numeric fields."""

    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    NONE = "none"


class DataType(str, Enum):
    """Supported data types for contract fields."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"

    @classmethod
    def from_python_type(cls, python_type: type | str) -> DataType:
        """Convert a Python type to a DataType enum value."""
        type_mapping: dict[type | str, DataType] = {
            str: cls.STRING,
            int: cls.INTEGER,
            float: cls.FLOAT,
            bool: cls.BOOLEAN,
            list: cls.ARRAY,
            dict: cls.OBJECT,
            "str": cls.STRING,
            "int": cls.INTEGER,
            "float": cls.FLOAT,
            "bool": cls.BOOLEAN,
            "list": cls.ARRAY,
            "dict": cls.OBJECT,
            "date": cls.DATE,
            "datetime": cls.DATETIME,
        }
        return type_mapping.get(python_type, cls.ANY)

    def to_python_type(self) -> type:
        """Convert DataType to Python type."""
        type_mapping: dict[DataType, type] = {
            DataType.STRING: str,
            DataType.INTEGER: int,
            DataType.FLOAT: float,
            DataType.BOOLEAN: bool,
            DataType.ARRAY: list,
            DataType.OBJECT: dict,
            DataType.DATE: str,  # dates stored as ISO strings
            DataType.DATETIME: str,  # datetimes stored as ISO strings
            DataType.ANY: object,
        }
        return type_mapping[self]


# =============================================================================
# PHASE 2 - PII/Privacy Types (FR-SDK-008)
# =============================================================================


class PIICategory(str, Enum):
    """
    Categories of Personally Identifiable Information (PII).

    Based on common privacy regulations (GDPR, CCPA, HIPAA).
    Used to classify fields containing personal data.
    """

    # Direct identifiers
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"  # Social Security Number
    NATIONAL_ID = "national_id"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"

    # Financial identifiers
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    FINANCIAL = "financial"

    # Biometric
    BIOMETRIC = "biometric"
    FACIAL = "facial"
    FINGERPRINT = "fingerprint"
    VOICE = "voice"

    # Health
    HEALTH = "health"
    MEDICAL_RECORD = "medical_record"
    GENETIC = "genetic"

    # Digital identifiers
    IP_ADDRESS = "ip_address"
    DEVICE_ID = "device_id"
    COOKIE = "cookie"
    USER_AGENT = "user_agent"

    # Location
    LOCATION = "location"
    GPS = "gps"
    GEOLOCATION = "geolocation"

    # Behavioral
    BEHAVIORAL = "behavioral"
    BROWSING_HISTORY = "browsing_history"
    PURCHASE_HISTORY = "purchase_history"

    # Demographics
    DATE_OF_BIRTH = "date_of_birth"
    AGE = "age"
    GENDER = "gender"
    ETHNICITY = "ethnicity"
    RELIGION = "religion"
    POLITICAL = "political"
    SEXUAL_ORIENTATION = "sexual_orientation"

    # Employment
    EMPLOYEE_ID = "employee_id"
    SALARY = "salary"

    # Other
    OTHER = "other"
    NONE = "none"


class SensitivityLevel(str, Enum):
    """
    Data sensitivity classification levels.

    Used to determine handling requirements and access controls.
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

    @property
    def numeric_level(self) -> int:
        """Return numeric sensitivity level for comparison."""
        levels = {
            SensitivityLevel.PUBLIC: 0,
            SensitivityLevel.INTERNAL: 1,
            SensitivityLevel.CONFIDENTIAL: 2,
            SensitivityLevel.RESTRICTED: 3,
            SensitivityLevel.TOP_SECRET: 4,
        }
        return levels[self]

    def __lt__(self, other: SensitivityLevel) -> bool:
        return self.numeric_level < other.numeric_level

    def __le__(self, other: SensitivityLevel) -> bool:
        return self.numeric_level <= other.numeric_level

    def __gt__(self, other: SensitivityLevel) -> bool:
        return self.numeric_level > other.numeric_level

    def __ge__(self, other: SensitivityLevel) -> bool:
        return self.numeric_level >= other.numeric_level


class MaskingStrategy(str, Enum):
    """
    Data masking/anonymization strategies.

    Used to protect sensitive data while preserving utility.
    """

    # Full masking
    REDACT = "redact"  # Replace with [REDACTED]
    NULL = "null"  # Replace with null/None
    CONSTANT = "constant"  # Replace with constant value

    # Partial masking
    PARTIAL = "partial"  # Show partial (e.g., ****1234)
    TRUNCATE = "truncate"  # Show first N characters
    MASK_EMAIL = "mask_email"  # j***@e***.com

    # Transformation
    HASH = "hash"  # One-way hash (SHA-256)
    ENCRYPT = "encrypt"  # Reversible encryption
    TOKENIZE = "tokenize"  # Replace with token

    # Anonymization
    GENERALIZE = "generalize"  # Reduce precision (age -> age range)
    NOISE = "noise"  # Add statistical noise
    SHUFFLE = "shuffle"  # Shuffle values within column

    # Synthetic
    SYNTHETIC = "synthetic"  # Replace with synthetic data

    # None
    NONE = "none"  # No masking


class LegalBasis(str, Enum):
    """
    Legal basis for processing personal data (GDPR Article 6).

    Determines under what legal grounds data can be processed.
    """

    CONSENT = "consent"  # Subject has given consent
    CONTRACT = "contract"  # Necessary for contract performance
    LEGAL_OBLIGATION = "legal_obligation"  # Required by law
    VITAL_INTEREST = "vital_interest"  # Protect vital interests
    PUBLIC_TASK = "public_task"  # Public interest or official authority
    LEGITIMATE_INTEREST = "legitimate_interest"  # Legitimate business interest

    # Extended bases
    EMPLOYMENT = "employment"  # Employment law context
    RESEARCH = "research"  # Scientific/historical research
    ARCHIVING = "archiving"  # Archiving in public interest

    # None/Unknown
    NONE = "none"
    UNKNOWN = "unknown"


# =============================================================================
# PHASE 2 - Data Residency Types (FR-SDK-011)
# =============================================================================


class DataRegion(str, Enum):
    """
    Geographic regions for data residency requirements.

    Based on common regulatory jurisdictions.
    """

    # Americas
    US = "us"
    US_EAST = "us-east"
    US_WEST = "us-west"
    CANADA = "canada"
    BRAZIL = "brazil"
    LATAM = "latam"

    # Europe
    EU = "eu"
    EU_WEST = "eu-west"
    EU_CENTRAL = "eu-central"
    UK = "uk"
    GERMANY = "germany"
    FRANCE = "france"
    SWITZERLAND = "switzerland"

    # Asia Pacific
    APAC = "apac"
    JAPAN = "japan"
    AUSTRALIA = "australia"
    SINGAPORE = "singapore"
    INDIA = "india"
    CHINA = "china"
    HONG_KONG = "hong_kong"
    SOUTH_KOREA = "south_korea"

    # Middle East & Africa
    MEA = "mea"
    UAE = "uae"
    SOUTH_AFRICA = "south_africa"

    # Global
    GLOBAL = "global"
    ANY = "any"


@dataclass
class ResidencyRule:
    """
    A single data residency rule.

    Specifies where data can and cannot be stored/processed.
    """

    allowed_regions: list[DataRegion] = dataclass_field(default_factory=list)
    forbidden_regions: list[DataRegion] = dataclass_field(default_factory=list)
    requires_encryption: bool = False
    requires_pseudonymization: bool = False
    max_retention_days: int | None = None
    notes: str | None = None

    def is_region_allowed(self, region: DataRegion) -> bool:
        """Check if a region is allowed by this rule."""
        if region in self.forbidden_regions:
            return False
        if self.allowed_regions and region not in self.allowed_regions:
            # If allowed_regions is specified, region must be in it
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "allowed_regions": [r.value for r in self.allowed_regions],
            "forbidden_regions": [r.value for r in self.forbidden_regions],
            "requires_encryption": self.requires_encryption,
            "requires_pseudonymization": self.requires_pseudonymization,
            "max_retention_days": self.max_retention_days,
            "notes": self.notes,
        }


@dataclass
class ResidencyConfig:
    """
    Data residency configuration for a contract.

    Defines geographic restrictions and compliance requirements.
    """

    default_rule: ResidencyRule | None = None
    field_rules: dict[str, ResidencyRule] = dataclass_field(default_factory=dict)
    compliance_frameworks: list[str] = dataclass_field(default_factory=list)
    data_controller: str | None = None
    data_processor: str | None = None
    dpo_contact: str | None = None  # Data Protection Officer

    def get_rule_for_field(self, field_name: str) -> ResidencyRule | None:
        """Get the residency rule for a specific field."""
        if field_name in self.field_rules:
            return self.field_rules[field_name]
        return self.default_rule

    def check_residency(
        self, field_name: str, region: DataRegion
    ) -> tuple[bool, str | None]:
        """
        Check if storing a field in a region is compliant.

        Returns:
            Tuple of (is_compliant, error_message).
        """
        rule = self.get_rule_for_field(field_name)
        if rule is None:
            return True, None

        if not rule.is_region_allowed(region):
            if region in rule.forbidden_regions:
                return False, f"Field '{field_name}' cannot be stored in {region.value} (forbidden)"
            return False, f"Field '{field_name}' must be stored in {[r.value for r in rule.allowed_regions]}"

        return True, None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "default_rule": self.default_rule.to_dict() if self.default_rule else None,
            "field_rules": {k: v.to_dict() for k, v in self.field_rules.items()},
            "compliance_frameworks": self.compliance_frameworks,
            "data_controller": self.data_controller,
            "data_processor": self.data_processor,
            "dpo_contact": self.dpo_contact,
        }


# =============================================================================
# PHASE 2 - Data Lineage Types (FR-SDK-012)
# =============================================================================


@dataclass
class Source:
    """
    Data source definition for lineage tracking.

    Represents where data originates from.
    """

    name: str
    type: str  # e.g., "database", "api", "file", "stream"
    system: str | None = None  # e.g., "salesforce", "postgres", "s3"
    location: str | None = None  # e.g., connection string, path, URL
    owner: str | None = None
    refresh_frequency: str | None = None  # e.g., "daily", "hourly", "real-time"
    sla: str | None = None  # e.g., "99.9%", "4h recovery"
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "system": self.system,
            "location": self.location,
            "owner": self.owner,
            "refresh_frequency": self.refresh_frequency,
            "sla": self.sla,
            "metadata": self.metadata,
        }


@dataclass
class Transformation:
    """
    Data transformation definition for lineage tracking.

    Represents how data is processed between source and destination.
    """

    name: str
    type: str  # e.g., "etl", "sql", "python", "dbt"
    description: str | None = None
    logic: str | None = None  # e.g., SQL query, transformation code
    input_fields: list[str] = dataclass_field(default_factory=list)
    output_fields: list[str] = dataclass_field(default_factory=list)
    owner: str | None = None
    schedule: str | None = None  # e.g., cron expression
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "logic": self.logic,
            "input_fields": self.input_fields,
            "output_fields": self.output_fields,
            "owner": self.owner,
            "schedule": self.schedule,
            "metadata": self.metadata,
        }


@dataclass
class Consumer:
    """
    Data consumer definition for lineage tracking.

    Represents systems/users that consume the data.
    """

    name: str
    type: str  # e.g., "dashboard", "report", "api", "ml_model", "application"
    system: str | None = None
    owner: str | None = None
    access_level: str | None = None  # e.g., "read", "write", "admin"
    purpose: str | None = None  # Why they need the data
    fields_used: list[str] = dataclass_field(default_factory=list)
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "system": self.system,
            "owner": self.owner,
            "access_level": self.access_level,
            "purpose": self.purpose,
            "fields_used": self.fields_used,
            "metadata": self.metadata,
        }


@dataclass
class LineageConfig:
    """
    Data lineage configuration for a contract.

    Tracks data flow from sources through transformations to consumers.
    """

    sources: list[Source] = dataclass_field(default_factory=list)
    transformations: list[Transformation] = dataclass_field(default_factory=list)
    consumers: list[Consumer] = dataclass_field(default_factory=list)

    # Field-level lineage
    field_sources: dict[str, str] = dataclass_field(default_factory=dict)  # field -> source
    field_transformations: dict[str, list[str]] = dataclass_field(
        default_factory=dict
    )  # field -> [transformations]

    # Ownership
    data_owner: str | None = None
    data_steward: str | None = None
    technical_owner: str | None = None

    def get_field_lineage(self, field_name: str) -> dict[str, Any]:
        """Get complete lineage information for a field."""
        return {
            "field": field_name,
            "source": self.field_sources.get(field_name),
            "transformations": self.field_transformations.get(field_name, []),
            "consumers": [c.name for c in self.consumers if field_name in c.fields_used],
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sources": [s.to_dict() for s in self.sources],
            "transformations": [t.to_dict() for t in self.transformations],
            "consumers": [c.to_dict() for c in self.consumers],
            "field_sources": self.field_sources,
            "field_transformations": self.field_transformations,
            "data_owner": self.data_owner,
            "data_steward": self.data_steward,
            "technical_owner": self.technical_owner,
        }
