"""Run management endpoints.

Provides endpoints for tracking pipeline/validation runs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from griot_registry.api.dependencies import Storage
from griot_registry.auth import CurrentUser, OptionalUser

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================


class RunCreateRequest(BaseModel):
    """Request to create a run."""

    contract_id: str
    contract_version: str | None = None
    schema_name: str | None = None
    pipeline_id: str | None = None
    environment: str | None = Field(
        default=None,
        description="Environment: development, staging, production",
    )
    trigger: str | None = Field(
        default=None,
        description="What triggered the run: scheduled, manual, ci",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunUpdateRequest(BaseModel):
    """Request to update a run status."""

    status: str = Field(..., description="Status: pending, running, completed, failed")
    result: dict[str, Any] | None = None


class Run(BaseModel):
    """A run record."""

    id: str
    contract_id: str
    contract_version: str | None = None
    schema_name: str | None = None
    pipeline_id: str | None = None
    environment: str | None = None
    trigger: str | None = None
    status: str
    result: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    created_by: str | None = None


class RunListResponse(BaseModel):
    """Response for listing runs."""

    items: list[Run]
    total: int
    limit: int
    offset: int


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/runs",
    operation_id="createRun",
    summary="Create a run",
    status_code=status.HTTP_201_CREATED,
    response_model=Run,
)
async def create_run(
    request: RunCreateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Run:
    """Create a new run record.

    Use this to track pipeline executions and their results.
    """
    run = await storage.runs.create({
        "contract_id": request.contract_id,
        "contract_version": request.contract_version,
        "schema_name": request.schema_name,
        "pipeline_id": request.pipeline_id,
        "environment": request.environment,
        "trigger": request.trigger,
        "metadata": request.metadata,
        "created_by": user.id,
    })

    return Run(
        id=run["id"],
        contract_id=run["contract_id"],
        contract_version=run.get("contract_version"),
        schema_name=run.get("schema_name"),
        pipeline_id=run.get("pipeline_id"),
        environment=run.get("environment"),
        trigger=run.get("trigger"),
        status=run["status"],
        result=run.get("result"),
        created_at=run["created_at"],
        updated_at=run.get("updated_at"),
        completed_at=run.get("completed_at"),
        created_by=run.get("created_by"),
    )


@router.get(
    "/runs/{run_id}",
    operation_id="getRun",
    summary="Get a run",
    response_model=Run,
    responses={404: {"description": "Run not found"}},
)
async def get_run(
    run_id: str,
    storage: Storage,
    user: OptionalUser,
) -> Run:
    """Get a run by ID."""
    run = await storage.runs.get(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Run '{run_id}' not found"},
        )

    return Run(
        id=run["id"],
        contract_id=run["contract_id"],
        contract_version=run.get("contract_version"),
        schema_name=run.get("schema_name"),
        pipeline_id=run.get("pipeline_id"),
        environment=run.get("environment"),
        trigger=run.get("trigger"),
        status=run["status"],
        result=run.get("result"),
        created_at=run["created_at"],
        updated_at=run.get("updated_at"),
        completed_at=run.get("completed_at"),
        created_by=run.get("created_by"),
    )


@router.patch(
    "/runs/{run_id}",
    operation_id="updateRunStatus",
    summary="Update run status",
    response_model=Run,
    responses={404: {"description": "Run not found"}},
)
async def update_run_status(
    run_id: str,
    request: RunUpdateRequest,
    storage: Storage,
    user: CurrentUser,
) -> Run:
    """Update a run's status and optionally set the result."""
    try:
        run = await storage.runs.update_status(
            run_id=run_id,
            status=request.status,
            result=request.result,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )

    return Run(
        id=run["id"],
        contract_id=run["contract_id"],
        contract_version=run.get("contract_version"),
        schema_name=run.get("schema_name"),
        pipeline_id=run.get("pipeline_id"),
        environment=run.get("environment"),
        trigger=run.get("trigger"),
        status=run["status"],
        result=run.get("result"),
        created_at=run["created_at"],
        updated_at=run.get("updated_at"),
        completed_at=run.get("completed_at"),
        created_by=run.get("created_by"),
    )


@router.get(
    "/runs",
    operation_id="listRuns",
    summary="List runs",
    response_model=RunListResponse,
)
async def list_runs(
    storage: Storage,
    user: OptionalUser,
    contract_id: str | None = Query(default=None, description="Filter by contract ID"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status",
    ),
    from_date: datetime | None = Query(default=None, description="Filter from date"),
    to_date: datetime | None = Query(default=None, description="Filter to date"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RunListResponse:
    """List runs with optional filtering."""
    runs, total = await storage.runs.list(
        contract_id=contract_id,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )

    return RunListResponse(
        items=[
            Run(
                id=r["id"],
                contract_id=r["contract_id"],
                contract_version=r.get("contract_version"),
                schema_name=r.get("schema_name"),
                pipeline_id=r.get("pipeline_id"),
                environment=r.get("environment"),
                trigger=r.get("trigger"),
                status=r["status"],
                result=r.get("result"),
                created_at=r["created_at"],
                updated_at=r.get("updated_at"),
                completed_at=r.get("completed_at"),
                created_by=r.get("created_by"),
            )
            for r in runs
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
