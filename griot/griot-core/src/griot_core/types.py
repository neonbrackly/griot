"""
Griot Core Type Definitions

Enums and type definitions for the Griot data contract system.
All types use Python stdlib only (no external dependencies).
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, TypeVar, Union

__all__ = [
    "ConstraintType",
    "Severity",
    "FieldFormat",
    "AggregationType",
    "DataType",
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
