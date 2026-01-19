"""Validation history endpoints."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from griot_registry.schemas import (
    ErrorResponse,
    ValidationList,
    ValidationRecord,
    ValidationReport,
)
from griot_registry.storage.base import StorageBackend

router = APIRouter()


async def get_storage(request: Request) -> StorageBackend:
    """Dependency to get storage backend from app state."""
    return request.app.state.storage


StorageDep = Annotated[StorageBackend, Depends(get_storage)]


@router.post(
    "/validations",
    response_model=ValidationRecord,
    status_code=status.HTTP_201_CREATED,
    operation_id="reportValidation",
)
async def report_validation(
    storage: StorageDep,
    report: ValidationReport,
) -> ValidationRecord:
    """Report a validation result.

    Called by griot-validate to report runtime validation results.
    The validation is recorded in history for auditing and analytics.
    """
    # Verify contract exists
    contract = await storage.get_contract(report.contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"Contract '{report.contract_id}' not found",
            },
        )

    return await storage.record_validation(report)


@router.get(
    "/validations",
    response_model=ValidationList,
    operation_id="listValidations",
)
async def list_validations(
    storage: StorageDep,
    contract_id: str | None = None,
    passed: bool | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ValidationList:
    """List validation history with optional filters.

    Filter by:
    - contract_id: Specific contract
    - passed: Only passed (true) or failed (false) validations
    - from_date/to_date: Date range
    """
    return await storage.list_validations(
        contract_id=contract_id,
        passed=passed,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/contracts/{contract_id}/validations",
    response_model=ValidationList,
    operation_id="getContractValidations",
    responses={404: {"model": ErrorResponse}},
)
async def get_contract_validations(
    storage: StorageDep,
    contract_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ValidationList:
    """Get validation history for a specific contract."""
    # Verify contract exists
    contract = await storage.get_contract(contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Contract '{contract_id}' not found"},
        )

    return await storage.list_validations(
        contract_id=contract_id,
        limit=limit,
        offset=offset,
    )
