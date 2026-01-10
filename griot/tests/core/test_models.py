"""
Tests for griot_core.models module.

Tests Field, FieldInfo, GriotModel and related functionality.
"""
from __future__ import annotations

from typing import Any, Optional

import pytest

from griot_core.models import Field, FieldInfo, GriotModel
from griot_core.types import AggregationType, DataType, FieldFormat


class TestField:
    """Tests for Field class."""

    def test_field_creation_basic(self) -> None:
        """Test creating a basic field with description."""
        field = Field(description="A test field")
        assert field.description == "A test field"
        assert field.nullable is False
        assert field.primary_key is False
        assert field.unique is False

    def test_field_with_string_constraints(self) -> None:
        """Test field with string-specific constraints."""
        field = Field(
            description="Email field",
            min_length=5,
            max_length=255,
            format="email",
        )
        assert field.min_length == 5
        assert field.max_length == 255
        assert field.format == FieldFormat.EMAIL

    def test_field_with_pattern(self) -> None:
        """Test field with regex pattern."""
        field = Field(
            description="ID field",
            pattern=r"^CUST-\d{6}$",
        )
        assert field.pattern == r"^CUST-\d{6}$"

    def test_field_with_invalid_pattern_raises(self) -> None:
        """Test that invalid regex pattern raises ValueError."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            Field(description="Bad pattern", pattern=r"[invalid")

    def test_field_with_numeric_constraints(self) -> None:
        """Test field with numeric constraints."""
        field = Field(
            description="Age field",
            ge=0,
            le=150,
            unit="years",
        )
        assert field.ge == 0
        assert field.le == 150
        assert field.unit == "years"

    def test_field_ge_gt_conflict_raises(self) -> None:
        """Test that specifying both ge and gt raises ValueError."""
        with pytest.raises(ValueError, match="Cannot specify both 'ge' and 'gt'"):
            Field(description="Conflicting field", ge=0, gt=0)

    def test_field_le_lt_conflict_raises(self) -> None:
        """Test that specifying both le and lt raises ValueError."""
        with pytest.raises(ValueError, match="Cannot specify both 'le' and 'lt'"):
            Field(description="Conflicting field", le=100, lt=100)

    def test_field_invalid_range_raises(self) -> None:
        """Test that invalid ranges raise ValueError."""
        with pytest.raises(ValueError, match="Invalid range"):
            Field(description="Bad range", ge=100, le=50)

    def test_field_invalid_length_range_raises(self) -> None:
        """Test that min_length > max_length raises ValueError."""
        with pytest.raises(ValueError, match="min_length"):
            Field(description="Bad length", min_length=100, max_length=10)

    def test_field_with_enum(self) -> None:
        """Test field with enum constraint."""
        field = Field(
            description="Status field",
            enum=["active", "inactive", "suspended"],
        )
        assert field.enum == ["active", "inactive", "suspended"]

    def test_field_with_default(self) -> None:
        """Test field with default value."""
        field = Field(description="With default", default="unknown")
        assert field.has_default() is True
        assert field.get_default() == "unknown"

    def test_field_without_default(self) -> None:
        """Test field without default value."""
        field = Field(description="No default")
        assert field.has_default() is False
        assert field.get_default() is None

    def test_field_with_default_factory(self) -> None:
        """Test field with default factory."""
        field = Field(description="With factory", default_factory=list)
        assert field.has_default() is True
        result1 = field.get_default()
        result2 = field.get_default()
        assert result1 == []
        assert result1 is not result2  # Should be different instances

    def test_field_default_and_factory_conflict(self) -> None:
        """Test that specifying both default and default_factory raises."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            Field(description="Conflict", default="x", default_factory=list)

    def test_field_with_aggregation(self) -> None:
        """Test field with aggregation hint."""
        field = Field(description="Amount", aggregation="sum")
        assert field.aggregation == AggregationType.SUM

    def test_field_with_glossary_term(self) -> None:
        """Test field with glossary term reference."""
        field = Field(description="Field", glossary_term="customer_id")
        assert field.glossary_term == "customer_id"

    def test_field_repr(self) -> None:
        """Test field string representation."""
        field = Field(description="ID", primary_key=True, pattern=r"^ID-\d+$")
        repr_str = repr(field)
        assert "description='ID'" in repr_str
        assert "primary_key=True" in repr_str
        assert "pattern=" in repr_str

    def test_field_to_field_info(self) -> None:
        """Test converting Field to FieldInfo."""
        field = Field(
            description="Customer ID",
            primary_key=True,
            pattern=r"^CUST-\d{6}$",
            min_length=11,
            max_length=11,
        )
        info = field.to_field_info("customer_id", str)

        assert info.name == "customer_id"
        assert info.type == DataType.STRING
        assert info.python_type == str
        assert info.description == "Customer ID"
        assert info.primary_key is True
        assert info.pattern == r"^CUST-\d{6}$"
        assert info.min_length == 11
        assert info.max_length == 11


class TestFieldInfo:
    """Tests for FieldInfo class."""

    def test_field_info_creation(self) -> None:
        """Test creating a FieldInfo instance."""
        info = FieldInfo(
            name="test_field",
            type=DataType.STRING,
            python_type=str,
            description="A test field",
        )
        assert info.name == "test_field"
        assert info.type == DataType.STRING
        assert info.python_type == str
        assert info.description == "A test field"

    def test_field_info_to_dict(self) -> None:
        """Test converting FieldInfo to dictionary."""
        info = FieldInfo(
            name="email",
            type=DataType.STRING,
            python_type=str,
            description="Email address",
            format=FieldFormat.EMAIL,
            max_length=255,
        )
        result = info.to_dict()

        assert result["name"] == "email"
        assert result["type"] == "string"
        assert result["description"] == "Email address"
        assert result["format"] == "email"
        assert result["max_length"] == 255

    def test_field_info_get_constraints(self) -> None:
        """Test getting active constraints from FieldInfo."""
        info = FieldInfo(
            name="age",
            type=DataType.INTEGER,
            python_type=int,
            description="Age",
            ge=0,
            le=150,
        )
        constraints = info.get_constraints()

        assert constraints["ge"] == 0
        assert constraints["le"] == 150
        assert "min_length" not in constraints  # Not set


class TestGriotModel:
    """Tests for GriotModel base class."""

    def test_simple_model_definition(self) -> None:
        """Test defining a simple model."""

        class SimpleModel(GriotModel):
            name: str = Field(description="Name field")
            age: int = Field(description="Age field", ge=0)

        fields = SimpleModel.list_fields()
        assert len(fields) == 2

        name_field = SimpleModel.get_field("name")
        assert name_field is not None
        assert name_field.name == "name"
        assert name_field.type == DataType.STRING

        age_field = SimpleModel.get_field("age")
        assert age_field is not None
        assert age_field.name == "age"
        assert age_field.type == DataType.INTEGER

    def test_model_with_primary_key(self) -> None:
        """Test model with primary key field."""

        class ModelWithPK(GriotModel):
            id: str = Field(description="Primary key", primary_key=True)
            value: str = Field(description="Value")

        assert ModelWithPK.get_primary_key() == "id"

    def test_model_without_primary_key(self) -> None:
        """Test model without primary key."""

        class ModelNoPK(GriotModel):
            field1: str = Field(description="Field 1")
            field2: str = Field(description="Field 2")

        assert ModelNoPK.get_primary_key() is None

    def test_model_field_names(self) -> None:
        """Test getting field names from model."""

        class NamedModel(GriotModel):
            alpha: str = Field(description="Alpha")
            beta: int = Field(description="Beta")
            gamma: float = Field(description="Gamma")

        names = NamedModel.field_names()
        assert set(names) == {"alpha", "beta", "gamma"}

    def test_model_with_optional_field(self) -> None:
        """Test model with optional (nullable) field."""

        class OptionalModel(GriotModel):
            required: str = Field(description="Required field")
            optional: Optional[str] = Field(description="Optional field", nullable=True)

        optional_field = OptionalModel.get_field("optional")
        assert optional_field is not None
        assert optional_field.nullable is True

    def test_model_inheritance(self) -> None:
        """Test that models can inherit fields."""

        class BaseModel(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            created_at: str = Field(description="Creation timestamp")

        class ExtendedModel(BaseModel):
            name: str = Field(description="Name")

        fields = ExtendedModel.list_fields()
        field_names = {f.name for f in fields}

        assert "id" in field_names
        assert "created_at" in field_names
        assert "name" in field_names
        assert ExtendedModel.get_primary_key() == "id"

    def test_model_to_dict(self) -> None:
        """Test converting model to dictionary."""

        class DictModel(GriotModel):
            """A model for testing to_dict."""

            field1: str = Field(description="Field 1")
            field2: int = Field(description="Field 2", ge=0)

        result = DictModel.to_dict()

        assert result["name"] == "DictModel"
        assert "field1" in result["fields"]
        assert "field2" in result["fields"]
        assert result["fields"]["field2"]["ge"] == 0

    def test_model_repr(self) -> None:
        """Test model string representation."""

        class ReprModel(GriotModel):
            a: str = Field(description="A")
            b: str = Field(description="B")

        instance = ReprModel()
        repr_str = repr(instance)
        assert "ReprModel" in repr_str
        assert "2 fields" in repr_str


class TestComplexModel:
    """Tests for complex model definitions."""

    def test_customer_model(self) -> None:
        """Test a realistic customer model definition."""

        class Customer(GriotModel):
            """Customer profile contract."""

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

        assert Customer.get_primary_key() == "customer_id"
        assert len(Customer.list_fields()) == 4

        email_field = Customer.get_field("email")
        assert email_field is not None
        assert email_field.format == FieldFormat.EMAIL
        assert email_field.max_length == 255

        age_field = Customer.get_field("age")
        assert age_field is not None
        assert age_field.ge == 0
        assert age_field.le == 150
        assert age_field.unit == "years"

        status_field = Customer.get_field("status")
        assert status_field is not None
        assert status_field.enum == ["active", "inactive", "suspended"]

    def test_model_with_all_constraint_types(self) -> None:
        """Test model using all available constraints."""

        class FullConstraintModel(GriotModel):
            string_field: str = Field(
                description="String with constraints",
                min_length=1,
                max_length=100,
                pattern=r"^[A-Z]+$",
            )
            number_field: int = Field(
                description="Number with range",
                gt=0,
                lt=1000,
                multiple_of=5,
            )
            unique_field: str = Field(
                description="Unique field",
                unique=True,
            )
            enum_field: str = Field(
                description="Enum field",
                enum=["a", "b", "c"],
            )

        assert len(FullConstraintModel.list_fields()) == 4

        string_info = FullConstraintModel.get_field("string_field")
        assert string_info is not None
        constraints = string_info.get_constraints()
        assert "min_length" in constraints
        assert "max_length" in constraints
        assert "pattern" in constraints
