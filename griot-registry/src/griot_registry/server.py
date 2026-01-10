"""FastAPI application factory and server entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from griot_registry.api import contracts, health, search, validations
from griot_registry.config import Settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()
    # Startup: initialize storage backend
    storage = await _init_storage(settings)
    app.state.storage = storage
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
        description="Central registry for Griot data contracts. Provides storage, "
        "versioning, validation history, and search capabilities.",
        version="0.1.0",
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
    app.include_router(health.router, prefix=api_prefix, tags=["health"])
    app.include_router(contracts.router, prefix=api_prefix, tags=["contracts"])
    app.include_router(validations.router, prefix=api_prefix, tags=["validations"])
    app.include_router(search.router, prefix=api_prefix, tags=["search"])

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
