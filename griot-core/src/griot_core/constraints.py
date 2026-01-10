"""
Griot Core Constraints

Constraint definitions and validation logic.
This module provides reusable constraint validators.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from griot_core.types import ConstraintType, FieldFormat

__all__ = [
    "Constraint",
    "ConstraintValidator",
    "get_constraint_validator",
    "validate_constraint",
]


@dataclass
class Constraint:
    """Represents a single constraint on a field."""

    type: ConstraintType
    value: Any
    message: str | None = None

    def validate(self, field_value: Any) -> tuple[bool, str]:
        """
        Validate a value against this constraint.

        Returns:
            Tuple of (is_valid, error_message).
        """
        validator = get_constraint_validator(self.type)
        is_valid = validator(field_value, self.value)
        if is_valid:
            return True, ""
        return False, self.message or f"Constraint {self.type.value} failed"


# Type alias for constraint validators
ConstraintValidator = Callable[[Any, Any], bool]


def _validate_min_length(value: Any, constraint_value: int) -> bool:
    """Validate minimum length constraint."""
    if value is None:
        return True
    return len(str(value)) >= constraint_value


def _validate_max_length(value: Any, constraint_value: int) -> bool:
    """Validate maximum length constraint."""
    if value is None:
        return True
    return len(str(value)) <= constraint_value


def _validate_pattern(value: Any, constraint_value: str) -> bool:
    """Validate regex pattern constraint."""
    if value is None:
        return True
    return bool(re.match(constraint_value, str(value)))


def _validate_format(value: Any, constraint_value: FieldFormat) -> bool:
    """Validate format constraint."""
    if value is None:
        return True

    from griot_core.validation import _FORMAT_VALIDATORS

    validator = _FORMAT_VALIDATORS.get(constraint_value)
    if validator:
        return validator(str(value))
    return True


def _validate_ge(value: Any, constraint_value: int | float) -> bool:
    """Validate greater-than-or-equal constraint."""
    if value is None:
        return True
    try:
        return float(value) >= constraint_value
    except (TypeError, ValueError):
        return False


def _validate_le(value: Any, constraint_value: int | float) -> bool:
    """Validate less-than-or-equal constraint."""
    if value is None:
        return True
    try:
        return float(value) <= constraint_value
    except (TypeError, ValueError):
        return False


def _validate_gt(value: Any, constraint_value: int | float) -> bool:
    """Validate greater-than constraint."""
    if value is None:
        return True
    try:
        return float(value) > constraint_value
    except (TypeError, ValueError):
        return False


def _validate_lt(value: Any, constraint_value: int | float) -> bool:
    """Validate less-than constraint."""
    if value is None:
        return True
    try:
        return float(value) < constraint_value
    except (TypeError, ValueError):
        return False


def _validate_multiple_of(value: Any, constraint_value: int | float) -> bool:
    """Validate multiple-of constraint."""
    if value is None:
        return True
    try:
        return float(value) % constraint_value == 0
    except (TypeError, ValueError):
        return False


def _validate_enum(value: Any, constraint_value: list[Any]) -> bool:
    """Validate enum constraint."""
    if value is None:
        return True
    return value in constraint_value


def _validate_unique(value: Any, constraint_value: set[Any]) -> bool:
    """Validate unique constraint (value not in seen set)."""
    if value is None:
        return True
    return value not in constraint_value


_VALIDATORS: dict[ConstraintType, ConstraintValidator] = {
    ConstraintType.MIN_LENGTH: _validate_min_length,
    ConstraintType.MAX_LENGTH: _validate_max_length,
    ConstraintType.PATTERN: _validate_pattern,
    ConstraintType.FORMAT: _validate_format,
    ConstraintType.GE: _validate_ge,
    ConstraintType.LE: _validate_le,
    ConstraintType.GT: _validate_gt,
    ConstraintType.LT: _validate_lt,
    ConstraintType.MULTIPLE_OF: _validate_multiple_of,
    ConstraintType.ENUM: _validate_enum,
    ConstraintType.UNIQUE: _validate_unique,
}


def get_constraint_validator(constraint_type: ConstraintType) -> ConstraintValidator:
    """Get the validator function for a constraint type."""
    return _VALIDATORS.get(constraint_type, lambda v, c: True)


def validate_constraint(
    constraint_type: ConstraintType,
    value: Any,
    constraint_value: Any,
) -> bool:
    """
    Validate a value against a specific constraint.

    Args:
        constraint_type: The type of constraint to validate.
        value: The value to validate.
        constraint_value: The constraint parameter (e.g., max length, pattern).

    Returns:
        True if the constraint is satisfied, False otherwise.
    """
    validator = get_constraint_validator(constraint_type)
    return validator(value, constraint_value)
