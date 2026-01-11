"""
Griot Core Models

GriotModel base class and Field definition for data contracts.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from griot_core.types import (
    AggregationType,
    ContractStatus,
    DataRegion,
    DataType,
    FieldFormat,
    LegalBasis,
    LineageConfig,
    MaskingStrategy,
    PIICategory,
    ResidencyConfig,
    SensitivityLevel,
)

if TYPE_CHECKING:
    from griot_core.validation import ValidationResult

__all__ = [
    "Field",
    "FieldInfo",
    "GriotModel",
]

T = TypeVar("T")


@dataclass
class FieldInfo:
    """Detailed information about a field in a contract."""

    name: str
    type: DataType
    python_type: type
    description: str
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False

    # Constraints
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: FieldFormat | None = None
    ge: int | float | None = None
    le: int | float | None = None
    gt: int | float | None = None
    lt: int | float | None = None
    multiple_of: int | float | None = None
    enum: list[Any] | None = None

    # Default values
    default: Any = None
    has_default: bool = False
    default_factory: Callable[[], Any] | None = None

    # Semantic metadata
    unit: str | None = None
    aggregation: AggregationType | None = None
    glossary_term: str | None = None

    # PII/Privacy metadata (FR-SDK-008)
    pii_category: PIICategory | None = None
    sensitivity_level: SensitivityLevel | None = None
    masking_strategy: MaskingStrategy | None = None
    legal_basis: LegalBasis | None = None
    retention_days: int | None = None
    consent_required: bool = False

    @property
    def is_pii(self) -> bool:
        """Check if this field contains PII."""
        return self.pii_category is not None and self.pii_category != PIICategory.NONE

    @property
    def is_sensitive(self) -> bool:
        """Check if this field is classified as sensitive."""
        if self.sensitivity_level is None:
            return False
        return self.sensitivity_level >= SensitivityLevel.CONFIDENTIAL

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "nullable": self.nullable,
        }

        if self.primary_key:
            result["primary_key"] = True
        if self.unique:
            result["unique"] = True

        # Add constraints if set
        for constraint in [
            "min_length",
            "max_length",
            "pattern",
            "ge",
            "le",
            "gt",
            "lt",
            "multiple_of",
        ]:
            value = getattr(self, constraint)
            if value is not None:
                result[constraint] = value

        if self.format:
            result["format"] = self.format.value
        if self.enum:
            result["enum"] = self.enum
        if self.has_default:
            result["default"] = self.default
        if self.unit:
            result["unit"] = self.unit
        if self.aggregation:
            result["aggregation"] = self.aggregation.value
        if self.glossary_term:
            result["glossary_term"] = self.glossary_term

        # PII metadata
        if self.pii_category and self.pii_category != PIICategory.NONE:
            result["pii_category"] = self.pii_category.value
        if self.sensitivity_level:
            result["sensitivity_level"] = self.sensitivity_level.value
        if self.masking_strategy and self.masking_strategy != MaskingStrategy.NONE:
            result["masking_strategy"] = self.masking_strategy.value
        if self.legal_basis and self.legal_basis != LegalBasis.NONE:
            result["legal_basis"] = self.legal_basis.value
        if self.retention_days is not None:
            result["retention_days"] = self.retention_days
        if self.consent_required:
            result["consent_required"] = True

        return result

    def get_constraints(self) -> dict[str, Any]:
        """Return a dictionary of active constraints."""
        constraints: dict[str, Any] = {}
        constraint_attrs = [
            "min_length",
            "max_length",
            "pattern",
            "format",
            "ge",
            "le",
            "gt",
            "lt",
            "multiple_of",
            "enum",
            "unique",
        ]
        for attr in constraint_attrs:
            value = getattr(self, attr)
            if value is not None and value is not False:
                constraints[attr] = value
        return constraints


class Field:
    """
    Define a field with type, constraints, and metadata.

    Used as default values in GriotModel subclasses to specify
    field constraints and documentation.

    Example:
        class Customer(GriotModel):
            customer_id: str = Field(
                description="Unique customer identifier",
                primary_key=True,
                pattern=r"^CUST-\\d{6}$"
            )
            email: str = Field(
                description="Customer email address",
                format="email",
                max_length=255
            )
    """

    __slots__ = (
        "description",
        "default",
        "default_factory",
        "min_length",
        "max_length",
        "pattern",
        "format",
        "ge",
        "le",
        "gt",
        "lt",
        "multiple_of",
        "enum",
        "unique",
        "primary_key",
        "nullable",
        "unit",
        "aggregation",
        "glossary_term",
        # PII/Privacy metadata
        "pii_category",
        "sensitivity_level",
        "masking_strategy",
        "legal_basis",
        "retention_days",
        "consent_required",
        "_name",
        "_has_default",
    )

    def __init__(
        self,
        description: str,
        *,
        default: Any = ...,
        default_factory: Callable[[], Any] | None = None,
        # String constraints
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        format: FieldFormat | str | None = None,
        # Numeric constraints
        ge: int | float | None = None,
        le: int | float | None = None,
        gt: int | float | None = None,
        lt: int | float | None = None,
        multiple_of: int | float | None = None,
        # Other constraints
        enum: list[Any] | None = None,
        unique: bool = False,
        primary_key: bool = False,
        nullable: bool = False,
        # Semantic metadata
        unit: str | None = None,
        aggregation: AggregationType | str | None = None,
        glossary_term: str | None = None,
        # PII/Privacy metadata (FR-SDK-008)
        pii_category: PIICategory | str | None = None,
        sensitivity_level: SensitivityLevel | str | None = None,
        masking_strategy: MaskingStrategy | str | None = None,
        legal_basis: LegalBasis | str | None = None,
        retention_days: int | None = None,
        consent_required: bool = False,
    ) -> None:
        self.description = description
        self.default = default
        self.default_factory = default_factory
        self._has_default = default is not ...
        self._name: str | None = None

        # String constraints
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.format = (
            FieldFormat(format) if isinstance(format, str) else format
        )

        # Numeric constraints
        self.ge = ge
        self.le = le
        self.gt = gt
        self.lt = lt
        self.multiple_of = multiple_of

        # Other constraints
        self.enum = enum
        self.unique = unique
        self.primary_key = primary_key
        self.nullable = nullable

        # Semantic metadata
        self.unit = unit
        self.aggregation = (
            AggregationType(aggregation)
            if isinstance(aggregation, str)
            else aggregation
        )
        self.glossary_term = glossary_term

        # PII/Privacy metadata
        self.pii_category = (
            PIICategory(pii_category)
            if isinstance(pii_category, str)
            else pii_category
        )
        self.sensitivity_level = (
            SensitivityLevel(sensitivity_level)
            if isinstance(sensitivity_level, str)
            else sensitivity_level
        )
        self.masking_strategy = (
            MaskingStrategy(masking_strategy)
            if isinstance(masking_strategy, str)
            else masking_strategy
        )
        self.legal_basis = (
            LegalBasis(legal_basis)
            if isinstance(legal_basis, str)
            else legal_basis
        )
        self.retention_days = retention_days
        self.consent_required = consent_required

        # Validate constraint combinations
        self._validate_constraints()

    def _validate_constraints(self) -> None:
        """Validate that constraint combinations are sensible."""
        # Check pattern is valid regex
        if self.pattern is not None:
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}") from e

        # Check numeric ranges
        if self.ge is not None and self.gt is not None:
            raise ValueError("Cannot specify both 'ge' and 'gt'")
        if self.le is not None and self.lt is not None:
            raise ValueError("Cannot specify both 'le' and 'lt'")

        # Check range validity
        lower = self.ge if self.ge is not None else self.gt
        upper = self.le if self.le is not None else self.lt
        if lower is not None and upper is not None:
            if lower > upper:
                raise ValueError(
                    f"Invalid range: lower bound ({lower}) > upper bound ({upper})"
                )

        # Check length constraints
        if (
            self.min_length is not None
            and self.max_length is not None
            and self.min_length > self.max_length
        ):
            raise ValueError(
                f"min_length ({self.min_length}) > max_length ({self.max_length})"
            )

        # Check default and default_factory aren't both set
        if self._has_default and self.default_factory is not None:
            raise ValueError("Cannot specify both 'default' and 'default_factory'")

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when the Field is assigned as a class attribute."""
        self._name = name

    def get_default(self) -> Any:
        """Return the default value for this field."""
        if self.default_factory is not None:
            return self.default_factory()
        if self._has_default:
            return self.default
        return None

    def has_default(self) -> bool:
        """Check if this field has a default value."""
        return self._has_default or self.default_factory is not None

    def to_field_info(self, name: str, python_type: type) -> FieldInfo:
        """Convert this Field to a FieldInfo instance."""
        return FieldInfo(
            name=name,
            type=DataType.from_python_type(python_type),
            python_type=python_type,
            description=self.description,
            nullable=self.nullable,
            primary_key=self.primary_key,
            unique=self.unique,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            format=self.format,
            ge=self.ge,
            le=self.le,
            gt=self.gt,
            lt=self.lt,
            multiple_of=self.multiple_of,
            enum=self.enum,
            default=self.default if self._has_default else None,
            has_default=self._has_default,
            default_factory=self.default_factory,
            unit=self.unit,
            aggregation=self.aggregation,
            glossary_term=self.glossary_term,
            # PII/Privacy metadata
            pii_category=self.pii_category,
            sensitivity_level=self.sensitivity_level,
            masking_strategy=self.masking_strategy,
            legal_basis=self.legal_basis,
            retention_days=self.retention_days,
            consent_required=self.consent_required,
        )

    def __repr__(self) -> str:
        parts = [f"description={self.description!r}"]
        if self.primary_key:
            parts.append("primary_key=True")
        if self.nullable:
            parts.append("nullable=True")
        if self.pattern:
            parts.append(f"pattern={self.pattern!r}")
        if self.format:
            parts.append(f"format={self.format.value!r}")
        return f"Field({', '.join(parts)})"


class GriotModelMeta(type):
    """Metaclass for GriotModel that processes field definitions."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> GriotModelMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip processing for the base GriotModel class
        if name == "GriotModel" and not bases:
            return cls

        # Collect fields from this class and all parent classes
        fields: dict[str, FieldInfo] = {}

        # Inherit fields from parent classes
        for base in reversed(bases):
            if hasattr(base, "_griot_fields"):
                fields.update(base._griot_fields)

        # Get type hints for this class
        try:
            hints = get_type_hints(cls)
        except Exception:
            hints = getattr(cls, "__annotations__", {})

        # Process fields defined in this class
        for field_name, field_type in hints.items():
            if field_name.startswith("_"):
                continue

            # Get the Field descriptor if it exists
            field_def = namespace.get(field_name)

            if isinstance(field_def, Field):
                # Convert Field to FieldInfo
                python_type = _extract_base_type(field_type)
                field_info = field_def.to_field_info(field_name, python_type)
                fields[field_name] = field_info
            elif field_def is None or not isinstance(field_def, (classmethod, staticmethod, property)):
                # Create a default FieldInfo for annotated fields without Field()
                if field_name not in fields:
                    python_type = _extract_base_type(field_type)
                    fields[field_name] = FieldInfo(
                        name=field_name,
                        type=DataType.from_python_type(python_type),
                        python_type=python_type,
                        description=f"Field: {field_name}",
                        nullable=_is_optional(field_type),
                        has_default=field_def is not None,
                        default=field_def,
                    )

        # Store fields on the class
        cls._griot_fields = fields
        cls._griot_field_names = tuple(fields.keys())

        # Find primary key
        cls._griot_primary_key = None
        for fname, finfo in fields.items():
            if finfo.primary_key:
                cls._griot_primary_key = fname
                break

        return cls


def _extract_base_type(type_hint: Any) -> type:
    """Extract the base type from a type hint (handling Optional, Union, etc.)."""
    origin = getattr(type_hint, "__origin__", None)

    if origin is Union:
        # Get non-None types from Union
        args = getattr(type_hint, "__args__", ())
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _extract_base_type(non_none[0])
        return type(None)

    if origin is not None:
        # For generic types like List[str], return the origin (list)
        return origin

    if isinstance(type_hint, type):
        return type_hint

    # For string annotations or other cases
    return object


def _is_optional(type_hint: Any) -> bool:
    """Check if a type hint is Optional (Union with None)."""
    origin = getattr(type_hint, "__origin__", None)
    if origin is Union:
        args = getattr(type_hint, "__args__", ())
        return type(None) in args
    return False


class GriotModel(metaclass=GriotModelMeta):
    """
    Base class for defining data contracts.

    Subclass this to create contracts with typed fields and validation rules.

    Example:
        class Customer(GriotModel):
            customer_id: str = Field(
                description="Unique customer identifier",
                primary_key=True,
                pattern=r"^CUST-\\d{6}$"
            )
            email: str = Field(
                description="Customer email address",
                format="email"
            )
            age: int = Field(
                description="Customer age in years",
                ge=0,
                le=150,
                unit="years"
            )

        # Validate data
        result = Customer.validate(data)
        if not result.passed:
            for error in result.errors:
                print(f"{error.field}: {error.message}")

    Contract-Level Metadata (T-310 - ODCS):
        Contracts can have the following metadata attributes:
        - _griot_api_version: API schema version (default: "v1.0.0")
        - _griot_kind: Always "DataContract"
        - _griot_id: Unique contract identifier
        - _griot_version: Semantic version (MAJOR.MINOR.PATCH)
        - _griot_status: Contract lifecycle status (draft/active/deprecated/retired)
    """

    # Field metadata
    _griot_fields: ClassVar[dict[str, FieldInfo]] = {}
    _griot_field_names: ClassVar[tuple[str, ...]] = ()
    _griot_primary_key: ClassVar[str | None] = None

    # Phase 6 - Contract-level metadata (T-310 - ODCS)
    _griot_api_version: ClassVar[str] = "v1.0.0"
    _griot_kind: ClassVar[str] = "DataContract"
    _griot_id: ClassVar[str | None] = None
    _griot_version: ClassVar[str] = "1.0.0"
    _griot_status: ClassVar[ContractStatus] = ContractStatus.DRAFT

    # Configuration (Phase 2)
    _griot_residency_config: ClassVar[ResidencyConfig | None] = None
    _griot_lineage_config: ClassVar[LineageConfig | None] = None

    # Phase 6 - ODCS Section Composition (T-327)
    _griot_description: ClassVar[Any | None] = None  # Description dataclass
    _griot_quality_rules: ClassVar[list[Any]] = []  # List of QualityRule
    _griot_custom_checks: ClassVar[list[Any]] = []  # List of CustomCheck
    _griot_legal: ClassVar[Any | None] = None  # Legal dataclass
    _griot_compliance: ClassVar[Any | None] = None  # Compliance dataclass
    _griot_sla: ClassVar[Any | None] = None  # SLA dataclass
    _griot_access: ClassVar[Any | None] = None  # AccessConfig dataclass
    _griot_distribution: ClassVar[Any | None] = None  # Distribution dataclass
    _griot_governance: ClassVar[Any | None] = None  # Governance dataclass
    _griot_team: ClassVar[Any | None] = None  # Team dataclass
    _griot_servers: ClassVar[list[Any]] = []  # List of Server
    _griot_roles: ClassVar[list[Any]] = []  # List of Role
    _griot_timestamps: ClassVar[Any | None] = None  # Timestamps dataclass

    # =========================================================================
    # Contract-Level Metadata Accessors (T-310 - ODCS)
    # =========================================================================

    @classmethod
    def get_api_version(cls) -> str:
        """Get the contract API schema version."""
        return cls._griot_api_version

    @classmethod
    def get_kind(cls) -> str:
        """Get the contract kind (always 'DataContract')."""
        return cls._griot_kind

    @classmethod
    def get_id(cls) -> str | None:
        """Get the unique contract identifier."""
        return cls._griot_id

    @classmethod
    def set_id(cls, contract_id: str) -> None:
        """Set the unique contract identifier."""
        cls._griot_id = contract_id

    @classmethod
    def get_version(cls) -> str:
        """Get the contract semantic version."""
        return cls._griot_version

    @classmethod
    def set_version(cls, version: str) -> None:
        """Set the contract semantic version."""
        cls._griot_version = version

    @classmethod
    def get_status(cls) -> ContractStatus:
        """Get the contract lifecycle status."""
        return cls._griot_status

    @classmethod
    def set_status(cls, status: ContractStatus | str) -> None:
        """Set the contract lifecycle status."""
        if isinstance(status, str):
            status = ContractStatus(status)
        cls._griot_status = status

    @classmethod
    def get_contract_metadata(cls) -> dict[str, Any]:
        """
        Get all contract-level metadata as a dictionary.

        Returns:
            Dictionary containing api_version, kind, id, version, status.
        """
        return {
            "api_version": cls._griot_api_version,
            "kind": cls._griot_kind,
            "id": cls._griot_id,
            "name": cls.__name__,
            "version": cls._griot_version,
            "status": cls._griot_status.value,
        }

    # =========================================================================
    # ODCS Section Accessors (T-327)
    # =========================================================================

    @classmethod
    def get_description(cls) -> Any | None:
        """Get the contract description section."""
        return cls._griot_description

    @classmethod
    def set_description(cls, description: Any) -> None:
        """Set the contract description section."""
        cls._griot_description = description

    @classmethod
    def get_quality_rules(cls) -> list[Any]:
        """Get the list of quality rules."""
        return cls._griot_quality_rules

    @classmethod
    def set_quality_rules(cls, rules: list[Any]) -> None:
        """Set the list of quality rules."""
        cls._griot_quality_rules = rules

    @classmethod
    def add_quality_rule(cls, rule: Any) -> None:
        """Add a quality rule."""
        cls._griot_quality_rules.append(rule)

    @classmethod
    def get_custom_checks(cls) -> list[Any]:
        """Get the list of custom checks."""
        return cls._griot_custom_checks

    @classmethod
    def set_custom_checks(cls, checks: list[Any]) -> None:
        """Set the list of custom checks."""
        cls._griot_custom_checks = checks

    @classmethod
    def add_custom_check(cls, check: Any) -> None:
        """Add a custom check."""
        cls._griot_custom_checks.append(check)

    @classmethod
    def get_legal(cls) -> Any | None:
        """Get the legal section."""
        return cls._griot_legal

    @classmethod
    def set_legal(cls, legal: Any) -> None:
        """Set the legal section."""
        cls._griot_legal = legal

    @classmethod
    def get_compliance(cls) -> Any | None:
        """Get the compliance section."""
        return cls._griot_compliance

    @classmethod
    def set_compliance(cls, compliance: Any) -> None:
        """Set the compliance section."""
        cls._griot_compliance = compliance

    @classmethod
    def get_sla(cls) -> Any | None:
        """Get the SLA section."""
        return cls._griot_sla

    @classmethod
    def set_sla(cls, sla: Any) -> None:
        """Set the SLA section."""
        cls._griot_sla = sla

    @classmethod
    def get_access(cls) -> Any | None:
        """Get the access configuration section."""
        return cls._griot_access

    @classmethod
    def set_access(cls, access: Any) -> None:
        """Set the access configuration section."""
        cls._griot_access = access

    @classmethod
    def get_distribution(cls) -> Any | None:
        """Get the distribution section."""
        return cls._griot_distribution

    @classmethod
    def set_distribution(cls, distribution: Any) -> None:
        """Set the distribution section."""
        cls._griot_distribution = distribution

    @classmethod
    def get_governance(cls) -> Any | None:
        """Get the governance section."""
        return cls._griot_governance

    @classmethod
    def set_governance(cls, governance: Any) -> None:
        """Set the governance section."""
        cls._griot_governance = governance

    @classmethod
    def get_team(cls) -> Any | None:
        """Get the team section."""
        return cls._griot_team

    @classmethod
    def set_team(cls, team: Any) -> None:
        """Set the team section."""
        cls._griot_team = team

    @classmethod
    def get_servers(cls) -> list[Any]:
        """Get the list of servers."""
        return cls._griot_servers

    @classmethod
    def set_servers(cls, servers: list[Any]) -> None:
        """Set the list of servers."""
        cls._griot_servers = servers

    @classmethod
    def add_server(cls, server: Any) -> None:
        """Add a server configuration."""
        cls._griot_servers.append(server)

    @classmethod
    def get_roles(cls) -> list[Any]:
        """Get the list of roles."""
        return cls._griot_roles

    @classmethod
    def set_roles(cls, roles: list[Any]) -> None:
        """Set the list of roles."""
        cls._griot_roles = roles

    @classmethod
    def add_role(cls, role: Any) -> None:
        """Add a role definition."""
        cls._griot_roles.append(role)

    @classmethod
    def get_timestamps(cls) -> Any | None:
        """Get the timestamps section."""
        return cls._griot_timestamps

    @classmethod
    def set_timestamps(cls, timestamps: Any) -> None:
        """Set the timestamps section."""
        cls._griot_timestamps = timestamps

    @classmethod
    def get_odcs_sections(cls) -> dict[str, Any]:
        """
        Get all ODCS sections as a dictionary.

        Returns:
            Dictionary containing all ODCS sections with their values.
        """
        sections: dict[str, Any] = {}

        if cls._griot_description:
            sections["description"] = cls._griot_description.to_dict()
        if cls._griot_quality_rules:
            sections["quality"] = [r.to_dict() for r in cls._griot_quality_rules]
        if cls._griot_custom_checks:
            sections["custom_checks"] = [c.to_dict() for c in cls._griot_custom_checks]
        if cls._griot_legal:
            sections["legal"] = cls._griot_legal.to_dict()
        if cls._griot_compliance:
            sections["compliance"] = cls._griot_compliance.to_dict()
        if cls._griot_sla:
            sections["sla"] = cls._griot_sla.to_dict()
        if cls._griot_access:
            sections["access"] = cls._griot_access.to_dict()
        if cls._griot_distribution:
            sections["distribution"] = cls._griot_distribution.to_dict()
        if cls._griot_governance:
            sections["governance"] = cls._griot_governance.to_dict()
        if cls._griot_team:
            sections["team"] = cls._griot_team.to_dict()
        if cls._griot_servers:
            sections["servers"] = [s.to_dict() for s in cls._griot_servers]
        if cls._griot_roles:
            sections["roles"] = [r.to_dict() for r in cls._griot_roles]
        if cls._griot_timestamps:
            sections["timestamps"] = cls._griot_timestamps.to_dict()

        return sections

    # =========================================================================
    # Field Accessors
    # =========================================================================

    @classmethod
    def list_fields(cls) -> list[FieldInfo]:
        """List all fields with their metadata."""
        return list(cls._griot_fields.values())

    @classmethod
    def get_field(cls, name: str) -> FieldInfo | None:
        """Get field metadata by name."""
        return cls._griot_fields.get(name)

    @classmethod
    def get_primary_key(cls) -> str | None:
        """Get the primary key field name."""
        return cls._griot_primary_key

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        """Get tuple of all field names."""
        return cls._griot_field_names

    @classmethod
    def validate(
        cls,
        data: list[dict[str, Any]] | dict[str, Any],
    ) -> ValidationResult:
        """
        Validate data against this contract.

        Args:
            data: Either a single row (dict) or multiple rows (list of dicts).
                  Can also accept DataFrame-like objects with to_dict() method.

        Returns:
            ValidationResult containing pass/fail status and any errors.
        """
        # Import here to avoid circular imports
        from griot_core.validation import validate_data

        return validate_data(cls, data)

    @classmethod
    def validate_row(cls, row: dict[str, Any]) -> list:
        """
        Validate a single row of data.

        Args:
            row: Dictionary representing one data row.

        Returns:
            List of FieldValidationError for any validation failures.
        """
        from griot_core.validation import validate_single_row

        return validate_single_row(cls, row)

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """
        Export contract as a dictionary in registry-compatible format.

        Returns fields as a list with nested constraints/metadata structure
        matching the registry API schema.
        """
        from griot_core.contract import model_to_dict

        return model_to_dict(cls)

    @classmethod
    def to_yaml(cls) -> str:
        """Export contract as YAML string."""
        # Import here to avoid circular dependency
        from griot_core.contract import model_to_yaml

        return model_to_yaml(cls)

    @classmethod
    def to_yaml_file(cls, path: str) -> None:
        """Write contract to YAML file."""
        from pathlib import Path

        yaml_content = cls.to_yaml()
        Path(path).write_text(yaml_content, encoding="utf-8")

    @classmethod
    def from_yaml(cls, path: str) -> type[GriotModel]:
        """Load contract definition from YAML file."""
        from griot_core.contract import load_contract

        return load_contract(path)

    @classmethod
    def from_yaml_string(cls, content: str) -> type[GriotModel]:
        """Load contract from YAML string."""
        from griot_core.contract import load_contract_from_string

        return load_contract_from_string(content)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> type[GriotModel]:
        """Load contract from dictionary."""
        from griot_core.contract import load_contract_from_dict

        return load_contract_from_dict(data)

    @classmethod
    def mock(cls, rows: int = 100, seed: int | None = None) -> list[dict[str, Any]]:
        """
        Generate synthetic data conforming to this contract.

        Args:
            rows: Number of rows to generate.
            seed: Random seed for reproducibility.

        Returns:
            List of dictionaries containing mock data.
        """
        from griot_core.mock import generate_mock_data

        return generate_mock_data(cls, rows=rows, seed=seed)

    @classmethod
    def diff(cls, other: type[GriotModel]) -> Any:
        """
        Compare with another contract version.

        Args:
            other: Another GriotModel class to compare against.

        Returns:
            ContractDiff object describing the differences.
        """
        from griot_core.contract import diff_contracts

        return diff_contracts(cls, other)

    @classmethod
    def lint(cls) -> list:
        """
        Check contract for quality issues.

        Returns:
            List of LintIssue objects describing any problems.
        """
        from griot_core.contract import lint_contract

        return lint_contract(cls)

    @classmethod
    def to_manifest(
        cls,
        format: str = "json_ld",
    ) -> str:
        """
        Export metadata for AI/LLM consumption.

        Args:
            format: Output format - 'json_ld', 'markdown', or 'llm_context'.

        Returns:
            String representation in the requested format.
        """
        from griot_core.manifest import export_manifest

        return export_manifest(cls, format=format)

    @classmethod
    def pii_inventory(cls) -> list[FieldInfo]:
        """
        List all fields containing PII.

        Returns a list of FieldInfo objects for all fields that have been
        marked with a pii_category (other than NONE).

        Returns:
            List of FieldInfo objects for PII fields.

        Example:
            class Customer(GriotModel):
                email: str = Field(
                    description="Email",
                    pii_category="email",
                    sensitivity_level="confidential"
                )
                name: str = Field(description="Name")

            pii_fields = Customer.pii_inventory()
            # Returns [FieldInfo(name='email', ...)]
        """
        return [f for f in cls._griot_fields.values() if f.is_pii]

    @classmethod
    def sensitive_fields(cls) -> list[FieldInfo]:
        """
        List all fields classified as sensitive (confidential or higher).

        Returns:
            List of FieldInfo objects for sensitive fields.
        """
        return [f for f in cls._griot_fields.values() if f.is_sensitive]

    @classmethod
    def pii_summary(cls) -> dict[str, Any]:
        """
        Generate a summary of PII data in this contract.

        Returns a dictionary with statistics about PII fields including
        counts by category, sensitivity levels, and masking strategies.

        Returns:
            Dictionary with PII statistics.
        """
        pii_fields = cls.pii_inventory()

        # Count by category
        categories: dict[str, int] = {}
        for field in pii_fields:
            if field.pii_category:
                cat = field.pii_category.value
                categories[cat] = categories.get(cat, 0) + 1

        # Count by sensitivity level
        sensitivity_levels: dict[str, int] = {}
        for field in cls._griot_fields.values():
            if field.sensitivity_level:
                level = field.sensitivity_level.value
                sensitivity_levels[level] = sensitivity_levels.get(level, 0) + 1

        # Count by masking strategy
        masking_strategies: dict[str, int] = {}
        for field in pii_fields:
            if field.masking_strategy:
                strategy = field.masking_strategy.value
                masking_strategies[strategy] = masking_strategies.get(strategy, 0) + 1

        # Fields requiring consent
        consent_required = [f.name for f in pii_fields if f.consent_required]

        # Retention periods
        retention_periods = {
            f.name: f.retention_days
            for f in pii_fields
            if f.retention_days is not None
        }

        return {
            "total_fields": len(cls._griot_fields),
            "pii_field_count": len(pii_fields),
            "pii_fields": [f.name for f in pii_fields],
            "categories": categories,
            "sensitivity_levels": sensitivity_levels,
            "masking_strategies": masking_strategies,
            "consent_required": consent_required,
            "retention_periods": retention_periods,
        }

    # =========================================================================
    # Data Residency Methods (FR-SDK-011)
    # =========================================================================

    @classmethod
    def set_residency_config(cls, config: ResidencyConfig) -> None:
        """
        Set the data residency configuration for this contract.

        Args:
            config: ResidencyConfig with rules for geographic data storage.

        Example:
            from griot_core.types import ResidencyConfig, ResidencyRule, DataRegion

            Customer.set_residency_config(ResidencyConfig(
                default_rule=ResidencyRule(allowed_regions=[DataRegion.EU]),
                compliance_frameworks=["GDPR"],
            ))
        """
        cls._griot_residency_config = config

    @classmethod
    def get_residency_config(cls) -> ResidencyConfig | None:
        """Get the current residency configuration."""
        return cls._griot_residency_config

    @classmethod
    def check_residency(
        cls,
        region: DataRegion | str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Check if data can be stored in a given region.

        Args:
            region: The target region for data storage.
            fields: Optional list of specific fields to check.
                    If None, checks all fields.

        Returns:
            Dictionary with compliance status and any violations.

        Example:
            result = Customer.check_residency(DataRegion.US)
            if not result["compliant"]:
                for violation in result["violations"]:
                    print(f"{violation['field']}: {violation['reason']}")
        """
        if cls._griot_residency_config is None:
            return {
                "compliant": True,
                "region": region.value if isinstance(region, DataRegion) else region,
                "violations": [],
                "warnings": ["No residency configuration set"],
            }

        # Convert string to enum if needed
        if isinstance(region, str):
            region = DataRegion(region)

        # Determine fields to check
        fields_to_check = fields or list(cls._griot_fields.keys())

        violations = []
        for field_name in fields_to_check:
            if field_name not in cls._griot_fields:
                continue

            is_compliant, error = cls._griot_residency_config.check_residency(
                field_name, region
            )
            if not is_compliant:
                violations.append({
                    "field": field_name,
                    "reason": error,
                })

        return {
            "compliant": len(violations) == 0,
            "region": region.value,
            "fields_checked": fields_to_check,
            "violations": violations,
            "config": cls._griot_residency_config.to_dict() if violations else None,
        }

    @classmethod
    def get_allowed_regions(cls) -> list[DataRegion]:
        """
        Get all regions where this contract's data can be stored.

        Returns:
            List of DataRegion values where all fields can be stored.
        """
        if cls._griot_residency_config is None:
            # No restrictions
            return list(DataRegion)

        config = cls._griot_residency_config
        allowed = []

        for region in DataRegion:
            result = cls.check_residency(region)
            if result["compliant"]:
                allowed.append(region)

        return allowed

    # =========================================================================
    # Data Lineage Methods (FR-SDK-012)
    # =========================================================================

    @classmethod
    def set_lineage_config(cls, config: LineageConfig) -> None:
        """
        Set the data lineage configuration for this contract.

        Args:
            config: LineageConfig with source, transformation, and consumer info.

        Example:
            from griot_core.types import LineageConfig, Source, Consumer

            Customer.set_lineage_config(LineageConfig(
                sources=[Source(name="crm", type="database", system="salesforce")],
                data_owner="Data Team",
            ))
        """
        cls._griot_lineage_config = config

    @classmethod
    def get_lineage_config(cls) -> LineageConfig | None:
        """Get the current lineage configuration."""
        return cls._griot_lineage_config

    @classmethod
    def get_field_lineage(cls, field_name: str) -> dict[str, Any]:
        """
        Get lineage information for a specific field.

        Args:
            field_name: Name of the field to trace.

        Returns:
            Dictionary with source, transformations, and consumers for the field.
        """
        if cls._griot_lineage_config is None:
            return {
                "field": field_name,
                "source": None,
                "transformations": [],
                "consumers": [],
            }

        return cls._griot_lineage_config.get_field_lineage(field_name)

    @classmethod
    def lineage_summary(cls) -> dict[str, Any]:
        """
        Get a summary of data lineage for this contract.

        Returns:
            Dictionary with lineage statistics and information.
        """
        if cls._griot_lineage_config is None:
            return {
                "sources": [],
                "transformations": [],
                "consumers": [],
                "data_owner": None,
                "data_steward": None,
            }

        config = cls._griot_lineage_config
        return {
            "sources": [s.name for s in config.sources],
            "transformations": [t.name for t in config.transformations],
            "consumers": [c.name for c in config.consumers],
            "data_owner": config.data_owner,
            "data_steward": config.data_steward,
            "technical_owner": config.technical_owner,
            "fields_with_lineage": list(config.field_sources.keys()),
        }

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Hook for subclass creation."""
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} contract with {len(self._griot_fields)} fields>"
