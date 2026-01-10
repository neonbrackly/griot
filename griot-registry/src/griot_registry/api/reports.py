"""Report generation endpoints for griot-registry (T-102).

Provides API endpoints for generating various reports from contracts using
the griot-core report generators.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

router = APIRouter()


class ReportType(str, Enum):
    """Types of reports that can be generated."""

    ANALYTICS = "analytics"
    AI_READINESS = "ai_readiness"
    AUDIT = "audit"
    READINESS = "readiness"


class ReportResponse(BaseModel):
    """Generic report response wrapper."""

    report_type: str
    contract_id: str
    contract_version: str
    generated_at: str
    data: dict[str, Any]


class ReportListResponse(BaseModel):
    """Response for listing available report types."""

    available_reports: list[dict[str, str]]


@router.get(
    "/reports",
    response_model=ReportListResponse,
    summary="List available report types",
    description="Get a list of all available report types and their descriptions.",
)
async def list_report_types() -> ReportListResponse:
    """List all available report types."""
    return ReportListResponse(
        available_reports=[
            {
                "type": "analytics",
                "name": "Analytics Report",
                "description": "Field statistics, constraints, documentation coverage, and PII analysis.",
            },
            {
                "type": "ai_readiness",
                "name": "AI Readiness Report",
                "description": "Assessment of contract's readiness for AI/ML workloads with scoring.",
            },
            {
                "type": "audit",
                "name": "Audit Report",
                "description": "Compliance audit with GDPR, CCPA, HIPAA readiness assessment.",
            },
            {
                "type": "readiness",
                "name": "Combined Readiness Report",
                "description": "Comprehensive report combining analytics, AI readiness, and audit.",
            },
        ]
    )


async def _get_contract_model(request: Request, contract_id: str, version: str | None = None):
    """Helper to get contract and convert to GriotModel for report generation.

    Note: This is a simplified implementation. In production, you would:
    1. Fetch the contract from storage
    2. Convert it to a GriotModel instance
    3. Pass it to the report generators

    For now, we'll create a mock model from the contract data.
    """
    storage = request.app.state.storage
    contract = await storage.get_contract(contract_id, version)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTRACT_NOT_FOUND",
                "message": f"Contract not found: {contract_id}",
            },
        )

    return contract


def _contract_to_report_data(contract) -> dict[str, Any]:
    """Convert contract to data suitable for report generation.

    This creates a simplified representation of the contract
    for report generation purposes.
    """
    from datetime import datetime, timezone

    fields_data = []
    for f in contract.fields:
        field_dict = f.model_dump() if hasattr(f, 'model_dump') else dict(f)
        fields_data.append(field_dict)

    return {
        "contract_id": contract.id,
        "contract_name": contract.name,
        "contract_version": contract.version,
        "description": contract.description,
        "owner": contract.owner,
        "fields": fields_data,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _generate_analytics_report(contract_data: dict[str, Any]) -> dict[str, Any]:
    """Generate analytics report from contract data."""
    fields = contract_data.get("fields", [])

    # Field type distribution
    field_types: dict[str, int] = {}
    nullable_fields = []
    required_fields = []
    pii_fields = []
    sensitive_fields = []
    documented_fields = 0
    fields_with_constraints = 0
    constraint_types: dict[str, int] = {}
    primary_key = None
    unique_fields = []

    for field in fields:
        # Count field types
        ftype = field.get("type", field.get("data_type", "unknown"))
        field_types[ftype] = field_types.get(ftype, 0) + 1

        # Track nullable/required
        if field.get("nullable", True):
            nullable_fields.append(field.get("name", ""))
        else:
            required_fields.append(field.get("name", ""))

        # Track PII
        if field.get("pii_category"):
            pii_fields.append(field.get("name", ""))
        if field.get("sensitivity_level"):
            sensitive_fields.append(field.get("name", ""))

        # Track documentation
        if field.get("description"):
            documented_fields += 1

        # Track constraints
        has_constraint = False
        for constraint_key in ["min_value", "max_value", "min_length", "max_length",
                              "pattern", "enum", "ge", "le", "gt", "lt"]:
            if field.get(constraint_key) is not None:
                has_constraint = True
                constraint_types[constraint_key] = constraint_types.get(constraint_key, 0) + 1
        if has_constraint:
            fields_with_constraints += 1

        # Track keys
        if field.get("primary_key"):
            primary_key = field.get("name", "")
        if field.get("unique"):
            unique_fields.append(field.get("name", ""))

    total_fields = len(fields)
    doc_coverage = (documented_fields / total_fields * 100) if total_fields > 0 else 0

    recommendations = []
    if doc_coverage < 80:
        recommendations.append(f"Documentation coverage is {doc_coverage:.1f}%. Consider adding descriptions to more fields.")
    if not primary_key:
        recommendations.append("No primary key defined. Consider adding a primary key for data integrity.")
    if len(pii_fields) > 0 and len(sensitive_fields) == 0:
        recommendations.append("PII fields detected but no sensitivity levels set. Consider adding sensitivity classifications.")

    return {
        "report_type": "analytics",
        "contract_name": contract_data.get("contract_name", ""),
        "generated_at": contract_data.get("generated_at", ""),
        "summary": {
            "total_fields": total_fields,
            "nullable_count": len(nullable_fields),
            "required_count": len(required_fields),
            "fields_with_constraints": fields_with_constraints,
            "pii_field_count": len(pii_fields),
            "documentation_coverage": doc_coverage,
        },
        "field_types": field_types,
        "constraints": {
            "types": constraint_types,
        },
        "keys": {
            "primary_key": primary_key,
            "unique_fields": unique_fields,
        },
        "privacy": {
            "pii_fields": pii_fields,
            "sensitive_fields": sensitive_fields,
        },
        "recommendations": recommendations,
    }


def _generate_ai_readiness_report(contract_data: dict[str, Any]) -> dict[str, Any]:
    """Generate AI readiness report from contract data."""
    fields = contract_data.get("fields", [])

    # Score components
    total_fields = len(fields)
    documented_fields = sum(1 for f in fields if f.get("description"))
    typed_fields = sum(1 for f in fields if f.get("type") or f.get("data_type"))
    constrained_fields = sum(1 for f in fields if any(
        f.get(k) is not None for k in ["min_value", "max_value", "pattern", "enum"]
    ))

    # Calculate scores (0-100)
    documentation_score = (documented_fields / total_fields * 100) if total_fields > 0 else 0
    type_coverage_score = (typed_fields / total_fields * 100) if total_fields > 0 else 0
    constraint_score = (constrained_fields / total_fields * 100) if total_fields > 0 else 0

    # Overall AI readiness score
    overall_score = (documentation_score * 0.4 + type_coverage_score * 0.3 + constraint_score * 0.3)

    # Determine readiness level
    if overall_score >= 80:
        readiness_level = "HIGH"
        readiness_message = "Contract is well-prepared for AI/ML workloads"
    elif overall_score >= 50:
        readiness_level = "MEDIUM"
        readiness_message = "Contract has moderate AI readiness, improvements recommended"
    else:
        readiness_level = "LOW"
        readiness_message = "Contract needs significant improvements for AI readiness"

    strengths = []
    weaknesses = []

    if documentation_score >= 80:
        strengths.append("Excellent field documentation")
    else:
        weaknesses.append(f"Documentation coverage at {documentation_score:.1f}%")

    if type_coverage_score >= 90:
        strengths.append("Comprehensive type definitions")
    else:
        weaknesses.append(f"Type coverage at {type_coverage_score:.1f}%")

    if constraint_score >= 50:
        strengths.append("Good constraint coverage for data validation")
    else:
        weaknesses.append(f"Limited constraints ({constraint_score:.1f}%)")

    return {
        "report_type": "ai_readiness",
        "contract_name": contract_data.get("contract_name", ""),
        "generated_at": contract_data.get("generated_at", ""),
        "overall_score": round(overall_score, 1),
        "readiness_level": readiness_level,
        "readiness_message": readiness_message,
        "component_scores": {
            "documentation": round(documentation_score, 1),
            "type_coverage": round(type_coverage_score, 1),
            "constraints": round(constraint_score, 1),
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": [
            "Add descriptions to all fields for better AI context",
            "Ensure all fields have explicit types",
            "Add constraints to validate data ranges and formats",
        ] if overall_score < 80 else [],
    }


def _generate_audit_report(contract_data: dict[str, Any]) -> dict[str, Any]:
    """Generate compliance audit report from contract data."""
    fields = contract_data.get("fields", [])

    # PII analysis
    pii_inventory = []
    legal_basis_coverage = 0
    consent_required_fields = []
    retention_defined_fields = []

    for field in fields:
        if field.get("pii_category"):
            pii_inventory.append({
                "field": field.get("name", ""),
                "category": field.get("pii_category"),
                "sensitivity": field.get("sensitivity_level", "unknown"),
                "masking": field.get("masking_strategy"),
                "legal_basis": field.get("legal_basis"),
            })
            if field.get("legal_basis"):
                legal_basis_coverage += 1
            if field.get("consent_required"):
                consent_required_fields.append(field.get("name", ""))
            if field.get("retention_days"):
                retention_defined_fields.append(field.get("name", ""))

    pii_count = len(pii_inventory)
    legal_basis_pct = (legal_basis_coverage / pii_count * 100) if pii_count > 0 else 100

    # Compliance readiness
    gdpr_ready = legal_basis_pct >= 80 and pii_count > 0
    ccpa_ready = pii_count == 0 or any(f.get("masking_strategy") for f in fields if f.get("pii_category"))
    hipaa_ready = not any(f.get("pii_category") == "HEALTH" for f in fields) or all(
        f.get("sensitivity_level") in ["CONFIDENTIAL", "RESTRICTED"]
        for f in fields if f.get("pii_category") == "HEALTH"
    )

    # Compliance score
    compliance_score = 0
    checks_passed = 0
    total_checks = 5

    if pii_count == 0 or legal_basis_pct >= 80:
        checks_passed += 1
    if pii_count == 0 or len(retention_defined_fields) >= pii_count * 0.5:
        checks_passed += 1
    if gdpr_ready:
        checks_passed += 1
    if ccpa_ready:
        checks_passed += 1
    if hipaa_ready:
        checks_passed += 1

    compliance_score = (checks_passed / total_checks * 100)

    return {
        "report_type": "audit",
        "contract_name": contract_data.get("contract_name", ""),
        "generated_at": contract_data.get("generated_at", ""),
        "compliance_score": round(compliance_score, 1),
        "pii_summary": {
            "total_pii_fields": pii_count,
            "legal_basis_coverage": round(legal_basis_pct, 1),
            "consent_required_count": len(consent_required_fields),
            "retention_defined_count": len(retention_defined_fields),
        },
        "pii_inventory": pii_inventory,
        "regulatory_readiness": {
            "gdpr": {"ready": gdpr_ready, "issues": [] if gdpr_ready else ["Legal basis not fully documented"]},
            "ccpa": {"ready": ccpa_ready, "issues": [] if ccpa_ready else ["Masking strategy not defined for PII"]},
            "hipaa": {"ready": hipaa_ready, "issues": [] if hipaa_ready else ["Health data not properly classified"]},
        },
        "recommendations": [
            "Define legal basis for all PII fields" if legal_basis_pct < 100 else None,
            "Set retention periods for PII data" if len(retention_defined_fields) < pii_count else None,
            "Add masking strategies for sensitive fields" if not ccpa_ready else None,
        ],
    }


def _generate_readiness_report(contract_data: dict[str, Any]) -> dict[str, Any]:
    """Generate combined readiness report."""
    analytics = _generate_analytics_report(contract_data)
    ai_readiness = _generate_ai_readiness_report(contract_data)
    audit = _generate_audit_report(contract_data)

    # Calculate overall readiness
    overall_score = (
        analytics["summary"]["documentation_coverage"] * 0.2 +
        ai_readiness["overall_score"] * 0.4 +
        audit["compliance_score"] * 0.4
    )

    # Determine grade
    if overall_score >= 90:
        grade = "A"
    elif overall_score >= 80:
        grade = "B"
    elif overall_score >= 70:
        grade = "C"
    elif overall_score >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "report_type": "readiness",
        "contract_name": contract_data.get("contract_name", ""),
        "generated_at": contract_data.get("generated_at", ""),
        "overall_score": round(overall_score, 1),
        "grade": grade,
        "component_scores": {
            "data_quality": round(analytics["summary"]["documentation_coverage"], 1),
            "ai_readiness": round(ai_readiness["overall_score"], 1),
            "compliance": round(audit["compliance_score"], 1),
        },
        "summary": {
            "analytics": analytics["summary"],
            "ai_readiness": {
                "level": ai_readiness["readiness_level"],
                "strengths": ai_readiness["strengths"],
                "weaknesses": ai_readiness["weaknesses"],
            },
            "compliance": {
                "pii_count": audit["pii_summary"]["total_pii_fields"],
                "gdpr_ready": audit["regulatory_readiness"]["gdpr"]["ready"],
                "ccpa_ready": audit["regulatory_readiness"]["ccpa"]["ready"],
                "hipaa_ready": audit["regulatory_readiness"]["hipaa"]["ready"],
            },
        },
        "recommendations": (
            analytics.get("recommendations", []) +
            ai_readiness.get("recommendations", []) +
            [r for r in audit.get("recommendations", []) if r]
        )[:10],  # Limit to top 10 recommendations
    }


@router.get(
    "/contracts/{contract_id}/reports/{report_type}",
    response_model=ReportResponse,
    summary="Generate report for contract",
    description="Generate a specific type of report for a contract.",
)
async def generate_report(
    request: Request,
    contract_id: str,
    report_type: ReportType,
    version: str | None = Query(None, description="Contract version (latest if not specified)"),
) -> ReportResponse:
    """Generate a report for a contract."""
    contract = await _get_contract_model(request, contract_id, version)
    contract_data = _contract_to_report_data(contract)

    # Generate the appropriate report
    if report_type == ReportType.ANALYTICS:
        report_data = _generate_analytics_report(contract_data)
    elif report_type == ReportType.AI_READINESS:
        report_data = _generate_ai_readiness_report(contract_data)
    elif report_type == ReportType.AUDIT:
        report_data = _generate_audit_report(contract_data)
    elif report_type == ReportType.READINESS:
        report_data = _generate_readiness_report(contract_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_REPORT_TYPE",
                "message": f"Unknown report type: {report_type}",
            },
        )

    return ReportResponse(
        report_type=report_type.value,
        contract_id=contract_id,
        contract_version=contract.version,
        generated_at=contract_data["generated_at"],
        data=report_data,
    )


@router.get(
    "/contracts/{contract_id}/reports",
    response_model=dict[str, ReportResponse],
    summary="Generate all reports for contract",
    description="Generate all available reports for a contract.",
)
async def generate_all_reports(
    request: Request,
    contract_id: str,
    version: str | None = Query(None, description="Contract version (latest if not specified)"),
) -> dict[str, ReportResponse]:
    """Generate all reports for a contract."""
    contract = await _get_contract_model(request, contract_id, version)
    contract_data = _contract_to_report_data(contract)

    reports = {}
    for report_type in ReportType:
        if report_type == ReportType.ANALYTICS:
            report_data = _generate_analytics_report(contract_data)
        elif report_type == ReportType.AI_READINESS:
            report_data = _generate_ai_readiness_report(contract_data)
        elif report_type == ReportType.AUDIT:
            report_data = _generate_audit_report(contract_data)
        elif report_type == ReportType.READINESS:
            report_data = _generate_readiness_report(contract_data)

        reports[report_type.value] = ReportResponse(
            report_type=report_type.value,
            contract_id=contract_id,
            contract_version=contract.version,
            generated_at=contract_data["generated_at"],
            data=report_data,
        )

    return reports
