"""Filesystem-based storage backend."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from griot_registry.schemas import (
    ConstraintChange,
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    FieldConstraints,
    SchemaProperty,
    SearchHit,
    SearchResults,
    SectionChange,
    TypeChange,
    ValidationList,
    ValidationRecord,
    ValidationReport,
    VersionList,
    VersionSummary,
)
from griot_registry.storage.base import StorageBackend


class FilesystemStorage(StorageBackend):
    """Filesystem-based storage backend.

    Stores contracts as YAML files organized by contract ID and version.
    Validation history is stored as JSON files.

    Directory structure:
        storage_path/
        ├── contracts/
        │   └── {contract_id}/
        │       ├── metadata.json      # Contract metadata
        │       ├── latest.yaml        # Symlink to latest version
        │       └── versions/
        │           ├── 1.0.0.yaml
        │           └── 1.1.0.yaml
        └── validations/
            └── {contract_id}/
                └── {timestamp}_{uuid}.json
    """

    def __init__(self, storage_path: str) -> None:
        """Initialize filesystem storage.

        Args:
            storage_path: Root directory for storage.
        """
        self.root = Path(storage_path)
        self.contracts_dir = self.root / "contracts"
        self.validations_dir = self.root / "validations"

    async def initialize(self) -> None:
        """Create storage directories if they don't exist."""
        self.contracts_dir.mkdir(parents=True, exist_ok=True)
        self.validations_dir.mkdir(parents=True, exist_ok=True)

    async def close(self) -> None:
        """No cleanup needed for filesystem storage."""
        pass

    async def health_check(self) -> bool:
        """Check if storage directories are accessible."""
        if not self.contracts_dir.exists():
            raise RuntimeError("Contracts directory does not exist")
        if not self.validations_dir.exists():
            raise RuntimeError("Validations directory does not exist")
        return True

    # =========================================================================
    # Contract CRUD
    # =========================================================================
    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract with version 1.0.0.

        Supports both legacy fields format and ODCS schema format.
        """
        contract_dir = self.contracts_dir / contract.id
        versions_dir = contract_dir / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        version = "1.0.0"

        # Create the full contract with all ODCS sections
        full_contract = Contract(
            # Core identifiers
            id=contract.id,
            name=contract.name,
            api_version=contract.api_version,
            kind=contract.kind,
            description=contract.description,
            owner=contract.owner,
            # Version info
            version=version,
            status="draft",
            # ODCS sections
            description_section=contract.description_section,
            schema=contract.schema,
            legal=contract.legal,
            compliance=contract.compliance,
            lineage=contract.lineage,
            sla=contract.sla,
            access=contract.access,
            distribution=contract.distribution,
            governance=contract.governance,
            team=contract.team,
            servers=contract.servers,
            roles=contract.roles,
            # Timestamps
            created_at=now,
            updated_at=now,
        )

        # Save version file
        version_file = versions_dir / f"{version}.yaml"
        self._save_contract_yaml(version_file, full_contract)

        # Save metadata
        metadata = {
            "id": contract.id,
            "latest_version": version,
            "status": "draft",
            "created_at": now.isoformat(),
            "versions": [
                {
                    "version": version,
                    "created_at": now.isoformat(),
                    "change_type": "major",
                    "change_notes": "Initial version",
                }
            ],
        }
        self._save_json(contract_dir / "metadata.json", metadata)

        return full_contract

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract, optionally at a specific version."""
        contract_dir = self.contracts_dir / contract_id
        if not contract_dir.exists():
            return None

        # Get version to load
        if version is None:
            metadata = self._load_json(contract_dir / "metadata.json")
            if metadata is None:
                return None
            version = metadata.get("latest_version", "1.0.0")

        version_file = contract_dir / "versions" / f"{version}.yaml"
        if not version_file.exists():
            return None

        return self._load_contract_yaml(version_file)

    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get contract as raw YAML string."""
        contract_dir = self.contracts_dir / contract_id

        if version is None:
            metadata = self._load_json(contract_dir / "metadata.json")
            if metadata is None:
                return ""
            version = metadata.get("latest_version", "1.0.0")

        version_file = contract_dir / "versions" / f"{version}.yaml"
        if not version_file.exists():
            return ""

        return version_file.read_text()

    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
        is_breaking: bool = False,
        breaking_changes: list[dict[str, Any]] | None = None,
    ) -> Contract:
        """Update contract, creating new version (T-373 enhanced).

        Tracks breaking changes in version history for audit purposes.
        """
        contract_dir = self.contracts_dir / contract_id
        metadata = self._load_json(contract_dir / "metadata.json")
        current_version = metadata["latest_version"]

        # Calculate new version
        # If breaking changes exist and change_type is not major, force major version
        change_type = update.change_type
        if is_breaking and change_type != "major":
            change_type = "major"  # Breaking changes require major version bump

        new_version = self._bump_version(current_version, change_type)

        # Load current contract and apply updates
        current = await self.get_contract(contract_id)
        if current is None:
            raise ValueError(f"Contract {contract_id} not found")

        now = datetime.now(timezone.utc)
        updated = Contract(
            # Core identifiers
            id=current.id,
            name=update.name if update.name else current.name,
            api_version=current.api_version,
            kind=current.kind,
            description=update.description if update.description else current.description,
            owner=current.owner,
            # Version info
            version=new_version,
            status=current.status,
            # ODCS sections - update if provided, otherwise keep current
            description_section=update.description_section if update.description_section else current.description_section,
            schema=update.schema if update.schema else current.schema,
            legal=update.legal if update.legal else current.legal,
            compliance=update.compliance if update.compliance else current.compliance,
            lineage=update.lineage if update.lineage else current.lineage,
            sla=update.sla if update.sla else current.sla,
            access=update.access if update.access else current.access,
            distribution=update.distribution if update.distribution else current.distribution,
            governance=update.governance if update.governance else current.governance,
            team=update.team if update.team else current.team,
            servers=update.servers if update.servers else current.servers,
            roles=update.roles if update.roles else current.roles,
            # Timestamps
            created_at=current.created_at,
            updated_at=now,
        )

        # Save new version
        version_file = contract_dir / "versions" / f"{new_version}.yaml"
        self._save_contract_yaml(version_file, updated)

        # T-373: Update metadata with breaking change tracking
        version_entry: dict[str, Any] = {
            "version": new_version,
            "created_at": now.isoformat(),
            "change_type": change_type,
            "change_notes": update.change_notes,
            "is_breaking": is_breaking,
        }

        # Store breaking change details if present
        if is_breaking and breaking_changes:
            version_entry["breaking_changes"] = breaking_changes

        metadata["latest_version"] = new_version
        metadata["versions"].append(version_entry)
        self._save_json(contract_dir / "metadata.json", metadata)

        return updated

    async def deprecate_contract(self, contract_id: str) -> None:
        """Mark contract as deprecated."""
        contract_dir = self.contracts_dir / contract_id
        metadata = self._load_json(contract_dir / "metadata.json")
        metadata["status"] = "deprecated"
        self._save_json(contract_dir / "metadata.json", metadata)

        # Update latest version file
        contract = await self.get_contract(contract_id)
        if contract:
            contract.status = "deprecated"
            version_file = contract_dir / "versions" / f"{contract.version}.yaml"
            self._save_contract_yaml(version_file, contract)

    async def update_contract_status(
        self,
        contract_id: str,
        new_status: str,
    ) -> Contract:
        """Update contract status.

        Used by the approval workflow to transition contract status.
        """
        contract_dir = self.contracts_dir / contract_id
        metadata = self._load_json(contract_dir / "metadata.json")
        if metadata is None:
            raise ValueError(f"Contract {contract_id} not found")

        # Update metadata status
        old_status = metadata.get("status", "draft")
        metadata["status"] = new_status
        metadata["status_changed_at"] = datetime.now(timezone.utc).isoformat()
        metadata["status_changed_from"] = old_status
        self._save_json(contract_dir / "metadata.json", metadata)

        # Update the latest version file
        contract = await self.get_contract(contract_id)
        if contract is None:
            raise ValueError(f"Contract {contract_id} not found")

        contract.status = new_status
        contract.updated_at = datetime.now(timezone.utc)
        version_file = contract_dir / "versions" / f"{contract.version}.yaml"
        self._save_contract_yaml(version_file, contract)

        return contract

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List all contracts with optional filtering."""
        contracts: list[Contract] = []

        for contract_dir in sorted(self.contracts_dir.iterdir()):
            if not contract_dir.is_dir():
                continue

            contract = await self.get_contract(contract_dir.name)
            if contract is None:
                continue

            # Apply filters
            if status and contract.status != status:
                continue
            if owner and contract.owner != owner:
                continue

            contracts.append(contract)

        total = len(contracts)
        items = contracts[offset : offset + limit]

        return ContractList(items=items, total=total, limit=limit, offset=offset)

    # =========================================================================
    # Versions
    # =========================================================================
    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> VersionList:
        """List all versions of a contract (T-373 enhanced).

        Now includes accurate is_breaking flag from version metadata.
        """
        contract_dir = self.contracts_dir / contract_id
        metadata = self._load_json(contract_dir / "metadata.json")

        if metadata is None:
            return VersionList(items=[], total=0)

        versions_data = metadata.get("versions", [])
        versions = [
            VersionSummary(
                version=v["version"],
                created_at=datetime.fromisoformat(v["created_at"]),
                change_type=v.get("change_type"),
                change_notes=v.get("change_notes"),
                # T-373: Use stored is_breaking flag, fall back to major check for old data
                is_breaking=v.get("is_breaking", v.get("change_type") == "major"),
            )
            for v in versions_data
        ]

        # Sort by version descending
        versions.sort(key=lambda v: self._version_tuple(v.version), reverse=True)

        total = len(versions)
        items = versions[offset : offset + limit]

        return VersionList(items=items, total=total)

    async def diff_contracts(
        self,
        from_contract: Contract,
        to_contract: Contract,
    ) -> ContractDiff:
        """Compute diff between two contract versions (T-374 enhanced for ODCS)."""
        # Extract properties from ODCS schema (schema_name.property_name format)
        from_props = self._extract_all_properties(from_contract.schema)
        to_props = self._extract_all_properties(to_contract.schema)

        added = [name for name in to_props if name not in from_props]
        removed = [name for name in from_props if name not in to_props]

        type_changes: list[TypeChange] = []
        constraint_changes: list[ConstraintChange] = []

        # Check for changes in existing properties
        for name in from_props:
            if name not in to_props:
                continue

            from_p = from_props[name]
            to_p = to_props[name]

            # Type change (using logical_type from SchemaProperty)
            from_type = from_p.logical_type if from_p.logical_type else "string"
            to_type = to_p.logical_type if to_p.logical_type else "string"
            if from_type != to_type:
                type_changes.append(TypeChange(
                    field=name,
                    from_type=from_type,
                    to_type=to_type,
                    is_breaking=True,
                ))

            # Constraint changes
            self._compare_property_constraints(name, from_p, to_p, constraint_changes)

        # T-374: Detect ODCS section changes
        section_changes: list[SectionChange] = []
        added_schemas: list[str] = []
        removed_schemas: list[str] = []
        modified_schemas: list[str] = []

        # Compare ODCS sections
        odcs_sections = [
            ("legal", "Legal requirements"),
            ("compliance", "Compliance settings"),
            ("sla", "Service level agreements"),
            ("access", "Access control"),
            ("distribution", "Distribution channels"),
            ("governance", "Governance settings"),
            ("lineage", "Data lineage"),
            ("team", "Team information"),
        ]

        for section_name, section_desc in odcs_sections:
            from_section = getattr(from_contract, section_name, None)
            to_section = getattr(to_contract, section_name, None)

            if from_section is None and to_section is not None:
                section_changes.append(SectionChange(
                    section=section_name,
                    change_type="added",
                    summary=f"{section_desc} section added",
                    is_breaking=False,
                ))
            elif from_section is not None and to_section is None:
                section_changes.append(SectionChange(
                    section=section_name,
                    change_type="removed",
                    summary=f"{section_desc} section removed",
                    is_breaking=True,  # Removing sections is breaking
                ))
            elif from_section is not None and to_section is not None:
                # Compare section contents (simplified - just check if different)
                from_dict = from_section.model_dump() if hasattr(from_section, 'model_dump') else {}
                to_dict = to_section.model_dump() if hasattr(to_section, 'model_dump') else {}
                if from_dict != to_dict:
                    section_changes.append(SectionChange(
                        section=section_name,
                        change_type="modified",
                        summary=f"{section_desc} section modified",
                        is_breaking=False,
                    ))

        # Compare schema definitions (ODCS schema section)
        from_schemas = {s.name: s for s in (from_contract.schema or [])}
        to_schemas = {s.name: s for s in (to_contract.schema or [])}

        added_schemas = [name for name in to_schemas if name not in from_schemas]
        removed_schemas = [name for name in from_schemas if name not in to_schemas]

        for name in from_schemas:
            if name in to_schemas:
                from_s = from_schemas[name]
                to_s = to_schemas[name]
                from_dict = from_s.model_dump() if hasattr(from_s, 'model_dump') else {}
                to_dict = to_s.model_dump() if hasattr(to_s, 'model_dump') else {}
                if from_dict != to_dict:
                    modified_schemas.append(name)

        # Calculate breaking changes
        has_breaking = (
            len(removed) > 0
            or len(removed_schemas) > 0
            or any(tc.is_breaking for tc in type_changes)
            or any(cc.is_breaking for cc in constraint_changes)
            or any(sc.is_breaking for sc in section_changes)
        )

        return ContractDiff(
            from_version=from_contract.version,
            to_version=to_contract.version,
            has_breaking_changes=has_breaking,
            added_fields=added,
            removed_fields=removed,
            type_changes=type_changes,
            constraint_changes=constraint_changes,
            section_changes=section_changes,
            added_schemas=added_schemas,
            removed_schemas=removed_schemas,
            modified_schemas=modified_schemas,
        )

    # =========================================================================
    # Validations
    # =========================================================================
    async def record_validation(
        self,
        report: ValidationReport,
    ) -> ValidationRecord:
        """Store a validation result."""
        validation_dir = self.validations_dir / report.contract_id
        validation_dir.mkdir(parents=True, exist_ok=True)

        record_id = uuid4()
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        record = ValidationRecord(
            id=record_id,
            contract_id=report.contract_id,
            contract_version=report.contract_version,
            passed=report.passed,
            row_count=report.row_count,
            error_count=report.error_count,
            recorded_at=now,
        )

        # Save full report with extra details
        report_data = {
            "id": str(record_id),
            "contract_id": report.contract_id,
            "contract_version": report.contract_version,
            "passed": report.passed,
            "row_count": report.row_count,
            "error_count": report.error_count,
            "error_rate": report.error_rate,
            "duration_ms": report.duration_ms,
            "environment": report.environment,
            "pipeline_id": report.pipeline_id,
            "run_id": report.run_id,
            "recorded_at": now.isoformat(),
            "sample_errors": [e.model_dump() for e in report.sample_errors],
        }

        filename = f"{timestamp}_{record_id}.json"
        self._save_json(validation_dir / filename, report_data)

        return record

    async def list_validations(
        self,
        contract_id: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ValidationList:
        """List validation history with filtering."""
        records: list[ValidationRecord] = []

        # Determine which directories to scan
        if contract_id:
            dirs = [self.validations_dir / contract_id]
        else:
            dirs = [d for d in self.validations_dir.iterdir() if d.is_dir()]

        for validation_dir in dirs:
            if not validation_dir.exists():
                continue

            for file in validation_dir.glob("*.json"):
                data = self._load_json(file)
                if data is None:
                    continue

                recorded_at = datetime.fromisoformat(data["recorded_at"])

                # Apply filters
                if passed is not None and data["passed"] != passed:
                    continue
                if from_date and recorded_at < from_date:
                    continue
                if to_date and recorded_at > to_date:
                    continue

                records.append(ValidationRecord(
                    id=data["id"],
                    contract_id=data["contract_id"],
                    contract_version=data.get("contract_version"),
                    passed=data["passed"],
                    row_count=data["row_count"],
                    error_count=data["error_count"],
                    recorded_at=recorded_at,
                ))

        # Sort by recorded_at descending
        records.sort(key=lambda r: r.recorded_at, reverse=True)

        total = len(records)
        items = records[offset : offset + limit]

        return ValidationList(items=items, total=total, limit=limit, offset=offset)

    # =========================================================================
    # Search
    # =========================================================================
    async def search(
        self,
        query: str,
        field_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResults:
        """Search contracts for matching terms."""
        query_lower = query.lower()
        hits: list[SearchHit] = []

        for contract_dir in self.contracts_dir.iterdir():
            if not contract_dir.is_dir():
                continue

            contract = await self.get_contract(contract_dir.name)
            if contract is None:
                continue

            # Search contract name
            if not field_filter and query_lower in contract.name.lower():
                hits.append(SearchHit(
                    contract_id=contract.id,
                    contract_name=contract.name,
                    match_type="name",
                    snippet=contract.name,
                ))

            # Search contract description
            if not field_filter and contract.description and query_lower in contract.description.lower():
                hits.append(SearchHit(
                    contract_id=contract.id,
                    contract_name=contract.name,
                    match_type="description",
                    snippet=self._snippet(contract.description, query),
                ))

            # Search schema properties (ODCS format)
            for schema_def in contract.schema or []:
                for prop in schema_def.properties or []:
                    full_name = f"{schema_def.name}.{prop.name}"
                    if field_filter and prop.name != field_filter:
                        continue

                    prop_desc = prop.description or ""
                    if query_lower in prop.name.lower():
                        hits.append(SearchHit(
                            contract_id=contract.id,
                            contract_name=contract.name,
                            field_name=full_name,
                            match_type="field",
                            snippet=f"{full_name}: {prop_desc}",
                        ))
                    elif prop_desc and query_lower in prop_desc.lower():
                        hits.append(SearchHit(
                            contract_id=contract.id,
                            contract_name=contract.name,
                            field_name=full_name,
                            match_type="field",
                            snippet=self._snippet(prop_desc, query),
                        ))

        total = len(hits)
        items = hits[offset : offset + limit]

        return SearchResults(query=query, items=items, total=total)

    # =========================================================================
    # Helpers
    # =========================================================================
    def _save_json(self, path: Path, data: dict[str, Any]) -> None:
        """Save data as JSON."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        """Load JSON data."""
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def _save_contract_yaml(self, path: Path, contract: Contract) -> None:
        """Save contract as YAML with full ODCS support."""
        # Use Pydantic's model_dump to serialize all fields properly
        data = contract.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,  # Use aliases like description_odcs
        )

        # Convert datetime strings if needed (model_dump in json mode handles this)
        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def _load_contract_yaml(self, path: Path) -> Contract:
        """Load contract from YAML with full ODCS support."""
        with open(path) as f:
            data = yaml.safe_load(f)

        # Convert string timestamps to datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        # Remove legacy fields if present (migrating old contracts)
        data.pop("fields", None)

        return Contract(**data)

    def _bump_version(self, version: str, change_type: str) -> str:
        """Increment version based on change type."""
        parts = [int(p) for p in version.split(".")]
        if len(parts) != 3:
            parts = [1, 0, 0]

        if change_type == "major":
            return f"{parts[0] + 1}.0.0"
        elif change_type == "minor":
            return f"{parts[0]}.{parts[1] + 1}.0"
        else:  # patch
            return f"{parts[0]}.{parts[1]}.{parts[2] + 1}"

    def _version_tuple(self, version: str) -> tuple[int, int, int]:
        """Convert version string to tuple for sorting."""
        parts = version.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def _extract_all_properties(
        self,
        schema_list: list | None,
    ) -> dict[str, SchemaProperty]:
        """Extract all properties from ODCS schema into a flat dictionary.

        Keys are in format 'schema_name.property_name' for uniqueness.
        """
        properties: dict[str, SchemaProperty] = {}
        if not schema_list:
            return properties

        for schema_def in schema_list:
            schema_name = schema_def.name
            for prop in schema_def.properties or []:
                key = f"{schema_name}.{prop.name}"
                properties[key] = prop

        return properties

    def _compare_property_constraints(
        self,
        field_name: str,
        from_p: SchemaProperty,
        to_p: SchemaProperty,
        changes: list[ConstraintChange],
    ) -> None:
        """Compare constraints between two schema properties."""
        from_c = from_p.constraints or FieldConstraints()
        to_c = to_p.constraints or FieldConstraints()

        constraint_fields = [
            "min_length", "max_length", "pattern", "format",
            "ge", "le", "gt", "lt", "multiple_of", "enum"
        ]

        for c in constraint_fields:
            from_val = getattr(from_c, c, None)
            to_val = getattr(to_c, c, None)

            if from_val != to_val:
                # Determine if breaking (more restrictive)
                is_breaking = self._is_breaking_constraint_change(c, from_val, to_val)
                changes.append(ConstraintChange(
                    field=field_name,
                    constraint=c,
                    from_value=from_val,
                    to_value=to_val,
                    is_breaking=is_breaking,
                ))

    def _is_breaking_constraint_change(
        self,
        constraint: str,
        from_val: Any,
        to_val: Any,
    ) -> bool:
        """Determine if a constraint change is breaking."""
        # Adding a new constraint where there was none is breaking
        if from_val is None and to_val is not None:
            return True

        # Removing a constraint is not breaking
        if from_val is not None and to_val is None:
            return False

        # For min constraints, increasing is breaking
        if constraint in ("min_length", "ge", "gt"):
            return to_val > from_val

        # For max constraints, decreasing is breaking
        if constraint in ("max_length", "le", "lt"):
            return to_val < from_val

        # Pattern changes are always breaking
        if constraint == "pattern":
            return True

        # Enum changes: reducing options is breaking
        if constraint == "enum":
            return not set(to_val).issuperset(set(from_val))

        return True

    def _snippet(self, text: str, query: str, context: int = 50) -> str:
        """Extract a snippet around the query match."""
        lower_text = text.lower()
        lower_query = query.lower()
        pos = lower_text.find(lower_query)

        if pos == -1:
            return text[:100] + "..." if len(text) > 100 else text

        start = max(0, pos - context)
        end = min(len(text), pos + len(query) + context)

        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet
