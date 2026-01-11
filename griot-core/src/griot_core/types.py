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
    # Phase 6 - ODCS types (Open Data Contract Standard)
    "ContractStatus",
    "PhysicalType",
    "QualityRuleType",
    "CheckType",
    "ExtractionMethod",
    "PartitioningStrategy",
    "ReviewCadence",
    "AccessLevel",
    "DistributionType",
    "SourceType",
    # Phase 6 - ODCS dataclasses
    "CustomProperty",
    "Description",
    "SemanticInfo",
    "PrivacyInfo",
    "FieldConstraints",
    "ForeignKey",
    "SchemaProperty",
    "QualityRule",
    "CustomCheck",
    "Legal",
    "CrossBorder",
    "Compliance",
    "AuditRequirements",
    "SLA",
    "AvailabilitySLA",
    "FreshnessSLA",
    "CompletenessSLA",
    "AccuracySLA",
    "ResponseTimeSLA",
    "AccessGrant",
    "AccessApproval",
    "AccessConfig",
    "DistributionChannel",
    "Distribution",
    "GovernanceProducer",
    "GovernanceConsumer",
    "ApprovalRecord",
    "ReviewConfig",
    "ChangeManagement",
    "Governance",
    "Team",
    "Steward",
    "Server",
    "Role",
    "Timestamps",
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


# =============================================================================
# PHASE 6 - Open Data Contract Standard (ODCS) Types
# =============================================================================


class ContractStatus(str, Enum):
    """
    Contract lifecycle status (T-340).

    Indicates the current state of a data contract in its lifecycle.
    Based on Open Data Contract Standard.
    """

    DRAFT = "draft"  # Contract is being developed, not yet active
    ACTIVE = "active"  # Contract is in production use
    DEPRECATED = "deprecated"  # Contract is being phased out
    RETIRED = "retired"  # Contract is no longer in use


class PhysicalType(str, Enum):
    """
    Physical storage type for schema objects (T-341).

    Describes how the data is physically stored or accessed.
    """

    TABLE = "table"  # Database table
    VIEW = "view"  # Database view
    FILE = "file"  # File-based storage (CSV, Parquet, etc.)
    STREAM = "stream"  # Streaming data (Kafka, Kinesis, etc.)


class QualityRuleType(str, Enum):
    """
    Types of data quality rules (T-342).

    Standard quality dimensions for data quality checks.
    """

    COMPLETENESS = "completeness"  # Check for missing values
    ACCURACY = "accuracy"  # Check for data accuracy
    FRESHNESS = "freshness"  # Check for data timeliness
    VOLUME = "volume"  # Check for expected data volume
    DISTRIBUTION = "distribution"  # Check for value distribution


class CheckType(str, Enum):
    """
    Types of custom quality checks (T-343).

    Specifies the language/framework for custom quality check definitions.
    """

    SQL = "sql"  # SQL-based check
    PYTHON = "python"  # Python-based check
    GREAT_EXPECTATIONS = "great_expectations"  # Great Expectations framework


class ExtractionMethod(str, Enum):
    """
    Data extraction methods for lineage (T-344).

    Describes how data is extracted from source systems.
    """

    FULL = "full"  # Full extraction (complete data refresh)
    INCREMENTAL = "incremental"  # Incremental extraction (delta only)
    CDC = "cdc"  # Change Data Capture


class PartitioningStrategy(str, Enum):
    """
    Data partitioning strategies (T-345).

    Describes how data is partitioned for storage/distribution.
    """

    DATE = "date"  # Partitioned by date/time
    HASH = "hash"  # Hash-based partitioning
    RANGE = "range"  # Range-based partitioning


class ReviewCadence(str, Enum):
    """
    Contract review frequency (T-346).

    Specifies how often contracts should be reviewed.
    """

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class AccessLevel(str, Enum):
    """
    Data access levels (T-347).

    Defines the level of access granted to principals.
    """

    READ = "read"  # Read-only access
    WRITE = "write"  # Read and write access
    ADMIN = "admin"  # Full administrative access


class DistributionType(str, Enum):
    """
    Data distribution channel types (T-348).

    Describes where and how data is made available.
    """

    WAREHOUSE = "warehouse"  # Data warehouse (BigQuery, Snowflake, Redshift)
    LAKE = "lake"  # Data lake (S3, GCS, ADLS)
    API = "api"  # REST/GraphQL API
    STREAM = "stream"  # Streaming platform (Kafka, Kinesis)
    FILE = "file"  # File export


class SourceType(str, Enum):
    """
    Data source types for lineage (T-349).

    Describes the type of upstream data source.
    """

    SYSTEM = "system"  # Internal system/database
    CONTRACT = "contract"  # Another data contract
    FILE = "file"  # File-based source
    API = "api"  # External API
    STREAM = "stream"  # Streaming source


# =============================================================================
# PHASE 6 - ODCS Dataclasses (T-311 through T-326)
# =============================================================================


@dataclass
class CustomProperty:
    """
    Custom property for contract descriptions (T-311).

    Allows arbitrary key-value metadata with descriptions.
    """

    name: str
    value: str
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"name": self.name, "value": self.value}
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class Description:
    """
    Contract description metadata (T-311).

    Provides context about the contract's purpose, usage, and limitations.
    """

    purpose: str | None = None
    usage: str | None = None
    limitations: str | None = None
    custom_properties: list[CustomProperty] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.purpose:
            result["purpose"] = self.purpose
        if self.usage:
            result["usage"] = self.usage
        if self.limitations:
            result["limitations"] = self.limitations
        if self.custom_properties:
            result["customProperties"] = [p.to_dict() for p in self.custom_properties]
        return result


@dataclass
class SemanticInfo:
    """
    Semantic metadata for a field (T-312).

    Provides business context and meaning for a field.
    """

    description: str | None = None
    unit: str | None = None
    precision: int | None = None
    business_term: str | None = None
    glossary_uri: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.description:
            result["description"] = self.description
        if self.unit:
            result["unit"] = self.unit
        if self.precision is not None:
            result["precision"] = self.precision
        if self.business_term:
            result["business_term"] = self.business_term
        if self.glossary_uri:
            result["glossary_uri"] = self.glossary_uri
        return result


@dataclass
class PrivacyInfo:
    """
    Privacy metadata for a field (T-312).

    Defines PII classification and handling requirements.
    """

    contains_pii: bool = False
    pii_category: PIICategory | None = None
    sensitivity_level: SensitivityLevel | None = None
    masking: MaskingStrategy | None = None
    retention_days: int | None = None
    legal_basis: LegalBasis | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"contains_pii": self.contains_pii}
        if self.pii_category:
            result["pii_category"] = self.pii_category.value
        if self.sensitivity_level:
            result["sensitivity_level"] = self.sensitivity_level.value
        if self.masking:
            result["masking"] = self.masking.value
        if self.retention_days is not None:
            result["retention_days"] = self.retention_days
        if self.legal_basis:
            result["legal_basis"] = self.legal_basis.value
        return result


@dataclass
class FieldConstraints:
    """
    Field constraints (T-312).

    Validation rules for field values.
    """

    pattern: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    enum: list[Any] | None = None
    unique: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.pattern:
            result["pattern"] = self.pattern
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.max_length is not None:
            result["max_length"] = self.max_length
        if self.enum:
            result["enum"] = self.enum
        if self.unique:
            result["unique"] = self.unique
        return result


@dataclass
class ForeignKey:
    """
    Foreign key reference (T-313).

    References a field in another contract.
    """

    contract: str  # Referenced contract ID
    field: str  # Referenced field name

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {"contract": self.contract, "field": self.field}


@dataclass
class SchemaProperty:
    """
    Schema property definition (T-312).

    Complete field definition with all ODCS metadata.
    """

    name: str
    description: str | None = None
    logical_type: str | None = None  # string, integer, date, etc.
    physical_type: str | None = None  # UUID, VARCHAR, etc.
    nullable: bool = True
    examples: list[Any] = dataclass_field(default_factory=list)
    primary_key: bool = False
    foreign_key: ForeignKey | None = None
    constraints: FieldConstraints | None = None
    semantic: SemanticInfo | None = None
    privacy: PrivacyInfo | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"name": self.name}
        if self.description:
            result["description"] = self.description
        if self.logical_type:
            result["logicalType"] = self.logical_type
        if self.physical_type:
            result["physicalType"] = self.physical_type
        result["nullable"] = self.nullable
        if self.examples:
            result["examples"] = self.examples
        if self.primary_key:
            result["primary_key"] = self.primary_key
        if self.foreign_key:
            result["foreign_key"] = self.foreign_key.to_dict()
        if self.constraints:
            result["constraints"] = self.constraints.to_dict()
        if self.semantic:
            result["semantic"] = self.semantic.to_dict()
        if self.privacy:
            result["privacy"] = self.privacy.to_dict()
        return result


@dataclass
class QualityRule:
    """
    Data quality rule (T-314).

    Defines a quality check for the data.
    """

    rule: QualityRuleType
    # Completeness
    min_percent: float | None = None
    critical_fields: list[str] | None = None
    # Accuracy
    max_error_rate: float | None = None
    validation_method: str | None = None
    # Freshness
    max_age: str | None = None  # ISO 8601 duration
    timestamp_field: str | None = None
    # Volume
    min_rows: int | None = None
    max_rows: int | None = None
    # Distribution
    field: str | None = None
    expected_distribution: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"rule": self.rule.value}
        if self.min_percent is not None:
            result["min_percent"] = self.min_percent
        if self.critical_fields:
            result["critical_fields"] = self.critical_fields
        if self.max_error_rate is not None:
            result["max_error_rate"] = self.max_error_rate
        if self.validation_method:
            result["validation_method"] = self.validation_method
        if self.max_age:
            result["max_age"] = self.max_age
        if self.timestamp_field:
            result["timestamp_field"] = self.timestamp_field
        if self.min_rows is not None:
            result["min_rows"] = self.min_rows
        if self.max_rows is not None:
            result["max_rows"] = self.max_rows
        if self.field:
            result["field"] = self.field
        if self.expected_distribution:
            result["expected_distribution"] = self.expected_distribution
        return result


@dataclass
class CustomCheck:
    """
    Custom quality check (T-315).

    User-defined quality check using SQL, Python, or Great Expectations.
    """

    name: str
    type: CheckType
    definition: str
    severity: Severity | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "type": self.type.value,
            "definition": self.definition,
        }
        if self.severity:
            result["severity"] = self.severity.value
        return result


@dataclass
class CrossBorder:
    """
    Cross-border data transfer rules (T-316).

    Defines restrictions and mechanisms for international data transfer.
    """

    restrictions: list[str] = dataclass_field(default_factory=list)
    transfer_mechanisms: list[str] = dataclass_field(default_factory=list)
    data_residency: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.restrictions:
            result["restrictions"] = self.restrictions
        if self.transfer_mechanisms:
            result["transfer_mechanisms"] = self.transfer_mechanisms
        if self.data_residency:
            result["data_residency"] = self.data_residency
        return result


@dataclass
class Legal:
    """
    Legal metadata (T-316).

    Defines legal basis and jurisdiction for data processing.
    """

    jurisdiction: list[str] = dataclass_field(default_factory=list)
    basis: LegalBasis | None = None
    consent_id: str | None = None
    regulations: list[str] = dataclass_field(default_factory=list)
    cross_border: CrossBorder | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.jurisdiction:
            result["jurisdiction"] = self.jurisdiction
        if self.basis:
            result["basis"] = self.basis.value
        if self.consent_id:
            result["consent_id"] = self.consent_id
        if self.regulations:
            result["regulations"] = self.regulations
        if self.cross_border:
            result["cross_border"] = self.cross_border.to_dict()
        return result


@dataclass
class AuditRequirements:
    """
    Audit requirements (T-317).

    Defines audit logging requirements.
    """

    logging: bool = False
    log_retention: str | None = None  # ISO 8601 duration

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"logging": self.logging}
        if self.log_retention:
            result["log_retention"] = self.log_retention
        return result


@dataclass
class Compliance:
    """
    Compliance metadata (T-317).

    Defines regulatory compliance requirements.
    """

    data_classification: SensitivityLevel | None = None
    regulatory_scope: list[str] = dataclass_field(default_factory=list)
    audit_requirements: AuditRequirements | None = None
    certification_requirements: list[str] = dataclass_field(default_factory=list)
    export_restrictions: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.data_classification:
            result["data_classification"] = self.data_classification.value
        if self.regulatory_scope:
            result["regulatory_scope"] = self.regulatory_scope
        if self.audit_requirements:
            result["audit_requirements"] = self.audit_requirements.to_dict()
        if self.certification_requirements:
            result["certification_requirements"] = self.certification_requirements
        if self.export_restrictions:
            result["export_restrictions"] = self.export_restrictions
        return result


@dataclass
class AvailabilitySLA:
    """Availability SLA (T-318)."""

    target_percent: float
    measurement_window: str | None = None  # ISO 8601 duration

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"target_percent": self.target_percent}
        if self.measurement_window:
            result["measurement_window"] = self.measurement_window
        return result


@dataclass
class FreshnessSLA:
    """Freshness SLA (T-318)."""

    target: str  # ISO 8601 duration
    measurement_field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"target": self.target}
        if self.measurement_field:
            result["measurement_field"] = self.measurement_field
        return result


@dataclass
class CompletenessSLA:
    """Completeness SLA (T-318)."""

    target_percent: float
    critical_fields: list[str] = dataclass_field(default_factory=list)
    critical_target_percent: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"target_percent": self.target_percent}
        if self.critical_fields:
            result["critical_fields"] = self.critical_fields
        if self.critical_target_percent is not None:
            result["critical_target_percent"] = self.critical_target_percent
        return result


@dataclass
class AccuracySLA:
    """Accuracy SLA (T-318)."""

    error_rate_target: float
    validation_method: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"error_rate_target": self.error_rate_target}
        if self.validation_method:
            result["validation_method"] = self.validation_method
        return result


@dataclass
class ResponseTimeSLA:
    """Response time SLA (T-318)."""

    p50_ms: int | None = None
    p99_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.p50_ms is not None:
            result["p50_ms"] = self.p50_ms
        if self.p99_ms is not None:
            result["p99_ms"] = self.p99_ms
        return result


@dataclass
class SLA:
    """
    Service Level Agreement (T-318).

    Defines quality targets for the data.
    """

    availability: AvailabilitySLA | None = None
    freshness: FreshnessSLA | None = None
    completeness: CompletenessSLA | None = None
    accuracy: AccuracySLA | None = None
    response_time: ResponseTimeSLA | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {}
        if self.availability:
            result["availability"] = self.availability.to_dict()
        if self.freshness:
            result["freshness"] = self.freshness.to_dict()
        if self.completeness:
            result["completeness"] = self.completeness.to_dict()
        if self.accuracy:
            result["accuracy"] = self.accuracy.to_dict()
        if self.response_time:
            result["response_time"] = self.response_time.to_dict()
        return result


@dataclass
class AccessGrant:
    """Access grant (T-319)."""

    principal: str  # team://, role://, user://, service://
    level: AccessLevel
    fields: list[str] | None = None
    expiry: str | None = None  # ISO 8601 date
    conditions: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "principal": self.principal,
            "level": self.level.value,
        }
        if self.fields:
            result["fields"] = self.fields
        if self.expiry:
            result["expiry"] = self.expiry
        if self.conditions:
            result["conditions"] = self.conditions
        return result


@dataclass
class AccessApproval:
    """Access approval requirements (T-319)."""

    required: bool = False
    approvers: list[str] = dataclass_field(default_factory=list)
    workflow: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"required": self.required}
        if self.approvers:
            result["approvers"] = self.approvers
        if self.workflow:
            result["workflow"] = self.workflow
        return result


@dataclass
class AccessConfig:
    """
    Access configuration (T-319).

    Defines who can access the data and how.
    """

    default_level: AccessLevel | None = None
    grants: list[AccessGrant] = dataclass_field(default_factory=list)
    approval: AccessApproval | None = None
    authentication: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.default_level:
            result["default_level"] = self.default_level.value
        if self.grants:
            result["grants"] = [g.to_dict() for g in self.grants]
        if self.approval:
            result["approval"] = self.approval.to_dict()
        if self.authentication:
            result["authentication"] = self.authentication
        return result


@dataclass
class DistributionChannel:
    """Distribution channel (T-320)."""

    type: DistributionType
    identifier: str
    format: str | None = None
    partitioning: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type.value,
            "identifier": self.identifier,
        }
        if self.format:
            result["format"] = self.format
        if self.partitioning:
            result["partitioning"] = self.partitioning
        return result


@dataclass
class Distribution:
    """
    Distribution configuration (T-320).

    Defines where and how data is distributed.
    """

    channels: list[DistributionChannel] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.channels:
            result["channels"] = [c.to_dict() for c in self.channels]
        return result


@dataclass
class GovernanceProducer:
    """Governance producer (T-321)."""

    team: str
    contact: str | None = None
    responsibilities: list[str] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"team": self.team}
        if self.contact:
            result["contact"] = self.contact
        if self.responsibilities:
            result["responsibilities"] = self.responsibilities
        return result


@dataclass
class GovernanceConsumer:
    """Governance consumer (T-321)."""

    team: str
    contact: str | None = None
    use_case: str | None = None
    approved_date: str | None = None  # ISO 8601 date
    approved_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"team": self.team}
        if self.contact:
            result["contact"] = self.contact
        if self.use_case:
            result["use_case"] = self.use_case
        if self.approved_date:
            result["approved_date"] = self.approved_date
        if self.approved_by:
            result["approved_by"] = self.approved_by
        return result


@dataclass
class ApprovalRecord:
    """Approval record (T-321)."""

    role: str
    approver: str | None = None
    approved_date: str | None = None  # ISO 8601 datetime
    comments: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"role": self.role}
        if self.approver:
            result["approver"] = self.approver
        if self.approved_date:
            result["approved_date"] = self.approved_date
        if self.comments:
            result["comments"] = self.comments
        return result


@dataclass
class ReviewConfig:
    """Review configuration (T-321)."""

    cadence: ReviewCadence | None = None
    last_review: str | None = None  # ISO 8601 date
    next_review: str | None = None  # ISO 8601 date
    reviewers: list[str] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cadence:
            result["cadence"] = self.cadence.value
        if self.last_review:
            result["last_review"] = self.last_review
        if self.next_review:
            result["next_review"] = self.next_review
        if self.reviewers:
            result["reviewers"] = self.reviewers
        return result


@dataclass
class ChangeManagement:
    """Change management configuration (T-322)."""

    breaking_change_notice: str | None = None  # ISO 8601 duration
    deprecation_notice: str | None = None  # ISO 8601 duration
    communication_channels: list[str] = dataclass_field(default_factory=list)
    migration_support: bool = False

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.breaking_change_notice:
            result["breaking_change_notice"] = self.breaking_change_notice
        if self.deprecation_notice:
            result["deprecation_notice"] = self.deprecation_notice
        if self.communication_channels:
            result["communication_channels"] = self.communication_channels
        if self.migration_support:
            result["migration_support"] = self.migration_support
        return result


@dataclass
class Governance:
    """
    Governance configuration (T-321, T-322).

    Defines ownership, consumers, approvals, and change management.
    """

    producer: GovernanceProducer | None = None
    consumers: list[GovernanceConsumer] = dataclass_field(default_factory=list)
    approval_chain: list[ApprovalRecord] = dataclass_field(default_factory=list)
    review: ReviewConfig | None = None
    change_management: ChangeManagement | None = None
    dispute_resolution: dict[str, Any] | None = None
    documentation: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.producer:
            result["producer"] = self.producer.to_dict()
        if self.consumers:
            result["consumers"] = [c.to_dict() for c in self.consumers]
        if self.approval_chain:
            result["approval_chain"] = [a.to_dict() for a in self.approval_chain]
        if self.review:
            result["review"] = self.review.to_dict()
        if self.change_management:
            result["change_management"] = self.change_management.to_dict()
        if self.dispute_resolution:
            result["dispute_resolution"] = self.dispute_resolution
        if self.documentation:
            result["documentation"] = self.documentation
        return result


@dataclass
class Steward:
    """Data steward (T-323)."""

    name: str
    email: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"name": self.name}
        if self.email:
            result["email"] = self.email
        return result


@dataclass
class Team:
    """
    Team metadata (T-323).

    Defines the accountable team for the contract.
    """

    name: str
    department: str | None = None
    steward: Steward | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"name": self.name}
        if self.department:
            result["department"] = self.department
        if self.steward:
            result["steward"] = self.steward.to_dict()
        return result


@dataclass
class Server:
    """
    Server configuration (T-324).

    Defines where the data is physically stored.
    """

    server: str
    environment: str  # development, staging, production
    type: str  # bigquery, redshift, snowflake, s3, kafka, etc.
    project: str
    dataset: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "server": self.server,
            "environment": self.environment,
            "type": self.type,
            "project": self.project,
            "dataset": self.dataset,
        }


@dataclass
class Role:
    """
    Role definition (T-325).

    Defines access roles for the contract.
    """

    role: str
    access: AccessLevel

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "access": self.access.value}


@dataclass
class Timestamps:
    """
    Contract timestamps (T-326).

    Tracks creation, updates, and effective dates.
    """

    created_at: str | None = None  # ISO 8601 datetime
    updated_at: str | None = None  # ISO 8601 datetime
    effective_from: str | None = None  # ISO 8601 date
    effective_until: str | None = None  # ISO 8601 date

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.created_at:
            result["created_at"] = self.created_at
        if self.updated_at:
            result["updated_at"] = self.updated_at
        if self.effective_from:
            result["effective_from"] = self.effective_from
        if self.effective_until:
            result["effective_until"] = self.effective_until
        return result
