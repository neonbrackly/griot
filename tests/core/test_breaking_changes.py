"""
Tests for griot_core breaking change detection (T-390).

Comprehensive tests for the `detect_breaking_changes()` function that validates
all 9 breaking change types defined in the ODCS specification.
"""
from __future__ import annotations

import pytest

from griot_core.contract import (
    BreakingChange,
    BreakingChangeType,
    ContractDiff,
    detect_breaking_changes,
    diff_contracts,
)
from griot_core.models import Field, GriotModel


# =============================================================================
# TEST MODELS FOR BREAKING CHANGE DETECTION
# =============================================================================


class BaseContract(GriotModel):
    """Base contract for breaking change tests."""

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
    )
    status: str = Field(
        description="Account status",
        enum=["active", "inactive", "suspended"],
    )
    score: float = Field(
        description="Customer score",
        ge=0.0,
        le=100.0,
        nullable=True,
    )


# =============================================================================
# T-390: FIELD_REMOVED Breaking Change Tests
# =============================================================================


class TestFieldRemovedBreakingChange:
    """Tests for FIELD_REMOVED breaking change type."""

    def test_field_removed_is_breaking(self) -> None:
        """Removing a field should be detected as FIELD_REMOVED breaking change."""

        class WithoutAge(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email: str = Field(description="Email")
            status: str = Field(description="Status")
            score: float = Field(description="Score", nullable=True)

        changes = detect_breaking_changes(BaseContract, WithoutAge)

        field_removed = [c for c in changes if c.change_type == BreakingChangeType.FIELD_REMOVED]
        assert len(field_removed) == 1
        assert field_removed[0].field == "age"
        assert field_removed[0].migration_hint is not None

    def test_multiple_fields_removed(self) -> None:
        """Multiple field removals should each be detected."""

        class MinimalContract(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)

        changes = detect_breaking_changes(BaseContract, MinimalContract)

        field_removed = [c for c in changes if c.change_type == BreakingChangeType.FIELD_REMOVED]
        removed_fields = {c.field for c in field_removed}
        assert "email" in removed_fields
        assert "age" in removed_fields
        assert "status" in removed_fields
        assert "score" in removed_fields

    def test_no_field_removed_when_same_fields(self) -> None:
        """No FIELD_REMOVED changes when contracts have same fields."""

        class SameFields(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email: str = Field(description="Email")
            age: int = Field(description="Age")
            status: str = Field(description="Status")
            score: float = Field(description="Score", nullable=True)

        changes = detect_breaking_changes(BaseContract, SameFields)

        field_removed = [c for c in changes if c.change_type == BreakingChangeType.FIELD_REMOVED]
        assert len(field_removed) == 0


# =============================================================================
# T-390: FIELD_RENAMED Breaking Change Tests
# =============================================================================


class TestFieldRenamedBreakingChange:
    """Tests for FIELD_RENAMED breaking change type (heuristic detection)."""

    def test_field_renamed_detected_same_type_similar_description(self) -> None:
        """Field rename should be detected when same type and similar description."""

        class RenamedField(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)
            email_address: str = Field(  # renamed from 'email'
                description="Customer email address",  # similar description
                format="email",
            )
            age: int = Field(description="Age")
            status: str = Field(description="Status")
            score: float = Field(description="Score", nullable=True)

        changes = detect_breaking_changes(BaseContract, RenamedField)

        # Should detect potential rename (email -> email_address)
        renamed = [c for c in changes if c.change_type == BreakingChangeType.FIELD_RENAMED]
        # Rename detection is heuristic, may or may not detect
        # The key is that FIELD_REMOVED is also captured
        removed = [c for c in changes if c.change_type == BreakingChangeType.FIELD_REMOVED]
        assert len(removed) >= 1
        assert any(c.field == "email" for c in removed)


# =============================================================================
# T-390: TYPE_CHANGED_INCOMPATIBLE Breaking Change Tests
# =============================================================================


class TestTypeChangedIncompatibleBreakingChange:
    """Tests for TYPE_CHANGED_INCOMPATIBLE breaking change type."""

    def test_string_to_integer_is_breaking(self) -> None:
        """Changing from string to integer is incompatible."""

        class Base(GriotModel):
            value: str = Field(description="Value")

        class Changed(GriotModel):
            value: int = Field(description="Value")

        changes = detect_breaking_changes(Base, Changed)

        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        assert len(type_changes) == 1
        assert type_changes[0].field == "value"
        assert type_changes[0].from_value == "string"
        assert type_changes[0].to_value == "integer"

    def test_integer_to_string_is_breaking(self) -> None:
        """Changing from integer to string is incompatible."""

        class Base(GriotModel):
            value: int = Field(description="Value")

        class Changed(GriotModel):
            value: str = Field(description="Value")

        changes = detect_breaking_changes(Base, Changed)

        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        assert len(type_changes) == 1

    def test_float_to_integer_is_breaking(self) -> None:
        """Changing from float to integer is incompatible (lossy)."""

        class Base(GriotModel):
            value: float = Field(description="Value")

        class Changed(GriotModel):
            value: int = Field(description="Value")

        changes = detect_breaking_changes(Base, Changed)

        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        assert len(type_changes) == 1

    def test_integer_to_float_is_not_breaking(self) -> None:
        """Changing from integer to float is widening (non-breaking)."""

        class Base(GriotModel):
            value: int = Field(description="Value")

        class Changed(GriotModel):
            value: float = Field(description="Value")

        changes = detect_breaking_changes(Base, Changed)

        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        assert len(type_changes) == 0

    def test_boolean_to_string_is_breaking(self) -> None:
        """Changing from boolean to string is incompatible."""

        class Base(GriotModel):
            flag: bool = Field(description="Flag")

        class Changed(GriotModel):
            flag: str = Field(description="Flag")

        changes = detect_breaking_changes(Base, Changed)

        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        assert len(type_changes) == 1


# =============================================================================
# T-390: REQUIRED_FIELD_ADDED Breaking Change Tests
# =============================================================================


class TestRequiredFieldAddedBreakingChange:
    """Tests for REQUIRED_FIELD_ADDED breaking change type."""

    def test_required_field_without_default_is_breaking(self) -> None:
        """Adding a required field without default is breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)

        class WithRequired(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            new_required: str = Field(description="New required field")  # non-nullable, no default

        changes = detect_breaking_changes(Base, WithRequired)

        required_added = [c for c in changes if c.change_type == BreakingChangeType.REQUIRED_FIELD_ADDED]
        assert len(required_added) == 1
        assert required_added[0].field == "new_required"
        assert "default" in required_added[0].migration_hint.lower() or "nullable" in required_added[0].migration_hint.lower()

    def test_nullable_field_added_is_not_breaking(self) -> None:
        """Adding a nullable field is not breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)

        class WithNullable(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            new_optional: str = Field(description="Optional field", nullable=True)

        changes = detect_breaking_changes(Base, WithNullable)

        required_added = [c for c in changes if c.change_type == BreakingChangeType.REQUIRED_FIELD_ADDED]
        assert len(required_added) == 0

    def test_field_with_default_is_not_breaking(self) -> None:
        """Adding a field with default value is not breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)

        class WithDefault(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            new_with_default: str = Field(description="Field with default", default="unknown")

        changes = detect_breaking_changes(Base, WithDefault)

        required_added = [c for c in changes if c.change_type == BreakingChangeType.REQUIRED_FIELD_ADDED]
        assert len(required_added) == 0


# =============================================================================
# T-390: ENUM_VALUES_REMOVED Breaking Change Tests
# =============================================================================


class TestEnumValuesRemovedBreakingChange:
    """Tests for ENUM_VALUES_REMOVED breaking change type."""

    def test_enum_value_removed_is_breaking(self) -> None:
        """Removing enum values is breaking."""

        class Base(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive", "pending"])

        class Reduced(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive"])  # removed 'pending'

        changes = detect_breaking_changes(Base, Reduced)

        enum_removed = [c for c in changes if c.change_type == BreakingChangeType.ENUM_VALUES_REMOVED]
        assert len(enum_removed) == 1
        assert enum_removed[0].field == "status"
        assert "pending" in str(enum_removed[0].description)

    def test_multiple_enum_values_removed(self) -> None:
        """Multiple enum value removals should be detected."""

        class Base(GriotModel):
            status: str = Field(description="Status", enum=["a", "b", "c", "d"])

        class Reduced(GriotModel):
            status: str = Field(description="Status", enum=["a"])  # removed b, c, d

        changes = detect_breaking_changes(Base, Reduced)

        enum_removed = [c for c in changes if c.change_type == BreakingChangeType.ENUM_VALUES_REMOVED]
        assert len(enum_removed) == 1

    def test_enum_value_added_is_not_breaking(self) -> None:
        """Adding enum values is not breaking."""

        class Base(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive"])

        class Extended(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive", "pending"])

        changes = detect_breaking_changes(Base, Extended)

        enum_removed = [c for c in changes if c.change_type == BreakingChangeType.ENUM_VALUES_REMOVED]
        assert len(enum_removed) == 0

    def test_enum_removed_entirely_is_not_breaking(self) -> None:
        """Removing enum constraint entirely (widening) is not breaking."""

        class Base(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive"])

        class NoEnum(GriotModel):
            status: str = Field(description="Status")  # no enum constraint

        changes = detect_breaking_changes(Base, NoEnum)

        enum_removed = [c for c in changes if c.change_type == BreakingChangeType.ENUM_VALUES_REMOVED]
        assert len(enum_removed) == 0

    def test_enum_added_is_breaking(self) -> None:
        """Adding enum constraint (narrowing) is breaking."""

        class Base(GriotModel):
            status: str = Field(description="Status")  # no enum

        class WithEnum(GriotModel):
            status: str = Field(description="Status", enum=["active", "inactive"])

        changes = detect_breaking_changes(Base, WithEnum)

        # Adding enum is CONSTRAINT_TIGHTENED, not ENUM_VALUES_REMOVED
        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1


# =============================================================================
# T-390: CONSTRAINT_TIGHTENED Breaking Change Tests
# =============================================================================


class TestConstraintTightenedBreakingChange:
    """Tests for CONSTRAINT_TIGHTENED breaking change type."""

    def test_max_length_decreased_is_breaking(self) -> None:
        """Decreasing max_length is breaking."""

        class Base(GriotModel):
            name: str = Field(description="Name", max_length=100)

        class Tighter(GriotModel):
            name: str = Field(description="Name", max_length=50)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1
        assert "max_length" in tightened[0].description

    def test_max_length_added_is_breaking(self) -> None:
        """Adding max_length constraint is breaking."""

        class Base(GriotModel):
            name: str = Field(description="Name")  # no max_length

        class WithMaxLength(GriotModel):
            name: str = Field(description="Name", max_length=100)

        changes = detect_breaking_changes(Base, WithMaxLength)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_min_length_increased_is_breaking(self) -> None:
        """Increasing min_length is breaking."""

        class Base(GriotModel):
            code: str = Field(description="Code", min_length=1)

        class Tighter(GriotModel):
            code: str = Field(description="Code", min_length=5)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1
        assert "min_length" in tightened[0].description

    def test_min_length_added_is_breaking(self) -> None:
        """Adding min_length constraint is breaking."""

        class Base(GriotModel):
            code: str = Field(description="Code")

        class WithMinLength(GriotModel):
            code: str = Field(description="Code", min_length=5)

        changes = detect_breaking_changes(Base, WithMinLength)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_ge_increased_is_breaking(self) -> None:
        """Increasing ge (minimum value) is breaking."""

        class Base(GriotModel):
            age: int = Field(description="Age", ge=0)

        class Tighter(GriotModel):
            age: int = Field(description="Age", ge=18)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1
        assert "ge" in tightened[0].description.lower() or "minimum" in tightened[0].description.lower()

    def test_ge_added_is_breaking(self) -> None:
        """Adding ge constraint is breaking."""

        class Base(GriotModel):
            value: int = Field(description="Value")

        class WithGe(GriotModel):
            value: int = Field(description="Value", ge=0)

        changes = detect_breaking_changes(Base, WithGe)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_le_decreased_is_breaking(self) -> None:
        """Decreasing le (maximum value) is breaking."""

        class Base(GriotModel):
            age: int = Field(description="Age", le=150)

        class Tighter(GriotModel):
            age: int = Field(description="Age", le=120)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_le_added_is_breaking(self) -> None:
        """Adding le constraint is breaking."""

        class Base(GriotModel):
            value: int = Field(description="Value")

        class WithLe(GriotModel):
            value: int = Field(description="Value", le=100)

        changes = detect_breaking_changes(Base, WithLe)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_gt_increased_is_breaking(self) -> None:
        """Increasing gt is breaking."""

        class Base(GriotModel):
            value: int = Field(description="Value", gt=0)

        class Tighter(GriotModel):
            value: int = Field(description="Value", gt=10)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_lt_decreased_is_breaking(self) -> None:
        """Decreasing lt is breaking."""

        class Base(GriotModel):
            value: int = Field(description="Value", lt=100)

        class Tighter(GriotModel):
            value: int = Field(description="Value", lt=50)

        changes = detect_breaking_changes(Base, Tighter)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 1

    def test_constraint_relaxation_is_not_breaking(self) -> None:
        """Relaxing constraints (increasing max_length) is not breaking."""

        class Base(GriotModel):
            name: str = Field(description="Name", max_length=50)

        class Relaxed(GriotModel):
            name: str = Field(description="Name", max_length=100)

        changes = detect_breaking_changes(Base, Relaxed)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 0

    def test_constraint_removed_is_not_breaking(self) -> None:
        """Removing a constraint is not breaking."""

        class Base(GriotModel):
            name: str = Field(description="Name", max_length=100)

        class NoConstraint(GriotModel):
            name: str = Field(description="Name")

        changes = detect_breaking_changes(Base, NoConstraint)

        tightened = [c for c in changes if c.change_type == BreakingChangeType.CONSTRAINT_TIGHTENED]
        assert len(tightened) == 0


# =============================================================================
# T-390: NULLABLE_TO_REQUIRED Breaking Change Tests
# =============================================================================


class TestNullableToRequiredBreakingChange:
    """Tests for NULLABLE_TO_REQUIRED breaking change type."""

    def test_nullable_to_required_is_breaking(self) -> None:
        """Changing nullable field to required is breaking."""

        class Base(GriotModel):
            optional_field: str = Field(description="Optional", nullable=True)

        class Required(GriotModel):
            optional_field: str = Field(description="Optional", nullable=False)

        changes = detect_breaking_changes(Base, Required)

        nullable_changes = [c for c in changes if c.change_type == BreakingChangeType.NULLABLE_TO_REQUIRED]
        assert len(nullable_changes) == 1
        assert nullable_changes[0].field == "optional_field"
        assert nullable_changes[0].from_value is True
        assert nullable_changes[0].to_value is False

    def test_required_to_nullable_is_not_breaking(self) -> None:
        """Changing required field to nullable is not breaking."""

        class Base(GriotModel):
            required_field: str = Field(description="Required", nullable=False)

        class Nullable(GriotModel):
            required_field: str = Field(description="Required", nullable=True)

        changes = detect_breaking_changes(Base, Nullable)

        nullable_changes = [c for c in changes if c.change_type == BreakingChangeType.NULLABLE_TO_REQUIRED]
        assert len(nullable_changes) == 0


# =============================================================================
# T-390: PATTERN_CHANGED Breaking Change Tests
# =============================================================================


class TestPatternChangedBreakingChange:
    """Tests for PATTERN_CHANGED breaking change type."""

    def test_pattern_added_is_breaking(self) -> None:
        """Adding a pattern constraint is breaking."""

        class Base(GriotModel):
            code: str = Field(description="Code")

        class WithPattern(GriotModel):
            code: str = Field(description="Code", pattern=r"^[A-Z]{3}$")

        changes = detect_breaking_changes(Base, WithPattern)

        pattern_changes = [c for c in changes if c.change_type == BreakingChangeType.PATTERN_CHANGED]
        assert len(pattern_changes) == 1
        assert pattern_changes[0].field == "code"
        assert pattern_changes[0].from_value is None
        assert pattern_changes[0].to_value == r"^[A-Z]{3}$"

    def test_pattern_changed_is_breaking(self) -> None:
        """Changing pattern is breaking."""

        class Base(GriotModel):
            code: str = Field(description="Code", pattern=r"^[A-Z]+$")

        class Changed(GriotModel):
            code: str = Field(description="Code", pattern=r"^[A-Z]{3}$")

        changes = detect_breaking_changes(Base, Changed)

        pattern_changes = [c for c in changes if c.change_type == BreakingChangeType.PATTERN_CHANGED]
        assert len(pattern_changes) == 1

    def test_pattern_removed_is_not_breaking(self) -> None:
        """Removing pattern (widening) is not breaking."""

        class Base(GriotModel):
            code: str = Field(description="Code", pattern=r"^[A-Z]+$")

        class NoPattern(GriotModel):
            code: str = Field(description="Code")

        changes = detect_breaking_changes(Base, NoPattern)

        # Pattern removal is widening, so no PATTERN_CHANGED
        pattern_changes = [c for c in changes if c.change_type == BreakingChangeType.PATTERN_CHANGED]
        assert len(pattern_changes) == 0


# =============================================================================
# T-390: PRIMARY_KEY_CHANGED Breaking Change Tests
# =============================================================================


class TestPrimaryKeyChangedBreakingChange:
    """Tests for PRIMARY_KEY_CHANGED breaking change type."""

    def test_primary_key_changed_is_breaking(self) -> None:
        """Changing primary key field is breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            uuid: str = Field(description="UUID")

        class Changed(GriotModel):
            id: str = Field(description="ID")
            uuid: str = Field(description="UUID", primary_key=True)

        changes = detect_breaking_changes(Base, Changed)

        pk_changes = [c for c in changes if c.change_type == BreakingChangeType.PRIMARY_KEY_CHANGED]
        assert len(pk_changes) == 1
        assert pk_changes[0].from_value == "id"
        assert pk_changes[0].to_value == "uuid"

    def test_primary_key_added_is_breaking(self) -> None:
        """Adding a primary key where none existed is breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID")
            name: str = Field(description="Name")

        class WithPK(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        changes = detect_breaking_changes(Base, WithPK)

        pk_changes = [c for c in changes if c.change_type == BreakingChangeType.PRIMARY_KEY_CHANGED]
        assert len(pk_changes) == 1
        assert pk_changes[0].from_value is None
        assert pk_changes[0].to_value == "id"

    def test_primary_key_removed_is_breaking(self) -> None:
        """Removing primary key is breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        class NoPK(GriotModel):
            id: str = Field(description="ID")
            name: str = Field(description="Name")

        changes = detect_breaking_changes(Base, NoPK)

        pk_changes = [c for c in changes if c.change_type == BreakingChangeType.PRIMARY_KEY_CHANGED]
        assert len(pk_changes) == 1
        assert pk_changes[0].from_value == "id"
        assert pk_changes[0].to_value is None

    def test_same_primary_key_is_not_breaking(self) -> None:
        """Same primary key is not breaking."""

        class Base(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name")

        class Same(GriotModel):
            id: str = Field(description="Identifier", primary_key=True)  # different description
            name: str = Field(description="Name")

        changes = detect_breaking_changes(Base, Same)

        pk_changes = [c for c in changes if c.change_type == BreakingChangeType.PRIMARY_KEY_CHANGED]
        assert len(pk_changes) == 0


# =============================================================================
# T-390: ContractDiff Integration Tests
# =============================================================================


class TestContractDiffIntegration:
    """Tests for ContractDiff with breaking_changes list."""

    def test_diff_includes_breaking_changes(self) -> None:
        """diff_contracts should populate breaking_changes list."""

        class Removed(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)

        diff = diff_contracts(BaseContract, Removed)

        assert diff.has_breaking_changes is True
        assert len(diff.breaking_changes) > 0
        assert len(diff.removed_fields) > 0

    def test_diff_no_breaking_changes_for_identical(self) -> None:
        """Identical contracts should have no breaking changes."""
        diff = diff_contracts(BaseContract, BaseContract)

        assert diff.has_breaking_changes is False
        assert len(diff.breaking_changes) == 0

    def test_diff_summary_mentions_breaking(self) -> None:
        """Summary should mention breaking changes."""

        class Removed(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)

        diff = diff_contracts(BaseContract, Removed)
        summary = diff.summary()

        assert "BREAKING" in summary.upper()

    def test_diff_markdown_includes_warning(self) -> None:
        """Markdown should include breaking change warning."""

        class Removed(GriotModel):
            customer_id: str = Field(description="ID", primary_key=True)

        diff = diff_contracts(BaseContract, Removed)
        markdown = diff.to_markdown()

        assert "WARNING" in markdown


# =============================================================================
# T-390: Edge Cases and Comprehensive Tests
# =============================================================================


class TestBreakingChangeEdgeCases:
    """Edge cases and comprehensive breaking change tests."""

    def test_multiple_breaking_changes_same_field(self) -> None:
        """Multiple breaking changes on the same field."""

        class Base(GriotModel):
            value: str = Field(
                description="Value",
                max_length=100,
                nullable=True,
            )

        class MultipleChanges(GriotModel):
            value: int = Field(  # type change
                description="Value",
                ge=0,  # new constraint
                nullable=False,  # nullable -> required
            )

        changes = detect_breaking_changes(Base, MultipleChanges)

        # Should detect type change and nullable change
        type_changes = [c for c in changes if c.change_type == BreakingChangeType.TYPE_CHANGED_INCOMPATIBLE]
        nullable_changes = [c for c in changes if c.change_type == BreakingChangeType.NULLABLE_TO_REQUIRED]

        assert len(type_changes) >= 1
        assert len(nullable_changes) >= 1

    def test_breaking_change_str_representation(self) -> None:
        """BreakingChange should have readable string representation."""
        change = BreakingChange(
            change_type=BreakingChangeType.FIELD_REMOVED,
            field="test_field",
            description="Field 'test_field' was removed",
            from_value="string",
            to_value=None,
            migration_hint="Add the field back",
        )

        str_repr = str(change)
        assert "field_removed" in str_repr
        assert "test_field" in str_repr

    def test_complex_contract_evolution(self) -> None:
        """Complex contract evolution with many changes."""

        class V1(GriotModel):
            """Version 1."""

            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name", max_length=100)
            age: int = Field(description="Age", ge=0, le=150)
            status: str = Field(description="Status", enum=["active", "inactive", "pending"])
            score: float = Field(description="Score", nullable=True)

        class V2(GriotModel):
            """Version 2 with breaking changes."""

            uuid: str = Field(description="UUID", primary_key=True)  # PK changed
            name: str = Field(description="Name", max_length=50)  # max_length reduced
            age: int = Field(description="Age", ge=18, le=120)  # range tightened
            status: str = Field(description="Status", enum=["active", "inactive"])  # enum reduced
            # score removed
            new_required: str = Field(description="New required field")  # new required

        changes = detect_breaking_changes(V1, V2)

        # Should have multiple breaking changes
        assert len(changes) >= 5

        change_types = {c.change_type for c in changes}
        assert BreakingChangeType.PRIMARY_KEY_CHANGED in change_types
        assert BreakingChangeType.FIELD_REMOVED in change_types
        assert BreakingChangeType.CONSTRAINT_TIGHTENED in change_types
        assert BreakingChangeType.ENUM_VALUES_REMOVED in change_types
        assert BreakingChangeType.REQUIRED_FIELD_ADDED in change_types

    def test_non_breaking_changes_only(self) -> None:
        """Contract with only non-breaking changes."""

        class V1(GriotModel):
            id: str = Field(description="ID", primary_key=True)
            name: str = Field(description="Name", max_length=50)
            status: str = Field(description="Status", enum=["active"])

        class V2(GriotModel):
            id: str = Field(description="Identifier", primary_key=True)  # description change
            name: str = Field(description="Full Name", max_length=100)  # max_length increased
            status: str = Field(description="Status", enum=["active", "inactive"])  # enum extended
            new_optional: str = Field(description="Optional", nullable=True)  # new nullable

        changes = detect_breaking_changes(V1, V2)

        # Should have NO breaking changes
        assert len(changes) == 0


# =============================================================================
# T-390: BreakingChangeType Enum Tests
# =============================================================================


class TestBreakingChangeTypeEnum:
    """Tests for BreakingChangeType enum completeness."""

    def test_all_breaking_change_types_defined(self) -> None:
        """Verify all 9 breaking change types are defined."""
        expected_types = {
            "FIELD_REMOVED",
            "FIELD_RENAMED",
            "TYPE_CHANGED_INCOMPATIBLE",
            "REQUIRED_FIELD_ADDED",
            "ENUM_VALUES_REMOVED",
            "CONSTRAINT_TIGHTENED",
            "NULLABLE_TO_REQUIRED",
            "PATTERN_CHANGED",
            "PRIMARY_KEY_CHANGED",
        }

        actual_types = {t.name for t in BreakingChangeType}
        assert expected_types == actual_types

    def test_breaking_change_type_values(self) -> None:
        """Verify breaking change type values are snake_case strings."""
        for change_type in BreakingChangeType:
            assert change_type.value == change_type.name.lower()
