"""Python client for the Griot Registry API.

This module provides both async and sync clients for interacting with
the Griot Registry API. It uses griot-core types directly for seamless
integration with the rest of the Griot ecosystem.

Usage (async):
    async with RegistryClient("http://localhost:8000") as client:
        contract = await client.get("my-contract")
        await client.push(updated_contract)

Usage (sync):
    with SyncRegistryClient("http://localhost:8000") as client:
        contract = client.get("my-contract")
        client.push(updated_contract)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from griot_core import Contract, load_contract_from_dict, contract_to_dict


class RegistryClientError(Exception):
    """Base exception for registry client errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ContractNotFoundError(RegistryClientError):
    """Raised when a contract is not found."""

    pass


class ValidationError(RegistryClientError):
    """Raised when contract validation fails."""

    pass


class BreakingChangeError(RegistryClientError):
    """Raised when an update contains breaking changes."""

    def __init__(
        self,
        message: str,
        breaking_changes: list[dict[str, Any]],
    ):
        super().__init__(message)
        self.breaking_changes = breaking_changes


class RegistryClient:
    """Async Python client for the Griot Registry API.

    Uses griot-core Contract type directly for seamless integration.

    Example:
        async with RegistryClient("http://localhost:8000", api_key="key") as client:
            # Create a contract
            contract = Contract(id="my-contract", name="My Contract", ...)
            await client.create(contract)

            # Get a contract
            contract = await client.get("my-contract")

            # Update a contract
            await client.update(updated_contract, change_type="minor")

            # Push (create or update)
            await client.push(contract)

            # Pull (get by ID)
            contract = await client.pull("my-contract")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize the registry client.

        Args:
            base_url: Base URL of the registry API
            api_key: API key for authentication (service accounts)
            token: JWT token for authentication (user sessions)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_prefix = "/api/v1"

        headers: dict[str, str] = {}
        if api_key:
            headers["X-API-Key"] = api_key
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "RegistryClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    def _url(self, path: str) -> str:
        """Build full URL for an endpoint."""
        return f"{self.api_prefix}{path}"

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 404:
            raise ContractNotFoundError(
                "Contract not found",
                status_code=404,
                details=response.json() if response.content else {},
            )

        if response.status_code == 409:
            data = response.json() if response.content else {}
            if data.get("code") == "BREAKING_CHANGES_DETECTED":
                raise BreakingChangeError(
                    data.get("message", "Breaking changes detected"),
                    breaking_changes=data.get("breaking_changes", []),
                )
            raise RegistryClientError(
                data.get("message", "Conflict"),
                status_code=409,
                details=data,
            )

        if response.status_code == 422:
            data = response.json() if response.content else {}
            raise ValidationError(
                "Validation failed",
                status_code=422,
                details=data,
            )

        if response.status_code >= 400:
            data = response.json() if response.content else {}
            raise RegistryClientError(
                data.get("message", f"Request failed with status {response.status_code}"),
                status_code=response.status_code,
                details=data,
            )

    # =========================================================================
    # Contract CRUD
    # =========================================================================

    async def create(self, contract: Contract) -> Contract:
        """Create a new contract in the registry.

        Args:
            contract: The contract to create

        Returns:
            The created contract

        Raises:
            RegistryClientError: If the contract already exists or validation fails
        """
        response = await self._client.post(
            self._url("/contracts"),
            json=contract_to_dict(contract),
        )
        self._handle_error(response)
        return load_contract_from_dict(response.json())

    async def get(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract:
        """Get a contract by ID.

        Args:
            contract_id: The contract ID
            version: Optional specific version (defaults to latest)

        Returns:
            The contract

        Raises:
            ContractNotFoundError: If the contract doesn't exist
        """
        if version:
            url = self._url(f"/contracts/{contract_id}/versions/{version}")
        else:
            url = self._url(f"/contracts/{contract_id}")

        response = await self._client.get(url)
        self._handle_error(response)
        return load_contract_from_dict(response.json())

    async def get_or_none(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract by ID, returning None if not found.

        Args:
            contract_id: The contract ID
            version: Optional specific version

        Returns:
            The contract, or None if not found
        """
        try:
            return await self.get(contract_id, version)
        except ContractNotFoundError:
            return None

    async def update(
        self,
        contract: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        allow_breaking: bool = False,
    ) -> Contract:
        """Update an existing contract.

        Args:
            contract: The updated contract
            change_type: Type of change (patch, minor, major)
            change_notes: Notes about the change
            allow_breaking: Whether to allow breaking changes

        Returns:
            The updated contract with new version

        Raises:
            ContractNotFoundError: If the contract doesn't exist
            BreakingChangeError: If breaking changes detected and not allowed
        """
        params: dict[str, Any] = {
            "allow_breaking": str(allow_breaking).lower(),
        }

        body = contract_to_dict(contract)
        body["change_type"] = change_type
        if change_notes:
            body["change_notes"] = change_notes

        response = await self._client.put(
            self._url(f"/contracts/{contract.id}"),
            json=body,
            params=params,
        )
        self._handle_error(response)
        return load_contract_from_dict(response.json())

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
    ) -> tuple[list[Contract], int]:
        """List contracts with optional filtering.

        Args:
            limit: Maximum number of contracts to return
            offset: Number of contracts to skip
            status: Filter by status (draft, active, deprecated, retired)
            schema_name: Filter by schema name
            owner: Filter by owner/team

        Returns:
            Tuple of (contracts, total_count)
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if schema_name:
            params["schema_name"] = schema_name
        if owner:
            params["owner"] = owner

        response = await self._client.get(
            self._url("/contracts"),
            params=params,
        )
        self._handle_error(response)

        data = response.json()
        contracts = [load_contract_from_dict(c) for c in data["items"]]
        return contracts, data["total"]

    async def deprecate(self, contract_id: str) -> None:
        """Deprecate a contract.

        Args:
            contract_id: The contract ID to deprecate

        Raises:
            ContractNotFoundError: If the contract doesn't exist
        """
        response = await self._client.delete(
            self._url(f"/contracts/{contract_id}"),
        )
        self._handle_error(response)

    async def update_status(
        self,
        contract_id: str,
        new_status: str,
    ) -> Contract:
        """Update contract status.

        Args:
            contract_id: The contract ID
            new_status: New status (draft, active, deprecated, retired)

        Returns:
            The updated contract

        Raises:
            RegistryClientError: If the status transition is invalid
        """
        response = await self._client.patch(
            self._url(f"/contracts/{contract_id}/status"),
            json={"status": new_status},
        )
        self._handle_error(response)
        return load_contract_from_dict(response.json())

    # =========================================================================
    # Version Operations
    # =========================================================================

    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List version history for a contract.

        Args:
            contract_id: The contract ID
            limit: Maximum number of versions to return
            offset: Number of versions to skip

        Returns:
            Tuple of (version_summaries, total_count)
        """
        response = await self._client.get(
            self._url(f"/contracts/{contract_id}/versions"),
            params={"limit": limit, "offset": offset},
        )
        self._handle_error(response)

        data = response.json()
        return data["items"], data.get("total", len(data["items"]))

    async def diff(
        self,
        contract_id: str,
        from_version: str,
        to_version: str,
    ) -> dict[str, Any]:
        """Get diff between two versions of a contract.

        Args:
            contract_id: The contract ID
            from_version: Source version
            to_version: Target version

        Returns:
            Diff information including changes and whether they're breaking
        """
        response = await self._client.get(
            self._url(f"/contracts/{contract_id}/diff"),
            params={"from": from_version, "to": to_version},
        )
        self._handle_error(response)
        return response.json()

    # =========================================================================
    # Schema Catalog
    # =========================================================================

    async def find_schemas(
        self,
        name: str | None = None,
        physical_name: str | None = None,
        field_name: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find schemas across all contracts.

        Args:
            name: Filter by schema name (partial match)
            physical_name: Filter by physical table name
            field_name: Filter by field name
            has_pii: Filter by PII flag
            limit: Maximum number of results

        Returns:
            List of schema catalog entries
        """
        params: dict[str, Any] = {"limit": limit}
        if name:
            params["name"] = name
        if physical_name:
            params["physical_name"] = physical_name
        if field_name:
            params["field_name"] = field_name
        if has_pii is not None:
            params["has_pii"] = str(has_pii).lower()

        response = await self._client.get(
            self._url("/schemas"),
            params=params,
        )
        self._handle_error(response)
        return response.json().get("items", [])

    # =========================================================================
    # Validation Records
    # =========================================================================

    async def record_validation(
        self,
        contract_id: str,
        passed: bool,
        row_count: int,
        error_count: int = 0,
        contract_version: str | None = None,
        schema_name: str | None = None,
        duration_ms: float | None = None,
        environment: str | None = None,
        pipeline_id: str | None = None,
        run_id: str | None = None,
        sample_errors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Record a validation result.

        Args:
            contract_id: The contract ID
            passed: Whether validation passed
            row_count: Number of rows validated
            error_count: Number of errors found
            contract_version: Version validated against
            schema_name: Specific schema validated
            duration_ms: Validation duration in milliseconds
            environment: Environment (development, staging, production)
            pipeline_id: Pipeline identifier
            run_id: Run identifier
            sample_errors: Sample of validation errors

        Returns:
            The recorded validation with ID
        """
        body: dict[str, Any] = {
            "contract_id": contract_id,
            "passed": passed,
            "row_count": row_count,
            "error_count": error_count,
        }
        if contract_version:
            body["contract_version"] = contract_version
        if schema_name:
            body["schema_name"] = schema_name
        if duration_ms is not None:
            body["duration_ms"] = duration_ms
        if environment:
            body["environment"] = environment
        if pipeline_id:
            body["pipeline_id"] = pipeline_id
        if run_id:
            body["run_id"] = run_id
        if sample_errors:
            body["sample_errors"] = sample_errors

        response = await self._client.post(
            self._url("/validations"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def list_validations(
        self,
        contract_id: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List validation records.

        Args:
            contract_id: Filter by contract ID
            passed: Filter by pass/fail status
            from_date: Filter by start date
            to_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (validation_records, total_count)
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if contract_id:
            params["contract_id"] = contract_id
        if passed is not None:
            params["passed"] = str(passed).lower()
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()

        response = await self._client.get(
            self._url("/validations"),
            params=params,
        )
        self._handle_error(response)

        data = response.json()
        return data["items"], data["total"]

    # =========================================================================
    # Convenience Methods (Push/Pull)
    # =========================================================================

    async def push(
        self,
        contract: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        allow_breaking: bool = False,
    ) -> Contract:
        """Push a contract to the registry (create or update).

        Args:
            contract: The contract to push
            change_type: Type of change if updating (patch, minor, major)
            change_notes: Notes about the change if updating
            allow_breaking: Whether to allow breaking changes if updating

        Returns:
            The created or updated contract
        """
        existing = await self.get_or_none(contract.id)

        if existing:
            return await self.update(
                contract,
                change_type=change_type,
                change_notes=change_notes,
                allow_breaking=allow_breaking,
            )

        return await self.create(contract)

    async def pull(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract:
        """Pull a contract from the registry.

        Args:
            contract_id: The contract ID
            version: Optional specific version

        Returns:
            The contract

        Raises:
            ContractNotFoundError: If the contract doesn't exist
        """
        return await self.get(contract_id, version)

    # =========================================================================
    # Search
    # =========================================================================

    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search contracts.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of search results
        """
        response = await self._client.get(
            self._url("/search"),
            params={"query": query, "limit": limit},
        )
        self._handle_error(response)
        return response.json().get("items", [])


class SyncRegistryClient:
    """Synchronous wrapper for RegistryClient.

    Provides the same API as RegistryClient but with synchronous methods.
    Uses asyncio under the hood.

    Example:
        with SyncRegistryClient("http://localhost:8000") as client:
            contract = client.get("my-contract")
            client.push(updated_contract)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize the sync registry client.

        Args:
            base_url: Base URL of the registry API
            api_key: API key for authentication
            token: JWT token for authentication
            timeout: Request timeout in seconds
        """
        import asyncio

        self._async_client = RegistryClient(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
        )
        self._loop = asyncio.new_event_loop()

    def _run(self, coro):
        """Run a coroutine synchronously."""
        return self._loop.run_until_complete(coro)

    def close(self) -> None:
        """Close the HTTP client."""
        self._run(self._async_client.close())
        self._loop.close()

    def __enter__(self) -> "SyncRegistryClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # Contract CRUD
    def create(self, contract: Contract) -> Contract:
        """Create a new contract."""
        return self._run(self._async_client.create(contract))

    def get(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract:
        """Get a contract by ID."""
        return self._run(self._async_client.get(contract_id, version))

    def get_or_none(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract by ID, returning None if not found."""
        return self._run(self._async_client.get_or_none(contract_id, version))

    def update(
        self,
        contract: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        allow_breaking: bool = False,
    ) -> Contract:
        """Update an existing contract."""
        return self._run(self._async_client.update(
            contract,
            change_type=change_type,
            change_notes=change_notes,
            allow_breaking=allow_breaking,
        ))

    def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
    ) -> tuple[list[Contract], int]:
        """List contracts with optional filtering."""
        return self._run(self._async_client.list_contracts(
            limit=limit,
            offset=offset,
            status=status,
            schema_name=schema_name,
            owner=owner,
        ))

    def deprecate(self, contract_id: str) -> None:
        """Deprecate a contract."""
        return self._run(self._async_client.deprecate(contract_id))

    def update_status(
        self,
        contract_id: str,
        new_status: str,
    ) -> Contract:
        """Update contract status."""
        return self._run(self._async_client.update_status(contract_id, new_status))

    # Version operations
    def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List version history for a contract."""
        return self._run(self._async_client.list_versions(contract_id, limit, offset))

    def diff(
        self,
        contract_id: str,
        from_version: str,
        to_version: str,
    ) -> dict[str, Any]:
        """Get diff between two versions."""
        return self._run(self._async_client.diff(contract_id, from_version, to_version))

    # Schema catalog
    def find_schemas(
        self,
        name: str | None = None,
        physical_name: str | None = None,
        field_name: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find schemas across all contracts."""
        return self._run(self._async_client.find_schemas(
            name=name,
            physical_name=physical_name,
            field_name=field_name,
            has_pii=has_pii,
            limit=limit,
        ))

    # Convenience methods
    def push(
        self,
        contract: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        allow_breaking: bool = False,
    ) -> Contract:
        """Push a contract (create or update)."""
        return self._run(self._async_client.push(
            contract,
            change_type=change_type,
            change_notes=change_notes,
            allow_breaking=allow_breaking,
        ))

    def pull(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract:
        """Pull a contract from the registry."""
        return self._run(self._async_client.pull(contract_id, version))

    # Search
    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search contracts."""
        return self._run(self._async_client.search(query, limit))
