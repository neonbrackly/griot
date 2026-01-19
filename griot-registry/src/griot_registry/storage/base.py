"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from griot_registry.schemas import (
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    SearchResults,
    ValidationList,
    ValidationRecord,
    ValidationReport,
    VersionList,
)


class StorageBackend(ABC):
    """Abstract base class for contract storage backends.

    All storage implementations must inherit from this class and implement
    the abstract methods. The storage backend handles persistence of contracts,
    their versions, validation history, and provides search capabilities.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend.

        Called once during application startup to set up any necessary
        resources (directories, database connections, etc.).
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the storage backend and release resources.

        Called during application shutdown.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the storage backend is healthy.

        Returns:
            True if healthy, raises exception otherwise.
        """
        ...

    # =========================================================================
    # Contract CRUD
    # =========================================================================
    @abstractmethod
    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract.

        Args:
            contract: Contract creation data.

        Returns:
            The created contract with version 1.0.0 and status 'draft'.
        """
        ...

    @abstractmethod
    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract by ID.

        Args:
            contract_id: The contract identifier.
            version: Optional specific version. Defaults to latest.

        Returns:
            The contract if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get a contract as YAML string.

        Args:
            contract_id: The contract identifier.
            version: Optional specific version. Defaults to latest.

        Returns:
            YAML representation of the contract.
        """
        ...

    @abstractmethod
    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
        is_breaking: bool = False,
        breaking_changes: list[dict[str, Any]] | None = None,
    ) -> Contract:
        """Update a contract, creating a new version (T-373 enhanced).

        Args:
            contract_id: The contract identifier.
            update: The update data.
            is_breaking: Whether this update contains breaking changes.
            breaking_changes: List of breaking change details for history tracking.

        Returns:
            The updated contract with new version.
        """
        ...

    @abstractmethod
    async def deprecate_contract(self, contract_id: str) -> None:
        """Mark a contract as deprecated.

        Args:
            contract_id: The contract identifier.
        """
        ...

    @abstractmethod
    async def update_contract_status(
        self,
        contract_id: str,
        new_status: str,
    ) -> Contract:
        """Update the status of a contract.

        Used by the approval workflow to transition contract status.
        Valid status values: draft, active, deprecated, retired

        Args:
            contract_id: The contract identifier.
            new_status: The new status to set.

        Returns:
            The updated contract with new status.
        """
        ...

    @abstractmethod
    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List contracts with optional filtering.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.
            status: Filter by status (draft, active, deprecated).
            owner: Filter by owner.

        Returns:
            Paginated list of contracts.
        """
        ...

    # =========================================================================
    # Versions
    # =========================================================================
    @abstractmethod
    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> VersionList:
        """List all versions of a contract.

        Args:
            contract_id: The contract identifier.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of version summaries.
        """
        ...

    @abstractmethod
    async def diff_contracts(
        self,
        from_contract: Contract,
        to_contract: Contract,
    ) -> ContractDiff:
        """Compute the diff between two contract versions.

        Args:
            from_contract: The source contract version.
            to_contract: The target contract version.

        Returns:
            Diff showing changes between versions.
        """
        ...

    # =========================================================================
    # Validations
    # =========================================================================
    @abstractmethod
    async def record_validation(
        self,
        report: ValidationReport,
    ) -> ValidationRecord:
        """Record a validation result.

        Args:
            report: The validation report from griot-validate.

        Returns:
            The stored validation record.
        """
        ...

    @abstractmethod
    async def list_validations(
        self,
        contract_id: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ValidationList:
        """List validation history with filtering.

        Args:
            contract_id: Filter by contract.
            passed: Filter by pass/fail status.
            from_date: Filter by start date.
            to_date: Filter by end date.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            Paginated list of validation records.
        """
        ...

    # =========================================================================
    # Search
    # =========================================================================
    @abstractmethod
    async def search(
        self,
        query: str,
        field_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResults:
        """Search contracts.

        Args:
            query: Search query string.
            field_filter: Optional field name to restrict search.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            Search results with matching contracts and fields.
        """
        ...
