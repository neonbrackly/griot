"""Contract service for business logic operations.

This service coordinates contract operations between the API layer
and the storage layer, handling:
- Validation before storage
- Version number management
- Breaking change detection
- Schema catalog updates
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from griot_core import Contract, ContractStatus

from griot_registry.auth.models import User
from griot_registry.config import Settings
from griot_registry.services.validation import ValidationResult, ValidationService
from griot_registry.storage.base import StorageBackend


@dataclass
class BreakingChange:
    """Information about a breaking change."""

    change_type: str
    field: str | None
    description: str
    from_value: Any
    to_value: Any
    migration_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_type": self.change_type,
            "field": self.field,
            "description": self.description,
            "from_value": self.from_value,
            "to_value": self.to_value,
            "migration_hint": self.migration_hint,
        }


@dataclass
class ContractCreateResult:
    """Result of contract creation."""

    success: bool
    contract: Contract | None
    validation: ValidationResult | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        result: dict[str, Any] = {"success": self.success}
        if self.contract:
            result["contract"] = self.contract.to_dict()
        if self.validation:
            result["validation"] = self.validation.to_dict()
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class ContractUpdateResult:
    """Result of contract update."""

    success: bool
    contract: Contract | None
    validation: ValidationResult | None
    breaking_changes: list[BreakingChange]
    blocked_by_breaking: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        result: dict[str, Any] = {
            "success": self.success,
            "blocked_by_breaking": self.blocked_by_breaking,
        }
        if self.contract:
            result["contract"] = self.contract.to_dict()
        if self.validation:
            result["validation"] = self.validation.to_dict()
        if self.breaking_changes:
            result["breaking_changes"] = [bc.to_dict() for bc in self.breaking_changes]
        if self.error:
            result["error"] = self.error
        return result


class ContractService:
    """Service for contract business logic.

    Coordinates between API endpoints and storage, handling:
    - Contract validation via griot-core
    - Version number management
    - Breaking change detection
    - Schema catalog updates
    """

    def __init__(
        self,
        storage: StorageBackend,
        settings: Settings,
    ):
        self.storage = storage
        self.settings = settings
        self.validation_service = ValidationService(settings)

    async def create_contract(
        self,
        contract: Contract,
        user: User | None = None,
        schema_refs: list[dict[str, Any]] | None = None,
    ) -> ContractCreateResult:
        """Create a new contract.

        Steps:
        1. Check if contract ID already exists
        2. Validate contract (if enabled)
        3. Store contract
        4. Update schema catalog

        Args:
            contract: The contract to create
            user: The user creating the contract

        Returns:
            ContractCreateResult with success status and any issues
        """
        # Check if contract already exists
        if await self.storage.contracts.exists(contract.id):
            return ContractCreateResult(
                success=False,
                contract=None,
                validation=None,
                error=f"Contract '{contract.id}' already exists",
            )

        # Validate if enabled
        validation_result = None
        if self.validation_service.should_validate_on_create():
            validation_result = self.validation_service.validate(contract)

            if not validation_result.is_valid:
                return ContractCreateResult(
                    success=False,
                    contract=None,
                    validation=validation_result,
                    error="Contract validation failed",
                )

        # Store contract
        created_by = user.id if user else None
        created = await self.storage.contracts.create(
            contract,
            created_by=created_by,
            schema_refs=schema_refs,
        )

        # Update schema catalog
        await self.storage.schema_catalog.update_for_contract(created)

        return ContractCreateResult(
            success=True,
            contract=created,
            validation=validation_result,
        )

    async def update_contract(
        self,
        contract_id: str,
        updated_contract: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        allow_breaking: bool = False,
        user: User | None = None,
    ) -> ContractUpdateResult:
        """Update an existing contract.

        Steps:
        1. Get current contract
        2. Validate updated contract (if enabled)
        3. Detect breaking changes
        4. Block if breaking changes and not allowed
        5. Increment version number
        6. Store updated contract
        7. Update schema catalog

        Args:
            contract_id: ID of the contract to update
            updated_contract: The updated contract data
            change_type: Type of change (patch, minor, major)
            change_notes: Notes about the change
            allow_breaking: Whether to allow breaking changes
            user: The user making the update

        Returns:
            ContractUpdateResult with success status and any issues
        """
        # Get current contract
        current = await self.storage.contracts.get(contract_id)
        if current is None:
            return ContractUpdateResult(
                success=False,
                contract=None,
                validation=None,
                breaking_changes=[],
                error=f"Contract '{contract_id}' not found",
            )

        # Validate if enabled
        validation_result = None
        if self.validation_service.should_validate_on_update():
            validation_result = self.validation_service.validate(updated_contract)

            if not validation_result.is_valid:
                return ContractUpdateResult(
                    success=False,
                    contract=None,
                    validation=validation_result,
                    breaking_changes=[],
                    error="Contract validation failed",
                )

        # Detect breaking changes
        breaking_changes = self._detect_breaking_changes(current, updated_contract)

        # Block if breaking changes and not allowed
        if breaking_changes and not allow_breaking:
            return ContractUpdateResult(
                success=False,
                contract=None,
                validation=validation_result,
                breaking_changes=breaking_changes,
                blocked_by_breaking=True,
                error=f"Update contains {len(breaking_changes)} breaking change(s). Use allow_breaking=true to force.",
            )

        # Calculate new version
        new_version = self._increment_version(current.version, change_type)

        # Create new contract with updated version
        # Note: We need to create a new Contract object with the new version
        updated_dict = updated_contract.to_dict()
        updated_dict["version"] = new_version
        from griot_core import load_contract_from_dict
        final_contract = load_contract_from_dict(updated_dict)

        # Store updated contract
        updated_by = user.id if user else None
        is_breaking = len(breaking_changes) > 0

        stored = await self.storage.contracts.update(
            contract_id,
            final_contract,
            change_type=change_type,
            change_notes=change_notes,
            is_breaking=is_breaking,
            breaking_changes=[bc.to_dict() for bc in breaking_changes] if is_breaking else None,
            updated_by=updated_by,
        )

        # Update schema catalog
        await self.storage.schema_catalog.update_for_contract(stored)

        return ContractUpdateResult(
            success=True,
            contract=stored,
            validation=validation_result,
            breaking_changes=breaking_changes,
        )

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract by ID and optionally version."""
        if version:
            return await self.storage.contracts.get_version(contract_id, version)
        return await self.storage.contracts.get(contract_id)

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
    ) -> tuple[list[Contract], int]:
        """List contracts with filtering."""
        return await self.storage.contracts.list(
            limit=limit,
            offset=offset,
            status=status,
            schema_name=schema_name,
            owner=owner,
        )

    async def update_status(
        self,
        contract_id: str,
        new_status: str,
        user: User | None = None,
    ) -> Contract:
        """Update contract status."""
        # Validate status transition
        current = await self.storage.contracts.get(contract_id)
        if current is None:
            raise ValueError(f"Contract '{contract_id}' not found")

        valid_transitions = {
            ContractStatus.DRAFT: [ContractStatus.ACTIVE, ContractStatus.DEPRECATED],
            ContractStatus.ACTIVE: [ContractStatus.DEPRECATED],
            ContractStatus.DEPRECATED: [ContractStatus.RETIRED],
            ContractStatus.RETIRED: [],
        }

        try:
            new_status_enum = ContractStatus(new_status)
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")

        allowed = valid_transitions.get(current.status, [])
        if new_status_enum not in allowed:
            raise ValueError(
                f"Cannot transition from '{current.status.value}' to '{new_status}'. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        updated_by = user.id if user else None
        return await self.storage.contracts.update_status(
            contract_id,
            new_status,
            updated_by=updated_by,
        )

    async def deprecate_contract(
        self,
        contract_id: str,
        user: User | None = None,
    ) -> bool:
        """Deprecate a contract."""
        try:
            await self.update_status(contract_id, "deprecated", user)
            return True
        except ValueError:
            return False

    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search contracts."""
        return await self.storage.contracts.search(query, limit)

    def _detect_breaking_changes(
        self,
        current: Contract,
        updated: Contract,
    ) -> list[BreakingChange]:
        """Detect breaking changes between two contract versions.

        Breaking changes include:
        - Removed schemas
        - Removed fields
        - Type changes (narrowing)
        - Nullable to required changes
        """
        breaking_changes: list[BreakingChange] = []

        # Extract schemas by name
        current_schemas = {s.name: s for s in current.schemas}
        updated_schemas = {s.name: s for s in updated.schemas}

        # Check for removed schemas
        for schema_name in current_schemas:
            if schema_name not in updated_schemas:
                breaking_changes.append(BreakingChange(
                    change_type="schema_removed",
                    field=schema_name,
                    description=f"Schema '{schema_name}' was removed",
                    from_value=schema_name,
                    to_value=None,
                    migration_hint="Add the schema back or migrate consumers",
                ))
                continue

            # Check for field changes within schema
            current_schema = current_schemas[schema_name]
            updated_schema = updated_schemas[schema_name]

            current_fields = current_schema.fields
            updated_fields = updated_schema.fields

            # Check for removed fields
            for field_name in current_fields:
                if field_name not in updated_fields:
                    breaking_changes.append(BreakingChange(
                        change_type="field_removed",
                        field=f"{schema_name}.{field_name}",
                        description=f"Field '{field_name}' was removed from schema '{schema_name}'",
                        from_value=current_fields[field_name].logical_type,
                        to_value=None,
                        migration_hint="Add the field back or migrate consumers",
                    ))
                    continue

                # Check for type changes
                old_field = current_fields[field_name]
                new_field = updated_fields[field_name]

                if old_field.logical_type != new_field.logical_type:
                    breaking_changes.append(BreakingChange(
                        change_type="type_changed",
                        field=f"{schema_name}.{field_name}",
                        description=f"Field type changed from '{old_field.logical_type}' to '{new_field.logical_type}'",
                        from_value=old_field.logical_type,
                        to_value=new_field.logical_type,
                        migration_hint="Use a compatible type or create a new field",
                    ))

                # Check for nullable to required change
                if old_field.nullable and not new_field.nullable:
                    breaking_changes.append(BreakingChange(
                        change_type="nullable_to_required",
                        field=f"{schema_name}.{field_name}",
                        description=f"Field '{field_name}' changed from nullable to required",
                        from_value=True,
                        to_value=False,
                        migration_hint="Keep nullable or ensure all data has values",
                    ))

        return breaking_changes

    def _increment_version(self, current_version: str, change_type: str) -> str:
        """Increment version number based on change type.

        Args:
            current_version: Current semantic version (e.g., "1.2.3")
            change_type: Type of change (patch, minor, major)

        Returns:
            New version string
        """
        try:
            parts = current_version.split(".")
            if len(parts) != 3:
                parts = ["1", "0", "0"]

            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

            if change_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif change_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1

            return f"{major}.{minor}.{patch}"
        except (ValueError, IndexError):
            return "1.0.1"
