"""Abstract base classes for storage backends.

This module defines the repository pattern for all storage operations.
The design is extensible to support multiple document types beyond contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar

from griot_core import Contract

# Generic type for document models
T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for CRUD operations on any document type."""

    @abstractmethod
    async def create(self, entity: T, **kwargs: Any) -> T:
        """Create a new entity."""
        ...

    @abstractmethod
    async def get(self, entity_id: str, **kwargs: Any) -> T | None:
        """Get an entity by ID."""
        ...

    @abstractmethod
    async def update(self, entity_id: str, entity: T, **kwargs: Any) -> T:
        """Update an existing entity."""
        ...

    @abstractmethod
    async def delete(self, entity_id: str, **kwargs: Any) -> bool:
        """Delete an entity. Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        **filters: Any,
    ) -> tuple[list[T], int]:
        """List entities with pagination and filtering. Returns (items, total_count)."""
        ...

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if an entity exists."""
        ...


class ContractRepository(BaseRepository[Contract]):
    """Repository interface for Contract storage.

    Extends BaseRepository with contract-specific operations.
    Uses griot-core Contract type directly.
    """

    @abstractmethod
    async def get_version(
        self,
        contract_id: str,
        version: str,
    ) -> Contract | None:
        """Get a specific version of a contract."""
        ...

    @abstractmethod
    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List version history for a contract."""
        ...

    @abstractmethod
    async def update_status(
        self,
        contract_id: str,
        new_status: str,
        updated_by: str | None = None,
    ) -> Contract:
        """Update contract status (for approval workflow)."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Full-text search across contracts."""
        ...


class SchemaCatalogRepository(ABC):
    """Repository interface for schema catalog (cross-contract schema index)."""

    @abstractmethod
    async def find_schemas(
        self,
        name: str | None = None,
        physical_name: str | None = None,
        field_name: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find schemas across all contracts."""
        ...

    @abstractmethod
    async def get_contracts_by_schema(
        self,
        schema_name: str,
    ) -> list[str]:
        """Get contract IDs that contain a schema with given name."""
        ...

    @abstractmethod
    async def rebuild_catalog(self) -> int:
        """Rebuild the entire schema catalog. Returns count of entries created."""
        ...


class ValidationRecordRepository(ABC):
    """Repository interface for validation records."""

    @abstractmethod
    async def record(self, validation: dict[str, Any]) -> dict[str, Any]:
        """Record a validation result."""
        ...

    @abstractmethod
    async def list(
        self,
        contract_id: str | None = None,
        schema_name: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List validation records with filtering."""
        ...

    @abstractmethod
    async def get_stats(
        self,
        contract_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get validation statistics for a contract."""
        ...


class RunRepository(ABC):
    """Repository interface for contract runs (pipeline executions)."""

    @abstractmethod
    async def create(self, run: dict[str, Any]) -> dict[str, Any]:
        """Create a new run record."""
        ...

    @abstractmethod
    async def get(self, run_id: str) -> dict[str, Any] | None:
        """Get a run by ID."""
        ...

    @abstractmethod
    async def update_status(
        self,
        run_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update run status and optionally set result."""
        ...

    @abstractmethod
    async def list(
        self,
        contract_id: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List runs with filtering."""
        ...


class IssueRepository(ABC):
    """Repository interface for contract issues (problems found during runs)."""

    @abstractmethod
    async def create(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Create a new issue."""
        ...

    @abstractmethod
    async def get(self, issue_id: str) -> dict[str, Any] | None:
        """Get an issue by ID."""
        ...

    @abstractmethod
    async def update(self, issue_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update an issue."""
        ...

    @abstractmethod
    async def resolve(
        self,
        issue_id: str,
        resolution: str,
        resolved_by: str,
    ) -> dict[str, Any]:
        """Mark an issue as resolved."""
        ...

    @abstractmethod
    async def list(
        self,
        contract_id: str | None = None,
        run_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List issues with filtering."""
        ...


class CommentRepository(ABC):
    """Repository interface for comments on contracts (collaboration)."""

    @abstractmethod
    async def create(self, comment: dict[str, Any]) -> dict[str, Any]:
        """Create a new comment."""
        ...

    @abstractmethod
    async def get(self, comment_id: str) -> dict[str, Any] | None:
        """Get a comment by ID."""
        ...

    @abstractmethod
    async def update(
        self,
        comment_id: str,
        content: str,
        updated_by: str,
    ) -> dict[str, Any]:
        """Update a comment's content."""
        ...

    @abstractmethod
    async def delete(self, comment_id: str) -> bool:
        """Delete a comment."""
        ...

    @abstractmethod
    async def list(
        self,
        contract_id: str,
        thread_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List comments for a contract, optionally filtered by thread."""
        ...

    @abstractmethod
    async def add_reaction(
        self,
        comment_id: str,
        reaction: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Add a reaction to a comment."""
        ...


class ApprovalRepository(ABC):
    """Repository interface for contract approvals (workflow)."""

    @abstractmethod
    async def create_request(
        self,
        contract_id: str,
        requested_by: str,
        approvers: list[str],
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Create an approval request."""
        ...

    @abstractmethod
    async def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Get an approval request by ID."""
        ...

    @abstractmethod
    async def approve(
        self,
        request_id: str,
        approver: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        """Record an approval."""
        ...

    @abstractmethod
    async def reject(
        self,
        request_id: str,
        rejector: str,
        reason: str,
    ) -> dict[str, Any]:
        """Record a rejection."""
        ...

    @abstractmethod
    async def list_pending(
        self,
        approver: str | None = None,
        contract_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List pending approval requests."""
        ...


class StorageBackend(ABC):
    """Main storage backend interface that provides access to all repositories.

    This is the single entry point for storage operations. Implementations
    should initialize and provide access to all repository types.
    """

    @property
    @abstractmethod
    def contracts(self) -> ContractRepository:
        """Get the contract repository."""
        ...

    @property
    @abstractmethod
    def schema_catalog(self) -> SchemaCatalogRepository:
        """Get the schema catalog repository."""
        ...

    @property
    @abstractmethod
    def validations(self) -> ValidationRecordRepository:
        """Get the validation record repository."""
        ...

    @property
    @abstractmethod
    def runs(self) -> RunRepository:
        """Get the run repository."""
        ...

    @property
    @abstractmethod
    def issues(self) -> IssueRepository:
        """Get the issue repository."""
        ...

    @property
    @abstractmethod
    def comments(self) -> CommentRepository:
        """Get the comment repository."""
        ...

    @property
    @abstractmethod
    def approvals(self) -> ApprovalRepository:
        """Get the approval repository."""
        ...

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend (create indexes, etc.)."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the storage backend and release resources."""
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check storage health. Returns status dict."""
        ...
