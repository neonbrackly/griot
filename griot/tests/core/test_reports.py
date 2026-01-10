"""
Tests for griot_core.reports module.

Tests analytics and AI readiness report generation functionality.
"""
from __future__ import annotations

import json
from typing import Optional

import pytest

from griot_core.models import Field, GriotModel
from griot_core.reports import (
    AIReadinessReport,
    AnalyticsReport,
    generate_ai_readiness_report,
    generate_analytics_report,
)


# =============================================================================
# TEST MODELS
# =============================================================================


class WellDocumentedModel(GriotModel):
    """A well-documented model for testing AI readiness."""

    customer_id: str = Field(
        description="Unique customer identifier for tracking across all systems and services",
        primary_key=True,
        pattern=r"^CUST-\d{6}$",
    )
    email: str = Field(
        description="Primary email address used for all customer communications and notifications",
        format="email",
        max_length=255,
        pii_category="email",
        sensitivity_level="confidential",
        masking_strategy="partial",
        legal_basis="consent",
    )
    age: int = Field(
        description="Customer age calculated from date of birth, used for eligibility checks",
        ge=0,
        le=150,
        unit="years",
        aggregation="avg",
    )
    status: str = Field(
        description="Current account status indicating active, inactive, or suspended state",
        enum=["active", "inactive", "suspended"],
        glossary_term="account_status",
    )


class PoorlyDocumentedModel(GriotModel):
    """Poorly documented model."""

    id: str = Field(description="ID")
    value: int = Field(description="Val")
    data: str = Field(description="Data")


class EmptyModel(GriotModel):
    """Model with no fields."""

    pass


class PIIModel(GriotModel):
    """Model with PII fields."""

    id: str = Field(description="ID", primary_key=True)
    email: str = Field(
        description="Email address",
        pii_category="email",
        sensitivity_level="confidential",
    )
    phone: str = Field(
        description="Phone number",
        pii_category="phone",
        sensitivity_level="confidential",
        masking_strategy="partial",
    )
    ssn: str = Field(
        description="Social Security Number",
        pii_category="ssn",
        sensitivity_level="restricted",
        masking_strategy="hash",
        legal_basis="legal_obligation",
    )


class NoPrimaryKeyModel(GriotModel):
    """Model without a primary key."""

    name: str = Field(description="Name field")
    value: int = Field(description="Value field")


# =============================================================================
# ANALYTICS REPORT TESTS
# =============================================================================


class TestAnalyticsReportDataclass:
    """Tests for AnalyticsReport dataclass."""

    def test_analytics_report_creation(self) -> None:
        """Test creating an AnalyticsReport instance."""
        report = AnalyticsReport(
            contract_name="TestContract",
            generated_at="2025-01-15T10:00:00",
        )
        assert report.contract_name == "TestContract"
        assert report.generated_at == "2025-01-15T10:00:00"
        assert report.version == "1.0"
        assert report.total_fields == 0

    def test_analytics_report_to_dict(self) -> None:
        """Test AnalyticsReport to_dict method."""
        report = AnalyticsReport(
            contract_name="Test",
            generated_at="2025-01-15",
            total_fields=5,
            primary_key="id",
        )
        result = report.to_dict()

        assert result["report_type"] == "analytics"
        assert result["contract_name"] == "Test"
        assert result["summary"]["total_fields"] == 5
        assert result["keys"]["primary_key"] == "id"

    def test_analytics_report_to_json(self) -> None:
        """Test AnalyticsReport to_json method."""
        report = AnalyticsReport(
            contract_name="Test",
            generated_at="2025-01-15",
        )
        result = report.to_json()

        data = json.loads(result)
        assert data["contract_name"] == "Test"

    def test_analytics_report_to_markdown(self) -> None:
        """Test AnalyticsReport to_markdown method."""
        report = AnalyticsReport(
            contract_name="TestContract",
            generated_at="2025-01-15",
            total_fields=3,
            required_fields=["id", "name"],
            nullable_fields=["optional"],
            field_types={"string": 2, "integer": 1},
            primary_key="id",
            unique_fields=["id"],
            fields_with_constraints=2,
            constraint_types={"min_length": 1, "max_length": 1},
            pii_fields=["email"],
            pii_categories={"email": 1},
            recommendations=["Add more constraints"],
        )
        result = report.to_markdown()

        assert "# Analytics Report: TestContract" in result
        assert "Total Fields | 3" in result
        assert "Primary Key" in result
        assert "Constraints" in result
        assert "Privacy Information" in result
        assert "Recommendations" in result
        assert "**string**: 2" in result

    def test_analytics_report_documentation_coverage_zero_fields(self) -> None:
        """Test documentation coverage calculation with zero fields."""
        report = AnalyticsReport(
            contract_name="Empty",
            generated_at="2025-01-15",
            total_fields=0,
            documented_fields=0,
        )
        result = report.to_dict()
        assert result["summary"]["documentation_coverage"] == 0


# =============================================================================
# AI READINESS REPORT TESTS
# =============================================================================


class TestAIReadinessReportDataclass:
    """Tests for AIReadinessReport dataclass."""

    def test_ai_readiness_report_creation(self) -> None:
        """Test creating an AIReadinessReport instance."""
        report = AIReadinessReport(
            contract_name="TestContract",
            generated_at="2025-01-15T10:00:00",
        )
        assert report.contract_name == "TestContract"
        assert report.readiness_score == 0.0
        assert report.readiness_grade == "F"

    def test_ai_readiness_report_to_dict(self) -> None:
        """Test AIReadinessReport to_dict method."""
        report = AIReadinessReport(
            contract_name="Test",
            generated_at="2025-01-15",
            readiness_score=85.0,
            readiness_grade="B",
            documentation_score=80.0,
            type_clarity_score=100.0,
        )
        result = report.to_dict()

        assert result["report_type"] == "ai_readiness"
        assert result["scores"]["overall"]["score"] == 85.0
        assert result["scores"]["overall"]["grade"] == "B"
        assert result["scores"]["components"]["documentation"] == 80.0

    def test_ai_readiness_report_to_json(self) -> None:
        """Test AIReadinessReport to_json method."""
        report = AIReadinessReport(
            contract_name="Test",
            generated_at="2025-01-15",
            readiness_score=75.0,
        )
        result = report.to_json()

        data = json.loads(result)
        assert data["scores"]["overall"]["score"] == 75.0

    def test_ai_readiness_report_to_markdown(self) -> None:
        """Test AIReadinessReport to_markdown method."""
        report = AIReadinessReport(
            contract_name="TestContract",
            generated_at="2025-01-15",
            readiness_score=85.5,
            readiness_grade="B",
            documentation_score=80.0,
            type_clarity_score=90.0,
            constraint_coverage_score=70.0,
            semantic_richness_score=60.0,
            privacy_clarity_score=80.0,
            strengths=["Good documentation", "Primary key defined"],
            weaknesses=["Limited semantic metadata"],
            recommendations=[
                {"priority": "high", "action": "Add more descriptions"},
                {"priority": "medium", "field": "email", "action": "Add unit"},
            ],
            suggested_context="Contract: Test\nFields: 5",
        )
        result = report.to_markdown()

        assert "# AI Readiness Report: TestContract" in result
        assert "85.5/100" in result
        assert "Grade: **B**" in result
        assert "Strengths" in result
        assert "Good documentation" in result
        assert "Areas for Improvement" in result
        assert "Recommendations" in result
        assert "[HIGH]" in result
        assert "Suggested LLM Context" in result


# =============================================================================
# GENERATE ANALYTICS REPORT TESTS
# =============================================================================


class TestGenerateAnalyticsReport:
    """Tests for generate_analytics_report function."""

    def test_generate_analytics_report_basic(self) -> None:
        """Test generating analytics report for basic model."""
        report = generate_analytics_report(WellDocumentedModel)

        assert report.contract_name == "WellDocumentedModel"
        assert report.total_fields == 4
        assert report.primary_key == "customer_id"
        assert "string" in report.field_types

    def test_generate_analytics_report_field_types(self) -> None:
        """Test analytics report field type distribution."""
        report = generate_analytics_report(WellDocumentedModel)

        assert report.field_types["string"] == 3
        assert report.field_types["integer"] == 1

    def test_generate_analytics_report_required_nullable(self) -> None:
        """Test analytics report required/nullable field tracking."""
        report = generate_analytics_report(WellDocumentedModel)

        # All fields are required (not nullable)
        assert len(report.required_fields) == 4
        assert len(report.nullable_fields) == 0

    def test_generate_analytics_report_constraints(self) -> None:
        """Test analytics report constraint tracking."""
        report = generate_analytics_report(WellDocumentedModel)

        assert report.fields_with_constraints > 0
        assert "customer_id" in report.fields_with_patterns
        assert "status" in report.fields_with_enums

    def test_generate_analytics_report_pii_fields(self) -> None:
        """Test analytics report PII field tracking."""
        report = generate_analytics_report(PIIModel)

        assert "email" in report.pii_fields
        assert "phone" in report.pii_fields
        assert "ssn" in report.pii_fields
        assert len(report.pii_categories) > 0
        assert len(report.sensitive_fields) > 0

    def test_generate_analytics_report_documentation(self) -> None:
        """Test analytics report documentation tracking."""
        report = generate_analytics_report(WellDocumentedModel)

        # Well-documented fields have descriptions > 10 chars
        assert report.documented_fields > 0
        assert "age" in report.fields_with_units

    def test_generate_analytics_report_recommendations(self) -> None:
        """Test analytics report recommendations generation."""
        report = generate_analytics_report(NoPrimaryKeyModel)

        # Should recommend adding a primary key
        assert any("primary key" in rec.lower() for rec in report.recommendations)

    def test_generate_analytics_report_recommendations_undocumented(self) -> None:
        """Test recommendations for undocumented fields."""
        report = generate_analytics_report(PoorlyDocumentedModel)

        # Should recommend adding descriptions
        assert any("description" in rec.lower() or "undocumented" in rec.lower()
                   for rec in report.recommendations)

    def test_generate_analytics_report_pii_without_sensitivity(self) -> None:
        """Test recommendations for PII without sensitivity levels."""

        class PIINoSensitivity(GriotModel):
            email: str = Field(description="Email address", pii_category="email")

        report = generate_analytics_report(PIINoSensitivity)
        assert any("sensitivity" in rec.lower() for rec in report.recommendations)


# =============================================================================
# GENERATE AI READINESS REPORT TESTS
# =============================================================================


class TestGenerateAIReadinessReport:
    """Tests for generate_ai_readiness_report function."""

    def test_generate_ai_readiness_report_basic(self) -> None:
        """Test generating AI readiness report for basic model."""
        report = generate_ai_readiness_report(WellDocumentedModel)

        assert report.contract_name == "WellDocumentedModel"
        assert report.readiness_score > 0
        assert report.readiness_grade in ["A", "B", "C", "D", "F"]

    def test_generate_ai_readiness_report_empty_model(self) -> None:
        """Test AI readiness report for empty model."""

        class NoFieldsModel(GriotModel):
            pass

        report = generate_ai_readiness_report(NoFieldsModel)

        assert report.readiness_score == 0
        assert report.readiness_grade == "F"
        assert len(report.weaknesses) > 0

    def test_generate_ai_readiness_report_scores(self) -> None:
        """Test AI readiness report component scores."""
        report = generate_ai_readiness_report(WellDocumentedModel)

        assert 0 <= report.documentation_score <= 100
        assert 0 <= report.type_clarity_score <= 100
        assert 0 <= report.constraint_coverage_score <= 100
        assert 0 <= report.semantic_richness_score <= 100
        assert 0 <= report.privacy_clarity_score <= 100

    def test_generate_ai_readiness_report_high_score(self) -> None:
        """Test AI readiness report with well-documented model."""
        report = generate_ai_readiness_report(WellDocumentedModel)

        # Well-documented model should have decent scores
        assert report.readiness_score >= 50
        assert len(report.well_documented_fields) > 0

    def test_generate_ai_readiness_report_low_score(self) -> None:
        """Test AI readiness report with poorly-documented model."""
        report = generate_ai_readiness_report(PoorlyDocumentedModel)

        # Poorly documented model should have lower scores
        assert report.readiness_score < 80
        assert len(report.needs_improvement) > 0

    def test_generate_ai_readiness_report_strengths(self) -> None:
        """Test AI readiness report identifies strengths."""
        report = generate_ai_readiness_report(WellDocumentedModel)

        # Should identify primary key as a strength
        assert any("primary key" in s.lower() for s in report.strengths)

    def test_generate_ai_readiness_report_weaknesses(self) -> None:
        """Test AI readiness report identifies weaknesses."""
        report = generate_ai_readiness_report(PoorlyDocumentedModel)

        # Should identify documentation issues
        assert len(report.weaknesses) > 0

    def test_generate_ai_readiness_report_recommendations(self) -> None:
        """Test AI readiness report generates recommendations."""
        report = generate_ai_readiness_report(PoorlyDocumentedModel)

        assert len(report.recommendations) > 0
        # Check recommendation structure
        for rec in report.recommendations:
            assert "priority" in rec or "action" in rec

    def test_generate_ai_readiness_report_grades(self) -> None:
        """Test AI readiness report grading thresholds."""

        class HighScoreModel(GriotModel):
            """A model designed to score high on AI readiness."""

            id: str = Field(
                description="A unique identifier field that is used across all systems",
                primary_key=True,
                pattern=r"^ID-\d{6}$",
                glossary_term="unique_identifier",
            )
            amount: float = Field(
                description="The monetary amount in the transaction record for accounting",
                ge=0,
                le=1000000,
                unit="USD",
                aggregation="sum",
                glossary_term="transaction_amount",
            )

        report = generate_ai_readiness_report(HighScoreModel)
        # This model should score at least a C
        assert report.readiness_grade in ["A", "B", "C"]

    def test_generate_ai_readiness_report_privacy_score_no_pii(self) -> None:
        """Test privacy score for model without PII."""

        class NoPIIModel(GriotModel):
            count: int = Field(description="A counter value")

        report = generate_ai_readiness_report(NoPIIModel)
        # No PII should get neutral score
        assert report.privacy_clarity_score == 80

    def test_generate_ai_readiness_report_privacy_score_with_pii(self) -> None:
        """Test privacy score for model with PII."""
        report = generate_ai_readiness_report(PIIModel)

        # Model with PII should calculate actual privacy score
        assert report.privacy_clarity_score >= 0
        assert report.privacy_clarity_score <= 100

    def test_generate_ai_readiness_report_suggested_context(self) -> None:
        """Test AI readiness report suggested context."""
        report = generate_ai_readiness_report(WellDocumentedModel)

        assert len(report.suggested_context) > 0
        assert "WellDocumentedModel" in report.suggested_context
        assert "customer_id" in report.suggested_context

    def test_generate_ai_readiness_report_truncates_context(self) -> None:
        """Test AI readiness report truncates context for large models."""

        # Create model with many fields
        class LargeModel(GriotModel):
            f1: str = Field(description="Field 1")
            f2: str = Field(description="Field 2")
            f3: str = Field(description="Field 3")
            f4: str = Field(description="Field 4")
            f5: str = Field(description="Field 5")
            f6: str = Field(description="Field 6")
            f7: str = Field(description="Field 7")
            f8: str = Field(description="Field 8")
            f9: str = Field(description="Field 9")
            f10: str = Field(description="Field 10")
            f11: str = Field(description="Field 11")
            f12: str = Field(description="Field 12")

        report = generate_ai_readiness_report(LargeModel)
        assert "and 2 more fields" in report.suggested_context


# =============================================================================
# REPORT OUTPUT FORMAT TESTS
# =============================================================================


class TestReportOutputFormats:
    """Tests for report output format consistency."""

    def test_analytics_report_json_parseable(self) -> None:
        """Test analytics report JSON is parseable."""
        report = generate_analytics_report(WellDocumentedModel)
        json_str = report.to_json()

        # Should not raise
        data = json.loads(json_str)
        assert "contract_name" in data

    def test_ai_readiness_report_json_parseable(self) -> None:
        """Test AI readiness report JSON is parseable."""
        report = generate_ai_readiness_report(WellDocumentedModel)
        json_str = report.to_json()

        # Should not raise
        data = json.loads(json_str)
        assert "contract_name" in data

    def test_analytics_report_markdown_headers(self) -> None:
        """Test analytics report markdown has proper headers."""
        report = generate_analytics_report(WellDocumentedModel)
        md = report.to_markdown()

        assert md.startswith("#")
        assert "##" in md  # Has subsections

    def test_ai_readiness_report_markdown_headers(self) -> None:
        """Test AI readiness report markdown has proper headers."""
        report = generate_ai_readiness_report(WellDocumentedModel)
        md = report.to_markdown()

        assert md.startswith("#")
        assert "##" in md  # Has subsections


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestReportEdgeCases:
    """Tests for edge cases in report generation."""

    def test_analytics_report_all_nullable_fields(self) -> None:
        """Test analytics report with all nullable fields."""

        class AllNullableModel(GriotModel):
            opt1: Optional[str] = Field(description="Optional 1", nullable=True)
            opt2: Optional[str] = Field(description="Optional 2", nullable=True)

        report = generate_analytics_report(AllNullableModel)

        assert len(report.nullable_fields) == 2
        assert len(report.required_fields) == 0

    def test_ai_readiness_needs_improvement_limit(self) -> None:
        """Test AI readiness limits recommendations to top 5."""

        class ManyBadFieldsModel(GriotModel):
            f1: str = Field(description="")
            f2: str = Field(description="")
            f3: str = Field(description="")
            f4: str = Field(description="")
            f5: str = Field(description="")
            f6: str = Field(description="")
            f7: str = Field(description="")
            f8: str = Field(description="")

        report = generate_ai_readiness_report(ManyBadFieldsModel)

        # Should have recommendations but limited
        field_recommendations = [r for r in report.recommendations if "field" in r]
        assert len(field_recommendations) <= 5
