"""
Tests for griot_core.validation module.

Tests validation engine, ValidationResult, and FieldValidationError.
"""
from __future__ import annotations

from typing import Any

import pytest

from griot_core.models import Field, GriotModel
from griot_core.types import FieldFormat, Severity
from griot_core.validation import (
    FieldStats,
    FieldValidationError,
    ValidationResult,
    validate_data,
    validate_single_row,
    validate_value,
)


# =============================================================================
# TEST MODELS
# =============================================================================


class Customer(GriotModel):
    """Test model: Customer profile."""

    customer_id: str = Field(
        description="Unique customer identifier",
        primary_key=True,
        pattern=r"^CUST-\d{6}$",
    )
    email: str = Field(
        description="Customer email address",
        format="email",
        max_length=255,
    )
    age: int = Field(
        description="Customer age in years",
        ge=0,
        le=150,
    )
    status: str = Field(
        description="Account status",
        enum=["active", "inactive", "suspended"],
    )


class NullableModel(GriotModel):
    """Test model with nullable fields."""

    required_field: str = Field(description="Required")
    nullable_field: str = Field(description="Optional", nullable=True)


class UniqueModel(GriotModel):
    """Test model with unique constraint."""

    id: str = Field(description="Unique ID", unique=True)
    name: str = Field(description="Name")


# =============================================================================
# FIELD VALIDATION ERROR TESTS
# =============================================================================


class TestFieldValidationError:
    """Tests for FieldValidationError."""

    def test_error_creation(self) -> None:
        """Test creating a validation error."""
        error = FieldValidationError(
            field="email",
            row=5,
            value="invalid",
            constraint="format",
            message="Invalid email format",
        )
        assert error.field == "email"
        assert error.row == 5
        assert error.value == "invalid"
        assert error.constraint == "format"
        assert error.message == "Invalid email format"
        assert error.severity == Severity.ERROR

    def test_error_to_dict(self) -> None:
        """Test converting error to dictionary."""
        error = FieldValidationError(
            field="age",
            row=10,
            value=-5,
            constraint="ge",
            message="Value must be >= 0",
        )
        result = error.to_dict()

        assert result["field"] == "age"
        assert result["row"] == 10
        assert result["value"] == -5
        assert result["constraint"] == "ge"
        assert result["severity"] == "error"

    def test_error_str_with_row(self) -> None:
        """Test error string representation with row."""
        error = FieldValidationError(
            field="email",
            row=5,
            value="bad",
            constraint="format",
            message="Invalid email",
        )
        assert str(error) == "email[row 5]: Invalid email"

    def test_error_str_without_row(self) -> None:
        """Test error string representation without row."""
        error = FieldValidationError(
            field="email",
            row=None,
            value="bad",
            constraint="format",
            message="Invalid email",
        )
        assert str(error) == "email: Invalid email"


# =============================================================================
# FIELD STATS TESTS
# =============================================================================


class TestFieldStats:
    """Tests for FieldStats."""

    def test_stats_creation(self) -> None:
        """Test creating field stats."""
        stats = FieldStats(field="test")
        assert stats.field == "test"
        assert stats.total == 0
        assert stats.valid == 0
        assert stats.invalid == 0
        assert stats.null_count == 0

    def test_valid_rate_empty(self) -> None:
        """Test valid rate with no data."""
        stats = FieldStats(field="test")
        assert stats.valid_rate == 1.0

    def test_valid_rate_calculated(self) -> None:
        """Test valid rate calculation."""
        stats = FieldStats(field="test", total=100, valid=80, invalid=20)
        assert stats.valid_rate == 0.8
        assert stats.invalid_rate == 0.2

    def test_stats_to_dict(self) -> None:
        """Test converting stats to dictionary."""
        stats = FieldStats(
            field="test",
            total=100,
            valid=90,
            invalid=10,
            null_count=5,
        )
        result = stats.to_dict()

        assert result["field"] == "test"
        assert result["total"] == 100
        assert result["valid"] == 90
        assert result["invalid"] == 10
        assert result["null_count"] == 5
        assert result["valid_rate"] == 0.9


# =============================================================================
# VALIDATION RESULT TESTS
# =============================================================================


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_passed_result(self) -> None:
        """Test a passing validation result."""
        result = ValidationResult(
            passed=True,
            row_count=100,
            error_count=0,
            errors=[],
            duration_ms=50.0,
        )
        assert result.passed is True
        assert result.error_rate == 0.0

    def test_failed_result(self) -> None:
        """Test a failing validation result."""
        errors = [
            FieldValidationError(
                field="email", row=5, value="bad", constraint="format", message="msg"
            ),
            FieldValidationError(
                field="age", row=10, value=-1, constraint="ge", message="msg"
            ),
        ]
        result = ValidationResult(
            passed=False,
            row_count=100,
            error_count=2,
            errors=errors,
            duration_ms=75.0,
        )
        assert result.passed is False
        assert result.error_count == 2
        assert result.error_rate == 0.02  # 2 rows with errors out of 100

    def test_result_to_dict(self) -> None:
        """Test converting result to dictionary."""
        result = ValidationResult(
            passed=True,
            row_count=50,
            error_count=0,
            duration_ms=25.0,
        )
        d = result.to_dict()

        assert d["passed"] is True
        assert d["row_count"] == 50
        assert d["error_count"] == 0
        assert d["duration_ms"] == 25.0

    def test_result_to_json(self) -> None:
        """Test converting result to JSON."""
        result = ValidationResult(
            passed=True,
            row_count=10,
            error_count=0,
            duration_ms=5.0,
        )
        json_str = result.to_json()

        assert '"passed": true' in json_str
        assert '"row_count": 10' in json_str

    def test_result_summary(self) -> None:
        """Test result summary generation."""
        result = ValidationResult(
            passed=True,
            row_count=1000,
            error_count=0,
            duration_ms=123.45,
        )
        summary = result.summary()

        assert "PASSED" in summary
        assert "1,000" in summary
        assert "123.45ms" in summary

    def test_result_summary_with_errors(self) -> None:
        """Test result summary with errors."""
        errors = [
            FieldValidationError(
                field=f"field{i}",
                row=i,
                value="bad",
                constraint="test",
                message=f"Error {i}",
            )
            for i in range(10)
        ]
        result = ValidationResult(
            passed=False,
            row_count=100,
            error_count=10,
            errors=errors,
            duration_ms=50.0,
        )
        summary = result.summary()

        assert "FAILED" in summary
        assert "Sample errors:" in summary
        assert "... and 5 more" in summary  # Shows only first 5

    def test_raise_on_failure_passes(self) -> None:
        """Test raise_on_failure doesn't raise when passed."""
        result = ValidationResult(
            passed=True, row_count=10, error_count=0, duration_ms=1.0
        )
        result.raise_on_failure()  # Should not raise

    def test_raise_on_failure_raises(self) -> None:
        """Test raise_on_failure raises ValidationError when failed."""
        from griot_core.exceptions import ValidationError

        result = ValidationResult(
            passed=False,
            row_count=10,
            error_count=1,
            errors=[
                FieldValidationError(
                    field="x", row=0, value="y", constraint="z", message="m"
                )
            ],
            duration_ms=1.0,
        )
        with pytest.raises(ValidationError):
            result.raise_on_failure()


# =============================================================================
# VALIDATE VALUE TESTS
# =============================================================================


class TestValidateValue:
    """Tests for validate_value function."""

    def test_validate_null_nullable_field(self) -> None:
        """Test validating null in nullable field."""
        field_info = NullableModel.get_field("nullable_field")
        assert field_info is not None
        errors = validate_value(None, field_info, row=0)
        assert len(errors) == 0

    def test_validate_null_required_field(self) -> None:
        """Test validating null in required field."""
        field_info = NullableModel.get_field("required_field")
        assert field_info is not None
        errors = validate_value(None, field_info, row=0)
        assert len(errors) == 1
        assert errors[0].constraint == "nullable"

    def test_validate_string_type(self) -> None:
        """Test type validation for strings."""
        field_info = Customer.get_field("email")
        assert field_info is not None

        # Valid string
        errors = validate_value("test@example.com", field_info, row=0)
        assert all(e.constraint != "type" for e in errors)

        # Invalid type
        errors = validate_value(123, field_info, row=0)
        assert any(e.constraint == "type" for e in errors)

    def test_validate_integer_type(self) -> None:
        """Test type validation for integers."""
        field_info = Customer.get_field("age")
        assert field_info is not None

        # Valid integer
        errors = validate_value(30, field_info, row=0)
        assert len(errors) == 0

        # String (invalid)
        errors = validate_value("thirty", field_info, row=0)
        assert any(e.constraint == "type" for e in errors)

    def test_validate_min_length(self) -> None:
        """Test min_length validation."""

        class MinLengthModel(GriotModel):
            field: str = Field(description="Test", min_length=5)

        field_info = MinLengthModel.get_field("field")
        assert field_info is not None

        # Valid length
        errors = validate_value("hello", field_info, row=0)
        assert len(errors) == 0

        # Too short
        errors = validate_value("hi", field_info, row=0)
        assert any(e.constraint == "min_length" for e in errors)

    def test_validate_max_length(self) -> None:
        """Test max_length validation."""

        class MaxLengthModel(GriotModel):
            field: str = Field(description="Test", max_length=5)

        field_info = MaxLengthModel.get_field("field")
        assert field_info is not None

        # Valid length
        errors = validate_value("hello", field_info, row=0)
        assert len(errors) == 0

        # Too long
        errors = validate_value("hello world", field_info, row=0)
        assert any(e.constraint == "max_length" for e in errors)

    def test_validate_pattern(self) -> None:
        """Test pattern validation."""
        field_info = Customer.get_field("customer_id")
        assert field_info is not None

        # Valid pattern
        errors = validate_value("CUST-123456", field_info, row=0)
        assert len(errors) == 0

        # Invalid pattern
        errors = validate_value("invalid-id", field_info, row=0)
        assert any(e.constraint == "pattern" for e in errors)

    def test_validate_email_format(self) -> None:
        """Test email format validation."""
        field_info = Customer.get_field("email")
        assert field_info is not None

        # Valid email
        errors = validate_value("test@example.com", field_info, row=0)
        assert not any(e.constraint == "format" for e in errors)

        # Invalid email
        errors = validate_value("not-an-email", field_info, row=0)
        assert any(e.constraint == "format" for e in errors)

    def test_validate_ge_constraint(self) -> None:
        """Test ge (greater than or equal) validation."""
        field_info = Customer.get_field("age")
        assert field_info is not None

        # Valid (at boundary)
        errors = validate_value(0, field_info, row=0)
        assert not any(e.constraint == "ge" for e in errors)

        # Invalid (below)
        errors = validate_value(-1, field_info, row=0)
        assert any(e.constraint == "ge" for e in errors)

    def test_validate_le_constraint(self) -> None:
        """Test le (less than or equal) validation."""
        field_info = Customer.get_field("age")
        assert field_info is not None

        # Valid (at boundary)
        errors = validate_value(150, field_info, row=0)
        assert not any(e.constraint == "le" for e in errors)

        # Invalid (above)
        errors = validate_value(151, field_info, row=0)
        assert any(e.constraint == "le" for e in errors)

    def test_validate_gt_constraint(self) -> None:
        """Test gt (greater than) validation."""

        class GTModel(GriotModel):
            value: int = Field(description="Test", gt=0)

        field_info = GTModel.get_field("value")
        assert field_info is not None

        # Valid
        errors = validate_value(1, field_info, row=0)
        assert len(errors) == 0

        # Invalid (at boundary)
        errors = validate_value(0, field_info, row=0)
        assert any(e.constraint == "gt" for e in errors)

    def test_validate_lt_constraint(self) -> None:
        """Test lt (less than) validation."""

        class LTModel(GriotModel):
            value: int = Field(description="Test", lt=100)

        field_info = LTModel.get_field("value")
        assert field_info is not None

        # Valid
        errors = validate_value(99, field_info, row=0)
        assert len(errors) == 0

        # Invalid (at boundary)
        errors = validate_value(100, field_info, row=0)
        assert any(e.constraint == "lt" for e in errors)

    def test_validate_multiple_of(self) -> None:
        """Test multiple_of validation."""

        class MultipleModel(GriotModel):
            value: int = Field(description="Test", multiple_of=5)

        field_info = MultipleModel.get_field("value")
        assert field_info is not None

        # Valid
        errors = validate_value(15, field_info, row=0)
        assert len(errors) == 0

        # Invalid
        errors = validate_value(17, field_info, row=0)
        assert any(e.constraint == "multiple_of" for e in errors)

    def test_validate_enum(self) -> None:
        """Test enum validation."""
        field_info = Customer.get_field("status")
        assert field_info is not None

        # Valid values
        for value in ["active", "inactive", "suspended"]:
            errors = validate_value(value, field_info, row=0)
            assert not any(e.constraint == "enum" for e in errors)

        # Invalid value
        errors = validate_value("unknown", field_info, row=0)
        assert any(e.constraint == "enum" for e in errors)


# =============================================================================
# VALIDATE DATA TESTS
# =============================================================================


class TestValidateData:
    """Tests for validate_data function."""

    def test_validate_empty_data(self) -> None:
        """Test validating empty dataset."""
        result = validate_data(Customer, [])
        assert result.passed is True
        assert result.row_count == 0
        assert result.error_count == 0

    def test_validate_single_valid_row(self) -> None:
        """Test validating a single valid row."""
        data = {
            "customer_id": "CUST-000001",
            "email": "test@example.com",
            "age": 30,
            "status": "active",
        }
        result = validate_data(Customer, data)
        assert result.passed is True
        assert result.row_count == 1
        assert result.error_count == 0

    def test_validate_multiple_valid_rows(
        self, sample_customer_data: list[dict[str, Any]]
    ) -> None:
        """Test validating multiple valid rows."""
        result = validate_data(Customer, sample_customer_data)
        assert result.passed is True
        assert result.row_count == 3
        assert result.error_count == 0

    def test_validate_invalid_rows(
        self, sample_invalid_customer_data: list[dict[str, Any]]
    ) -> None:
        """Test validating invalid rows."""
        result = validate_data(Customer, sample_invalid_customer_data)
        assert result.passed is False
        assert result.error_count > 0

    def test_validate_missing_required_field(self) -> None:
        """Test validation catches missing required fields."""
        data = {
            "customer_id": "CUST-000001",
            # email is missing
            "age": 30,
            "status": "active",
        }
        result = validate_data(Customer, data)
        assert result.passed is False
        assert any(e.constraint == "required" for e in result.errors)

    def test_validate_uniqueness(self) -> None:
        """Test uniqueness constraint validation."""
        data = [
            {"id": "001", "name": "Alice"},
            {"id": "002", "name": "Bob"},
            {"id": "001", "name": "Charlie"},  # Duplicate ID
        ]
        result = validate_data(UniqueModel, data)
        assert result.passed is False
        assert any(e.constraint == "unique" for e in result.errors)

    def test_validate_field_stats(self) -> None:
        """Test that field stats are populated."""
        data = [
            {
                "customer_id": "CUST-000001",
                "email": "a@b.com",
                "age": 25,
                "status": "active",
            },
            {
                "customer_id": "CUST-000002",
                "email": "bad-email",
                "age": 30,
                "status": "active",
            },
        ]
        result = validate_data(Customer, data)

        assert "email" in result.field_stats
        email_stats = result.field_stats["email"]
        assert email_stats.total == 2
        assert email_stats.invalid == 1
        assert email_stats.valid == 1

    def test_validate_duration_tracked(self) -> None:
        """Test that validation duration is tracked."""
        data = [
            {
                "customer_id": "CUST-000001",
                "email": "test@example.com",
                "age": 30,
                "status": "active",
            }
        ]
        result = validate_data(Customer, data)
        assert result.duration_ms > 0


# =============================================================================
# FORMAT VALIDATORS TESTS
# =============================================================================


class TestFormatValidators:
    """Tests for built-in format validators."""

    def test_uuid_format(self) -> None:
        """Test UUID format validation."""

        class UUIDModel(GriotModel):
            uuid: str = Field(description="UUID", format="uuid")

        field_info = UUIDModel.get_field("uuid")
        assert field_info is not None

        # Valid UUID
        errors = validate_value(
            "550e8400-e29b-41d4-a716-446655440000", field_info, row=0
        )
        assert not any(e.constraint == "format" for e in errors)

        # Invalid UUID
        errors = validate_value("not-a-uuid", field_info, row=0)
        assert any(e.constraint == "format" for e in errors)

    def test_date_format(self) -> None:
        """Test date format validation."""

        class DateModel(GriotModel):
            date: str = Field(description="Date", format="date")

        field_info = DateModel.get_field("date")
        assert field_info is not None

        # Valid date
        errors = validate_value("2025-01-10", field_info, row=0)
        assert not any(e.constraint == "format" for e in errors)

        # Invalid date
        errors = validate_value("not-a-date", field_info, row=0)
        assert any(e.constraint == "format" for e in errors)

    def test_datetime_format(self) -> None:
        """Test datetime format validation."""

        class DatetimeModel(GriotModel):
            dt: str = Field(description="Datetime", format="datetime")

        field_info = DatetimeModel.get_field("dt")
        assert field_info is not None

        # Valid datetime formats
        valid_datetimes = [
            "2025-01-10T12:30:45",
            "2025-01-10T12:30:45Z",
            "2025-01-10 12:30:45",
        ]
        for dt in valid_datetimes:
            errors = validate_value(dt, field_info, row=0)
            assert not any(e.constraint == "format" for e in errors), f"Failed for {dt}"

    def test_uri_format(self) -> None:
        """Test URI format validation."""

        class URIModel(GriotModel):
            uri: str = Field(description="URI", format="uri")

        field_info = URIModel.get_field("uri")
        assert field_info is not None

        # Valid URI
        errors = validate_value("https://example.com/path", field_info, row=0)
        assert not any(e.constraint == "format" for e in errors)

        # Invalid URI
        errors = validate_value("not a uri", field_info, row=0)
        assert any(e.constraint == "format" for e in errors)

    def test_ipv4_format(self) -> None:
        """Test IPv4 format validation."""

        class IPv4Model(GriotModel):
            ip: str = Field(description="IP", format="ipv4")

        field_info = IPv4Model.get_field("ip")
        assert field_info is not None

        # Valid IPv4
        errors = validate_value("192.168.1.1", field_info, row=0)
        assert not any(e.constraint == "format" for e in errors)

        # Invalid IPv4
        errors = validate_value("256.256.256.256", field_info, row=0)
        assert any(e.constraint == "format" for e in errors)

    def test_hostname_format(self) -> None:
        """Test hostname format validation."""

        class HostnameModel(GriotModel):
            host: str = Field(description="Hostname", format="hostname")

        field_info = HostnameModel.get_field("host")
        assert field_info is not None

        # Valid hostname
        errors = validate_value("api.example.com", field_info, row=0)
        assert not any(e.constraint == "format" for e in errors)
