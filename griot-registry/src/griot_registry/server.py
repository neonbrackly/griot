"""FastAPI application factory and server entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from griot_registry.api import (
    health,
    auth,
    contracts,
    schemas,
    validations,
    runs,
    issues,
    comments,
    approvals,
    search,
    users,
    teams,
    roles,
    notifications,
    tasks,
)
from griot_registry.config import Settings, get_settings
from griot_registry.services import ContractService, ValidationService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()

    # Startup: initialize storage backend
    storage = await _init_storage(settings)
    app.state.storage = storage

    # Initialize services
    app.state.contract_service = ContractService(storage, settings)
    app.state.validation_service = ValidationService(settings)
    app.state.settings = settings

    yield

    # Shutdown: cleanup
    if hasattr(app.state, "storage"):
        await app.state.storage.close()


async def _init_storage(settings: Settings):
    """Initialize the configured storage backend."""
    from griot_registry.storage import create_storage

    return await create_storage(settings)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override. Uses environment if not provided.

    Returns:
        Configured FastAPI application instance.
    """
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="Griot Registry API",
        description=(
            "Central registry for Griot data contracts. Provides storage, "
            "versioning, validation history, and search capabilities.\n\n"
            "## Authentication\n"
            "- **API Key**: Use `X-API-Key` header for service-to-service auth\n"
            "- **JWT Bearer**: Use `Authorization: Bearer <token>` for user sessions\n\n"
            "## Storage\n"
            "Uses MongoDB for document storage with full-text search capabilities.\n\n"
            "## Key Features\n"
            "- Contract CRUD with validation\n"
            "- Semantic versioning with breaking change detection\n"
            "- Schema catalog for cross-contract queries\n"
            "- Validation history and statistics\n"
            "- Run tracking for pipeline integrations\n"
            "- Issue management\n"
            "- Collaboration comments\n"
            "- Approval workflows"
        ),
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    api_prefix = settings.api_v1_prefix

    # Health checks (no auth required)
    app.include_router(health.router, prefix=api_prefix, tags=["health"])

    # Authentication
    app.include_router(auth.router, prefix=api_prefix, tags=["auth"])

    # Core contract management
    app.include_router(contracts.router, prefix=api_prefix, tags=["contracts"])

    # Schema catalog
    app.include_router(schemas.router, prefix=api_prefix, tags=["schemas"])

    # Validation records
    app.include_router(validations.router, prefix=api_prefix, tags=["validations"])

    # Run tracking
    app.include_router(runs.router, prefix=api_prefix, tags=["runs"])

    # Issue management
    app.include_router(issues.router, prefix=api_prefix, tags=["issues"])

    # Comments/collaboration
    app.include_router(comments.router, prefix=api_prefix, tags=["comments"])

    # Approval workflow
    app.include_router(approvals.router, prefix=api_prefix, tags=["approvals"])

    # Search
    app.include_router(search.router, prefix=api_prefix, tags=["search"])

    # User management
    app.include_router(users.router, prefix=api_prefix, tags=["users"])

    # Team management
    app.include_router(teams.router, prefix=api_prefix, tags=["teams"])

    # Role management
    app.include_router(roles.router, prefix=api_prefix, tags=["roles"])

    # Notifications
    app.include_router(notifications.router, prefix=api_prefix, tags=["notifications"])

    # Tasks
    app.include_router(tasks.router, prefix=api_prefix, tags=["tasks"])

    return app


def main() -> None:
    """Run the server using uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "griot_registry.server:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
