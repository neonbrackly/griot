"""Validation record endpoints.

Provides endpoints for recording and querying validation results.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import Storage
from griot_registry.auth import CurrentUser, OptionalUser

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class ValidationRecordRequest(BaseModel):
    """Request to record a validation result."""

    contract_id: str
    contract_version: str | None = None
    schema_name: str | None = None
    passed: bool
    row_count: int
    error_count: int = 0
    error_rate: float = 0.0
    duration_ms: float | None = None
    environment: str | None = Field(
        default=None,
        description="Environment: development, staging, production",
    )
    pipeline_id: str | None = None
    run_id: str | None = None
    sample_errors: list[dict[str, Any]] = Field(default_factory=list)


class ValidationRecord(BaseModel):
    """A stored validation record."""

    id: str
    contract_id: str
    contract_version: str | None = None
    schema_name: str | None = None
    passed: bool
    row_count: int
    error_count: int
    error_rate: float
    duration_ms: float | None = None
    environment: str | None = None
    pipeline_id: str | None = None
    run_id: str | None = None
    recorded_at: datetime


class ValidationListResponse(BaseModel):
    """Response for listing validation records."""

    items: list[ValidationRecord]
    total: int
    limit: int
    offset: int


class ValidationStats(BaseModel):
    """Validation statistics for a contract."""

    contract_id: str
    period_days: int
    total_runs: int
    passed_runs: int
    failed_runs: int
    pass_rate: float
    total_rows: int
    total_errors: int
    avg_duration_ms: float


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/validations",
    operation_id="recordValidation",
    summary="Record a validation result",
    status_code=status.HTTP_201_CREATED,
    response_model=ValidationRecord,
)
async def record_validation(
    request: ValidationRecordRequest,
    storage: Storage,
    user: CurrentUser,
) -> ValidationRecord:
    """Record a validation result.

    This endpoint is called by griot-validate or pipeline integrations
    to record validation results for monitoring and auditing.
    """
    record = await storage.validations.record({
        "contract_id": request.contract_id,
        "contract_version": request.contract_version,
        "schema_name": request.schema_name,
        "passed": request.passed,
        "row_count": request.row_count,
        "error_count": request.error_count,
        "error_rate": request.error_rate,
        "duration_ms": request.duration_ms,
        "environment": request.environment,
        "pipeline_id": request.pipeline_id,
        "run_id": request.run_id,
        "sample_errors": request.sample_errors,
        "recorded_by": user.id,
    })

    return ValidationRecord(
        id=record["id"],
        contract_id=record["contract_id"],
        contract_version=record.get("contract_version"),
        schema_name=record.get("schema_name"),
        passed=record["passed"],
        row_count=record["row_count"],
        error_count=record.get("error_count", 0),
        error_rate=record.get("error_rate", 0.0),
        duration_ms=record.get("duration_ms"),
        environment=record.get("environment"),
        pipeline_id=record.get("pipeline_id"),
        run_id=record.get("run_id"),
        recorded_at=record["recorded_at"],
    )


@router.get(
    "/validations",
    operation_id="listValidations",
    summary="List validation records",
    response_model=ValidationListResponse,
)
async def list_validations(
    storage: Storage,
    user: OptionalUser,
    contract_id: str | None = Query(default=None, description="Filter by contract ID"),
    schema_name: str | None = Query(default=None, description="Filter by schema name"),
    passed: bool | None = Query(default=None, description="Filter by pass/fail"),
    from_date: datetime | None = Query(default=None, description="Filter from date"),
    to_date: datetime | None = Query(default=None, description="Filter to date"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ValidationListResponse:
    """List validation records with optional filtering.

    Supports filtering by contract, schema, pass/fail status, and date range.
    """
    records, total = await storage.validations.list(
        contract_id=contract_id,
        schema_name=schema_name,
        passed=passed,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )

    return ValidationListResponse(
        items=[
            ValidationRecord(
                id=r["id"],
                contract_id=r["contract_id"],
                contract_version=r.get("contract_version"),
                schema_name=r.get("schema_name"),
                passed=r["passed"],
                row_count=r["row_count"],
                error_count=r.get("error_count", 0),
                error_rate=r.get("error_rate", 0.0),
                duration_ms=r.get("duration_ms"),
                environment=r.get("environment"),
                pipeline_id=r.get("pipeline_id"),
                run_id=r.get("run_id"),
                recorded_at=r["recorded_at"],
            )
            for r in records
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/validations/stats/{contract_id}",
    operation_id="getValidationStats",
    summary="Get validation statistics",
    response_model=ValidationStats,
)
async def get_validation_stats(
    contract_id: str,
    storage: Storage,
    user: OptionalUser,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> ValidationStats:
    """Get validation statistics for a contract.

    Returns aggregated statistics over the specified time period.
    """
    stats = await storage.validations.get_stats(contract_id, days=days)

    return ValidationStats(
        contract_id=stats["contract_id"],
        period_days=stats["period_days"],
        total_runs=stats["total_runs"],
        passed_runs=stats["passed_runs"],
        failed_runs=stats["failed_runs"],
        pass_rate=stats["pass_rate"],
        total_rows=stats["total_rows"],
        total_errors=stats["total_errors"],
        avg_duration_ms=stats.get("avg_duration_ms", 0.0),
    )
