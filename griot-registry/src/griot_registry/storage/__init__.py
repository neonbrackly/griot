"""Storage backends for griot-registry.

This module provides the storage layer abstraction with MongoDB as the
primary backend. The design follows the repository pattern for extensibility.
"""

from griot_registry.config import Settings
from griot_registry.storage.base import (
    StorageBackend,
    ContractRepository,
    SchemaCatalogRepository,
    ValidationRecordRepository,
    RunRepository,
    IssueRepository,
    CommentRepository,
    ApprovalRepository,
)


async def create_storage(settings: Settings) -> StorageBackend:
    """Create and initialize the configured storage backend.

    Args:
        settings: Application settings containing storage configuration.

    Returns:
        Initialized storage backend instance.

    Raises:
        ValueError: If the configured backend is not supported.
    """
    if settings.storage_backend == "mongodb":
        from griot_registry.storage.mongodb import MongoDBStorage

        storage = MongoDBStorage(
            connection_string=settings.mongodb_uri,
            database_name=settings.mongodb_database,
        )
        await storage.initialize()
        return storage

    else:
        raise ValueError(
            f"Unsupported storage backend: {settings.storage_backend}. "
            f"Supported backends: mongodb"
        )


__all__ = [
    # Factory
    "create_storage",
    # Base classes
    "StorageBackend",
    "ContractRepository",
    "SchemaCatalogRepository",
    "ValidationRecordRepository",
    "RunRepository",
    "IssueRepository",
    "CommentRepository",
    "ApprovalRepository",
]
