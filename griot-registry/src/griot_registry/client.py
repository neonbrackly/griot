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

    async def advanced_search(
        self,
        query: str | None = None,
        name: str | None = None,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Advanced search with multiple filters.

        Args:
            query: Text search query
            name: Filter by contract name
            status: Filter by status (draft, active, deprecated, retired)
            schema_name: Filter by schema name
            owner: Filter by owner
            has_pii: Filter by PII flag
            limit: Maximum number of results

        Returns:
            List of search results
        """
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if name:
            params["name"] = name
        if status:
            params["status"] = status
        if schema_name:
            params["schema_name"] = schema_name
        if owner:
            params["owner"] = owner
        if has_pii is not None:
            params["has_pii"] = str(has_pii).lower()

        response = await self._client.get(
            self._url("/search/advanced"),
            params=params,
        )
        self._handle_error(response)
        return response.json().get("items", [])

    # =========================================================================
    # Schema Catalog (additional methods)
    # =========================================================================

    async def get_contracts_by_schema(
        self,
        schema_name: str,
    ) -> dict[str, Any]:
        """Get all contracts containing a specific schema.

        Args:
            schema_name: The schema name to search for

        Returns:
            Dict with schema_name, contract_ids, and count
        """
        response = await self._client.get(
            self._url(f"/schemas/contracts/{schema_name}"),
        )
        self._handle_error(response)
        return response.json()

    async def rebuild_schema_catalog(self) -> dict[str, Any]:
        """Rebuild the schema catalog index.

        Returns:
            Dict with status and schemas_indexed count
        """
        response = await self._client.post(
            self._url("/schemas/rebuild"),
        )
        self._handle_error(response)
        return response.json()

    # =========================================================================
    # Validation Records (additional methods)
    # =========================================================================

    async def get_validation_stats(
        self,
        contract_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get validation statistics for a contract.

        Args:
            contract_id: The contract ID
            days: Number of days to include (1-365, default 30)

        Returns:
            Dict with validation statistics including pass_rate, total_runs, etc.
        """
        response = await self._client.get(
            self._url(f"/validations/stats/{contract_id}"),
            params={"days": days},
        )
        self._handle_error(response)
        return response.json()

    # =========================================================================
    # Runs
    # =========================================================================

    async def create_run(
        self,
        contract_id: str,
        contract_version: str | None = None,
        schema_name: str | None = None,
        pipeline_id: str | None = None,
        environment: str | None = None,
        trigger: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new run record.

        Args:
            contract_id: The contract ID
            contract_version: Version being validated
            schema_name: Specific schema being validated
            pipeline_id: Pipeline identifier
            environment: Environment (development, staging, production)
            trigger: What triggered the run
            metadata: Additional metadata

        Returns:
            The created run record with ID
        """
        body: dict[str, Any] = {"contract_id": contract_id}
        if contract_version:
            body["contract_version"] = contract_version
        if schema_name:
            body["schema_name"] = schema_name
        if pipeline_id:
            body["pipeline_id"] = pipeline_id
        if environment:
            body["environment"] = environment
        if trigger:
            body["trigger"] = trigger
        if metadata:
            body["metadata"] = metadata

        response = await self._client.post(
            self._url("/runs"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def get_run(self, run_id: str) -> dict[str, Any]:
        """Get a run by ID.

        Args:
            run_id: The run ID

        Returns:
            The run record
        """
        response = await self._client.get(
            self._url(f"/runs/{run_id}"),
        )
        self._handle_error(response)
        return response.json()

    async def update_run_status(
        self,
        run_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update a run's status.

        Args:
            run_id: The run ID
            status: New status (pending, running, completed, failed)
            result: Optional result data

        Returns:
            The updated run record
        """
        body: dict[str, Any] = {"status": status}
        if result:
            body["result"] = result

        response = await self._client.patch(
            self._url(f"/runs/{run_id}"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def list_runs(
        self,
        contract_id: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List runs with optional filtering.

        Args:
            contract_id: Filter by contract ID
            status: Filter by status (pending, running, completed, failed)
            from_date: Filter by start date
            to_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (runs, total_count)
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if contract_id:
            params["contract_id"] = contract_id
        if status:
            params["status"] = status
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()

        response = await self._client.get(
            self._url("/runs"),
            params=params,
        )
        self._handle_error(response)

        data = response.json()
        return data["items"], data["total"]

    # =========================================================================
    # Issues
    # =========================================================================

    async def create_issue(
        self,
        contract_id: str,
        title: str,
        description: str | None = None,
        severity: str = "warning",
        category: str | None = None,
        run_id: str | None = None,
        affected_field: str | None = None,
        affected_schema: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new issue.

        Args:
            contract_id: The contract ID
            title: Issue title
            description: Issue description
            severity: Severity level (error, warning, info)
            category: Issue category
            run_id: Associated run ID
            affected_field: Affected field name
            affected_schema: Affected schema name
            metadata: Additional metadata

        Returns:
            The created issue with ID
        """
        body: dict[str, Any] = {
            "contract_id": contract_id,
            "title": title,
            "severity": severity,
        }
        if description:
            body["description"] = description
        if category:
            body["category"] = category
        if run_id:
            body["run_id"] = run_id
        if affected_field:
            body["affected_field"] = affected_field
        if affected_schema:
            body["affected_schema"] = affected_schema
        if metadata:
            body["metadata"] = metadata

        response = await self._client.post(
            self._url("/issues"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def get_issue(self, issue_id: str) -> dict[str, Any]:
        """Get an issue by ID.

        Args:
            issue_id: The issue ID

        Returns:
            The issue record
        """
        response = await self._client.get(
            self._url(f"/issues/{issue_id}"),
        )
        self._handle_error(response)
        return response.json()

    async def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        description: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
    ) -> dict[str, Any]:
        """Update an issue.

        Args:
            issue_id: The issue ID
            title: New title
            description: New description
            severity: New severity
            status: New status
            assignee: New assignee

        Returns:
            The updated issue
        """
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if severity is not None:
            body["severity"] = severity
        if status is not None:
            body["status"] = status
        if assignee is not None:
            body["assignee"] = assignee

        response = await self._client.patch(
            self._url(f"/issues/{issue_id}"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def resolve_issue(
        self,
        issue_id: str,
        resolution: str,
    ) -> dict[str, Any]:
        """Resolve an issue.

        Args:
            issue_id: The issue ID
            resolution: Resolution description

        Returns:
            The resolved issue
        """
        response = await self._client.post(
            self._url(f"/issues/{issue_id}/resolve"),
            json={"resolution": resolution},
        )
        self._handle_error(response)
        return response.json()

    async def list_issues(
        self,
        contract_id: str | None = None,
        run_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List issues with optional filtering.

        Args:
            contract_id: Filter by contract ID
            run_id: Filter by run ID
            status: Filter by status (open, resolved)
            severity: Filter by severity (error, warning, info)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (issues, total_count)
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if contract_id:
            params["contract_id"] = contract_id
        if run_id:
            params["run_id"] = run_id
        if status:
            params["status"] = status
        if severity:
            params["severity"] = severity

        response = await self._client.get(
            self._url("/issues"),
            params=params,
        )
        self._handle_error(response)

        data = response.json()
        return data["items"], data["total"]

    # =========================================================================
    # Comments
    # =========================================================================

    async def create_comment(
        self,
        contract_id: str,
        content: str,
        thread_id: str | None = None,
        section: str | None = None,
        field_path: str | None = None,
    ) -> dict[str, Any]:
        """Create a new comment on a contract.

        Args:
            contract_id: The contract ID
            content: Comment content
            thread_id: Optional parent comment ID for threading
            section: Contract section being commented on
            field_path: Specific field path being commented on

        Returns:
            The created comment with ID
        """
        body: dict[str, Any] = {
            "contract_id": contract_id,
            "content": content,
        }
        if thread_id:
            body["thread_id"] = thread_id
        if section:
            body["section"] = section
        if field_path:
            body["field_path"] = field_path

        response = await self._client.post(
            self._url("/comments"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def get_comment(self, comment_id: str) -> dict[str, Any]:
        """Get a comment by ID.

        Args:
            comment_id: The comment ID

        Returns:
            The comment record
        """
        response = await self._client.get(
            self._url(f"/comments/{comment_id}"),
        )
        self._handle_error(response)
        return response.json()

    async def update_comment(
        self,
        comment_id: str,
        content: str,
    ) -> dict[str, Any]:
        """Update a comment.

        Args:
            comment_id: The comment ID
            content: New content

        Returns:
            The updated comment
        """
        response = await self._client.patch(
            self._url(f"/comments/{comment_id}"),
            json={"content": content},
        )
        self._handle_error(response)
        return response.json()

    async def delete_comment(self, comment_id: str) -> None:
        """Delete a comment.

        Args:
            comment_id: The comment ID to delete
        """
        response = await self._client.delete(
            self._url(f"/comments/{comment_id}"),
        )
        self._handle_error(response)

    async def add_reaction(
        self,
        comment_id: str,
        reaction: str,
    ) -> dict[str, Any]:
        """Add a reaction to a comment.

        Args:
            comment_id: The comment ID
            reaction: The reaction emoji

        Returns:
            The updated comment with reactions
        """
        response = await self._client.post(
            self._url(f"/comments/{comment_id}/reactions"),
            json={"reaction": reaction},
        )
        self._handle_error(response)
        return response.json()

    async def list_contract_comments(
        self,
        contract_id: str,
        thread_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List comments for a contract.

        Args:
            contract_id: The contract ID
            thread_id: Optional filter by thread
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (comments, total_count)
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if thread_id:
            params["thread_id"] = thread_id

        response = await self._client.get(
            self._url(f"/contracts/{contract_id}/comments"),
            params=params,
        )
        self._handle_error(response)

        data = response.json()
        return data["items"], data["total"]

    # =========================================================================
    # Approvals
    # =========================================================================

    async def create_approval_request(
        self,
        contract_id: str,
        request_type: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an approval request.

        Args:
            contract_id: The contract ID
            request_type: Type of request (activation, deprecation, update, deletion)
            title: Request title
            description: Request description

        Returns:
            The created approval request with ID
        """
        body: dict[str, Any] = {
            "contract_id": contract_id,
            "request_type": request_type,
            "title": title,
        }
        if description:
            body["description"] = description

        response = await self._client.post(
            self._url("/approvals"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def list_pending_approvals(
        self,
        my_approvals: bool = False,
    ) -> list[dict[str, Any]]:
        """List pending approval requests.

        Args:
            my_approvals: If True, only return approvals assigned to current user

        Returns:
            List of pending approval requests
        """
        params: dict[str, Any] = {}
        if my_approvals:
            params["my_approvals"] = "true"

        response = await self._client.get(
            self._url("/approvals/pending"),
            params=params,
        )
        self._handle_error(response)
        return response.json()

    async def get_approval_request(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """Get an approval request by ID.

        Args:
            request_id: The approval request ID

        Returns:
            The approval request
        """
        response = await self._client.get(
            self._url(f"/approvals/{request_id}"),
        )
        self._handle_error(response)
        return response.json()

    async def approve_request(
        self,
        request_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Approve an approval request.

        Args:
            request_id: The approval request ID
            comment: Optional approval comment

        Returns:
            The updated approval request
        """
        body: dict[str, Any] = {}
        if comment:
            body["comment"] = comment

        response = await self._client.post(
            self._url(f"/approvals/{request_id}/approve"),
            json=body,
        )
        self._handle_error(response)
        return response.json()

    async def reject_request(
        self,
        request_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Reject an approval request.

        Args:
            request_id: The approval request ID
            comment: Optional rejection comment

        Returns:
            The updated approval request
        """
        body: dict[str, Any] = {}
        if comment:
            body["comment"] = comment

        response = await self._client.post(
            self._url(f"/approvals/{request_id}/reject"),
            json=body,
        )
        self._handle_error(response)
        return response.json()


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

    def advanced_search(
        self,
        query: str | None = None,
        name: str | None = None,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Advanced search with multiple filters."""
        return self._run(self._async_client.advanced_search(
            query=query,
            name=name,
            status=status,
            schema_name=schema_name,
            owner=owner,
            has_pii=has_pii,
            limit=limit,
        ))

    # Schema catalog (additional methods)
    def get_contracts_by_schema(
        self,
        schema_name: str,
    ) -> dict[str, Any]:
        """Get all contracts containing a specific schema."""
        return self._run(self._async_client.get_contracts_by_schema(schema_name))

    def rebuild_schema_catalog(self) -> dict[str, Any]:
        """Rebuild the schema catalog index."""
        return self._run(self._async_client.rebuild_schema_catalog())

    # Validation records (additional methods)
    def get_validation_stats(
        self,
        contract_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get validation statistics for a contract."""
        return self._run(self._async_client.get_validation_stats(contract_id, days))

    def record_validation(
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
        """Record a validation result."""
        return self._run(self._async_client.record_validation(
            contract_id=contract_id,
            passed=passed,
            row_count=row_count,
            error_count=error_count,
            contract_version=contract_version,
            schema_name=schema_name,
            duration_ms=duration_ms,
            environment=environment,
            pipeline_id=pipeline_id,
            run_id=run_id,
            sample_errors=sample_errors,
        ))

    def list_validations(
        self,
        contract_id: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List validation records."""
        return self._run(self._async_client.list_validations(
            contract_id=contract_id,
            passed=passed,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        ))

    # Runs
    def create_run(
        self,
        contract_id: str,
        contract_version: str | None = None,
        schema_name: str | None = None,
        pipeline_id: str | None = None,
        environment: str | None = None,
        trigger: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new run record."""
        return self._run(self._async_client.create_run(
            contract_id=contract_id,
            contract_version=contract_version,
            schema_name=schema_name,
            pipeline_id=pipeline_id,
            environment=environment,
            trigger=trigger,
            metadata=metadata,
        ))

    def get_run(self, run_id: str) -> dict[str, Any]:
        """Get a run by ID."""
        return self._run(self._async_client.get_run(run_id))

    def update_run_status(
        self,
        run_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update a run's status."""
        return self._run(self._async_client.update_run_status(run_id, status, result))

    def list_runs(
        self,
        contract_id: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List runs with optional filtering."""
        return self._run(self._async_client.list_runs(
            contract_id=contract_id,
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        ))

    # Issues
    def create_issue(
        self,
        contract_id: str,
        title: str,
        description: str | None = None,
        severity: str = "warning",
        category: str | None = None,
        run_id: str | None = None,
        affected_field: str | None = None,
        affected_schema: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new issue."""
        return self._run(self._async_client.create_issue(
            contract_id=contract_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            run_id=run_id,
            affected_field=affected_field,
            affected_schema=affected_schema,
            metadata=metadata,
        ))

    def get_issue(self, issue_id: str) -> dict[str, Any]:
        """Get an issue by ID."""
        return self._run(self._async_client.get_issue(issue_id))

    def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        description: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
    ) -> dict[str, Any]:
        """Update an issue."""
        return self._run(self._async_client.update_issue(
            issue_id=issue_id,
            title=title,
            description=description,
            severity=severity,
            status=status,
            assignee=assignee,
        ))

    def resolve_issue(
        self,
        issue_id: str,
        resolution: str,
    ) -> dict[str, Any]:
        """Resolve an issue."""
        return self._run(self._async_client.resolve_issue(issue_id, resolution))

    def list_issues(
        self,
        contract_id: str | None = None,
        run_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List issues with optional filtering."""
        return self._run(self._async_client.list_issues(
            contract_id=contract_id,
            run_id=run_id,
            status=status,
            severity=severity,
            limit=limit,
            offset=offset,
        ))

    # Comments
    def create_comment(
        self,
        contract_id: str,
        content: str,
        thread_id: str | None = None,
        section: str | None = None,
        field_path: str | None = None,
    ) -> dict[str, Any]:
        """Create a new comment on a contract."""
        return self._run(self._async_client.create_comment(
            contract_id=contract_id,
            content=content,
            thread_id=thread_id,
            section=section,
            field_path=field_path,
        ))

    def get_comment(self, comment_id: str) -> dict[str, Any]:
        """Get a comment by ID."""
        return self._run(self._async_client.get_comment(comment_id))

    def update_comment(
        self,
        comment_id: str,
        content: str,
    ) -> dict[str, Any]:
        """Update a comment."""
        return self._run(self._async_client.update_comment(comment_id, content))

    def delete_comment(self, comment_id: str) -> None:
        """Delete a comment."""
        return self._run(self._async_client.delete_comment(comment_id))

    def add_reaction(
        self,
        comment_id: str,
        reaction: str,
    ) -> dict[str, Any]:
        """Add a reaction to a comment."""
        return self._run(self._async_client.add_reaction(comment_id, reaction))

    def list_contract_comments(
        self,
        contract_id: str,
        thread_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List comments for a contract."""
        return self._run(self._async_client.list_contract_comments(
            contract_id=contract_id,
            thread_id=thread_id,
            limit=limit,
            offset=offset,
        ))

    # Approvals
    def create_approval_request(
        self,
        contract_id: str,
        request_type: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an approval request."""
        return self._run(self._async_client.create_approval_request(
            contract_id=contract_id,
            request_type=request_type,
            title=title,
            description=description,
        ))

    def list_pending_approvals(
        self,
        my_approvals: bool = False,
    ) -> list[dict[str, Any]]:
        """List pending approval requests."""
        return self._run(self._async_client.list_pending_approvals(my_approvals))

    def get_approval_request(
        self,
        request_id: str,
    ) -> dict[str, Any]:
        """Get an approval request by ID."""
        return self._run(self._async_client.get_approval_request(request_id))

    def approve_request(
        self,
        request_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Approve an approval request."""
        return self._run(self._async_client.approve_request(request_id, comment))

    def reject_request(
        self,
        request_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Reject an approval request."""
        return self._run(self._async_client.reject_request(request_id, comment))
