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
        # Fields are now in list format (ODCS)
        assert isinstance(result["fields"], list)
        field_names = [f["name"] for f in result["fields"]]
        assert "field1" in field_names
        assert "field2" in field_names
        field2 = next(f for f in result["fields"] if f["name"] == "field2")
        assert field2["constraints"]["ge"] == 0

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


# =============================================================================
# PII/PRIVACY METADATA TESTS
# =============================================================================


class TestFieldPIIMetadata:
    """Tests for PII/privacy metadata in Field class."""

    def test_field_with_pii_category_string(self) -> None:
        """Test field with PII category as string."""
        from griot_core.types import PIICategory

        field = Field(
            description="Email address",
            pii_category="email",
        )
        assert field.pii_category == PIICategory.EMAIL

    def test_field_with_pii_category_enum(self) -> None:
        """Test field with PII category as enum."""
        from griot_core.types import PIICategory

        field = Field(
            description="Name",
            pii_category=PIICategory.NAME,
        )
        assert field.pii_category == PIICategory.NAME

    def test_field_with_sensitivity_level_string(self) -> None:
        """Test field with sensitivity level as string."""
        from griot_core.types import SensitivityLevel

        field = Field(
            description="SSN",
            sensitivity_level="confidential",
        )
        assert field.sensitivity_level == SensitivityLevel.CONFIDENTIAL

    def test_field_with_sensitivity_level_enum(self) -> None:
        """Test field with sensitivity level as enum."""
        from griot_core.types import SensitivityLevel

        field = Field(
            description="Internal data",
            sensitivity_level=SensitivityLevel.INTERNAL,
        )
        assert field.sensitivity_level == SensitivityLevel.INTERNAL

    def test_field_with_masking_strategy_string(self) -> None:
        """Test field with masking strategy as string."""
        from griot_core.types import MaskingStrategy

        field = Field(
            description="Credit card",
            masking_strategy="partial",
        )
        assert field.masking_strategy == MaskingStrategy.PARTIAL

    def test_field_with_legal_basis_string(self) -> None:
        """Test field with legal basis as string."""
        from griot_core.types import LegalBasis

        field = Field(
            description="Marketing preference",
            legal_basis="consent",
        )
        assert field.legal_basis == LegalBasis.CONSENT

    def test_field_with_full_pii_metadata(self) -> None:
        """Test field with all PII metadata."""
        from griot_core.types import (
            LegalBasis,
            MaskingStrategy,
            PIICategory,
            SensitivityLevel,
        )

        field = Field(
            description="Social Security Number",
            pii_category="ssn",
            sensitivity_level="restricted",
            masking_strategy="hash",
            legal_basis="legal_obligation",
            retention_days=365,
            consent_required=True,
        )
        assert field.pii_category == PIICategory.SSN
        assert field.sensitivity_level == SensitivityLevel.RESTRICTED
        assert field.masking_strategy == MaskingStrategy.HASH
        assert field.legal_basis == LegalBasis.LEGAL_OBLIGATION
        assert field.retention_days == 365
        assert field.consent_required is True


class TestFieldInfoPIIProperties:
    """Tests for PII-related properties in FieldInfo class."""

    def test_is_pii_true_for_email_category(self) -> None:
        """Test is_pii returns True for email PII category."""
        from griot_core.types import PIICategory

        info = FieldInfo(
            name="email",
            type=DataType.STRING,
            python_type=str,
            description="Email",
            pii_category=PIICategory.EMAIL,
        )
        assert info.is_pii is True

    def test_is_pii_false_for_none_category(self) -> None:
        """Test is_pii returns False for NONE PII category."""
        from griot_core.types import PIICategory

        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            pii_category=PIICategory.NONE,
        )
        assert info.is_pii is False

    def test_is_pii_false_when_category_not_set(self) -> None:
        """Test is_pii returns False when PII category not set."""
        info = FieldInfo(
            name="count",
            type=DataType.INTEGER,
            python_type=int,
            description="Count",
        )
        assert info.is_pii is False

    def test_is_sensitive_true_for_confidential(self) -> None:
        """Test is_sensitive returns True for CONFIDENTIAL level."""
        from griot_core.types import SensitivityLevel

        info = FieldInfo(
            name="salary",
            type=DataType.FLOAT,
            python_type=float,
            description="Salary",
            sensitivity_level=SensitivityLevel.CONFIDENTIAL,
        )
        assert info.is_sensitive is True

    def test_is_sensitive_true_for_restricted(self) -> None:
        """Test is_sensitive returns True for RESTRICTED level."""
        from griot_core.types import SensitivityLevel

        info = FieldInfo(
            name="ssn",
            type=DataType.STRING,
            python_type=str,
            description="SSN",
            sensitivity_level=SensitivityLevel.RESTRICTED,
        )
        assert info.is_sensitive is True

    def test_is_sensitive_false_for_internal(self) -> None:
        """Test is_sensitive returns False for INTERNAL level."""
        from griot_core.types import SensitivityLevel

        info = FieldInfo(
            name="dept",
            type=DataType.STRING,
            python_type=str,
            description="Department",
            sensitivity_level=SensitivityLevel.INTERNAL,
        )
        assert info.is_sensitive is False

    def test_is_sensitive_false_for_public(self) -> None:
        """Test is_sensitive returns False for PUBLIC level."""
        from griot_core.types import SensitivityLevel

        info = FieldInfo(
            name="website",
            type=DataType.STRING,
            python_type=str,
            description="Website",
            sensitivity_level=SensitivityLevel.PUBLIC,
        )
        assert info.is_sensitive is False

    def test_is_sensitive_false_when_not_set(self) -> None:
        """Test is_sensitive returns False when level not set."""
        info = FieldInfo(
            name="data",
            type=DataType.STRING,
            python_type=str,
            description="Data",
        )
        assert info.is_sensitive is False


class TestFieldInfoToDictPII:
    """Tests for PII metadata in FieldInfo.to_dict()."""

    def test_to_dict_includes_pii_category(self) -> None:
        """Test to_dict includes PII category."""
        from griot_core.types import PIICategory

        info = FieldInfo(
            name="phone",
            type=DataType.STRING,
            python_type=str,
            description="Phone",
            pii_category=PIICategory.PHONE,
        )
        result = info.to_dict()
        assert result["pii_category"] == "phone"

    def test_to_dict_excludes_none_pii_category(self) -> None:
        """Test to_dict excludes NONE PII category."""
        from griot_core.types import PIICategory

        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            pii_category=PIICategory.NONE,
        )
        result = info.to_dict()
        assert "pii_category" not in result

    def test_to_dict_includes_sensitivity_level(self) -> None:
        """Test to_dict includes sensitivity level."""
        from griot_core.types import SensitivityLevel

        info = FieldInfo(
            name="salary",
            type=DataType.FLOAT,
            python_type=float,
            description="Salary",
            sensitivity_level=SensitivityLevel.CONFIDENTIAL,
        )
        result = info.to_dict()
        assert result["sensitivity_level"] == "confidential"

    def test_to_dict_includes_masking_strategy(self) -> None:
        """Test to_dict includes masking strategy."""
        from griot_core.types import MaskingStrategy

        info = FieldInfo(
            name="ssn",
            type=DataType.STRING,
            python_type=str,
            description="SSN",
            masking_strategy=MaskingStrategy.REDACT,
        )
        result = info.to_dict()
        assert result["masking_strategy"] == "redact"

    def test_to_dict_excludes_none_masking_strategy(self) -> None:
        """Test to_dict excludes NONE masking strategy."""
        from griot_core.types import MaskingStrategy

        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            masking_strategy=MaskingStrategy.NONE,
        )
        result = info.to_dict()
        assert "masking_strategy" not in result

    def test_to_dict_includes_legal_basis(self) -> None:
        """Test to_dict includes legal basis."""
        from griot_core.types import LegalBasis

        info = FieldInfo(
            name="consent",
            type=DataType.BOOLEAN,
            python_type=bool,
            description="Consent",
            legal_basis=LegalBasis.CONSENT,
        )
        result = info.to_dict()
        assert result["legal_basis"] == "consent"

    def test_to_dict_excludes_none_legal_basis(self) -> None:
        """Test to_dict excludes NONE legal basis."""
        from griot_core.types import LegalBasis

        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            legal_basis=LegalBasis.NONE,
        )
        result = info.to_dict()
        assert "legal_basis" not in result

    def test_to_dict_includes_retention_days(self) -> None:
        """Test to_dict includes retention days."""
        info = FieldInfo(
            name="email",
            type=DataType.STRING,
            python_type=str,
            description="Email",
            retention_days=730,
        )
        result = info.to_dict()
        assert result["retention_days"] == 730

    def test_to_dict_includes_consent_required(self) -> None:
        """Test to_dict includes consent_required when True."""
        info = FieldInfo(
            name="marketing_consent",
            type=DataType.BOOLEAN,
            python_type=bool,
            description="Marketing consent",
            consent_required=True,
        )
        result = info.to_dict()
        assert result["consent_required"] is True

    def test_to_dict_excludes_consent_required_when_false(self) -> None:
        """Test to_dict excludes consent_required when False."""
        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            consent_required=False,
        )
        result = info.to_dict()
        assert "consent_required" not in result


class TestGriotModelPII:
    """Tests for PII-related methods in GriotModel."""

    def test_pii_inventory_returns_pii_fields(self) -> None:
        """Test pii_inventory returns fields with PII category."""
        from griot_core.types import PIICategory

        class PIIModel(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email: str = Field(description="Email", pii_category="email")
            phone: str = Field(description="Phone", pii_category="phone")
            status: str = Field(description="Status")

        pii_fields = PIIModel.pii_inventory()
        pii_names = [f.name for f in pii_fields]

        assert "email" in pii_names
        assert "phone" in pii_names
        assert "customer_id" not in pii_names
        assert "status" not in pii_names
        assert len(pii_fields) == 2

    def test_pii_inventory_excludes_none_category(self) -> None:
        """Test pii_inventory excludes fields with NONE category."""
        from griot_core.types import PIICategory

        class NonPIIModel(GriotModel):
            id: str = Field(description="ID", pii_category="none")
            data: str = Field(description="Data")

        pii_fields = NonPIIModel.pii_inventory()
        assert len(pii_fields) == 0

    def test_sensitive_fields_returns_confidential_and_above(self) -> None:
        """Test sensitive_fields returns confidential and restricted fields."""
        from griot_core.types import SensitivityLevel

        class SensitiveModel(GriotModel):
            public_data: str = Field(
                description="Public",
                sensitivity_level="public",
            )
            internal_data: str = Field(
                description="Internal",
                sensitivity_level="internal",
            )
            confidential_data: str = Field(
                description="Confidential",
                sensitivity_level="confidential",
            )
            restricted_data: str = Field(
                description="Restricted",
                sensitivity_level="restricted",
            )

        sensitive = SensitiveModel.sensitive_fields()
        sensitive_names = [f.name for f in sensitive]

        assert "confidential_data" in sensitive_names
        assert "restricted_data" in sensitive_names
        assert "public_data" not in sensitive_names
        assert "internal_data" not in sensitive_names
        assert len(sensitive) == 2

    def test_pii_summary_returns_correct_stats(self) -> None:
        """Test pii_summary returns correct statistics."""
        from griot_core.types import (
            MaskingStrategy,
            PIICategory,
            SensitivityLevel,
        )

        class FullPIIModel(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email: str = Field(
                description="Email",
                pii_category="email",
                sensitivity_level="confidential",
                masking_strategy="partial",
                retention_days=365,
                consent_required=True,
            )
            phone: str = Field(
                description="Phone",
                pii_category="phone",
                sensitivity_level="confidential",
                masking_strategy="redact",
                consent_required=True,
            )
            address: str = Field(
                description="Address",
                pii_category="address",
                sensitivity_level="internal",
            )
            status: str = Field(description="Status")

        summary = FullPIIModel.pii_summary()

        assert summary["total_fields"] == 5
        assert summary["pii_field_count"] == 3
        assert set(summary["pii_fields"]) == {"email", "phone", "address"}
        assert summary["categories"]["email"] == 1
        assert summary["categories"]["phone"] == 1
        assert summary["categories"]["address"] == 1
        assert summary["sensitivity_levels"]["confidential"] == 2
        assert summary["sensitivity_levels"]["internal"] == 1
        assert summary["masking_strategies"]["partial"] == 1
        assert summary["masking_strategies"]["redact"] == 1
        assert set(summary["consent_required"]) == {"email", "phone"}
        assert summary["retention_periods"]["email"] == 365


# =============================================================================
# GRIOT MODEL METHOD TESTS
# =============================================================================


class TestGriotModelMethods:
    """Tests for GriotModel class methods."""

    def test_validate_row_returns_errors_list(self) -> None:
        """Test validate_row returns list of errors."""

        class ValidateRowModel(GriotModel):
            name: str = Field(description="Name", min_length=2)
            age: int = Field(description="Age", ge=0)

        # Valid row
        errors = ValidateRowModel.validate_row({"name": "John", "age": 25})
        assert errors == []

        # Invalid row
        errors = ValidateRowModel.validate_row({"name": "J", "age": -5})
        assert len(errors) >= 2

    def test_to_yaml_exports_contract(self) -> None:
        """Test to_yaml exports contract as YAML string."""

        class YAMLModel(GriotModel):
            """A model for YAML export."""

            id: str = Field(description="Identifier", primary_key=True)
            value: int = Field(description="Value", ge=0, le=100)

        yaml_str = YAMLModel.to_yaml()

        assert "name: YAMLModel" in yaml_str
        assert "description: A model for YAML export." in yaml_str
        # Fields are in list format (ODCS)
        assert "- name: id" in yaml_str
        assert "primary_key: true" in yaml_str
        assert "- name: value" in yaml_str
        assert "ge: 0" in yaml_str
        assert "le: 100" in yaml_str

    def test_from_yaml_string_loads_contract(self) -> None:
        """Test from_yaml_string loads contract from YAML."""
        yaml_content = """
name: LoadedModel
description: Model loaded from YAML
fields:
  id:
    type: string
    description: Identifier
    primary_key: true
  count:
    type: integer
    description: Count
    ge: 0
"""
        LoadedModel = GriotModel.from_yaml_string(yaml_content)

        assert LoadedModel.__name__ == "LoadedModel"
        assert LoadedModel.get_primary_key() == "id"
        count_field = LoadedModel.get_field("count")
        assert count_field is not None
        assert count_field.ge == 0

    def test_from_dict_loads_contract(self) -> None:
        """Test from_dict loads contract from dictionary."""
        data = {
            "name": "DictModel",
            "description": "Model from dict",
            "fields": {
                "id": {
                    "type": "string",
                    "description": "ID",
                    "primary_key": True,
                },
                "score": {
                    "type": "float",
                    "description": "Score",
                    "ge": 0.0,
                    "le": 100.0,
                },
            },
        }
        DictModel = GriotModel.from_dict(data)

        assert DictModel.__name__ == "DictModel"
        assert len(DictModel.list_fields()) == 2
        score_field = DictModel.get_field("score")
        assert score_field is not None
        assert score_field.ge == 0.0
        assert score_field.le == 100.0

    def test_to_manifest_json_ld(self) -> None:
        """Test to_manifest exports JSON-LD format."""
        import json

        class ManifestModel(GriotModel):
            """Test model."""

            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        result = ManifestModel.to_manifest(format="json_ld")
        data = json.loads(result)

        assert "@context" in data
        assert data["name"] == "ManifestModel"
        assert "properties" in data

    def test_to_manifest_markdown(self) -> None:
        """Test to_manifest exports Markdown format."""

        class MDModel(GriotModel):
            """A markdown test model."""

            id: str = Field(description="ID", primary_key=True)

        result = MDModel.to_manifest(format="markdown")

        assert "# MDModel" in result
        assert "## Fields" in result

    def test_to_manifest_llm_context(self) -> None:
        """Test to_manifest exports LLM context format."""

        class LLMModel(GriotModel):
            """LLM context test."""

            id: str = Field(description="ID", primary_key=True)

        result = LLMModel.to_manifest(format="llm_context")

        assert "DATA CONTRACT: LLMModel" in result
        assert "FIELDS:" in result

    def test_mock_generates_data(self) -> None:
        """Test mock method generates data."""

        class MockModel(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            score: int = Field(description="Score", ge=0, le=100)

        data = MockModel.mock(rows=10, seed=42)

        assert len(data) == 10
        for row in data:
            assert "id" in row
            assert "score" in row
            assert 0 <= row["score"] <= 100

    def test_diff_detects_changes(self) -> None:
        """Test diff method detects contract changes."""

        class OriginalModel(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        class ModifiedModel(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Updated name")
            email: str = Field(description="Email")

        diff = OriginalModel.diff(ModifiedModel)

        assert "email" in diff.added_fields

    def test_lint_finds_issues(self) -> None:
        """Test lint method finds quality issues."""

        class LintModel(GriotModel):
            SomeField: str = Field(description="Bad name")  # Not snake_case
            another: str = Field(description="Field: another")  # Generic description

        issues = LintModel.lint()
        codes = [i.code for i in issues]

        assert "G001" in codes  # No primary key
        assert "G005" in codes  # Bad field name


# =============================================================================
# FIELD INFO COMPREHENSIVE TESTS
# =============================================================================


class TestFieldInfoToDict:
    """Comprehensive tests for FieldInfo.to_dict() method."""

    def test_to_dict_includes_primary_key(self) -> None:
        """Test to_dict includes primary_key when True."""
        info = FieldInfo(
            name="id",
            type=DataType.STRING,
            python_type=str,
            description="ID",
            primary_key=True,
        )
        result = info.to_dict()
        assert result["primary_key"] is True

    def test_to_dict_includes_unique(self) -> None:
        """Test to_dict includes unique when True."""
        info = FieldInfo(
            name="code",
            type=DataType.STRING,
            python_type=str,
            description="Code",
            unique=True,
        )
        result = info.to_dict()
        assert result["unique"] is True

    def test_to_dict_includes_all_constraints(self) -> None:
        """Test to_dict includes all constraint types."""
        info = FieldInfo(
            name="value",
            type=DataType.INTEGER,
            python_type=int,
            description="Value",
            ge=0,
            le=100,
            gt=None,
            lt=None,
            multiple_of=5,
        )
        result = info.to_dict()
        assert result["ge"] == 0
        assert result["le"] == 100
        assert result["multiple_of"] == 5
        assert "gt" not in result
        assert "lt" not in result

    def test_to_dict_includes_gt_lt(self) -> None:
        """Test to_dict includes gt and lt constraints."""
        info = FieldInfo(
            name="value",
            type=DataType.FLOAT,
            python_type=float,
            description="Value",
            gt=0.0,
            lt=1.0,
        )
        result = info.to_dict()
        assert result["gt"] == 0.0
        assert result["lt"] == 1.0

    def test_to_dict_includes_enum(self) -> None:
        """Test to_dict includes enum values."""
        info = FieldInfo(
            name="status",
            type=DataType.STRING,
            python_type=str,
            description="Status",
            enum=["active", "inactive"],
        )
        result = info.to_dict()
        assert result["enum"] == ["active", "inactive"]

    def test_to_dict_includes_default(self) -> None:
        """Test to_dict includes default value."""
        info = FieldInfo(
            name="count",
            type=DataType.INTEGER,
            python_type=int,
            description="Count",
            default=0,
            has_default=True,
        )
        result = info.to_dict()
        assert result["default"] == 0

    def test_to_dict_includes_unit(self) -> None:
        """Test to_dict includes unit."""
        info = FieldInfo(
            name="weight",
            type=DataType.FLOAT,
            python_type=float,
            description="Weight",
            unit="kg",
        )
        result = info.to_dict()
        assert result["unit"] == "kg"

    def test_to_dict_includes_aggregation(self) -> None:
        """Test to_dict includes aggregation."""
        info = FieldInfo(
            name="amount",
            type=DataType.FLOAT,
            python_type=float,
            description="Amount",
            aggregation=AggregationType.SUM,
        )
        result = info.to_dict()
        assert result["aggregation"] == "sum"

    def test_to_dict_includes_glossary_term(self) -> None:
        """Test to_dict includes glossary term."""
        info = FieldInfo(
            name="mrr",
            type=DataType.FLOAT,
            python_type=float,
            description="Monthly recurring revenue",
            glossary_term="monthly_recurring_revenue",
        )
        result = info.to_dict()
        assert result["glossary_term"] == "monthly_recurring_revenue"


class TestFieldInfoGetConstraints:
    """Tests for FieldInfo.get_constraints() method."""

    def test_get_constraints_includes_format(self) -> None:
        """Test get_constraints includes format."""
        info = FieldInfo(
            name="email",
            type=DataType.STRING,
            python_type=str,
            description="Email",
            format=FieldFormat.EMAIL,
        )
        constraints = info.get_constraints()
        assert constraints["format"] == FieldFormat.EMAIL

    def test_get_constraints_includes_unique(self) -> None:
        """Test get_constraints includes unique when True."""
        info = FieldInfo(
            name="code",
            type=DataType.STRING,
            python_type=str,
            description="Code",
            unique=True,
        )
        constraints = info.get_constraints()
        assert constraints["unique"] is True

    def test_get_constraints_excludes_unique_when_false(self) -> None:
        """Test get_constraints excludes unique when False."""
        info = FieldInfo(
            name="name",
            type=DataType.STRING,
            python_type=str,
            description="Name",
            unique=False,
        )
        constraints = info.get_constraints()
        assert "unique" not in constraints

    def test_get_constraints_empty_when_no_constraints(self) -> None:
        """Test get_constraints returns empty dict when no constraints."""
        info = FieldInfo(
            name="data",
            type=DataType.STRING,
            python_type=str,
            description="Data",
        )
        constraints = info.get_constraints()
        assert constraints == {}


# =============================================================================
# FIELD REPR TESTS
# =============================================================================


class TestFieldRepr:
    """Tests for Field __repr__ method."""

    def test_field_repr_with_nullable(self) -> None:
        """Test Field repr includes nullable."""
        field = Field(description="Optional", nullable=True)
        repr_str = repr(field)
        assert "nullable=True" in repr_str

    def test_field_repr_with_format(self) -> None:
        """Test Field repr includes format."""
        field = Field(description="Email", format="email")
        repr_str = repr(field)
        assert "format='email'" in repr_str

    def test_field_repr_basic(self) -> None:
        """Test Field repr with minimal fields."""
        field = Field(description="Simple field")
        repr_str = repr(field)
        assert "Field(" in repr_str
        assert "description='Simple field'" in repr_str
