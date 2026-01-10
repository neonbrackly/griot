"""
Griot Core Mock Data Generator

Generate synthetic data conforming to contract constraints.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import random
import re
import string
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from griot_core.types import DataType, FieldFormat

if TYPE_CHECKING:
    from griot_core.models import FieldInfo, GriotModel

__all__ = ["generate_mock_data"]


def generate_mock_data(
    model: type[GriotModel],
    rows: int = 100,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    Generate synthetic data conforming to a contract.

    Args:
        model: The GriotModel class defining the contract.
        rows: Number of rows to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of dictionaries containing mock data.
    """
    if seed is not None:
        random.seed(seed)

    result: list[dict[str, Any]] = []
    seen_unique: dict[str, set[Any]] = {
        name: set()
        for name, info in model._griot_fields.items()
        if info.unique or info.primary_key
    }

    for row_idx in range(rows):
        row: dict[str, Any] = {}
        for field_name, field_info in model._griot_fields.items():
            # Handle nullable fields
            if field_info.nullable and random.random() < 0.1:
                row[field_name] = None
                continue

            # Generate value based on field type and constraints
            value = _generate_value(field_info, row_idx, seen_unique.get(field_name))

            # Track unique values
            if field_name in seen_unique:
                seen_unique[field_name].add(value)

            row[field_name] = value

        result.append(row)

    return result


def _generate_value(
    field_info: FieldInfo,
    row_idx: int,
    seen: set[Any] | None = None,
) -> Any:
    """Generate a mock value for a field."""
    # Handle enum constraint
    if field_info.enum:
        return random.choice(field_info.enum)

    # Handle default value
    if field_info.has_default and random.random() < 0.3:
        return field_info.default

    # Generate based on type
    if field_info.type == DataType.STRING:
        return _generate_string(field_info, row_idx, seen)
    elif field_info.type == DataType.INTEGER:
        return _generate_integer(field_info, seen)
    elif field_info.type == DataType.FLOAT:
        return _generate_float(field_info)
    elif field_info.type == DataType.BOOLEAN:
        return random.choice([True, False])
    elif field_info.type == DataType.DATE:
        return _generate_date()
    elif field_info.type == DataType.DATETIME:
        return _generate_datetime()
    elif field_info.type == DataType.ARRAY:
        return _generate_array()
    elif field_info.type == DataType.OBJECT:
        return _generate_object()
    else:
        return _generate_string(field_info, row_idx, seen)


def _generate_string(
    field_info: FieldInfo,
    row_idx: int,
    seen: set[Any] | None = None,
) -> str:
    """Generate a mock string value."""
    # Handle format constraint
    if field_info.format:
        return _generate_formatted_string(field_info.format, row_idx, seen)

    # Handle pattern constraint
    if field_info.pattern:
        return _generate_from_pattern(field_info.pattern, row_idx, seen)

    # Determine length
    min_len = field_info.min_length or 1
    max_len = field_info.max_length or 50

    # Generate unique value if needed
    if seen is not None:
        base = f"{field_info.name}_{row_idx}"
        while base in seen:
            base = f"{field_info.name}_{row_idx}_{random.randint(1000, 9999)}"
        return base[:max_len]

    # Generate random string
    length = random.randint(min_len, min(max_len, 20))
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _generate_formatted_string(
    format: FieldFormat,
    row_idx: int,
    seen: set[Any] | None = None,
) -> str:
    """Generate a string matching a specific format."""
    if format == FieldFormat.EMAIL:
        user = f"user{row_idx}"
        domain = random.choice(["example.com", "test.org", "mock.io"])
        return f"{user}@{domain}"

    elif format == FieldFormat.URI:
        path = f"resource{row_idx}"
        return f"https://example.com/{path}"

    elif format == FieldFormat.UUID:
        return str(uuid4())

    elif format == FieldFormat.DATE:
        return _generate_date()

    elif format == FieldFormat.DATETIME:
        return _generate_datetime()

    elif format == FieldFormat.IPV4:
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    elif format == FieldFormat.IPV6:
        parts = [f"{random.randint(0, 65535):x}" for _ in range(8)]
        return ":".join(parts)

    elif format == FieldFormat.HOSTNAME:
        return f"host{row_idx}.example.com"

    return f"formatted_{row_idx}"


def _generate_from_pattern(
    pattern: str,
    row_idx: int,
    seen: set[Any] | None = None,
) -> str:
    """Generate a string matching a regex pattern (best effort)."""
    # Simple pattern handling for common cases
    result = pattern

    # Remove anchors
    result = result.lstrip("^").rstrip("$")

    # Handle \d{n}
    import re

    def replace_digit_count(match: re.Match[str]) -> str:
        count = int(match.group(1))
        return "".join(str(random.randint(0, 9)) for _ in range(count))

    result = re.sub(r"\\d\{(\d+)\}", replace_digit_count, result)

    # Handle \d+ and \d
    result = re.sub(r"\\d\+", str(random.randint(100, 999)), result)
    result = re.sub(r"\\d", str(random.randint(0, 9)), result)

    # Handle [A-Z]{n}
    def replace_upper_count(match: re.Match[str]) -> str:
        count = int(match.group(1))
        return "".join(random.choices(string.ascii_uppercase, k=count))

    result = re.sub(r"\[A-Z\]\{(\d+)\}", replace_upper_count, result)

    # Handle [a-z]{n}
    def replace_lower_count(match: re.Match[str]) -> str:
        count = int(match.group(1))
        return "".join(random.choices(string.ascii_lowercase, k=count))

    result = re.sub(r"\[a-z\]\{(\d+)\}", replace_lower_count, result)

    # Add row index for uniqueness
    if seen is not None:
        # Try to make it unique
        base_result = result
        attempt = 0
        while result in seen and attempt < 100:
            result = base_result.replace("\\d", str(row_idx + attempt))
            attempt += 1

    return result


def _generate_integer(
    field_info: FieldInfo,
    seen: set[Any] | None = None,
) -> int:
    """Generate a mock integer value."""
    # Determine range
    min_val = field_info.ge if field_info.ge is not None else (field_info.gt + 1 if field_info.gt is not None else 0)
    max_val = field_info.le if field_info.le is not None else (field_info.lt - 1 if field_info.lt is not None else 1000)

    min_val = int(min_val)
    max_val = int(max_val)

    # Handle multiple_of constraint
    if field_info.multiple_of:
        mult = int(field_info.multiple_of)
        min_mult = (min_val + mult - 1) // mult
        max_mult = max_val // mult
        if max_mult < min_mult:
            return min_mult * mult
        return random.randint(min_mult, max_mult) * mult

    # Generate unique value if needed
    if seen is not None:
        value = random.randint(min_val, max_val)
        attempts = 0
        while value in seen and attempts < 1000:
            value = random.randint(min_val, max_val)
            attempts += 1
        return value

    return random.randint(min_val, max_val)


def _generate_float(field_info: FieldInfo) -> float:
    """Generate a mock float value."""
    min_val = field_info.ge if field_info.ge is not None else (field_info.gt + 0.001 if field_info.gt is not None else 0.0)
    max_val = field_info.le if field_info.le is not None else (field_info.lt - 0.001 if field_info.lt is not None else 1000.0)

    value = random.uniform(float(min_val), float(max_val))

    # Handle multiple_of constraint
    if field_info.multiple_of:
        mult = float(field_info.multiple_of)
        value = round(value / mult) * mult

    return round(value, 2)


def _generate_date() -> str:
    """Generate a random date in ISO format."""
    start = datetime(2020, 1, 1)
    end = datetime(2025, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date = start + timedelta(days=random_days)
    return date.strftime("%Y-%m-%d")


def _generate_datetime() -> str:
    """Generate a random datetime in ISO format."""
    start = datetime(2020, 1, 1)
    end = datetime(2025, 12, 31)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    dt = start + timedelta(seconds=random_seconds)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _generate_array() -> list[Any]:
    """Generate a random array."""
    length = random.randint(0, 5)
    return [random.randint(1, 100) for _ in range(length)]


def _generate_object() -> dict[str, Any]:
    """Generate a random object."""
    return {
        "key": f"value_{random.randint(1, 100)}",
        "count": random.randint(1, 10),
    }
