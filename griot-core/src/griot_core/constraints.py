"""
Griot Core Constraints

Constraint validation logic for ODCS contracts.
Constraints are defined in customProperties.constraints on each field.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import re
from typing import Any, Callable

__all__ = [
    "validate_constraint",
    "get_constraint_validator",
]


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


def _validate_min(value: Any, constraint_value: int | float) -> bool:
    """Validate minimum value constraint."""
    if value is None:
        return True
    try:
        return float(value) >= constraint_value
    except (TypeError, ValueError):
        return False


def _validate_max(value: Any, constraint_value: int | float) -> bool:
    """Validate maximum value constraint."""
    if value is None:
        return True
    try:
        return float(value) <= constraint_value
    except (TypeError, ValueError):
        return False


def _validate_enum(value: Any, constraint_value: list[Any]) -> bool:
    """Validate enum constraint."""
    if value is None:
        return True
    return value in constraint_value


_VALIDATORS: dict[str, ConstraintValidator] = {
    "min_length": _validate_min_length,
    "max_length": _validate_max_length,
    "pattern": _validate_pattern,
    "min": _validate_min,
    "max": _validate_max,
    "enum": _validate_enum,
}


def get_constraint_validator(constraint_name: str) -> ConstraintValidator:
    """Get the validator function for a constraint name."""
    return _VALIDATORS.get(constraint_name, lambda v, c: True)


def validate_constraint(
    constraint_name: str,
    value: Any,
    constraint_value: Any,
) -> bool:
    """
    Validate a value against a specific constraint.

    Args:
        constraint_name: The name of the constraint (e.g., "min_length", "pattern").
        value: The value to validate.
        constraint_value: The constraint parameter (e.g., max length value, pattern string).

    Returns:
        True if the constraint is satisfied, False otherwise.
    """
    validator = get_constraint_validator(constraint_name)
    return validator(value, constraint_value)
