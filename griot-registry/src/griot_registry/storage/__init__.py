"""Storage backends for griot-registry."""

from griot_registry.config import Settings
from griot_registry.storage.base import StorageBackend


async def create_storage(settings: Settings) -> StorageBackend:
    """Create and initialize the configured storage backend.

    Args:
        settings: Application settings containing storage configuration.

    Returns:
        Initialized storage backend instance.

    Raises:
        ValueError: If the configured backend is not supported.
    """
    if settings.storage_backend == "filesystem":
        from griot_registry.storage.filesystem import FilesystemStorage

        storage = FilesystemStorage(settings.storage_path)
        await storage.initialize()
        return storage

    elif settings.storage_backend == "git":
        from griot_registry.storage.git import GitStorage

        if settings.git_repo_path is None:
            raise ValueError("git_repo_path must be set when using git storage backend")
        storage = GitStorage(settings.git_repo_path, settings.git_branch)
        await storage.initialize()
        return storage

    elif settings.storage_backend == "postgres":
        from griot_registry.storage.postgres import PostgresStorage

        if settings.postgres_dsn is None:
            raise ValueError("postgres_dsn must be set when using postgres storage backend")
        storage = PostgresStorage(settings.postgres_dsn)
        await storage.initialize()
        return storage

    else:
        raise ValueError(f"Unsupported storage backend: {settings.storage_backend}")


__all__ = ["StorageBackend", "create_storage"]
