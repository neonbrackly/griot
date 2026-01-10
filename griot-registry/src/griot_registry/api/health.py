"""Health check endpoint."""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse, operation_id="healthCheck")
async def health_check(request: Request) -> HealthResponse:
    """Check service health status.

    Returns current health status, version, and timestamp.
    """
    # Check storage backend health
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    if hasattr(request.app.state, "storage"):
        try:
            await request.app.state.storage.health_check()
        except Exception:
            status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )
