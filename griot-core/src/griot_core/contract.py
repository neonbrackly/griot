"""
Griot Core Contract Loading and Manipulation

Functions for loading, saving, diffing, and linting contracts.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from griot_core.exceptions import ContractNotFoundError, ContractParseError
from griot_core.types import DataType, FieldFormat, Severity

if TYPE_CHECKING:
    from griot_core.models import GriotModel

__all__ = [
    "load_contract",
    "load_contract_from_string",
    "load_contract_from_dict",
    "model_to_yaml",
    "diff_contracts",
    "lint_contract",
    "ContractDiff",
    "TypeChange",
    "ConstraintChange",
    "MetadataChange",
    "LintIssue",
]


@dataclass
class TypeChange:
    """Field type change record."""

    field: str
    from_type: str
    to_type: str
    is_breaking: bool


@dataclass
class ConstraintChange:
    """Constraint change record."""

    field: str
    constraint: str
    from_value: Any
    to_value: Any
    is_breaking: bool


@dataclass
class MetadataChange:
    """Metadata change record (non-breaking)."""

    field: str
    attribute: str
    from_value: Any
    to_value: Any


@dataclass
class ContractDiff:
    """Differences between two contract versions."""

    has_breaking_changes: bool = False
    added_fields: list[str] = dataclass_field(default_factory=list)
    removed_fields: list[str] = dataclass_field(default_factory=list)
    type_changes: list[TypeChange] = dataclass_field(default_factory=list)
    constraint_changes: list[ConstraintChange] = dataclass_field(default_factory=list)
    metadata_changes: list[MetadataChange] = dataclass_field(default_factory=list)

    def summary(self) -> str:
        """Return a human-readable summary."""
        lines = []
        if self.has_breaking_changes:
            lines.append("BREAKING CHANGES DETECTED")
        else:
            lines.append("No breaking changes")

        if self.added_fields:
            lines.append(f"Added fields: {', '.join(self.added_fields)}")
        if self.removed_fields:
            lines.append(f"Removed fields (BREAKING): {', '.join(self.removed_fields)}")
        if self.type_changes:
            lines.append(f"Type changes: {len(self.type_changes)}")
        if self.constraint_changes:
            lines.append(f"Constraint changes: {len(self.constraint_changes)}")

        return "\n".join(lines) if lines else "No differences"

    def to_markdown(self) -> str:
        """Return a markdown-formatted diff report."""
        lines = ["# Contract Diff Report", ""]

        if self.has_breaking_changes:
            lines.append("**WARNING: Breaking changes detected!**")
            lines.append("")

        if self.added_fields:
            lines.append("## Added Fields")
            for f in self.added_fields:
                lines.append(f"- `{f}`")
            lines.append("")

        if self.removed_fields:
            lines.append("## Removed Fields (BREAKING)")
            for f in self.removed_fields:
                lines.append(f"- `{f}`")
            lines.append("")

        if self.type_changes:
            lines.append("## Type Changes")
            for tc in self.type_changes:
                breaking = " **(BREAKING)**" if tc.is_breaking else ""
                lines.append(f"- `{tc.field}`: {tc.from_type} -> {tc.to_type}{breaking}")
            lines.append("")

        if self.constraint_changes:
            lines.append("## Constraint Changes")
            for cc in self.constraint_changes:
                breaking = " **(BREAKING)**" if cc.is_breaking else ""
                lines.append(
                    f"- `{cc.field}.{cc.constraint}`: {cc.from_value} -> {cc.to_value}{breaking}"
                )
            lines.append("")

        return "\n".join(lines)


@dataclass
class LintIssue:
    """Contract quality issue."""

    code: str
    field: str | None
    message: str
    severity: Severity
    suggestion: str | None = None

    def __str__(self) -> str:
        loc = f" ({self.field})" if self.field else ""
        return f"[{self.code}]{loc}: {self.message}"


def load_contract(path: str | Path) -> type[GriotModel]:
    """
    Load a contract definition from a YAML file.

    Args:
        path: Path to the YAML contract file.

    Returns:
        A GriotModel subclass representing the contract.

    Raises:
        ContractNotFoundError: If the file doesn't exist.
        ContractParseError: If the YAML is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise ContractNotFoundError(str(path))

    content = path.read_text(encoding="utf-8")
    return load_contract_from_string(content, source=str(path))


def load_contract_from_string(
    content: str,
    source: str | None = None,
) -> type[GriotModel]:
    """
    Load a contract from a YAML string.

    Args:
        content: YAML content as a string.
        source: Optional source identifier for error messages.

    Returns:
        A GriotModel subclass representing the contract.
    """
    # Parse YAML manually (stdlib only - no pyyaml)
    data = _parse_simple_yaml(content, source)
    return load_contract_from_dict(data)


def load_contract_from_dict(data: dict[str, Any]) -> type[GriotModel]:
    """
    Load a contract from a dictionary.

    Args:
        data: Dictionary containing contract definition.

    Returns:
        A GriotModel subclass representing the contract.
    """
    from griot_core.models import Field, GriotModel

    name = data.get("name", "DynamicContract")
    description = data.get("description", "")
    fields_data = data.get("fields", {})

    # Build field definitions
    annotations: dict[str, type] = {}
    namespace: dict[str, Any] = {"__annotations__": annotations}

    if description:
        namespace["__doc__"] = description

    for field_name, field_def in fields_data.items():
        if isinstance(field_def, dict):
            # Parse field type
            type_str = field_def.get("type", "string")
            python_type = _type_str_to_python(type_str)
            annotations[field_name] = python_type

            # Build Field kwargs
            field_kwargs: dict[str, Any] = {
                "description": field_def.get("description", f"Field: {field_name}"),
            }

            # Copy constraint parameters
            for param in [
                "min_length",
                "max_length",
                "pattern",
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
                "glossary_term",
            ]:
                if param in field_def:
                    field_kwargs[param] = field_def[param]

            if "format" in field_def:
                field_kwargs["format"] = FieldFormat(field_def["format"])

            if "aggregation" in field_def:
                from griot_core.types import AggregationType

                field_kwargs["aggregation"] = AggregationType(field_def["aggregation"])

            if "default" in field_def:
                field_kwargs["default"] = field_def["default"]

            namespace[field_name] = Field(**field_kwargs)
        else:
            # Simple field with just a type
            annotations[field_name] = str
            namespace[field_name] = Field(description=f"Field: {field_name}")

    # Create the dynamic class
    return type(name, (GriotModel,), namespace)


def model_to_yaml(model: type[GriotModel]) -> str:
    """
    Export a GriotModel to YAML format.

    Args:
        model: The GriotModel class to export.

    Returns:
        YAML string representation.
    """
    lines = [
        f"name: {model.__name__}",
    ]

    if model.__doc__:
        doc = model.__doc__.strip()
        if "\n" in doc:
            lines.append("description: |")
            for line in doc.split("\n"):
                lines.append(f"  {line}")
        else:
            lines.append(f"description: {doc}")

    lines.append("fields:")

    for field_name, field_info in model._griot_fields.items():
        lines.append(f"  {field_name}:")
        lines.append(f"    type: {field_info.type.value}")
        lines.append(f"    description: {field_info.description}")

        if field_info.nullable:
            lines.append("    nullable: true")
        if field_info.primary_key:
            lines.append("    primary_key: true")
        if field_info.unique:
            lines.append("    unique: true")

        # Constraints
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
            value = getattr(field_info, constraint)
            if value is not None:
                lines.append(f"    {constraint}: {value}")

        if field_info.format:
            lines.append(f"    format: {field_info.format.value}")
        if field_info.enum:
            lines.append(f"    enum: {field_info.enum}")
        if field_info.has_default:
            lines.append(f"    default: {field_info.default}")
        if field_info.unit:
            lines.append(f"    unit: {field_info.unit}")
        if field_info.aggregation:
            lines.append(f"    aggregation: {field_info.aggregation.value}")
        if field_info.glossary_term:
            lines.append(f"    glossary_term: {field_info.glossary_term}")

    return "\n".join(lines)


def diff_contracts(
    base: type[GriotModel],
    other: type[GriotModel],
) -> ContractDiff:
    """
    Compare two contract versions.

    Args:
        base: The original contract version.
        other: The new contract version.

    Returns:
        ContractDiff describing the differences.
    """
    diff = ContractDiff()

    base_fields = set(base._griot_fields.keys())
    other_fields = set(other._griot_fields.keys())

    # Find added and removed fields
    diff.added_fields = list(other_fields - base_fields)
    diff.removed_fields = list(base_fields - other_fields)

    # Removed fields are breaking changes
    if diff.removed_fields:
        diff.has_breaking_changes = True

    # Check common fields for changes
    common_fields = base_fields & other_fields
    for field_name in common_fields:
        base_info = base._griot_fields[field_name]
        other_info = other._griot_fields[field_name]

        # Check type changes
        if base_info.type != other_info.type:
            is_breaking = not _is_type_widening(base_info.type, other_info.type)
            diff.type_changes.append(
                TypeChange(
                    field=field_name,
                    from_type=base_info.type.value,
                    to_type=other_info.type.value,
                    is_breaking=is_breaking,
                )
            )
            if is_breaking:
                diff.has_breaking_changes = True

        # Check constraint changes
        for constraint in [
            "min_length",
            "max_length",
            "ge",
            "le",
            "gt",
            "lt",
            "pattern",
            "enum",
        ]:
            base_val = getattr(base_info, constraint)
            other_val = getattr(other_info, constraint)
            if base_val != other_val:
                is_breaking = _is_constraint_breaking(constraint, base_val, other_val)
                diff.constraint_changes.append(
                    ConstraintChange(
                        field=field_name,
                        constraint=constraint,
                        from_value=base_val,
                        to_value=other_val,
                        is_breaking=is_breaking,
                    )
                )
                if is_breaking:
                    diff.has_breaking_changes = True

        # Check nullable changes (making non-nullable is breaking)
        if base_info.nullable and not other_info.nullable:
            diff.constraint_changes.append(
                ConstraintChange(
                    field=field_name,
                    constraint="nullable",
                    from_value=True,
                    to_value=False,
                    is_breaking=True,
                )
            )
            diff.has_breaking_changes = True

        # Check metadata changes (non-breaking)
        for attr in ["description", "unit", "aggregation", "glossary_term"]:
            base_val = getattr(base_info, attr)
            other_val = getattr(other_info, attr)
            if base_val != other_val:
                diff.metadata_changes.append(
                    MetadataChange(
                        field=field_name,
                        attribute=attr,
                        from_value=base_val,
                        to_value=other_val,
                    )
                )

    return diff


def lint_contract(model: type[GriotModel]) -> list[LintIssue]:
    """
    Check a contract for quality issues.

    Args:
        model: The GriotModel class to lint.

    Returns:
        List of LintIssue objects describing any problems.
    """
    issues: list[LintIssue] = []

    # G001: No primary key defined
    if model._griot_primary_key is None:
        issues.append(
            LintIssue(
                code="G001",
                field=None,
                message="No primary key defined",
                severity=Severity.WARNING,
                suggestion="Add primary_key=True to a unique identifier field",
            )
        )

    for field_name, field_info in model._griot_fields.items():
        # G002: Missing description
        if (
            not field_info.description
            or field_info.description == f"Field: {field_name}"
        ):
            issues.append(
                LintIssue(
                    code="G002",
                    field=field_name,
                    message="Field has no meaningful description",
                    severity=Severity.WARNING,
                    suggestion="Add a description explaining the field's purpose",
                )
            )

        # G003: String field without constraints
        if field_info.type == DataType.STRING:
            if (
                field_info.max_length is None
                and field_info.pattern is None
                and field_info.format is None
                and field_info.enum is None
            ):
                issues.append(
                    LintIssue(
                        code="G003",
                        field=field_name,
                        message="String field has no length or format constraints",
                        severity=Severity.INFO,
                        suggestion="Consider adding max_length, pattern, format, or enum",
                    )
                )

        # G004: Numeric field without range
        if field_info.type in (DataType.INTEGER, DataType.FLOAT):
            if all(
                getattr(field_info, c) is None for c in ["ge", "le", "gt", "lt"]
            ):
                issues.append(
                    LintIssue(
                        code="G004",
                        field=field_name,
                        message="Numeric field has no range constraints",
                        severity=Severity.INFO,
                        suggestion="Consider adding ge/le/gt/lt constraints",
                    )
                )

        # G005: Field name style
        if not _is_valid_field_name(field_name):
            issues.append(
                LintIssue(
                    code="G005",
                    field=field_name,
                    message="Field name should be snake_case",
                    severity=Severity.WARNING,
                    suggestion="Rename to snake_case format",
                )
            )

    return issues


def _is_valid_field_name(name: str) -> bool:
    """Check if a field name follows snake_case convention."""
    import re

    return bool(re.match(r"^[a-z][a-z0-9_]*$", name))


def _is_type_widening(from_type: DataType, to_type: DataType) -> bool:
    """Check if type change is a widening (non-breaking) conversion."""
    # int -> float is widening
    if from_type == DataType.INTEGER and to_type == DataType.FLOAT:
        return True
    # Any specific type -> any is widening
    if to_type == DataType.ANY:
        return True
    return False


def _is_constraint_breaking(
    constraint: str,
    old_value: Any,
    new_value: Any,
) -> bool:
    """Determine if a constraint change is breaking."""
    if old_value is None:
        # Adding a new constraint is breaking
        return new_value is not None

    if new_value is None:
        # Removing a constraint is not breaking
        return False

    # For range constraints, check if the new range is narrower
    if constraint in ("ge", "gt"):
        # Increasing lower bound is breaking
        return new_value > old_value
    if constraint in ("le", "lt"):
        # Decreasing upper bound is breaking
        return new_value < old_value
    if constraint in ("min_length",):
        # Increasing minimum is breaking
        return new_value > old_value
    if constraint in ("max_length",):
        # Decreasing maximum is breaking
        return new_value < old_value
    if constraint == "pattern":
        # Any pattern change could be breaking
        return True
    if constraint == "enum":
        # Removing values is breaking
        old_set = set(old_value) if old_value else set()
        new_set = set(new_value) if new_value else set()
        return bool(old_set - new_set)

    return True


def _type_str_to_python(type_str: str) -> type:
    """Convert a type string to Python type."""
    type_map = {
        "string": str,
        "str": str,
        "integer": int,
        "int": int,
        "float": float,
        "number": float,
        "boolean": bool,
        "bool": bool,
        "array": list,
        "list": list,
        "object": dict,
        "dict": dict,
        "date": str,
        "datetime": str,
        "any": object,
    }
    return type_map.get(type_str.lower(), str)


def _parse_simple_yaml(content: str, source: str | None = None) -> dict[str, Any]:
    """
    Parse simple YAML without external dependencies.

    This is a minimal YAML parser that handles the subset of YAML
    used in contract definitions. For complex YAML, pyyaml can be
    installed as an optional dependency.
    """
    result: dict[str, Any] = {}
    current_dict = result
    stack: list[tuple[dict[str, Any], int]] = [(result, -1)]

    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Calculate indentation
        indent = len(line) - len(line.lstrip())

        # Pop stack for dedents
        while stack and indent <= stack[-1][1]:
            stack.pop()

        if stack:
            current_dict = stack[-1][0]

        # Parse key: value
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value == "" or value == "|":
                # Nested dict or multiline
                new_dict: dict[str, Any] = {}
                current_dict[key] = new_dict
                stack.append((new_dict, indent))
            elif value.startswith("[") and value.endswith("]"):
                # Inline list
                items = value[1:-1].split(",")
                current_dict[key] = [_parse_yaml_value(i.strip()) for i in items if i.strip()]
            else:
                current_dict[key] = _parse_yaml_value(value)

    return result


def _parse_yaml_value(value: str) -> Any:
    """Parse a YAML value to Python type."""
    if not value:
        return None

    # Remove quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Boolean
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False

    # None
    if value.lower() in ("null", "~"):
        return None

    # Number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    return value
