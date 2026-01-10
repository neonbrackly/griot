"""
Tests for griot_core.exceptions module.

Tests exception hierarchy and behavior.
"""
from __future__ import annotations

import pytest

from griot_core.exceptions import (
    BreakingChangeError,
    ConstraintError,
    ContractNotFoundError,
    ContractParseError,
    GriotError,
    ValidationError,
)


class TestGriotError:
    """Tests for base GriotError."""

    def test_griot_error_creation(self) -> None:
        """Test creating base GriotError."""
        error = GriotError("Something went wrong")
        assert error.message == "Something went wrong"
        assert str(error) == "Something went wrong"

    def test_griot_error_repr(self) -> None:
        """Test GriotError repr."""
        error = GriotError("Test error")
        assert "GriotError" in repr(error)
        assert "Test error" in repr(error)

    def test_griot_error_is_exception(self) -> None:
        """Test that GriotError is an Exception."""
        assert issubclass(GriotError, Exception)


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_basic(self) -> None:
        """Test creating basic ValidationError."""
        error = ValidationError("Validation failed")
        assert error.message == "Validation failed"
        assert error.errors == []
        assert error.error_count == 0

    def test_validation_error_with_field_errors(self) -> None:
        """Test ValidationError with field-level errors."""
        from griot_core.validation import FieldValidationError
        from griot_core.types import Severity

        field_errors = [
            FieldValidationError(
                field="email",
                row=0,
                value="bad",
                constraint="format",
                message="Invalid email",
            ),
            FieldValidationError(
                field="age",
                row=1,
                value=-5,
                constraint="ge",
                message="Must be >= 0",
            ),
        ]
        error = ValidationError("Failed", errors=field_errors)

        assert error.error_count == 2
        assert len(error.errors) == 2

    def test_validation_error_str_with_count(self) -> None:
        """Test ValidationError string includes error count."""
        from griot_core.validation import FieldValidationError

        field_errors = [
            FieldValidationError(
                field="x", row=0, value="y", constraint="z", message="m"
            ),
            FieldValidationError(
                field="a", row=1, value="b", constraint="c", message="d"
            ),
        ]
        error = ValidationError("Validation failed", errors=field_errors)

        assert "(2 errors)" in str(error)

    def test_validation_error_inheritance(self) -> None:
        """Test ValidationError inherits from GriotError."""
        assert issubclass(ValidationError, GriotError)

    def test_validation_error_can_be_raised(self) -> None:
        """Test ValidationError can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Test error")

        assert "Test error" in str(exc_info.value)


class TestContractNotFoundError:
    """Tests for ContractNotFoundError."""

    def test_contract_not_found_error(self) -> None:
        """Test ContractNotFoundError creation."""
        error = ContractNotFoundError("/path/to/contract.yaml")
        assert error.path == "/path/to/contract.yaml"
        assert "Contract not found" in str(error)
        assert "/path/to/contract.yaml" in str(error)

    def test_contract_not_found_inheritance(self) -> None:
        """Test ContractNotFoundError inherits from GriotError."""
        assert issubclass(ContractNotFoundError, GriotError)


class TestContractParseError:
    """Tests for ContractParseError."""

    def test_parse_error_basic(self) -> None:
        """Test basic ContractParseError."""
        error = ContractParseError("Invalid syntax")
        assert "Invalid syntax" in str(error)
        assert "Contract parse error" in str(error)

    def test_parse_error_with_source(self) -> None:
        """Test ContractParseError with source file."""
        error = ContractParseError("Invalid YAML", source="contract.yaml")
        assert "contract.yaml" in str(error)

    def test_parse_error_with_location(self) -> None:
        """Test ContractParseError with line and column."""
        error = ContractParseError(
            "Unexpected token", source="contract.yaml", line=10, column=5
        )
        assert "line 10" in str(error)
        assert "column 5" in str(error)

    def test_parse_error_stores_location(self) -> None:
        """Test ContractParseError stores location info."""
        error = ContractParseError("Error", source="file.yaml", line=20, column=15)
        assert error.source == "file.yaml"
        assert error.line == 20
        assert error.column == 15

    def test_parse_error_inheritance(self) -> None:
        """Test ContractParseError inherits from GriotError."""
        assert issubclass(ContractParseError, GriotError)


class TestBreakingChangeError:
    """Tests for BreakingChangeError."""

    def test_breaking_change_basic(self) -> None:
        """Test basic BreakingChangeError."""
        error = BreakingChangeError("Removed required field")
        assert error.message == "Removed required field"
        assert error.diff is None

    def test_breaking_change_with_diff(self) -> None:
        """Test BreakingChangeError with diff object."""
        mock_diff = {"removed_fields": ["field_a"]}
        error = BreakingChangeError("Breaking change detected", diff=mock_diff)
        assert error.diff == mock_diff
        assert "see diff" in str(error)

    def test_breaking_change_inheritance(self) -> None:
        """Test BreakingChangeError inherits from GriotError."""
        assert issubclass(BreakingChangeError, GriotError)


class TestConstraintError:
    """Tests for ConstraintError."""

    def test_constraint_error_basic(self) -> None:
        """Test basic ConstraintError."""
        error = ConstraintError(constraint="pattern", value="[invalid")
        assert error.constraint == "pattern"
        assert error.value == "[invalid"
        assert "pattern" in str(error)

    def test_constraint_error_with_field(self) -> None:
        """Test ConstraintError with field name."""
        error = ConstraintError(
            constraint="min_length", value=-5, field="name", reason="must be positive"
        )
        assert error.field == "name"
        assert error.reason == "must be positive"
        assert "name" in str(error)
        assert "must be positive" in str(error)

    def test_constraint_error_inheritance(self) -> None:
        """Test ConstraintError inherits from GriotError."""
        assert issubclass(ConstraintError, GriotError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy relationships."""

    def test_all_exceptions_inherit_from_griot_error(self) -> None:
        """Verify all custom exceptions inherit from GriotError."""
        exception_classes = [
            ValidationError,
            ContractNotFoundError,
            ContractParseError,
            BreakingChangeError,
            ConstraintError,
        ]
        for exc_class in exception_classes:
            assert issubclass(exc_class, GriotError), f"{exc_class} should inherit from GriotError"

    def test_exceptions_can_be_caught_by_base(self) -> None:
        """Test that all exceptions can be caught by GriotError."""
        exceptions = [
            ValidationError("test"),
            ContractNotFoundError("path"),
            ContractParseError("msg"),
            BreakingChangeError("msg"),
            ConstraintError("c", "v"),
        ]

        for exc in exceptions:
            with pytest.raises(GriotError):
                raise exc
