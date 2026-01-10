"""
Griot Core Reports

Report generation for data contracts including analytics and AI readiness reports.
Uses Python stdlib only (no external dependencies).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from griot_core.models import GriotModel

__all__ = [
    "AnalyticsReport",
    "AIReadinessReport",
    "generate_analytics_report",
    "generate_ai_readiness_report",
]


@dataclass
class AnalyticsReport:
    """
    Analytics report for a data contract.

    Provides detailed statistics about the contract structure,
    field types, constraints, and data quality metrics.
    """

    contract_name: str
    generated_at: str
    version: str = "1.0"

    # Field statistics
    total_fields: int = 0
    field_types: dict[str, int] = dataclass_field(default_factory=dict)
    nullable_fields: list[str] = dataclass_field(default_factory=list)
    required_fields: list[str] = dataclass_field(default_factory=list)

    # Constraint statistics
    fields_with_constraints: int = 0
    constraint_types: dict[str, int] = dataclass_field(default_factory=dict)
    fields_with_patterns: list[str] = dataclass_field(default_factory=list)
    fields_with_enums: list[str] = dataclass_field(default_factory=list)

    # Key information
    primary_key: str | None = None
    unique_fields: list[str] = dataclass_field(default_factory=list)

    # PII/Privacy statistics
    pii_fields: list[str] = dataclass_field(default_factory=list)
    sensitive_fields: list[str] = dataclass_field(default_factory=list)
    pii_categories: dict[str, int] = dataclass_field(default_factory=dict)
    sensitivity_distribution: dict[str, int] = dataclass_field(default_factory=dict)

    # Documentation quality
    documented_fields: int = 0
    fields_with_units: list[str] = dataclass_field(default_factory=list)
    fields_with_glossary: list[str] = dataclass_field(default_factory=list)

    # Recommendations
    recommendations: list[str] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_type": "analytics",
            "contract_name": self.contract_name,
            "generated_at": self.generated_at,
            "version": self.version,
            "summary": {
                "total_fields": self.total_fields,
                "nullable_count": len(self.nullable_fields),
                "required_count": len(self.required_fields),
                "fields_with_constraints": self.fields_with_constraints,
                "pii_field_count": len(self.pii_fields),
                "documentation_coverage": (
                    self.documented_fields / self.total_fields * 100
                    if self.total_fields > 0
                    else 0
                ),
            },
            "field_types": self.field_types,
            "constraints": {
                "types": self.constraint_types,
                "fields_with_patterns": self.fields_with_patterns,
                "fields_with_enums": self.fields_with_enums,
            },
            "keys": {
                "primary_key": self.primary_key,
                "unique_fields": self.unique_fields,
            },
            "privacy": {
                "pii_fields": self.pii_fields,
                "sensitive_fields": self.sensitive_fields,
                "categories": self.pii_categories,
                "sensitivity_distribution": self.sensitivity_distribution,
            },
            "documentation": {
                "documented_fields": self.documented_fields,
                "fields_with_units": self.fields_with_units,
                "fields_with_glossary": self.fields_with_glossary,
            },
            "recommendations": self.recommendations,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Convert report to Markdown format."""
        lines = [
            f"# Analytics Report: {self.contract_name}",
            "",
            f"*Generated: {self.generated_at}*",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Fields | {self.total_fields} |",
            f"| Required Fields | {len(self.required_fields)} |",
            f"| Nullable Fields | {len(self.nullable_fields)} |",
            f"| Fields with Constraints | {self.fields_with_constraints} |",
            f"| PII Fields | {len(self.pii_fields)} |",
            f"| Documentation Coverage | {self.documented_fields}/{self.total_fields} |",
            "",
            "## Field Types",
            "",
        ]

        for ftype, count in sorted(self.field_types.items()):
            lines.append(f"- **{ftype}**: {count}")

        lines.extend([
            "",
            "## Keys",
            "",
            f"- **Primary Key**: {self.primary_key or 'Not defined'}",
            f"- **Unique Fields**: {', '.join(self.unique_fields) or 'None'}",
            "",
        ])

        if self.constraint_types:
            lines.extend([
                "## Constraints",
                "",
            ])
            for ctype, count in sorted(self.constraint_types.items()):
                lines.append(f"- **{ctype}**: {count} fields")
            lines.append("")

        if self.pii_fields:
            lines.extend([
                "## Privacy Information",
                "",
                f"**PII Fields ({len(self.pii_fields)}):** {', '.join(self.pii_fields)}",
                "",
            ])
            if self.pii_categories:
                lines.append("**Categories:**")
                for cat, count in sorted(self.pii_categories.items()):
                    lines.append(f"- {cat}: {count}")
            lines.append("")

        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)


@dataclass
class AIReadinessReport:
    """
    AI/LLM readiness assessment report for a data contract.

    Evaluates how well the contract is documented and structured
    for consumption by AI/ML systems.
    """

    contract_name: str
    generated_at: str
    version: str = "1.0"

    # Overall score (0-100)
    readiness_score: float = 0.0
    readiness_grade: str = "F"  # A, B, C, D, F

    # Component scores (0-100)
    documentation_score: float = 0.0
    type_clarity_score: float = 0.0
    constraint_coverage_score: float = 0.0
    semantic_richness_score: float = 0.0
    privacy_clarity_score: float = 0.0

    # Field-level assessments
    well_documented_fields: list[str] = dataclass_field(default_factory=list)
    needs_improvement: list[dict[str, str]] = dataclass_field(default_factory=list)

    # Strengths and weaknesses
    strengths: list[str] = dataclass_field(default_factory=list)
    weaknesses: list[str] = dataclass_field(default_factory=list)

    # Actionable recommendations
    recommendations: list[dict[str, str]] = dataclass_field(default_factory=list)

    # LLM context suggestions
    suggested_context: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_type": "ai_readiness",
            "contract_name": self.contract_name,
            "generated_at": self.generated_at,
            "version": self.version,
            "scores": {
                "overall": {
                    "score": self.readiness_score,
                    "grade": self.readiness_grade,
                },
                "components": {
                    "documentation": self.documentation_score,
                    "type_clarity": self.type_clarity_score,
                    "constraint_coverage": self.constraint_coverage_score,
                    "semantic_richness": self.semantic_richness_score,
                    "privacy_clarity": self.privacy_clarity_score,
                },
            },
            "field_assessments": {
                "well_documented": self.well_documented_fields,
                "needs_improvement": self.needs_improvement,
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "suggested_context": self.suggested_context,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Convert report to Markdown format."""
        lines = [
            f"# AI Readiness Report: {self.contract_name}",
            "",
            f"*Generated: {self.generated_at}*",
            "",
            "## Overall Score",
            "",
            f"**{self.readiness_score:.1f}/100** (Grade: **{self.readiness_grade}**)",
            "",
            "## Component Scores",
            "",
            "| Component | Score |",
            "|-----------|-------|",
            f"| Documentation | {self.documentation_score:.1f} |",
            f"| Type Clarity | {self.type_clarity_score:.1f} |",
            f"| Constraint Coverage | {self.constraint_coverage_score:.1f} |",
            f"| Semantic Richness | {self.semantic_richness_score:.1f} |",
            f"| Privacy Clarity | {self.privacy_clarity_score:.1f} |",
            "",
        ]

        if self.strengths:
            lines.extend([
                "## Strengths",
                "",
            ])
            for s in self.strengths:
                lines.append(f"- {s}")
            lines.append("")

        if self.weaknesses:
            lines.extend([
                "## Areas for Improvement",
                "",
            ])
            for w in self.weaknesses:
                lines.append(f"- {w}")
            lines.append("")

        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in self.recommendations:
                priority = rec.get("priority", "medium")
                action = rec.get("action", "")
                field = rec.get("field", "")
                if field:
                    lines.append(f"- [{priority.upper()}] **{field}**: {action}")
                else:
                    lines.append(f"- [{priority.upper()}] {action}")
            lines.append("")

        if self.suggested_context:
            lines.extend([
                "## Suggested LLM Context",
                "",
                "```",
                self.suggested_context,
                "```",
                "",
            ])

        return "\n".join(lines)


def generate_analytics_report(model: type[GriotModel]) -> AnalyticsReport:
    """
    Generate an analytics report for a GriotModel.

    Args:
        model: The GriotModel class to analyze.

    Returns:
        AnalyticsReport with detailed statistics.
    """
    from griot_core.types import PIICategory, SensitivityLevel

    report = AnalyticsReport(
        contract_name=model.__name__,
        generated_at=datetime.now().isoformat(),
        total_fields=len(model._griot_fields),
        primary_key=model._griot_primary_key,
    )

    # Analyze each field
    for field_name, field_info in model._griot_fields.items():
        # Field type distribution
        type_name = field_info.type.value
        report.field_types[type_name] = report.field_types.get(type_name, 0) + 1

        # Nullable vs required
        if field_info.nullable:
            report.nullable_fields.append(field_name)
        else:
            report.required_fields.append(field_name)

        # Unique fields
        if field_info.unique:
            report.unique_fields.append(field_name)

        # Constraint analysis
        constraints = field_info.get_constraints()
        if constraints:
            report.fields_with_constraints += 1
            for constraint_type in constraints:
                report.constraint_types[constraint_type] = (
                    report.constraint_types.get(constraint_type, 0) + 1
                )

        if field_info.pattern:
            report.fields_with_patterns.append(field_name)
        if field_info.enum:
            report.fields_with_enums.append(field_name)

        # PII analysis
        if field_info.pii_category and field_info.pii_category != PIICategory.NONE:
            report.pii_fields.append(field_name)
            cat = field_info.pii_category.value
            report.pii_categories[cat] = report.pii_categories.get(cat, 0) + 1

        if field_info.sensitivity_level:
            level = field_info.sensitivity_level.value
            report.sensitivity_distribution[level] = (
                report.sensitivity_distribution.get(level, 0) + 1
            )
            if field_info.sensitivity_level >= SensitivityLevel.CONFIDENTIAL:
                report.sensitive_fields.append(field_name)

        # Documentation quality
        if field_info.description and len(field_info.description) > 10:
            report.documented_fields += 1
        if field_info.unit:
            report.fields_with_units.append(field_name)
        if field_info.glossary_term:
            report.fields_with_glossary.append(field_name)

    # Generate recommendations
    if report.primary_key is None:
        report.recommendations.append(
            "Consider defining a primary key for unique row identification"
        )

    undocumented = report.total_fields - report.documented_fields
    if undocumented > 0:
        report.recommendations.append(
            f"Add descriptions to {undocumented} undocumented fields"
        )

    if report.fields_with_constraints < report.total_fields * 0.5:
        report.recommendations.append(
            "Consider adding more constraints to improve data quality"
        )

    if report.pii_fields and not report.sensitive_fields:
        report.recommendations.append(
            "PII fields detected - consider adding sensitivity levels"
        )

    return report


def generate_ai_readiness_report(model: type[GriotModel]) -> AIReadinessReport:
    """
    Generate an AI readiness assessment report for a GriotModel.

    Evaluates how well the contract is prepared for AI/LLM consumption.

    Args:
        model: The GriotModel class to assess.

    Returns:
        AIReadinessReport with scores and recommendations.
    """
    from griot_core.types import PIICategory

    report = AIReadinessReport(
        contract_name=model.__name__,
        generated_at=datetime.now().isoformat(),
    )

    total_fields = len(model._griot_fields)
    if total_fields == 0:
        report.readiness_score = 0
        report.readiness_grade = "F"
        report.weaknesses.append("No fields defined in contract")
        return report

    # Calculate component scores

    # 1. Documentation score (0-100)
    well_documented = 0
    for field_name, field_info in model._griot_fields.items():
        score = 0
        reasons = []

        # Description quality
        desc = field_info.description or ""
        if len(desc) >= 50:
            score += 40
        elif len(desc) >= 20:
            score += 25
        elif len(desc) > 0:
            score += 10
        else:
            reasons.append("Missing description")

        # Has unit
        if field_info.unit:
            score += 15
        elif field_info.type.value in ["integer", "float"]:
            reasons.append("Numeric field without unit")

        # Has glossary term
        if field_info.glossary_term:
            score += 15

        # Has aggregation hint
        if field_info.aggregation:
            score += 10

        # Has constraints
        if field_info.get_constraints():
            score += 20

        if score >= 70:
            report.well_documented_fields.append(field_name)
            well_documented += 1
        elif reasons:
            report.needs_improvement.append({
                "field": field_name,
                "reasons": reasons,
            })

    report.documentation_score = (well_documented / total_fields) * 100

    # 2. Type clarity score (0-100)
    typed_fields = sum(
        1 for f in model._griot_fields.values()
        if f.type.value != "any"
    )
    report.type_clarity_score = (typed_fields / total_fields) * 100

    # 3. Constraint coverage score (0-100)
    constrained = sum(
        1 for f in model._griot_fields.values()
        if f.get_constraints()
    )
    report.constraint_coverage_score = (constrained / total_fields) * 100

    # 4. Semantic richness score (0-100)
    semantic_points = 0
    max_semantic = total_fields * 3  # unit, glossary, aggregation

    for field_info in model._griot_fields.values():
        if field_info.unit:
            semantic_points += 1
        if field_info.glossary_term:
            semantic_points += 1
        if field_info.aggregation:
            semantic_points += 1

    report.semantic_richness_score = (
        (semantic_points / max_semantic) * 100 if max_semantic > 0 else 0
    )

    # 5. Privacy clarity score (0-100)
    pii_fields = [
        f for f in model._griot_fields.values()
        if f.pii_category and f.pii_category != PIICategory.NONE
    ]
    privacy_points = 0
    max_privacy = len(pii_fields) * 4 if pii_fields else 1

    for field_info in pii_fields:
        if field_info.pii_category:
            privacy_points += 1
        if field_info.sensitivity_level:
            privacy_points += 1
        if field_info.masking_strategy:
            privacy_points += 1
        if field_info.legal_basis:
            privacy_points += 1

    # If no PII, that's fine - score based on explicit NONE marking
    if not pii_fields:
        report.privacy_clarity_score = 80  # Neutral score
    else:
        report.privacy_clarity_score = (privacy_points / max_privacy) * 100

    # Calculate overall score (weighted average)
    report.readiness_score = (
        report.documentation_score * 0.30 +
        report.type_clarity_score * 0.20 +
        report.constraint_coverage_score * 0.20 +
        report.semantic_richness_score * 0.15 +
        report.privacy_clarity_score * 0.15
    )

    # Assign grade
    if report.readiness_score >= 90:
        report.readiness_grade = "A"
    elif report.readiness_score >= 80:
        report.readiness_grade = "B"
    elif report.readiness_score >= 70:
        report.readiness_grade = "C"
    elif report.readiness_score >= 60:
        report.readiness_grade = "D"
    else:
        report.readiness_grade = "F"

    # Identify strengths
    if report.documentation_score >= 80:
        report.strengths.append("Excellent field documentation")
    if report.type_clarity_score == 100:
        report.strengths.append("All fields have explicit types")
    if report.constraint_coverage_score >= 80:
        report.strengths.append("Strong constraint coverage")
    if report.semantic_richness_score >= 70:
        report.strengths.append("Rich semantic metadata")
    if model._griot_primary_key:
        report.strengths.append("Primary key defined")

    # Identify weaknesses
    if report.documentation_score < 50:
        report.weaknesses.append("Many fields lack adequate documentation")
    if report.constraint_coverage_score < 50:
        report.weaknesses.append("Low constraint coverage reduces data quality assurance")
    if report.semantic_richness_score < 30:
        report.weaknesses.append("Limited semantic metadata for AI context")
    if not model._griot_primary_key:
        report.weaknesses.append("No primary key defined")

    # Generate recommendations
    if report.documentation_score < 80:
        report.recommendations.append({
            "priority": "high",
            "action": "Improve field descriptions to be more detailed (50+ characters)",
            "impact": "Better AI understanding of field purposes",
        })

    for item in report.needs_improvement[:5]:  # Top 5
        field = item["field"]
        reasons = item.get("reasons", [])
        if reasons:
            report.recommendations.append({
                "priority": "medium",
                "field": field,
                "action": f"Address: {', '.join(reasons)}",
            })

    if report.semantic_richness_score < 50:
        report.recommendations.append({
            "priority": "medium",
            "action": "Add units to numeric fields and glossary terms for business concepts",
            "impact": "Improved AI interpretation of values",
        })

    # Generate suggested LLM context
    context_lines = [
        f"Contract: {model.__name__}",
        f"Description: {model.__doc__ or 'Data contract'}",
        f"Fields: {total_fields}",
    ]
    if model._griot_primary_key:
        context_lines.append(f"Primary Key: {model._griot_primary_key}")

    # Add field summaries
    context_lines.append("\nField Overview:")
    for field_name, field_info in list(model._griot_fields.items())[:10]:
        desc = field_info.description or "No description"
        context_lines.append(f"- {field_name} ({field_info.type.value}): {desc}")

    if total_fields > 10:
        context_lines.append(f"... and {total_fields - 10} more fields")

    report.suggested_context = "\n".join(context_lines)

    return report
