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
    FieldDefinition,
    SearchHit,
    SearchResults,
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
        """Create a new contract with version 1.0.0."""
        contract_dir = self.contracts_dir / contract.id
        versions_dir = contract_dir / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        version = "1.0.0"

        # Create the full contract
        full_contract = Contract(
            id=contract.id,
            name=contract.name,
            description=contract.description,
            owner=contract.owner,
            version=version,
            status="draft",
            fields=contract.fields,
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
    ) -> Contract:
        """Update contract, creating new version."""
        contract_dir = self.contracts_dir / contract_id
        metadata = self._load_json(contract_dir / "metadata.json")
        current_version = metadata["latest_version"]

        # Calculate new version
        new_version = self._bump_version(current_version, update.change_type)

        # Load current contract and apply updates
        current = await self.get_contract(contract_id)
        if current is None:
            raise ValueError(f"Contract {contract_id} not found")

        now = datetime.now(timezone.utc)
        updated = Contract(
            id=current.id,
            name=update.name if update.name else current.name,
            description=update.description if update.description else current.description,
            owner=current.owner,
            version=new_version,
            status=current.status,
            fields=update.fields if update.fields else current.fields,
            created_at=current.created_at,
            updated_at=now,
        )

        # Save new version
        version_file = contract_dir / "versions" / f"{new_version}.yaml"
        self._save_contract_yaml(version_file, updated)

        # Update metadata
        metadata["latest_version"] = new_version
        metadata["versions"].append({
            "version": new_version,
            "created_at": now.isoformat(),
            "change_type": update.change_type,
            "change_notes": update.change_notes,
        })
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
        """List all versions of a contract."""
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
                is_breaking=v.get("change_type") == "major",
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
        """Compute diff between two contract versions."""
        from_fields = {f.name: f for f in from_contract.fields}
        to_fields = {f.name: f for f in to_contract.fields}

        added = [name for name in to_fields if name not in from_fields]
        removed = [name for name in from_fields if name not in to_fields]

        type_changes: list[TypeChange] = []
        constraint_changes: list[ConstraintChange] = []

        # Check for changes in existing fields
        for name in from_fields:
            if name not in to_fields:
                continue

            from_f = from_fields[name]
            to_f = to_fields[name]

            # Type change
            if from_f.type != to_f.type:
                type_changes.append(TypeChange(
                    field=name,
                    from_type=from_f.type,
                    to_type=to_f.type,
                    is_breaking=True,
                ))

            # Constraint changes
            self._compare_constraints(name, from_f, to_f, constraint_changes)

        has_breaking = (
            len(removed) > 0
            or any(tc.is_breaking for tc in type_changes)
            or any(cc.is_breaking for cc in constraint_changes)
        )

        return ContractDiff(
            from_version=from_contract.version,
            to_version=to_contract.version,
            has_breaking_changes=has_breaking,
            added_fields=added,
            removed_fields=removed,
            type_changes=type_changes,
            constraint_changes=constraint_changes,
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

            # Search fields
            for field in contract.fields:
                if field_filter and field.name != field_filter:
                    continue

                if query_lower in field.name.lower():
                    hits.append(SearchHit(
                        contract_id=contract.id,
                        contract_name=contract.name,
                        field_name=field.name,
                        match_type="field",
                        snippet=f"{field.name}: {field.description}",
                    ))
                elif query_lower in field.description.lower():
                    hits.append(SearchHit(
                        contract_id=contract.id,
                        contract_name=contract.name,
                        field_name=field.name,
                        match_type="field",
                        snippet=self._snippet(field.description, query),
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
        """Save contract as YAML."""
        data = {
            "id": contract.id,
            "name": contract.name,
            "description": contract.description,
            "version": contract.version,
            "status": contract.status,
            "owner": contract.owner,
            "fields": [f.model_dump(exclude_none=True) for f in contract.fields],
            "created_at": contract.created_at.isoformat(),
            "updated_at": contract.updated_at.isoformat(),
        }
        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def _load_contract_yaml(self, path: Path) -> Contract:
        """Load contract from YAML."""
        with open(path) as f:
            data = yaml.safe_load(f)

        fields = [FieldDefinition(**f) for f in data.get("fields", [])]

        return Contract(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            version=data["version"],
            status=data["status"],
            owner=data.get("owner"),
            fields=fields,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

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

    def _compare_constraints(
        self,
        field_name: str,
        from_f: FieldDefinition,
        to_f: FieldDefinition,
        changes: list[ConstraintChange],
    ) -> None:
        """Compare constraints between two field definitions."""
        from_c = from_f.constraints or FieldConstraints()
        to_c = to_f.constraints or FieldConstraints()

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
