"""
Contract schema migration support (T-330).

Provides utilities to migrate contracts from older schema versions
to the current ODCS v1.0.0 format.

Example:
    from griot_core.migration import migrate_contract, detect_schema_version

    # Check version
    version = detect_schema_version(old_contract_dict)

    # Migrate to v1
    if version == "v0":
        new_contract = migrate_contract(old_contract_dict)
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

__all__ = [
    "detect_schema_version",
    "migrate_contract",
    "migrate_v0_to_v1",
    "MigrationResult",
]


class MigrationResult:
    """
    Result of a contract migration.

    Attributes:
        success: Whether migration completed successfully.
        contract: The migrated contract dictionary.
        source_version: The original schema version.
        target_version: The target schema version.
        warnings: List of migration warnings.
        changes: List of changes made during migration.
    """

    def __init__(
        self,
        success: bool,
        contract: dict[str, Any],
        source_version: str,
        target_version: str,
        warnings: list[str] | None = None,
        changes: list[str] | None = None,
    ):
        self.success = success
        self.contract = contract
        self.source_version = source_version
        self.target_version = target_version
        self.warnings = warnings or []
        self.changes = changes or []

    def __repr__(self) -> str:
        return (
            f"MigrationResult(success={self.success}, "
            f"{self.source_version} → {self.target_version}, "
            f"changes={len(self.changes)}, warnings={len(self.warnings)})"
        )


def detect_schema_version(contract: dict[str, Any]) -> str:
    """
    Detect the schema version of a contract.

    Version detection rules:
    - v1.0.0: Has api_version field with "v1.0.0"
    - v0: No api_version field (legacy format)

    Args:
        contract: Contract dictionary to analyze.

    Returns:
        Schema version string ("v0", "v1.0.0", etc.)
    """
    if "api_version" in contract:
        return contract["api_version"]

    # Check for ODCS indicators
    if "kind" in contract and contract.get("kind") == "DataContract":
        return "v1.0.0"

    # Legacy format indicators
    if "fields" in contract and "name" in contract:
        # Check if fields use old format
        fields = contract.get("fields", [])
        if isinstance(fields, dict):
            # Old dict-based field format
            return "v0"
        if isinstance(fields, list) and fields:
            first_field = fields[0]
            if isinstance(first_field, dict):
                # Check for ODCS-specific nested structures
                if "semantic" in first_field or "privacy" in first_field:
                    return "v1.0.0"
                # Check for old flat structure
                if "type" in first_field and "name" in first_field:
                    return "v0"

    return "v0"  # Default to v0 for unknown formats


def migrate_contract(
    contract: dict[str, Any],
    target_version: str = "v1.0.0",
) -> MigrationResult:
    """
    Migrate a contract to a target schema version.

    Args:
        contract: Contract dictionary to migrate.
        target_version: Target schema version (default: "v1.0.0").

    Returns:
        MigrationResult with the migrated contract.

    Example:
        result = migrate_contract(old_contract)
        if result.success:
            new_contract = result.contract
            print(f"Migrated with {len(result.changes)} changes")
    """
    source_version = detect_schema_version(contract)

    if source_version == target_version:
        return MigrationResult(
            success=True,
            contract=contract.copy(),
            source_version=source_version,
            target_version=target_version,
            warnings=["Contract is already at target version"],
            changes=[],
        )

    if source_version == "v0" and target_version == "v1.0.0":
        return migrate_v0_to_v1(contract)

    # Unknown migration path
    return MigrationResult(
        success=False,
        contract=contract,
        source_version=source_version,
        target_version=target_version,
        warnings=[f"No migration path from {source_version} to {target_version}"],
        changes=[],
    )


def migrate_v0_to_v1(contract: dict[str, Any]) -> MigrationResult:
    """
    Migrate a v0 contract to v1.0.0 ODCS format.

    This migration:
    1. Adds api_version, kind, status metadata
    2. Converts flat field structure to nested ODCS format
    3. Maps PII/privacy fields to privacy section
    4. Maps constraints to constraints section
    5. Preserves lineage and residency configurations

    Args:
        contract: v0 contract dictionary.

    Returns:
        MigrationResult with v1 contract.
    """
    changes: list[str] = []
    warnings: list[str] = []

    # Create new v1 contract
    v1_contract: dict[str, Any] = {}

    # Add ODCS metadata
    v1_contract["api_version"] = "v1.0.0"
    v1_contract["kind"] = "DataContract"
    changes.append("Added api_version: v1.0.0")
    changes.append("Added kind: DataContract")

    # Preserve or set name
    if "name" in contract:
        v1_contract["name"] = contract["name"]
    else:
        v1_contract["name"] = "MigratedContract"
        warnings.append("No name found, using 'MigratedContract'")

    # Add version (default to 1.0.0 for migrated contracts)
    v1_contract["version"] = contract.get("version", "1.0.0")
    if "version" not in contract:
        changes.append("Added default version: 1.0.0")

    # Add status (default to active for existing contracts)
    v1_contract["status"] = contract.get("status", "active")
    if "status" not in contract:
        changes.append("Added default status: active")

    # Preserve ID if present
    if "id" in contract:
        v1_contract["id"] = contract["id"]

    # Handle description
    if "description" in contract:
        if isinstance(contract["description"], str):
            # Convert string description to structured format
            v1_contract["description"] = {
                "purpose": contract["description"],
            }
            changes.append("Converted string description to structured format")
        else:
            v1_contract["description"] = contract["description"]

    # Migrate fields
    if "fields" in contract:
        v1_fields = _migrate_fields_v0_to_v1(contract["fields"], changes, warnings)
        v1_contract["fields"] = v1_fields

    # Preserve lineage if present
    if "lineage" in contract:
        v1_contract["lineage"] = contract["lineage"]

    # Preserve residency if present
    if "residency" in contract:
        v1_contract["residency"] = contract["residency"]

    # Add timestamps
    now = datetime.utcnow().isoformat() + "Z"
    v1_contract["timestamps"] = {
        "created_at": contract.get("created_at", now),
        "updated_at": now,
    }
    changes.append("Added timestamps section")

    # Preserve any other top-level keys
    preserved_keys = {
        "name", "description", "fields", "version", "status", "id",
        "lineage", "residency", "created_at", "updated_at",
    }
    for key in contract:
        if key not in preserved_keys and key not in v1_contract:
            v1_contract[key] = contract[key]
            warnings.append(f"Preserved unknown key: {key}")

    return MigrationResult(
        success=True,
        contract=v1_contract,
        source_version="v0",
        target_version="v1.0.0",
        warnings=warnings,
        changes=changes,
    )


def _migrate_fields_v0_to_v1(
    fields: list[dict[str, Any]] | dict[str, Any],
    changes: list[str],
    warnings: list[str],
) -> list[dict[str, Any]]:
    """
    Migrate v0 fields to v1 ODCS format.

    Args:
        fields: v0 fields (list or dict format).
        changes: List to append change descriptions.
        warnings: List to append warning messages.

    Returns:
        List of v1 field dictionaries.
    """
    v1_fields: list[dict[str, Any]] = []

    # Handle dict format (legacy)
    if isinstance(fields, dict):
        for field_name, field_def in fields.items():
            v1_field = _migrate_single_field(field_name, field_def, changes, warnings)
            v1_fields.append(v1_field)
        changes.append(f"Converted {len(fields)} fields from dict to list format")
        return v1_fields

    # Handle list format
    for field_def in fields:
        if isinstance(field_def, dict) and "name" in field_def:
            field_name = field_def["name"]
            v1_field = _migrate_single_field(field_name, field_def, changes, warnings)
            v1_fields.append(v1_field)
        else:
            warnings.append(f"Skipped invalid field definition: {field_def}")

    return v1_fields


def _migrate_single_field(
    field_name: str,
    field_def: dict[str, Any],
    changes: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    """
    Migrate a single field from v0 to v1 format.

    Args:
        field_name: Name of the field.
        field_def: v0 field definition.
        changes: List to append change descriptions.
        warnings: List to append warning messages.

    Returns:
        v1 field dictionary.
    """
    v1_field: dict[str, Any] = {"name": field_name}

    # Preserve basic properties
    if "type" in field_def:
        v1_field["type"] = field_def["type"]
    if "description" in field_def:
        v1_field["description"] = field_def["description"]
    if "nullable" in field_def:
        v1_field["nullable"] = field_def["nullable"]
    if "primary_key" in field_def:
        v1_field["primary_key"] = field_def["primary_key"]
    if "unique" in field_def:
        v1_field["unique"] = field_def["unique"]
    if "default" in field_def:
        v1_field["default"] = field_def["default"]

    # Build constraints section from flat fields
    constraints: dict[str, Any] = {}
    constraint_keys = [
        "min_length", "max_length", "pattern", "ge", "le", "gt", "lt",
        "multiple_of", "format", "enum",
    ]

    # Check top-level constraints
    for key in constraint_keys:
        if key in field_def:
            constraints[key] = field_def[key]

    # Check nested constraints
    if "constraints" in field_def and isinstance(field_def["constraints"], dict):
        for key, value in field_def["constraints"].items():
            if value is not None:
                constraints[key] = value

    if constraints:
        v1_field["constraints"] = constraints

    # Build semantic section from metadata
    semantic: dict[str, Any] = {}
    semantic_keys = ["unit", "precision", "business_term", "glossary_uri"]

    # Check top-level semantic fields
    for key in semantic_keys:
        if key in field_def:
            semantic[key] = field_def[key]

    # Check metadata section
    if "metadata" in field_def and isinstance(field_def["metadata"], dict):
        metadata = field_def["metadata"]
        if "unit" in metadata:
            semantic["unit"] = metadata["unit"]
        if "glossary_term" in metadata:
            semantic["business_term"] = metadata["glossary_term"]
            changes.append(f"Migrated glossary_term to business_term for {field_name}")
        if "aggregation" in metadata:
            semantic["aggregation"] = metadata["aggregation"]

    if semantic:
        v1_field["semantic"] = semantic

    # Build privacy section from PII fields
    privacy: dict[str, Any] = {}

    # Check for PII-related fields
    if "pii_category" in field_def:
        privacy["contains_pii"] = True
        privacy["pii_category"] = field_def["pii_category"]
    if "sensitivity_level" in field_def:
        privacy["sensitivity_level"] = field_def["sensitivity_level"]
    if "masking" in field_def:
        privacy["masking"] = field_def["masking"]
    if "retention_days" in field_def:
        privacy["retention_days"] = field_def["retention_days"]
    if "legal_basis" in field_def:
        privacy["legal_basis"] = field_def["legal_basis"]

    # Check nested privacy section
    if "privacy" in field_def and isinstance(field_def["privacy"], dict):
        for key, value in field_def["privacy"].items():
            if value is not None:
                privacy[key] = value

    if privacy:
        if "contains_pii" not in privacy:
            # Infer PII status
            privacy["contains_pii"] = bool(
                privacy.get("pii_category")
                or privacy.get("sensitivity_level") in ("confidential", "restricted")
            )
        v1_field["privacy"] = privacy
        changes.append(f"Created privacy section for {field_name}")

    return v1_field
