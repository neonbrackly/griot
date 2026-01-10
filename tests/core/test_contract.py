"""
Tests for griot_core.contract module.

Tests contract loading, saving, diffing, and linting functionality.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from griot_core.contract import (
    ConstraintChange,
    ContractDiff,
    LintIssue,
    MetadataChange,
    TypeChange,
    diff_contracts,
    lint_contract,
    load_contract,
    load_contract_from_dict,
    load_contract_from_string,
    model_to_yaml,
)
from griot_core.exceptions import ContractNotFoundError, ContractParseError
from griot_core.models import Field, GriotModel
from griot_core.types import DataType, Severity


# =============================================================================
# TEST MODELS FOR DIFFING
# =============================================================================


class BaseCustomer(GriotModel):
    """Base customer model for diff testing."""

    customer_id: str = Field(description="Customer ID", primary_key=True)
    email: str = Field(description="Email address", format="email")
    age: int = Field(description="Age", ge=0, le=150)


class ModifiedCustomer(GriotModel):
    """Modified customer model with changes."""

    customer_id: str = Field(description="Customer ID", primary_key=True)
    email: str = Field(description="Customer email", format="email", max_length=255)
    # age field removed - breaking change
    name: str = Field(description="Customer name")  # new field


class ConstraintChangedCustomer(GriotModel):
    """Customer with changed constraints."""

    customer_id: str = Field(description="Customer ID", primary_key=True)
    email: str = Field(description="Email address", format="email")
    age: int = Field(description="Age", ge=18, le=120)  # Stricter constraints


# =============================================================================
# LOAD CONTRACT TESTS
# =============================================================================


class TestLoadContract:
    """Tests for contract loading functions."""

    def test_load_contract_file_not_found(self, tmp_path: Path) -> None:
        """Test that loading non-existent file raises ContractNotFoundError."""
        with pytest.raises(ContractNotFoundError) as exc_info:
            load_contract(tmp_path / "nonexistent.yaml")
        assert "nonexistent.yaml" in str(exc_info.value)

    def test_load_contract_from_file(
        self, tmp_path: Path, sample_contract_yaml: str
    ) -> None:
        """Test loading contract from a YAML file."""
        contract_file = tmp_path / "contract.yaml"
        contract_file.write_text(sample_contract_yaml)

        model = load_contract(contract_file)

        assert model.__name__ == "Customer"
        assert "customer_id" in model._griot_fields
        assert "email" in model._griot_fields
        assert "age" in model._griot_fields

    def test_load_contract_from_string(self, sample_contract_yaml: str) -> None:
        """Test loading contract from YAML string."""
        model = load_contract_from_string(sample_contract_yaml)

        assert model.__name__ == "Customer"
        fields = model._griot_fields
        assert fields["customer_id"].primary_key is True
        assert fields["email"].max_length == 255
        assert fields["age"].ge == 0
        assert fields["age"].le == 150

    def test_load_contract_from_dict(self) -> None:
        """Test loading contract from dictionary."""
        data = {
            "name": "TestContract",
            "description": "A test contract",
            "fields": {
                "id": {
                    "type": "string",
                    "description": "Identifier",
                    "primary_key": True,
                },
                "value": {
                    "type": "integer",
                    "description": "Value",
                    "ge": 0,
                },
            },
        }
        model = load_contract_from_dict(data)

        assert model.__name__ == "TestContract"
        assert model.__doc__ == "A test contract"
        assert "id" in model._griot_fields
        assert model._griot_fields["id"].primary_key is True
        assert model._griot_fields["value"].ge == 0

    def test_load_contract_with_enum(self) -> None:
        """Test loading contract with enum constraint."""
        yaml_content = """
name: StatusContract
fields:
  status:
    type: string
    description: Status field
    enum: [active, inactive, pending]
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_fields["status"].enum == ["active", "inactive", "pending"]

    def test_load_contract_with_format(self) -> None:
        """Test loading contract with format constraint."""
        yaml_content = """
name: EmailContract
fields:
  email:
    type: string
    description: Email field
    format: email
"""
        model = load_contract_from_string(yaml_content)
        from griot_core.types import FieldFormat

        assert model._griot_fields["email"].format == FieldFormat.EMAIL

    def test_load_contract_with_aggregation(self) -> None:
        """Test loading contract with aggregation hint."""
        yaml_content = """
name: MetricsContract
fields:
  total:
    type: float
    description: Total amount
    aggregation: sum
"""
        model = load_contract_from_string(yaml_content)
        from griot_core.types import AggregationType

        assert model._griot_fields["total"].aggregation == AggregationType.SUM

    def test_load_contract_with_default(self) -> None:
        """Test loading contract with default value."""
        yaml_content = """
name: DefaultContract
fields:
  status:
    type: string
    description: Status
    default: unknown
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_fields["status"].default == "unknown"

    def test_load_contract_simple_field(self) -> None:
        """Test loading contract with simple field (just name, no constraints)."""
        data = {
            "name": "SimpleContract",
            "fields": {
                "simple_field": "string",
            },
        }
        model = load_contract_from_dict(data)
        assert "simple_field" in model._griot_fields

    def test_load_contract_all_types(self) -> None:
        """Test loading contract with all data types."""
        yaml_content = """
name: AllTypesContract
fields:
  string_field:
    type: string
    description: String
  int_field:
    type: integer
    description: Integer
  float_field:
    type: float
    description: Float
  bool_field:
    type: boolean
    description: Boolean
  date_field:
    type: date
    description: Date
  datetime_field:
    type: datetime
    description: Datetime
  array_field:
    type: array
    description: Array
  object_field:
    type: object
    description: Object
"""
        model = load_contract_from_string(yaml_content)

        assert model._griot_fields["string_field"].type == DataType.STRING
        assert model._griot_fields["int_field"].type == DataType.INTEGER
        assert model._griot_fields["float_field"].type == DataType.FLOAT
        assert model._griot_fields["bool_field"].type == DataType.BOOLEAN


# =============================================================================
# MODEL TO YAML TESTS
# =============================================================================


class TestModelToYaml:
    """Tests for model_to_yaml function."""

    def test_model_to_yaml_basic(self) -> None:
        """Test converting a basic model to YAML."""

        class SimpleModel(GriotModel):
            """Simple test model."""

            name: str = Field(description="Name field")

        yaml_str = model_to_yaml(SimpleModel)

        assert "name: SimpleModel" in yaml_str
        assert "description: Simple test model" in yaml_str
        assert "fields:" in yaml_str
        assert "name:" in yaml_str

    def test_model_to_yaml_with_constraints(self) -> None:
        """Test converting a model with constraints to YAML."""

        class ConstrainedModel(GriotModel):
            id: str = Field(
                description="ID", primary_key=True, pattern=r"^ID-\d+$", min_length=5
            )
            age: int = Field(description="Age", ge=0, le=150)

        yaml_str = model_to_yaml(ConstrainedModel)

        assert "primary_key: true" in yaml_str.lower() or "primary_key: True" in yaml_str
        assert "min_length:" in yaml_str
        assert "ge:" in yaml_str
        assert "le:" in yaml_str

    def test_model_to_yaml_with_nullable(self) -> None:
        """Test converting a model with nullable field to YAML."""

        class NullableModel(GriotModel):
            optional: str = Field(description="Optional", nullable=True)

        yaml_str = model_to_yaml(NullableModel)
        assert "nullable: true" in yaml_str.lower() or "nullable: True" in yaml_str

    def test_model_to_yaml_with_enum(self) -> None:
        """Test converting a model with enum to YAML."""

        class EnumModel(GriotModel):
            status: str = Field(
                description="Status", enum=["active", "inactive", "pending"]
            )

        yaml_str = model_to_yaml(EnumModel)
        assert "enum:" in yaml_str
        assert "active" in yaml_str

    def test_model_to_yaml_roundtrip(self) -> None:
        """Test that model->YAML->model preserves structure."""

        class RoundtripModel(GriotModel):
            """Test model for roundtrip."""

            id: str = Field(description="ID", primary_key=True)
            value: int = Field(description="Value", ge=0)

        yaml_str = model_to_yaml(RoundtripModel)
        loaded_model = load_contract_from_string(yaml_str)

        assert loaded_model.__name__ == "RoundtripModel"
        assert "id" in loaded_model._griot_fields
        assert loaded_model._griot_fields["id"].primary_key is True


# =============================================================================
# CONTRACT DIFF TESTS
# =============================================================================


class TestContractDiff:
    """Tests for contract diffing functionality."""

    def test_diff_identical_contracts(self) -> None:
        """Test diffing identical contracts shows no changes."""
        diff = diff_contracts(BaseCustomer, BaseCustomer)

        assert diff.has_breaking_changes is False
        assert len(diff.added_fields) == 0
        assert len(diff.removed_fields) == 0
        assert len(diff.type_changes) == 0
        assert len(diff.constraint_changes) == 0

    def test_diff_added_fields(self) -> None:
        """Test diffing detects added fields."""

        class Extended(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email: str = Field(description="Email")
            age: int = Field(description="Age")
            new_field: str = Field(description="New field")

        diff = diff_contracts(BaseCustomer, Extended)

        assert "new_field" in diff.added_fields
        assert diff.has_breaking_changes is False  # Adding is not breaking

    def test_diff_removed_fields(self) -> None:
        """Test diffing detects removed fields as breaking changes."""
        diff = diff_contracts(BaseCustomer, ModifiedCustomer)

        assert "age" in diff.removed_fields
        assert diff.has_breaking_changes is True

    def test_diff_constraint_changes(self) -> None:
        """Test diffing detects constraint changes."""
        diff = diff_contracts(BaseCustomer, ConstraintChangedCustomer)

        # ge changed from 0 to 18 (more restrictive - breaking)
        ge_changes = [c for c in diff.constraint_changes if c.constraint == "ge"]
        assert len(ge_changes) > 0
        assert diff.has_breaking_changes is True

    def test_diff_metadata_changes(self) -> None:
        """Test diffing detects metadata changes (non-breaking)."""

        class DescriptionChanged(GriotModel):
            customer_id: str = Field(description="Customer identifier", primary_key=True)
            email: str = Field(description="Contact email", format="email")
            age: int = Field(description="Customer age in years", ge=0, le=150)

        diff = diff_contracts(BaseCustomer, DescriptionChanged)

        assert len(diff.metadata_changes) > 0
        assert diff.has_breaking_changes is False  # Metadata is not breaking

    def test_diff_nullable_change_to_non_nullable(self) -> None:
        """Test that removing nullable is a breaking change."""

        class NullableModel(GriotModel):
            field: str = Field(description="Field", nullable=True)

        class NonNullableModel(GriotModel):
            field: str = Field(description="Field", nullable=False)

        diff = diff_contracts(NullableModel, NonNullableModel)

        nullable_changes = [
            c for c in diff.constraint_changes if c.constraint == "nullable"
        ]
        assert len(nullable_changes) > 0
        assert diff.has_breaking_changes is True

    def test_diff_summary(self) -> None:
        """Test diff summary generation."""
        diff = diff_contracts(BaseCustomer, ModifiedCustomer)
        summary = diff.summary()

        assert "BREAKING CHANGES" in summary
        assert "Removed fields" in summary

    def test_diff_to_markdown(self) -> None:
        """Test diff markdown report generation."""
        diff = diff_contracts(BaseCustomer, ModifiedCustomer)
        markdown = diff.to_markdown()

        assert "# Contract Diff Report" in markdown
        assert "WARNING" in markdown  # Breaking changes warning
        assert "Added Fields" in markdown or "Removed Fields" in markdown


class TestTypeChange:
    """Tests for TypeChange dataclass."""

    def test_type_change_creation(self) -> None:
        """Test creating a TypeChange."""
        change = TypeChange(
            field="age", from_type="integer", to_type="string", is_breaking=True
        )
        assert change.field == "age"
        assert change.from_type == "integer"
        assert change.to_type == "string"
        assert change.is_breaking is True


class TestConstraintChange:
    """Tests for ConstraintChange dataclass."""

    def test_constraint_change_creation(self) -> None:
        """Test creating a ConstraintChange."""
        change = ConstraintChange(
            field="age",
            constraint="ge",
            from_value=0,
            to_value=18,
            is_breaking=True,
        )
        assert change.field == "age"
        assert change.constraint == "ge"
        assert change.from_value == 0
        assert change.to_value == 18
        assert change.is_breaking is True


class TestMetadataChange:
    """Tests for MetadataChange dataclass."""

    def test_metadata_change_creation(self) -> None:
        """Test creating a MetadataChange."""
        change = MetadataChange(
            field="email",
            attribute="description",
            from_value="Email",
            to_value="Contact email",
        )
        assert change.field == "email"
        assert change.attribute == "description"


# =============================================================================
# CONTRACT LINT TESTS
# =============================================================================


class TestLintContract:
    """Tests for contract linting functionality."""

    def test_lint_no_primary_key(self) -> None:
        """Test linting warns about missing primary key."""

        class NoPKModel(GriotModel):
            field1: str = Field(description="Field 1")
            field2: str = Field(description="Field 2")

        issues = lint_contract(NoPKModel)

        g001_issues = [i for i in issues if i.code == "G001"]
        assert len(g001_issues) > 0
        assert g001_issues[0].severity == Severity.WARNING

    def test_lint_missing_description(self) -> None:
        """Test linting warns about missing/placeholder descriptions."""
        # Using Field: prefix indicates placeholder description
        data = {
            "name": "NoDescModel",
            "fields": {
                "field1": {
                    "type": "string",
                    "description": "Field: field1",
                },
            },
        }
        model = load_contract_from_dict(data)
        issues = lint_contract(model)

        g002_issues = [i for i in issues if i.code == "G002"]
        assert len(g002_issues) > 0

    def test_lint_unconstrained_string(self) -> None:
        """Test linting suggests constraints for unconstrained strings."""

        class UnconstrainedModel(GriotModel):
            name: str = Field(description="Name with no constraints")

        issues = lint_contract(UnconstrainedModel)

        g003_issues = [i for i in issues if i.code == "G003"]
        assert len(g003_issues) > 0
        assert g003_issues[0].severity == Severity.INFO

    def test_lint_unconstrained_numeric(self) -> None:
        """Test linting suggests range for unconstrained numbers."""

        class UnconstrainedNumModel(GriotModel):
            value: int = Field(description="Numeric value")

        issues = lint_contract(UnconstrainedNumModel)

        g004_issues = [i for i in issues if i.code == "G004"]
        assert len(g004_issues) > 0

    def test_lint_invalid_field_name(self) -> None:
        """Test linting warns about non-snake_case field names."""
        data = {
            "name": "BadNameModel",
            "fields": {
                "CamelCase": {"type": "string", "description": "Bad name"},
                "kebab-case": {"type": "string", "description": "Also bad"},
            },
        }
        model = load_contract_from_dict(data)
        issues = lint_contract(model)

        g005_issues = [i for i in issues if i.code == "G005"]
        assert len(g005_issues) >= 1

    def test_lint_well_formed_contract(self) -> None:
        """Test that well-formed contract has fewer warnings."""

        class WellFormedModel(GriotModel):
            """A well-documented model."""

            customer_id: str = Field(
                description="Unique customer identifier",
                primary_key=True,
                pattern=r"^CUST-\d+$",
            )
            email: str = Field(
                description="Customer contact email", format="email", max_length=255
            )
            age: int = Field(description="Customer age in years", ge=0, le=150)

        issues = lint_contract(WellFormedModel)

        # Should have no G001 (has primary key)
        g001_issues = [i for i in issues if i.code == "G001"]
        assert len(g001_issues) == 0

        # Should have no G003 (string fields have constraints)
        g003_issues = [i for i in issues if i.code == "G003"]
        assert len(g003_issues) == 0

    def test_lint_issue_str(self) -> None:
        """Test LintIssue string representation."""
        issue = LintIssue(
            code="G001",
            field=None,
            message="No primary key",
            severity=Severity.WARNING,
        )
        assert "[G001]" in str(issue)
        assert "No primary key" in str(issue)

    def test_lint_issue_with_field(self) -> None:
        """Test LintIssue string with field name."""
        issue = LintIssue(
            code="G002",
            field="email",
            message="Missing description",
            severity=Severity.WARNING,
        )
        assert "(email)" in str(issue)


class TestContractDiffDataclass:
    """Tests for ContractDiff dataclass."""

    def test_contract_diff_defaults(self) -> None:
        """Test ContractDiff default values."""
        diff = ContractDiff()

        assert diff.has_breaking_changes is False
        assert diff.added_fields == []
        assert diff.removed_fields == []
        assert diff.type_changes == []
        assert diff.constraint_changes == []
        assert diff.metadata_changes == []

    def test_contract_diff_no_differences_summary(self) -> None:
        """Test summary for no differences."""
        diff = ContractDiff()
        summary = diff.summary()

        assert "No breaking changes" in summary


# =============================================================================
# ADDITIONAL COVERAGE TESTS
# =============================================================================


class TestContractDiffMarkdown:
    """Tests for ContractDiff.to_markdown() method."""

    def test_to_markdown_with_type_changes(self) -> None:
        """Test markdown output includes type changes."""

        class IntModel(GriotModel):
            value: int = Field(description="Value")

        class StrModel(GriotModel):
            value: str = Field(description="Value")

        diff = diff_contracts(IntModel, StrModel)
        md = diff.to_markdown()

        assert "Type Changes" in md
        assert "value" in md

    def test_to_markdown_with_constraint_changes(self) -> None:
        """Test markdown output includes constraint changes."""
        diff = diff_contracts(BaseCustomer, ConstraintChangedCustomer)
        md = diff.to_markdown()

        assert "Constraint Changes" in md

    def test_to_markdown_empty_diff(self) -> None:
        """Test markdown output for empty diff."""
        diff = ContractDiff()
        md = diff.to_markdown()

        assert "# Contract Diff Report" in md


class TestDiffTypeWidening:
    """Tests for type widening detection in diff."""

    def test_int_to_float_is_widening(self) -> None:
        """Test int to float is non-breaking (widening)."""

        class IntModel(GriotModel):
            value: int = Field(description="Value")

        class FloatModel(GriotModel):
            value: float = Field(description="Value")

        diff = diff_contracts(IntModel, FloatModel)

        # int to float should not be breaking
        type_changes = diff.type_changes
        assert len(type_changes) == 1
        assert type_changes[0].is_breaking is False

    def test_type_to_any_is_widening(self) -> None:
        """Test any specific type to 'any' is widening."""

        class SpecificModel(GriotModel):
            value: str = Field(description="Value")

        data = {
            "name": "AnyModel",
            "fields": {
                "value": {"type": "any", "description": "Value"},
            },
        }
        AnyModel = load_contract_from_dict(data)

        diff = diff_contracts(SpecificModel, AnyModel)

        # string to any should not be breaking
        type_changes = diff.type_changes
        assert len(type_changes) == 1
        assert type_changes[0].is_breaking is False


class TestConstraintBreaking:
    """Tests for constraint breaking change detection."""

    def test_adding_constraint_is_breaking(self) -> None:
        """Test that adding a new constraint is breaking."""

        class NoConstraint(GriotModel):
            value: int = Field(description="Value")

        class WithConstraint(GriotModel):
            value: int = Field(description="Value", ge=0)

        diff = diff_contracts(NoConstraint, WithConstraint)

        # Adding ge is breaking
        constraint_changes = [c for c in diff.constraint_changes if c.constraint == "ge"]
        assert len(constraint_changes) > 0
        assert constraint_changes[0].is_breaking is True

    def test_removing_constraint_is_not_breaking(self) -> None:
        """Test that removing a constraint is not breaking."""

        class WithConstraint(GriotModel):
            value: int = Field(description="Value", ge=0)

        class NoConstraint(GriotModel):
            value: int = Field(description="Value")

        diff = diff_contracts(WithConstraint, NoConstraint)

        # Removing ge is not breaking
        constraint_changes = [c for c in diff.constraint_changes if c.constraint == "ge"]
        assert len(constraint_changes) > 0
        assert constraint_changes[0].is_breaking is False

    def test_le_decreasing_is_breaking(self) -> None:
        """Test that decreasing le (max) is breaking."""

        class LooseModel(GriotModel):
            value: int = Field(description="Value", le=100)

        class StrictModel(GriotModel):
            value: int = Field(description="Value", le=50)

        diff = diff_contracts(LooseModel, StrictModel)
        assert diff.has_breaking_changes is True

    def test_lt_decreasing_is_breaking(self) -> None:
        """Test that decreasing lt is breaking."""

        class LooseModel(GriotModel):
            value: int = Field(description="Value", lt=100)

        class StrictModel(GriotModel):
            value: int = Field(description="Value", lt=50)

        diff = diff_contracts(LooseModel, StrictModel)
        assert diff.has_breaking_changes is True

    def test_min_length_increasing_is_breaking(self) -> None:
        """Test that increasing min_length is breaking."""

        class LooseModel(GriotModel):
            code: str = Field(description="Code", min_length=1)

        class StrictModel(GriotModel):
            code: str = Field(description="Code", min_length=5)

        diff = diff_contracts(LooseModel, StrictModel)
        assert diff.has_breaking_changes is True

    def test_max_length_decreasing_is_breaking(self) -> None:
        """Test that decreasing max_length is breaking."""

        class LooseModel(GriotModel):
            code: str = Field(description="Code", max_length=100)

        class StrictModel(GriotModel):
            code: str = Field(description="Code", max_length=50)

        diff = diff_contracts(LooseModel, StrictModel)
        assert diff.has_breaking_changes is True

    def test_pattern_change_is_breaking(self) -> None:
        """Test that any pattern change is breaking."""

        class OriginalModel(GriotModel):
            code: str = Field(description="Code", pattern=r"^A-\d+$")

        class ChangedModel(GriotModel):
            code: str = Field(description="Code", pattern=r"^B-\d+$")

        diff = diff_contracts(OriginalModel, ChangedModel)
        assert diff.has_breaking_changes is True

    def test_enum_removing_value_is_breaking(self) -> None:
        """Test that removing enum value is breaking."""

        class WideModel(GriotModel):
            status: str = Field(description="Status", enum=["a", "b", "c"])

        class NarrowModel(GriotModel):
            status: str = Field(description="Status", enum=["a", "b"])

        diff = diff_contracts(WideModel, NarrowModel)
        assert diff.has_breaking_changes is True

    def test_enum_adding_value_is_not_breaking(self) -> None:
        """Test that adding enum value is not breaking."""

        class NarrowModel(GriotModel):
            status: str = Field(description="Status", enum=["a", "b"])

        class WideModel(GriotModel):
            status: str = Field(description="Status", enum=["a", "b", "c"])

        diff = diff_contracts(NarrowModel, WideModel)
        # Adding a value should not be breaking
        enum_changes = [c for c in diff.constraint_changes if c.constraint == "enum"]
        assert len(enum_changes) > 0
        assert enum_changes[0].is_breaking is False


class TestModelToYamlAdvanced:
    """Advanced tests for model_to_yaml."""

    def test_model_to_yaml_with_unique_field(self) -> None:
        """Test YAML export includes unique constraint."""

        class UniqueModel(GriotModel):
            code: str = Field(description="Unique code", unique=True)

        yaml_str = model_to_yaml(UniqueModel)
        assert "unique: true" in yaml_str.lower() or "unique: True" in yaml_str

    def test_model_to_yaml_with_format(self) -> None:
        """Test YAML export includes format."""

        class FormatModel(GriotModel):
            email: str = Field(description="Email", format="email")

        yaml_str = model_to_yaml(FormatModel)
        assert "format: email" in yaml_str

    def test_model_to_yaml_with_default(self) -> None:
        """Test YAML export includes default value."""

        class DefaultModel(GriotModel):
            status: str = Field(description="Status", default="active")

        yaml_str = model_to_yaml(DefaultModel)
        assert "default:" in yaml_str

    def test_model_to_yaml_with_unit(self) -> None:
        """Test YAML export includes unit."""

        class UnitModel(GriotModel):
            weight: float = Field(description="Weight", unit="kg")

        yaml_str = model_to_yaml(UnitModel)
        assert "unit: kg" in yaml_str

    def test_model_to_yaml_with_aggregation(self) -> None:
        """Test YAML export includes aggregation."""

        class AggModel(GriotModel):
            total: float = Field(description="Total", aggregation="sum")

        yaml_str = model_to_yaml(AggModel)
        assert "aggregation: sum" in yaml_str

    def test_model_to_yaml_with_glossary_term(self) -> None:
        """Test YAML export includes glossary term."""

        class GlossaryModel(GriotModel):
            mrr: float = Field(description="Monthly recurring revenue", glossary_term="mrr")

        yaml_str = model_to_yaml(GlossaryModel)
        assert "glossary_term: mrr" in yaml_str

    def test_model_to_yaml_with_gt_lt(self) -> None:
        """Test YAML export includes gt and lt constraints."""

        class RangeModel(GriotModel):
            value: int = Field(description="Value", gt=0, lt=100)

        yaml_str = model_to_yaml(RangeModel)
        assert "gt:" in yaml_str
        assert "lt:" in yaml_str

    def test_model_to_yaml_with_multiline_description(self) -> None:
        """Test YAML export handles multiline docstrings."""

        class MultilineDocModel(GriotModel):
            """This is a model with
            a multiline docstring
            for testing purposes."""

            field: str = Field(description="Field")

        yaml_str = model_to_yaml(MultilineDocModel)
        assert "description:" in yaml_str


class TestYamlParsing:
    """Tests for YAML parsing edge cases."""

    def test_parse_yaml_with_quoted_values(self) -> None:
        """Test parsing YAML with quoted string values."""
        yaml_content = """
name: QuotedContract
fields:
  message:
    type: string
    description: "A message with special: characters"
"""
        model = load_contract_from_string(yaml_content)
        assert model.__name__ == "QuotedContract"

    def test_parse_yaml_with_single_quotes(self) -> None:
        """Test parsing YAML with single-quoted values."""
        yaml_content = """
name: SingleQuoteContract
fields:
  code:
    type: string
    description: 'Single quoted description'
"""
        model = load_contract_from_string(yaml_content)
        assert "code" in model._griot_fields

    def test_parse_yaml_with_boolean_values(self) -> None:
        """Test parsing YAML boolean values."""
        yaml_content = """
name: BoolContract
fields:
  flag:
    type: boolean
    description: A flag
    nullable: yes
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_fields["flag"].nullable is True

    def test_parse_yaml_with_null_value(self) -> None:
        """Test parsing YAML null values."""
        yaml_content = """
name: NullContract
fields:
  optional:
    type: string
    description: Optional field
    default: null
"""
        model = load_contract_from_string(yaml_content)
        # null should be parsed as None, has_default should be True
        assert model._griot_fields["optional"].has_default is True

    def test_parse_yaml_with_float_value(self) -> None:
        """Test parsing YAML with float constraints."""
        yaml_content = """
name: FloatContract
fields:
  score:
    type: float
    description: Score
    ge: 0.0
    le: 100.5
"""
        model = load_contract_from_string(yaml_content)
        assert model._griot_fields["score"].ge == 0.0
        assert model._griot_fields["score"].le == 100.5

    def test_parse_yaml_comments_ignored(self) -> None:
        """Test that YAML comments are ignored."""
        yaml_content = """
# This is a comment
name: CommentContract
# Another comment
fields:
  # Field comment
  id:
    type: string
    description: ID field  # inline comment would break things
"""
        model = load_contract_from_string(yaml_content)
        assert model.__name__ == "CommentContract"

    def test_parse_yaml_empty_lines_handled(self) -> None:
        """Test that empty lines in YAML are handled."""
        yaml_content = """
name: EmptyLinesContract

fields:

  id:

    type: string

    description: ID
"""
        model = load_contract_from_string(yaml_content)
        assert model.__name__ == "EmptyLinesContract"
