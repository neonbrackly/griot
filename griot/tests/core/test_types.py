"""
Tests for griot_core.types module.

Tests all enum definitions and type conversion functions.
"""
from __future__ import annotations

import pytest

from griot_core.types import (
    AggregationType,
    ConstraintType,
    DataType,
    FieldFormat,
    Severity,
)


class TestConstraintType:
    """Tests for ConstraintType enum."""

    def test_all_constraint_types_exist(self) -> None:
        """Verify all expected constraint types are defined."""
        expected = {
            "MIN_LENGTH",
            "MAX_LENGTH",
            "PATTERN",
            "FORMAT",
            "GE",
            "LE",
            "GT",
            "LT",
            "MULTIPLE_OF",
            "ENUM",
            "UNIQUE",
        }
        actual = {c.name for c in ConstraintType}
        assert actual == expected

    def test_constraint_type_values(self) -> None:
        """Verify constraint type string values."""
        assert ConstraintType.MIN_LENGTH.value == "min_length"
        assert ConstraintType.MAX_LENGTH.value == "max_length"
        assert ConstraintType.PATTERN.value == "pattern"
        assert ConstraintType.GE.value == "ge"
        assert ConstraintType.LE.value == "le"

    def test_constraint_type_is_string_enum(self) -> None:
        """Verify ConstraintType is a string enum for serialization."""
        assert isinstance(ConstraintType.MIN_LENGTH.value, str)
        # String enum value is accessed via .value
        assert ConstraintType.MIN_LENGTH.value == "min_length"


class TestSeverity:
    """Tests for Severity enum."""

    def test_all_severities_exist(self) -> None:
        """Verify all expected severity levels are defined."""
        expected = {"ERROR", "WARNING", "INFO"}
        actual = {s.name for s in Severity}
        assert actual == expected

    def test_severity_values(self) -> None:
        """Verify severity string values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

    def test_severity_is_string_enum(self) -> None:
        """Verify Severity is a string enum."""
        assert isinstance(Severity.ERROR.value, str)


class TestFieldFormat:
    """Tests for FieldFormat enum."""

    def test_all_formats_exist(self) -> None:
        """Verify all expected field formats are defined."""
        expected = {
            "EMAIL",
            "URI",
            "UUID",
            "DATE",
            "DATETIME",
            "IPV4",
            "IPV6",
            "HOSTNAME",
        }
        actual = {f.name for f in FieldFormat}
        assert actual == expected

    def test_format_values(self) -> None:
        """Verify format string values."""
        assert FieldFormat.EMAIL.value == "email"
        assert FieldFormat.URI.value == "uri"
        assert FieldFormat.UUID.value == "uuid"
        assert FieldFormat.DATE.value == "date"
        assert FieldFormat.DATETIME.value == "datetime"
        assert FieldFormat.IPV4.value == "ipv4"

    def test_format_from_string(self) -> None:
        """Test creating FieldFormat from string value."""
        assert FieldFormat("email") == FieldFormat.EMAIL
        assert FieldFormat("uri") == FieldFormat.URI


class TestAggregationType:
    """Tests for AggregationType enum."""

    def test_all_aggregations_exist(self) -> None:
        """Verify all expected aggregation types are defined."""
        expected = {"SUM", "AVG", "COUNT", "MIN", "MAX", "NONE"}
        actual = {a.name for a in AggregationType}
        assert actual == expected

    def test_aggregation_values(self) -> None:
        """Verify aggregation string values."""
        assert AggregationType.SUM.value == "sum"
        assert AggregationType.AVG.value == "avg"
        assert AggregationType.COUNT.value == "count"
        assert AggregationType.NONE.value == "none"


class TestDataType:
    """Tests for DataType enum."""

    def test_all_data_types_exist(self) -> None:
        """Verify all expected data types are defined."""
        expected = {
            "STRING",
            "INTEGER",
            "FLOAT",
            "BOOLEAN",
            "DATE",
            "DATETIME",
            "ARRAY",
            "OBJECT",
            "ANY",
        }
        actual = {d.name for d in DataType}
        assert actual == expected

    def test_data_type_values(self) -> None:
        """Verify data type string values."""
        assert DataType.STRING.value == "string"
        assert DataType.INTEGER.value == "integer"
        assert DataType.FLOAT.value == "float"
        assert DataType.BOOLEAN.value == "boolean"

    def test_from_python_type_basic(self) -> None:
        """Test converting Python types to DataType."""
        assert DataType.from_python_type(str) == DataType.STRING
        assert DataType.from_python_type(int) == DataType.INTEGER
        assert DataType.from_python_type(float) == DataType.FLOAT
        assert DataType.from_python_type(bool) == DataType.BOOLEAN
        assert DataType.from_python_type(list) == DataType.ARRAY
        assert DataType.from_python_type(dict) == DataType.OBJECT

    def test_from_python_type_string_names(self) -> None:
        """Test converting string type names to DataType."""
        assert DataType.from_python_type("str") == DataType.STRING
        assert DataType.from_python_type("int") == DataType.INTEGER
        assert DataType.from_python_type("float") == DataType.FLOAT
        assert DataType.from_python_type("bool") == DataType.BOOLEAN
        assert DataType.from_python_type("list") == DataType.ARRAY
        assert DataType.from_python_type("dict") == DataType.OBJECT

    def test_from_python_type_unknown(self) -> None:
        """Test that unknown types map to ANY."""
        assert DataType.from_python_type(complex) == DataType.ANY
        assert DataType.from_python_type("unknown") == DataType.ANY

    def test_to_python_type(self) -> None:
        """Test converting DataType back to Python types."""
        assert DataType.STRING.to_python_type() == str
        assert DataType.INTEGER.to_python_type() == int
        assert DataType.FLOAT.to_python_type() == float
        assert DataType.BOOLEAN.to_python_type() == bool
        assert DataType.ARRAY.to_python_type() == list
        assert DataType.OBJECT.to_python_type() == dict
        assert DataType.ANY.to_python_type() == object

    def test_roundtrip_type_conversion(self) -> None:
        """Test that type conversion is consistent."""
        for python_type in [str, int, float, bool, list, dict]:
            data_type = DataType.from_python_type(python_type)
            assert data_type.to_python_type() == python_type
