"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter

from griot_registry.api.dependencies import Storage

router = APIRouter()


@router.get(
    "/health",
    operation_id="healthCheck",
    summary="Health check",
    response_model=dict[str, Any],
)
async def health_check(storage: Storage) -> dict[str, Any]:
    """Check the health of the registry service.

    Returns:
        Health status including storage backend status.
    """
    storage_health = await storage.health_check()

    return {
        "status": "healthy" if storage_health.get("status") == "healthy" else "degraded",
        "version": "0.2.0",
        "storage": storage_health,
    }


@router.get(
    "/health/live",
    operation_id="livenessCheck",
    summary="Liveness probe",
)
async def liveness() -> dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


@router.get(
    "/health/ready",
    operation_id="readinessCheck",
    summary="Readiness probe",
)
async def readiness(storage: Storage) -> dict[str, str]:
    """Kubernetes readiness probe endpoint."""
    health = await storage.health_check()
    if health.get("status") == "healthy":
        return {"status": "ready"}
    return {"status": "not ready"}
