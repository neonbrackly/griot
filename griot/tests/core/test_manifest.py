"""
Tests for griot_core.manifest module.

Tests manifest export functionality for JSON-LD, Markdown, and LLM context.
"""
from __future__ import annotations

import json
from typing import Optional

import pytest

from griot_core.manifest import export_manifest
from griot_core.models import Field, GriotModel


# =============================================================================
# TEST MODELS
# =============================================================================


class Customer(GriotModel):
    """Customer profile contract for AI systems."""

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
        unit="years",
    )
    status: str = Field(
        description="Account status",
        enum=["active", "inactive", "suspended"],
    )


class NullableModel(GriotModel):
    """Model with nullable fields."""

    id: str = Field(description="ID", primary_key=True)
    optional: Optional[str] = Field(description="Optional field", nullable=True)


class SimpleModel(GriotModel):
    name: str = Field(description="Name")
    value: int = Field(description="Value")


# =============================================================================
# JSON-LD EXPORT TESTS
# =============================================================================


class TestExportJsonLd:
    """Tests for JSON-LD export format."""

    def test_export_json_ld_basic(self) -> None:
        """Test basic JSON-LD export."""
        result = export_manifest(Customer, format="json_ld")

        # Should be valid JSON
        data = json.loads(result)

        # Check required JSON-LD fields
        assert "@context" in data
        assert "@type" in data
        assert data["@type"] == "DataContract"
        assert "name" in data
        assert data["name"] == "Customer"

    def test_export_json_ld_context(self) -> None:
        """Test JSON-LD context structure."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        context = data["@context"]
        assert "@vocab" in context
        assert "schema.org" in context["@vocab"]
        assert "griot" in context

    def test_export_json_ld_id(self) -> None:
        """Test JSON-LD @id field."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        assert "@id" in data
        assert "Customer" in data["@id"]

    def test_export_json_ld_properties(self) -> None:
        """Test JSON-LD properties structure."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        assert "properties" in data
        props = data["properties"]

        # Check customer_id property
        assert "customer_id" in props
        assert "@type" in props["customer_id"]
        assert "description" in props["customer_id"]

        # Check email property
        assert "email" in props
        assert props["email"]["format"] == "email"

    def test_export_json_ld_nullable(self) -> None:
        """Test JSON-LD handles nullable fields."""
        result = export_manifest(NullableModel, format="json_ld")
        data = json.loads(result)

        props = data["properties"]
        assert "optional" in props
        assert props["optional"].get("nullable") is True

    def test_export_json_ld_enum(self) -> None:
        """Test JSON-LD handles enum fields."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        props = data["properties"]
        assert "status" in props
        assert "enum" in props["status"]
        assert props["status"]["enum"] == ["active", "inactive", "suspended"]

    def test_export_json_ld_unit(self) -> None:
        """Test JSON-LD handles unit metadata."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        props = data["properties"]
        assert "age" in props
        assert props["age"].get("unitCode") == "years"

    def test_export_json_ld_identifier(self) -> None:
        """Test JSON-LD includes primary key as identifier."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        assert data.get("identifier") == "customer_id"

    def test_export_json_ld_description(self) -> None:
        """Test JSON-LD includes model description."""
        result = export_manifest(Customer, format="json_ld")
        data = json.loads(result)

        assert "description" in data
        assert "Customer profile" in data["description"]


# =============================================================================
# MARKDOWN EXPORT TESTS
# =============================================================================


class TestExportMarkdown:
    """Tests for Markdown export format."""

    def test_export_markdown_basic(self) -> None:
        """Test basic Markdown export."""
        result = export_manifest(Customer, format="markdown")

        assert "# Customer" in result
        assert "## Fields" in result

    def test_export_markdown_table(self) -> None:
        """Test Markdown includes field table."""
        result = export_manifest(Customer, format="markdown")

        assert "| Field | Type | Description | Constraints |" in result
        assert "|-------|------|-------------|-------------|" in result

    def test_export_markdown_field_entries(self) -> None:
        """Test Markdown includes field entries."""
        result = export_manifest(Customer, format="markdown")

        assert "`customer_id`" in result
        assert "`email`" in result
        assert "`age`" in result
        assert "`status`" in result

    def test_export_markdown_constraints(self) -> None:
        """Test Markdown shows constraints."""
        result = export_manifest(Customer, format="markdown")

        # Check for constraint indicators
        assert "PK" in result  # Primary key
        assert "format:email" in result
        assert ">=" in result or "ge:" in result  # ge constraint
        assert "enum" in result

    def test_export_markdown_nullable(self) -> None:
        """Test Markdown shows nullable indicator."""
        result = export_manifest(NullableModel, format="markdown")

        # Nullable type should have ? suffix
        assert "string?" in result or "nullable" in result.lower()

    def test_export_markdown_field_details(self) -> None:
        """Test Markdown includes field details section."""
        result = export_manifest(Customer, format="markdown")

        assert "## Field Details" in result
        assert "### customer_id" in result
        assert "**Type:**" in result
        assert "**Description:**" in result

    def test_export_markdown_enum_values(self) -> None:
        """Test Markdown shows enum values in details."""
        result = export_manifest(Customer, format="markdown")

        assert "**Allowed values:**" in result
        assert "active" in result
        assert "inactive" in result
        assert "suspended" in result

    def test_export_markdown_pattern(self) -> None:
        """Test Markdown shows pattern in details."""
        result = export_manifest(Customer, format="markdown")

        assert "**Pattern:**" in result
        assert "CUST" in result

    def test_export_markdown_unit(self) -> None:
        """Test Markdown shows unit in details."""
        result = export_manifest(Customer, format="markdown")

        assert "**Unit:**" in result
        assert "years" in result

    def test_export_markdown_description(self) -> None:
        """Test Markdown includes model docstring."""
        result = export_manifest(Customer, format="markdown")

        assert "Customer profile" in result


# =============================================================================
# LLM CONTEXT EXPORT TESTS
# =============================================================================


class TestExportLlmContext:
    """Tests for LLM context export format."""

    def test_export_llm_context_basic(self) -> None:
        """Test basic LLM context export."""
        result = export_manifest(Customer, format="llm_context")

        assert "DATA CONTRACT: Customer" in result
        assert "FIELDS:" in result

    def test_export_llm_context_purpose(self) -> None:
        """Test LLM context includes purpose."""
        result = export_manifest(Customer, format="llm_context")

        assert "PURPOSE:" in result
        assert "Customer profile" in result

    def test_export_llm_context_primary_key(self) -> None:
        """Test LLM context shows primary key."""
        result = export_manifest(Customer, format="llm_context")

        assert "PRIMARY KEY: customer_id" in result

    def test_export_llm_context_fields(self) -> None:
        """Test LLM context lists fields with types."""
        result = export_manifest(Customer, format="llm_context")

        assert "- customer_id (string)" in result
        assert "- email (string)" in result
        assert "- age (integer)" in result
        assert "- status (string)" in result

    def test_export_llm_context_nullable(self) -> None:
        """Test LLM context shows nullable indicator."""
        result = export_manifest(NullableModel, format="llm_context")

        assert "[nullable]" in result

    def test_export_llm_context_pk_indicator(self) -> None:
        """Test LLM context shows PK indicator."""
        result = export_manifest(Customer, format="llm_context")

        assert "[PK]" in result

    def test_export_llm_context_descriptions(self) -> None:
        """Test LLM context includes field descriptions."""
        result = export_manifest(Customer, format="llm_context")

        assert "Description:" in result
        assert "Unique customer identifier" in result
        assert "Customer email address" in result

    def test_export_llm_context_constraints(self) -> None:
        """Test LLM context shows constraints."""
        result = export_manifest(Customer, format="llm_context")

        assert "Constraints:" in result
        assert "format=email" in result
        assert "min=" in result or "max=" in result  # ge/le shown as min/max

    def test_export_llm_context_enum_values(self) -> None:
        """Test LLM context shows enum values."""
        result = export_manifest(Customer, format="llm_context")

        assert "values=" in result
        assert "active" in result

    def test_export_llm_context_unit(self) -> None:
        """Test LLM context shows unit."""
        result = export_manifest(Customer, format="llm_context")

        assert "unit=years" in result

    def test_export_llm_context_validation_rules(self) -> None:
        """Test LLM context includes validation rules section."""
        result = export_manifest(Customer, format="llm_context")

        assert "VALIDATION RULES:" in result
        assert "non-nullable fields are required" in result
        assert "Type constraints" in result
        assert "Enum fields" in result


# =============================================================================
# FORMAT VALIDATION TESTS
# =============================================================================


class TestExportFormat:
    """Tests for format validation."""

    def test_invalid_format_raises(self) -> None:
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            export_manifest(Customer, format="invalid_format")

        assert "Unknown format" in str(exc_info.value)
        assert "invalid_format" in str(exc_info.value)

    def test_valid_formats(self) -> None:
        """Test all valid formats work."""
        for fmt in ["json_ld", "markdown", "llm_context"]:
            result = export_manifest(Customer, format=fmt)
            assert result is not None
            assert len(result) > 0


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestExportEdgeCases:
    """Tests for edge cases in manifest export."""

    def test_export_model_without_docstring(self) -> None:
        """Test export handles model without docstring."""
        result = export_manifest(SimpleModel, format="markdown")

        assert "# SimpleModel" in result

    def test_export_model_without_primary_key(self) -> None:
        """Test export handles model without primary key."""
        result = export_manifest(SimpleModel, format="llm_context")

        # Should not have PRIMARY KEY line
        assert "PRIMARY KEY:" not in result

    def test_export_all_formats_consistent(self) -> None:
        """Test all formats include the same fields."""
        json_result = export_manifest(Customer, format="json_ld")
        md_result = export_manifest(Customer, format="markdown")
        llm_result = export_manifest(Customer, format="llm_context")

        # All should mention the fields
        for field_name in ["customer_id", "email", "age", "status"]:
            assert field_name in json_result
            assert field_name in md_result
            assert field_name in llm_result
