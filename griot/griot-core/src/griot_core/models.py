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

from griot_core.types import AggregationType, DataType, FieldFormat

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
    """

    _griot_fields: ClassVar[dict[str, FieldInfo]] = {}
    _griot_field_names: ClassVar[tuple[str, ...]] = ()
    _griot_primary_key: ClassVar[str | None] = None

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
        """Export contract as a dictionary."""
        return {
            "name": cls.__name__,
            "description": cls.__doc__ or "",
            "fields": {
                name: info.to_dict() for name, info in cls._griot_fields.items()
            },
            "primary_key": cls._griot_primary_key,
        }

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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Hook for subclass creation."""
        super().__init_subclass__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} contract with {len(self._griot_fields)} fields>"
