"""
Tests for griot_core.constraints module.

Tests constraint validators and the Constraint class.
"""
from __future__ import annotations

import pytest

from griot_core.constraints import (
    Constraint,
    get_constraint_validator,
    validate_constraint,
)
from griot_core.types import ConstraintType, FieldFormat


# =============================================================================
# CONSTRAINT CLASS TESTS
# =============================================================================


class TestConstraint:
    """Tests for Constraint dataclass."""

    def test_constraint_creation(self) -> None:
        """Test creating a Constraint instance."""
        constraint = Constraint(
            type=ConstraintType.MIN_LENGTH,
            value=5,
            message="Must be at least 5 characters",
        )
        assert constraint.type == ConstraintType.MIN_LENGTH
        assert constraint.value == 5
        assert constraint.message == "Must be at least 5 characters"

    def test_constraint_default_message(self) -> None:
        """Test Constraint with default message."""
        constraint = Constraint(
            type=ConstraintType.MAX_LENGTH,
            value=100,
        )
        assert constraint.message is None

    def test_constraint_validate_pass(self) -> None:
        """Test Constraint.validate returns True for valid value."""
        constraint = Constraint(
            type=ConstraintType.MIN_LENGTH,
            value=3,
        )
        is_valid, message = constraint.validate("hello")
        assert is_valid is True
        assert message == ""

    def test_constraint_validate_fail(self) -> None:
        """Test Constraint.validate returns False for invalid value."""
        constraint = Constraint(
            type=ConstraintType.MIN_LENGTH,
            value=10,
            message="Too short!",
        )
        is_valid, message = constraint.validate("hi")
        assert is_valid is False
        assert message == "Too short!"

    def test_constraint_validate_fail_default_message(self) -> None:
        """Test Constraint.validate uses default message on failure."""
        constraint = Constraint(
            type=ConstraintType.MAX_LENGTH,
            value=3,
        )
        is_valid, message = constraint.validate("hello")
        assert is_valid is False
        assert "max_length" in message


# =============================================================================
# GET CONSTRAINT VALIDATOR TESTS
# =============================================================================


class TestGetConstraintValidator:
    """Tests for get_constraint_validator function."""

    def test_get_validator_min_length(self) -> None:
        """Test getting min_length validator."""
        validator = get_constraint_validator(ConstraintType.MIN_LENGTH)
        assert callable(validator)
        assert validator("hello", 3) is True
        assert validator("hi", 5) is False

    def test_get_validator_max_length(self) -> None:
        """Test getting max_length validator."""
        validator = get_constraint_validator(ConstraintType.MAX_LENGTH)
        assert validator("hi", 5) is True
        assert validator("hello world", 5) is False

    def test_get_validator_pattern(self) -> None:
        """Test getting pattern validator."""
        validator = get_constraint_validator(ConstraintType.PATTERN)
        assert validator("abc123", r"^[a-z]+\d+$") is True
        assert validator("ABC", r"^[a-z]+$") is False

    def test_get_validator_ge(self) -> None:
        """Test getting ge validator."""
        validator = get_constraint_validator(ConstraintType.GE)
        assert validator(10, 5) is True
        assert validator(5, 5) is True
        assert validator(3, 5) is False

    def test_get_validator_le(self) -> None:
        """Test getting le validator."""
        validator = get_constraint_validator(ConstraintType.LE)
        assert validator(5, 10) is True
        assert validator(10, 10) is True
        assert validator(15, 10) is False

    def test_get_validator_gt(self) -> None:
        """Test getting gt validator."""
        validator = get_constraint_validator(ConstraintType.GT)
        assert validator(10, 5) is True
        assert validator(5, 5) is False

    def test_get_validator_lt(self) -> None:
        """Test getting lt validator."""
        validator = get_constraint_validator(ConstraintType.LT)
        assert validator(5, 10) is True
        assert validator(10, 10) is False

    def test_get_validator_multiple_of(self) -> None:
        """Test getting multiple_of validator."""
        validator = get_constraint_validator(ConstraintType.MULTIPLE_OF)
        assert validator(10, 5) is True
        assert validator(15, 5) is True
        assert validator(7, 5) is False

    def test_get_validator_enum(self) -> None:
        """Test getting enum validator."""
        validator = get_constraint_validator(ConstraintType.ENUM)
        assert validator("a", ["a", "b", "c"]) is True
        assert validator("d", ["a", "b", "c"]) is False

    def test_get_validator_unique(self) -> None:
        """Test getting unique validator."""
        validator = get_constraint_validator(ConstraintType.UNIQUE)
        seen = {"a", "b", "c"}
        assert validator("d", seen) is True
        assert validator("a", seen) is False

    def test_get_validator_format(self) -> None:
        """Test getting format validator."""
        validator = get_constraint_validator(ConstraintType.FORMAT)
        assert validator("test@example.com", FieldFormat.EMAIL) is True
        assert validator("not-an-email", FieldFormat.EMAIL) is False


# =============================================================================
# VALIDATE CONSTRAINT FUNCTION TESTS
# =============================================================================


class TestValidateConstraint:
    """Tests for validate_constraint function."""

    def test_validate_min_length(self) -> None:
        """Test validating min_length constraint."""
        assert validate_constraint(ConstraintType.MIN_LENGTH, "hello", 3) is True
        assert validate_constraint(ConstraintType.MIN_LENGTH, "hi", 5) is False

    def test_validate_max_length(self) -> None:
        """Test validating max_length constraint."""
        assert validate_constraint(ConstraintType.MAX_LENGTH, "hi", 5) is True
        assert validate_constraint(ConstraintType.MAX_LENGTH, "hello world", 5) is False

    def test_validate_pattern(self) -> None:
        """Test validating pattern constraint."""
        assert validate_constraint(ConstraintType.PATTERN, "123", r"^\d+$") is True
        assert validate_constraint(ConstraintType.PATTERN, "abc", r"^\d+$") is False

    def test_validate_ge(self) -> None:
        """Test validating ge constraint."""
        assert validate_constraint(ConstraintType.GE, 10, 5) is True
        assert validate_constraint(ConstraintType.GE, 5, 5) is True
        assert validate_constraint(ConstraintType.GE, 3, 5) is False

    def test_validate_le(self) -> None:
        """Test validating le constraint."""
        assert validate_constraint(ConstraintType.LE, 5, 10) is True
        assert validate_constraint(ConstraintType.LE, 10, 10) is True
        assert validate_constraint(ConstraintType.LE, 15, 10) is False

    def test_validate_gt(self) -> None:
        """Test validating gt constraint."""
        assert validate_constraint(ConstraintType.GT, 6, 5) is True
        assert validate_constraint(ConstraintType.GT, 5, 5) is False

    def test_validate_lt(self) -> None:
        """Test validating lt constraint."""
        assert validate_constraint(ConstraintType.LT, 4, 5) is True
        assert validate_constraint(ConstraintType.LT, 5, 5) is False

    def test_validate_multiple_of(self) -> None:
        """Test validating multiple_of constraint."""
        assert validate_constraint(ConstraintType.MULTIPLE_OF, 15, 5) is True
        assert validate_constraint(ConstraintType.MULTIPLE_OF, 17, 5) is False

    def test_validate_enum(self) -> None:
        """Test validating enum constraint."""
        options = ["red", "green", "blue"]
        assert validate_constraint(ConstraintType.ENUM, "red", options) is True
        assert validate_constraint(ConstraintType.ENUM, "yellow", options) is False

    def test_validate_unique(self) -> None:
        """Test validating unique constraint."""
        seen = {"existing1", "existing2"}
        assert validate_constraint(ConstraintType.UNIQUE, "new", seen) is True
        assert validate_constraint(ConstraintType.UNIQUE, "existing1", seen) is False


# =============================================================================
# NULL VALUE HANDLING TESTS
# =============================================================================


class TestNullValueHandling:
    """Tests for null value handling in validators."""

    def test_min_length_null_passes(self) -> None:
        """Test min_length allows None."""
        assert validate_constraint(ConstraintType.MIN_LENGTH, None, 5) is True

    def test_max_length_null_passes(self) -> None:
        """Test max_length allows None."""
        assert validate_constraint(ConstraintType.MAX_LENGTH, None, 5) is True

    def test_pattern_null_passes(self) -> None:
        """Test pattern allows None."""
        assert validate_constraint(ConstraintType.PATTERN, None, r"^\d+$") is True

    def test_ge_null_passes(self) -> None:
        """Test ge allows None."""
        assert validate_constraint(ConstraintType.GE, None, 0) is True

    def test_le_null_passes(self) -> None:
        """Test le allows None."""
        assert validate_constraint(ConstraintType.LE, None, 100) is True

    def test_gt_null_passes(self) -> None:
        """Test gt allows None."""
        assert validate_constraint(ConstraintType.GT, None, 0) is True

    def test_lt_null_passes(self) -> None:
        """Test lt allows None."""
        assert validate_constraint(ConstraintType.LT, None, 100) is True

    def test_multiple_of_null_passes(self) -> None:
        """Test multiple_of allows None."""
        assert validate_constraint(ConstraintType.MULTIPLE_OF, None, 5) is True

    def test_enum_null_passes(self) -> None:
        """Test enum allows None."""
        assert validate_constraint(ConstraintType.ENUM, None, ["a", "b"]) is True

    def test_unique_null_passes(self) -> None:
        """Test unique allows None."""
        assert validate_constraint(ConstraintType.UNIQUE, None, {"a", "b"}) is True

    def test_format_null_passes(self) -> None:
        """Test format allows None."""
        assert validate_constraint(ConstraintType.FORMAT, None, FieldFormat.EMAIL) is True


# =============================================================================
# TYPE COERCION TESTS
# =============================================================================


class TestTypeCoercion:
    """Tests for type handling in validators."""

    def test_ge_with_string_number(self) -> None:
        """Test ge handles invalid type."""
        # Non-numeric string should fail
        assert validate_constraint(ConstraintType.GE, "not_a_number", 0) is False

    def test_le_with_string_number(self) -> None:
        """Test le handles invalid type."""
        assert validate_constraint(ConstraintType.LE, "not_a_number", 100) is False

    def test_gt_with_invalid_type(self) -> None:
        """Test gt handles invalid type."""
        assert validate_constraint(ConstraintType.GT, "abc", 0) is False

    def test_lt_with_invalid_type(self) -> None:
        """Test lt handles invalid type."""
        assert validate_constraint(ConstraintType.LT, "abc", 100) is False

    def test_multiple_of_with_invalid_type(self) -> None:
        """Test multiple_of handles invalid type."""
        assert validate_constraint(ConstraintType.MULTIPLE_OF, "abc", 5) is False

    def test_min_length_with_non_string(self) -> None:
        """Test min_length converts to string."""
        # Should convert 12345 to "12345" (length 5)
        assert validate_constraint(ConstraintType.MIN_LENGTH, 12345, 5) is True
        assert validate_constraint(ConstraintType.MIN_LENGTH, 12345, 10) is False


# =============================================================================
# FLOAT CONSTRAINT TESTS
# =============================================================================


class TestFloatConstraints:
    """Tests for float value handling."""

    def test_ge_with_float(self) -> None:
        """Test ge with float values."""
        assert validate_constraint(ConstraintType.GE, 5.5, 5.0) is True
        assert validate_constraint(ConstraintType.GE, 5.0, 5.0) is True
        assert validate_constraint(ConstraintType.GE, 4.9, 5.0) is False

    def test_le_with_float(self) -> None:
        """Test le with float values."""
        assert validate_constraint(ConstraintType.LE, 4.5, 5.0) is True
        assert validate_constraint(ConstraintType.LE, 5.0, 5.0) is True
        assert validate_constraint(ConstraintType.LE, 5.1, 5.0) is False

    def test_multiple_of_with_float(self) -> None:
        """Test multiple_of with float values."""
        assert validate_constraint(ConstraintType.MULTIPLE_OF, 2.5, 0.5) is True
        assert validate_constraint(ConstraintType.MULTIPLE_OF, 2.7, 0.5) is False


# =============================================================================
# FORMAT VALIDATOR TESTS
# =============================================================================


class TestFormatValidators:
    """Tests for format-specific validators."""

    def test_email_format(self) -> None:
        """Test email format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        # Valid emails
        assert validator("test@example.com", FieldFormat.EMAIL) is True
        assert validator("user.name@domain.org", FieldFormat.EMAIL) is True

        # Invalid emails
        assert validator("not-an-email", FieldFormat.EMAIL) is False
        assert validator("@example.com", FieldFormat.EMAIL) is False

    def test_uri_format(self) -> None:
        """Test URI format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        assert validator("https://example.com", FieldFormat.URI) is True
        assert validator("http://example.com/path", FieldFormat.URI) is True
        assert validator("not a uri", FieldFormat.URI) is False

    def test_uuid_format(self) -> None:
        """Test UUID format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        assert validator("550e8400-e29b-41d4-a716-446655440000", FieldFormat.UUID) is True
        assert validator("not-a-uuid", FieldFormat.UUID) is False

    def test_date_format(self) -> None:
        """Test date format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        assert validator("2025-01-15", FieldFormat.DATE) is True
        assert validator("2025/01/15", FieldFormat.DATE) is False
        assert validator("not-a-date", FieldFormat.DATE) is False

    def test_ipv4_format(self) -> None:
        """Test IPv4 format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        assert validator("192.168.1.1", FieldFormat.IPV4) is True
        assert validator("10.0.0.1", FieldFormat.IPV4) is True
        assert validator("256.256.256.256", FieldFormat.IPV4) is False
        assert validator("not-an-ip", FieldFormat.IPV4) is False

    def test_hostname_format(self) -> None:
        """Test hostname format validation."""
        validator = get_constraint_validator(ConstraintType.FORMAT)

        assert validator("example.com", FieldFormat.HOSTNAME) is True
        assert validator("api.example.com", FieldFormat.HOSTNAME) is True
