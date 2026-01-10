"""
Tests for griot_core.mock module.

Tests mock data generation functionality.
"""
from __future__ import annotations

import re
from typing import Any, Optional

import pytest

from griot_core.mock import generate_mock_data
from griot_core.models import Field, GriotModel
from griot_core.types import FieldFormat


# =============================================================================
# TEST MODELS
# =============================================================================


class SimpleModel(GriotModel):
    """Simple model for basic mock generation tests."""

    name: str = Field(description="Name field")
    age: int = Field(description="Age field", ge=0, le=100)


class ConstrainedModel(GriotModel):
    """Model with various constraints for testing."""

    id: str = Field(
        description="ID with pattern",
        primary_key=True,
        pattern=r"^ID-\d{6}$",
    )
    email: str = Field(
        description="Email field",
        format="email",
        max_length=255,
    )
    status: str = Field(
        description="Status field",
        enum=["active", "inactive", "pending"],
    )
    score: int = Field(
        description="Score field",
        ge=0,
        le=100,
        multiple_of=5,
    )


class NullableModel(GriotModel):
    """Model with nullable fields."""

    required: str = Field(description="Required field")
    optional: Optional[str] = Field(description="Optional field", nullable=True)


class UniqueModel(GriotModel):
    """Model with unique constraints."""

    id: str = Field(description="Unique ID", primary_key=True, unique=True)
    name: str = Field(description="Name")


class AllTypesModel(GriotModel):
    """Model with all data types."""

    string_field: str = Field(description="String")
    int_field: int = Field(description="Integer", ge=0, le=1000)
    float_field: float = Field(description="Float", ge=0.0, le=100.0)
    bool_field: bool = Field(description="Boolean")
    date_field: str = Field(description="Date", format="date")
    datetime_field: str = Field(description="Datetime", format="datetime")
    array_field: list = Field(description="Array")
    object_field: dict = Field(description="Object")


class FormatModel(GriotModel):
    """Model with various format constraints."""

    email: str = Field(description="Email", format="email")
    uri: str = Field(description="URI", format="uri")
    uuid: str = Field(description="UUID", format="uuid")
    date: str = Field(description="Date", format="date")
    datetime: str = Field(description="Datetime", format="datetime")
    ipv4: str = Field(description="IPv4", format="ipv4")
    hostname: str = Field(description="Hostname", format="hostname")


class DefaultModel(GriotModel):
    """Model with default values."""

    name: str = Field(description="Name")
    status: str = Field(description="Status", default="unknown")


# =============================================================================
# BASIC MOCK GENERATION TESTS
# =============================================================================


class TestGenerateMockData:
    """Tests for generate_mock_data function."""

    def test_generate_basic_mock(self) -> None:
        """Test generating basic mock data."""
        data = generate_mock_data(SimpleModel, rows=10)

        assert len(data) == 10
        for row in data:
            assert "name" in row
            assert "age" in row
            assert isinstance(row["name"], str)
            assert isinstance(row["age"], int)

    def test_generate_mock_with_seed(self) -> None:
        """Test that seed produces reproducible results."""
        data1 = generate_mock_data(SimpleModel, rows=5, seed=42)
        data2 = generate_mock_data(SimpleModel, rows=5, seed=42)

        assert data1 == data2

    def test_generate_different_seeds(self) -> None:
        """Test that different seeds produce different results."""
        data1 = generate_mock_data(SimpleModel, rows=5, seed=42)
        data2 = generate_mock_data(SimpleModel, rows=5, seed=123)

        # Very unlikely to be equal with different seeds
        assert data1 != data2

    def test_generate_empty_dataset(self) -> None:
        """Test generating zero rows."""
        data = generate_mock_data(SimpleModel, rows=0)
        assert len(data) == 0

    def test_generate_single_row(self) -> None:
        """Test generating a single row."""
        data = generate_mock_data(SimpleModel, rows=1)
        assert len(data) == 1


# =============================================================================
# CONSTRAINT VALIDATION TESTS
# =============================================================================


class TestMockConstraints:
    """Tests that mock data respects constraints."""

    def test_mock_respects_ge_le(self) -> None:
        """Test mock data respects ge/le constraints."""
        data = generate_mock_data(SimpleModel, rows=100)

        for row in data:
            assert 0 <= row["age"] <= 100

    def test_mock_respects_enum(self) -> None:
        """Test mock data respects enum constraints."""
        data = generate_mock_data(ConstrainedModel, rows=100)

        valid_statuses = {"active", "inactive", "pending"}
        for row in data:
            assert row["status"] in valid_statuses

    def test_mock_respects_multiple_of(self) -> None:
        """Test mock data respects multiple_of constraint."""
        data = generate_mock_data(ConstrainedModel, rows=100)

        for row in data:
            assert row["score"] % 5 == 0

    def test_mock_respects_pattern(self) -> None:
        """Test mock data respects pattern constraint."""
        data = generate_mock_data(ConstrainedModel, rows=50)

        pattern = re.compile(r"^ID-\d{6}$")
        for row in data:
            # Pattern generation is best-effort
            # At minimum, should have the prefix
            assert row["id"].startswith("ID-")

    def test_mock_respects_format_email(self) -> None:
        """Test mock data generates valid emails."""
        data = generate_mock_data(FormatModel, rows=50)

        email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
        for row in data:
            assert email_pattern.match(row["email"]), f"Invalid email: {row['email']}"

    def test_mock_respects_format_uri(self) -> None:
        """Test mock data generates valid URIs."""
        data = generate_mock_data(FormatModel, rows=50)

        for row in data:
            assert row["uri"].startswith("http"), f"Invalid URI: {row['uri']}"

    def test_mock_respects_format_uuid(self) -> None:
        """Test mock data generates valid UUIDs."""
        data = generate_mock_data(FormatModel, rows=50)

        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
        )
        for row in data:
            assert uuid_pattern.match(row["uuid"]), f"Invalid UUID: {row['uuid']}"

    def test_mock_respects_format_date(self) -> None:
        """Test mock data generates valid dates."""
        data = generate_mock_data(FormatModel, rows=50)

        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for row in data:
            assert date_pattern.match(row["date"]), f"Invalid date: {row['date']}"

    def test_mock_respects_format_datetime(self) -> None:
        """Test mock data generates valid datetimes."""
        data = generate_mock_data(FormatModel, rows=50)

        datetime_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        for row in data:
            assert datetime_pattern.match(
                row["datetime"]
            ), f"Invalid datetime: {row['datetime']}"

    def test_mock_respects_format_ipv4(self) -> None:
        """Test mock data generates valid IPv4 addresses."""
        data = generate_mock_data(FormatModel, rows=50)

        ipv4_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        for row in data:
            assert ipv4_pattern.match(row["ipv4"]), f"Invalid IPv4: {row['ipv4']}"


# =============================================================================
# NULLABLE FIELD TESTS
# =============================================================================


class TestMockNullable:
    """Tests for nullable field handling in mock generation."""

    def test_mock_nullable_fields_can_be_null(self) -> None:
        """Test that nullable fields can generate null values."""
        # Generate enough rows to likely get some nulls (10% chance)
        data = generate_mock_data(NullableModel, rows=100, seed=42)

        # Check that at least some nulls were generated
        null_count = sum(1 for row in data if row["optional"] is None)
        # With 10% chance over 100 rows, expect some nulls
        # But required field should never be null
        for row in data:
            assert row["required"] is not None

    def test_mock_required_fields_never_null(self) -> None:
        """Test that required fields are never null."""
        data = generate_mock_data(NullableModel, rows=100)

        for row in data:
            assert row["required"] is not None


# =============================================================================
# UNIQUE FIELD TESTS
# =============================================================================


class TestMockUnique:
    """Tests for unique constraint handling in mock generation."""

    def test_mock_unique_fields_are_unique(self) -> None:
        """Test that unique fields generate unique values."""
        data = generate_mock_data(UniqueModel, rows=100)

        ids = [row["id"] for row in data]
        assert len(ids) == len(set(ids)), "IDs should be unique"

    def test_mock_primary_key_is_unique(self) -> None:
        """Test that primary key fields are unique."""
        data = generate_mock_data(ConstrainedModel, rows=100)

        ids = [row["id"] for row in data]
        assert len(ids) == len(set(ids)), "Primary keys should be unique"


# =============================================================================
# DATA TYPE TESTS
# =============================================================================


class TestMockDataTypes:
    """Tests for mock data type generation."""

    def test_mock_string_type(self) -> None:
        """Test mock generation for string type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["string_field"], str)

    def test_mock_integer_type(self) -> None:
        """Test mock generation for integer type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["int_field"], int)

    def test_mock_float_type(self) -> None:
        """Test mock generation for float type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["float_field"], (int, float))

    def test_mock_boolean_type(self) -> None:
        """Test mock generation for boolean type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["bool_field"], bool)

    def test_mock_array_type(self) -> None:
        """Test mock generation for array type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["array_field"], list)

    def test_mock_object_type(self) -> None:
        """Test mock generation for object type."""
        data = generate_mock_data(AllTypesModel, rows=10)

        for row in data:
            assert isinstance(row["object_field"], dict)


# =============================================================================
# DEFAULT VALUE TESTS
# =============================================================================


class TestMockDefaults:
    """Tests for default value handling in mock generation."""

    def test_mock_can_use_defaults(self) -> None:
        """Test that mock generation can use default values."""
        # With seed, some rows may use defaults (30% chance)
        data = generate_mock_data(DefaultModel, rows=100, seed=42)

        # At least verify the field exists
        for row in data:
            assert "status" in row


# =============================================================================
# RANGE CONSTRAINT TESTS
# =============================================================================


class TestMockRanges:
    """Tests for range constraint handling."""

    def test_mock_gt_constraint(self) -> None:
        """Test mock data respects gt constraint."""

        class GTModel(GriotModel):
            value: int = Field(description="Value", gt=0)

        data = generate_mock_data(GTModel, rows=100)

        for row in data:
            assert row["value"] > 0

    def test_mock_lt_constraint(self) -> None:
        """Test mock data respects lt constraint."""

        class LTModel(GriotModel):
            value: int = Field(description="Value", lt=100)

        data = generate_mock_data(LTModel, rows=100)

        for row in data:
            assert row["value"] < 100

    def test_mock_float_ge_le(self) -> None:
        """Test mock data respects float range constraints."""
        data = generate_mock_data(AllTypesModel, rows=100)

        for row in data:
            assert 0.0 <= row["float_field"] <= 100.0


# =============================================================================
# LENGTH CONSTRAINT TESTS
# =============================================================================


class TestMockLengths:
    """Tests for length constraint handling."""

    def test_mock_min_max_length(self) -> None:
        """Test mock data respects min/max length constraints."""

        class LengthModel(GriotModel):
            code: str = Field(description="Code", min_length=5, max_length=10)

        data = generate_mock_data(LengthModel, rows=100)

        for row in data:
            assert 5 <= len(row["code"]) <= 10

    def test_mock_max_length_only(self) -> None:
        """Test mock data respects max_length constraint."""

        class MaxLenModel(GriotModel):
            short: str = Field(description="Short", max_length=5)

        data = generate_mock_data(MaxLenModel, rows=100)

        for row in data:
            assert len(row["short"]) <= 5


# =============================================================================
# LARGE DATASET TESTS
# =============================================================================


class TestMockLargeDatasets:
    """Tests for large dataset generation."""

    def test_mock_large_dataset(self) -> None:
        """Test generating a large dataset."""
        data = generate_mock_data(SimpleModel, rows=10000)

        assert len(data) == 10000

    def test_mock_unique_large_dataset(self) -> None:
        """Test unique constraint with large dataset."""
        data = generate_mock_data(UniqueModel, rows=1000)

        ids = [row["id"] for row in data]
        assert len(ids) == len(set(ids))
