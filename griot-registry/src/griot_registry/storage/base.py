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
    async def update_metadata(
        self,
        contract_id: str,
        metadata: dict[str, Any],
        updated_by: str | None = None,
    ) -> Contract:
        """Update contract metadata without creating a new version.

        Use for non-content changes like reviewer assignment, tags, etc.
        """
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


class UserRepository(ABC):
    """Repository interface for user management."""

    @abstractmethod
    async def create(self, user: dict[str, Any]) -> dict[str, Any]:
        """Create a new user."""
        ...

    @abstractmethod
    async def get(self, user_id: str) -> dict[str, Any] | None:
        """Get a user by ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Get a user by email."""
        ...

    @abstractmethod
    async def update(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a user."""
        ...

    @abstractmethod
    async def list(
        self,
        search: str | None = None,
        role_id: str | None = None,
        team_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List users with filtering."""
        ...

    @abstractmethod
    async def increment_failed_login(self, user_id: str) -> int:
        """Increment failed login counter. Returns new count."""
        ...

    @abstractmethod
    async def reset_failed_login(self, user_id: str) -> None:
        """Reset failed login counter and unlock."""
        ...


class TeamRepository(ABC):
    """Repository interface for team management."""

    @abstractmethod
    async def create(self, team: dict[str, Any]) -> dict[str, Any]:
        """Create a new team."""
        ...

    @abstractmethod
    async def get(self, team_id: str) -> dict[str, Any] | None:
        """Get a team by ID."""
        ...

    @abstractmethod
    async def update(self, team_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a team."""
        ...

    @abstractmethod
    async def delete(self, team_id: str) -> bool:
        """Delete a team."""
        ...

    @abstractmethod
    async def list(
        self,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List teams with filtering."""
        ...

    @abstractmethod
    async def add_member(
        self,
        team_id: str,
        user_id: str,
        role_id: str,
    ) -> dict[str, Any]:
        """Add a member to a team."""
        ...

    @abstractmethod
    async def update_member_role(
        self,
        team_id: str,
        user_id: str,
        role_id: str,
    ) -> dict[str, Any]:
        """Update a member's role in a team."""
        ...

    @abstractmethod
    async def remove_member(
        self,
        team_id: str,
        user_id: str,
    ) -> bool:
        """Remove a member from a team."""
        ...


class RoleRepository(ABC):
    """Repository interface for role management."""

    @abstractmethod
    async def create(self, role: dict[str, Any]) -> dict[str, Any]:
        """Create a new role."""
        ...

    @abstractmethod
    async def get(self, role_id: str) -> dict[str, Any] | None:
        """Get a role by ID."""
        ...

    @abstractmethod
    async def update(self, role_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a role."""
        ...

    @abstractmethod
    async def delete(self, role_id: str) -> bool:
        """Delete a role."""
        ...

    @abstractmethod
    async def list(self) -> list[dict[str, Any]]:
        """List all roles."""
        ...

    @abstractmethod
    async def seed_system_roles(self) -> None:
        """Create/update system roles (Admin, Editor, Viewer)."""
        ...


class NotificationRepository(ABC):
    """Repository interface for notifications."""

    @abstractmethod
    async def create(self, notification: dict[str, Any]) -> dict[str, Any]:
        """Create a notification."""
        ...

    @abstractmethod
    async def list(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """List notifications for a user. Returns (items, total, unread_count)."""
        ...

    @abstractmethod
    async def mark_read(self, notification_id: str) -> dict[str, Any]:
        """Mark a notification as read."""
        ...

    @abstractmethod
    async def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read. Returns count updated."""
        ...


class TaskRepository(ABC):
    """Repository interface for tasks."""

    @abstractmethod
    async def create(self, task: dict[str, Any]) -> dict[str, Any]:
        """Create a task."""
        ...

    @abstractmethod
    async def get(self, task_id: str) -> dict[str, Any] | None:
        """Get a task by ID."""
        ...

    @abstractmethod
    async def update(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a task."""
        ...

    @abstractmethod
    async def list(
        self,
        user_id: str,
        type: str | None = None,
        status: str | None = None,
        limit: int = 10,
    ) -> tuple[list[dict[str, Any]], int]:
        """List tasks for a user."""
        ...


class PasswordResetRepository(ABC):
    """Repository interface for password reset tokens."""

    @abstractmethod
    async def create(self, token_data: dict[str, Any]) -> dict[str, Any]:
        """Create a password reset token."""
        ...

    @abstractmethod
    async def get_by_token(self, token: str) -> dict[str, Any] | None:
        """Get token data by token string."""
        ...

    @abstractmethod
    async def mark_used(self, token_id: str) -> None:
        """Mark a token as used."""
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Delete expired tokens. Returns count deleted."""
        ...


class SchemaRepository(ABC):
    """Repository interface for standalone schema management.

    Schemas are first-class entities that can be:
    - Created manually (source="manual")
    - Discovered from connections (source="connection")
    - Referenced by contracts via schemaId + version
    """

    @abstractmethod
    async def create(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Create a new schema."""
        ...

    @abstractmethod
    async def get(self, schema_id: str) -> dict[str, Any] | None:
        """Get a schema by ID (returns current version)."""
        ...

    @abstractmethod
    async def get_version(
        self,
        schema_id: str,
        version: str,
    ) -> dict[str, Any] | None:
        """Get a specific version of a schema."""
        ...

    @abstractmethod
    async def update(
        self,
        schema_id: str,
        updates: dict[str, Any],
        updated_by: str,
    ) -> dict[str, Any]:
        """Update a schema. May create new version for breaking changes."""
        ...

    @abstractmethod
    async def delete(self, schema_id: str) -> bool:
        """Delete a schema. Only allowed if not referenced by contracts."""
        ...

    @abstractmethod
    async def list(
        self,
        search: str | None = None,
        domain: str | None = None,
        source: str | None = None,
        status: str | None = None,
        owner_id: str | None = None,
        owner_team_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List schemas with filtering."""
        ...

    @abstractmethod
    async def exists(self, schema_id: str) -> bool:
        """Check if a schema exists."""
        ...

    @abstractmethod
    async def update_status(
        self,
        schema_id: str,
        new_status: str,
        updated_by: str,
    ) -> dict[str, Any]:
        """Update schema status (publish, deprecate, etc.)."""
        ...

    @abstractmethod
    async def list_versions(
        self,
        schema_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List version history for a schema."""
        ...

    @abstractmethod
    async def create_version(
        self,
        schema_id: str,
        new_version: str,
        schema_data: dict[str, Any],
        change_type: str,
        change_notes: str,
        created_by: str,
    ) -> dict[str, Any]:
        """Create a new version of a schema."""
        ...

    @abstractmethod
    async def get_contracts_using_schema(
        self,
        schema_id: str,
        version: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get contracts that reference this schema."""
        ...

    @abstractmethod
    async def can_delete(self, schema_id: str) -> tuple[bool, list[dict[str, Any]]]:
        """Check if schema can be deleted. Returns (can_delete, dependent_contracts)."""
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

    @property
    @abstractmethod
    def users(self) -> UserRepository:
        """Get the user repository."""
        ...

    @property
    @abstractmethod
    def teams(self) -> TeamRepository:
        """Get the team repository."""
        ...

    @property
    @abstractmethod
    def roles(self) -> RoleRepository:
        """Get the role repository."""
        ...

    @property
    @abstractmethod
    def notifications(self) -> NotificationRepository:
        """Get the notification repository."""
        ...

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Get the task repository."""
        ...

    @property
    @abstractmethod
    def password_resets(self) -> PasswordResetRepository:
        """Get the password reset repository."""
        ...

    @property
    @abstractmethod
    def schemas(self) -> SchemaRepository:
        """Get the schema repository for standalone schema management."""
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
