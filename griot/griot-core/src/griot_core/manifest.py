"""
Griot Core Manifest Export

Export contract metadata for AI/LLM consumption.
Supports JSON-LD, Markdown, and LLM context formats.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from griot_core.types import DataType

if TYPE_CHECKING:
    from griot_core.models import GriotModel

__all__ = ["export_manifest"]


def export_manifest(
    model: type[GriotModel],
    format: str = "json_ld",
) -> str:
    """
    Export contract metadata for AI/LLM consumption.

    Args:
        model: The GriotModel class to export.
        format: Output format - 'json_ld', 'markdown', or 'llm_context'.

    Returns:
        String representation in the requested format.
    """
    if format == "json_ld":
        return _export_json_ld(model)
    elif format == "markdown":
        return _export_markdown(model)
    elif format == "llm_context":
        return _export_llm_context(model)
    else:
        raise ValueError(f"Unknown format: {format}. Use 'json_ld', 'markdown', or 'llm_context'")


def _export_json_ld(model: type[GriotModel]) -> str:
    """Export as JSON-LD (Linked Data format)."""
    properties: dict[str, Any] = {}

    for field_name, field_info in model._griot_fields.items():
        prop: dict[str, Any] = {
            "@type": _datatype_to_schema_org(field_info.type),
            "description": field_info.description,
        }

        if field_info.nullable:
            prop["nullable"] = True
        if field_info.enum:
            prop["enum"] = field_info.enum
        if field_info.unit:
            prop["unitCode"] = field_info.unit
        if field_info.format:
            prop["format"] = field_info.format.value

        properties[field_name] = prop

    json_ld = {
        "@context": {
            "@vocab": "https://schema.org/",
            "griot": "https://griot.dev/schema/",
        },
        "@type": "DataContract",
        "@id": f"griot:{model.__name__}",
        "name": model.__name__,
        "description": model.__doc__ or "",
        "properties": properties,
    }

    if model._griot_primary_key:
        json_ld["identifier"] = model._griot_primary_key

    return json.dumps(json_ld, indent=2, default=str)


def _export_markdown(model: type[GriotModel]) -> str:
    """Export as Markdown documentation."""
    lines = [
        f"# {model.__name__}",
        "",
    ]

    if model.__doc__:
        lines.append(model.__doc__.strip())
        lines.append("")

    lines.append("## Fields")
    lines.append("")
    lines.append("| Field | Type | Description | Constraints |")
    lines.append("|-------|------|-------------|-------------|")

    for field_name, field_info in model._griot_fields.items():
        type_str = field_info.type.value
        if field_info.nullable:
            type_str += "?"

        constraints: list[str] = []
        if field_info.primary_key:
            constraints.append("PK")
        if field_info.unique:
            constraints.append("unique")
        if field_info.format:
            constraints.append(f"format:{field_info.format.value}")
        if field_info.min_length is not None:
            constraints.append(f"min_len:{field_info.min_length}")
        if field_info.max_length is not None:
            constraints.append(f"max_len:{field_info.max_length}")
        if field_info.ge is not None:
            constraints.append(f">={field_info.ge}")
        if field_info.le is not None:
            constraints.append(f"<={field_info.le}")
        if field_info.pattern:
            constraints.append(f"pattern")
        if field_info.enum:
            constraints.append(f"enum({len(field_info.enum)})")

        constraint_str = ", ".join(constraints) if constraints else "-"
        lines.append(
            f"| `{field_name}` | {type_str} | {field_info.description} | {constraint_str} |"
        )

    lines.append("")

    # Add detailed field information
    lines.append("## Field Details")
    lines.append("")

    for field_name, field_info in model._griot_fields.items():
        lines.append(f"### {field_name}")
        lines.append("")
        lines.append(f"**Type:** `{field_info.type.value}`")
        lines.append("")
        lines.append(f"**Description:** {field_info.description}")
        lines.append("")

        if field_info.enum:
            lines.append(f"**Allowed values:** {', '.join(str(v) for v in field_info.enum)}")
            lines.append("")

        if field_info.pattern:
            lines.append(f"**Pattern:** `{field_info.pattern}`")
            lines.append("")

        if field_info.unit:
            lines.append(f"**Unit:** {field_info.unit}")
            lines.append("")

        if field_info.glossary_term:
            lines.append(f"**Glossary term:** {field_info.glossary_term}")
            lines.append("")

    return "\n".join(lines)


def _export_llm_context(model: type[GriotModel]) -> str:
    """Export as optimized context for LLM consumption."""
    lines = [
        f"DATA CONTRACT: {model.__name__}",
        "",
    ]

    if model.__doc__:
        lines.append(f"PURPOSE: {model.__doc__.strip()}")
        lines.append("")

    if model._griot_primary_key:
        lines.append(f"PRIMARY KEY: {model._griot_primary_key}")
        lines.append("")

    lines.append("FIELDS:")
    lines.append("")

    for field_name, field_info in model._griot_fields.items():
        # Build a concise field description
        parts = [f"- {field_name} ({field_info.type.value})"]

        if field_info.nullable:
            parts.append(" [nullable]")
        if field_info.primary_key:
            parts.append(" [PK]")
        if field_info.unique:
            parts.append(" [unique]")

        lines.append("".join(parts))
        lines.append(f"  Description: {field_info.description}")

        # Add constraints
        constraints: list[str] = []
        if field_info.format:
            constraints.append(f"format={field_info.format.value}")
        if field_info.enum:
            enum_str = str(field_info.enum[:3])
            if len(field_info.enum) > 3:
                enum_str = enum_str[:-1] + ", ...]"
            constraints.append(f"values={enum_str}")
        if field_info.min_length is not None:
            constraints.append(f"min_len={field_info.min_length}")
        if field_info.max_length is not None:
            constraints.append(f"max_len={field_info.max_length}")
        if field_info.ge is not None:
            constraints.append(f"min={field_info.ge}")
        if field_info.le is not None:
            constraints.append(f"max={field_info.le}")
        if field_info.pattern:
            constraints.append(f"pattern={field_info.pattern}")
        if field_info.unit:
            constraints.append(f"unit={field_info.unit}")

        if constraints:
            lines.append(f"  Constraints: {', '.join(constraints)}")

        lines.append("")

    # Add usage guidance for LLM
    lines.append("VALIDATION RULES:")
    lines.append("- All non-nullable fields are required")
    lines.append("- Type constraints must be strictly followed")
    lines.append("- Enum fields only accept listed values")
    lines.append("- Pattern fields must match the regex")
    lines.append("")

    return "\n".join(lines)


def _datatype_to_schema_org(dtype: DataType) -> str:
    """Convert DataType to schema.org type."""
    mapping = {
        DataType.STRING: "Text",
        DataType.INTEGER: "Integer",
        DataType.FLOAT: "Number",
        DataType.BOOLEAN: "Boolean",
        DataType.DATE: "Date",
        DataType.DATETIME: "DateTime",
        DataType.ARRAY: "ItemList",
        DataType.OBJECT: "Thing",
        DataType.ANY: "DataType",
    }
    return mapping.get(dtype, "Text")
