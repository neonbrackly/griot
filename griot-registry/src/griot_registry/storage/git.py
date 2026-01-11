"""Git-backed storage backend for griot-registry."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import yaml

from griot_registry.schemas import (
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    FieldChange,
    SearchResult,
    SearchResults,
    ValidationList,
    ValidationRecord,
    ValidationReport,
    VersionInfo,
    VersionList,
)
from griot_registry.storage.base import StorageBackend

if TYPE_CHECKING:
    from git import Repo


class GitStorage(StorageBackend):
    """Git-backed storage backend.

    Stores contracts in a Git repository, using commits for versioning
    and tags for version tracking. Each contract is stored as a YAML file
    with metadata in a JSON sidecar file.
    """

    def __init__(self, repo_path: str, branch: str = "main") -> None:
        """Initialize Git storage.

        Args:
            repo_path: Path to Git repository.
            branch: Branch to use for contract storage.
        """
        self.repo_path = Path(repo_path)
        self.branch = branch
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        """Get the Git repository instance."""
        if self._repo is None:
            raise RuntimeError("Git storage not initialized. Call initialize() first.")
        return self._repo

    async def initialize(self) -> None:
        """Initialize or open Git repository."""
        try:
            from git import Repo
        except ImportError as e:
            raise ImportError(
                "GitPython is required for Git storage. "
                "Install with: pip install griot-registry[git]"
            ) from e

        self.repo_path.mkdir(parents=True, exist_ok=True)
        contracts_dir = self.repo_path / "contracts"
        contracts_dir.mkdir(exist_ok=True)

        if (self.repo_path / ".git").exists():
            self._repo = Repo(self.repo_path)
        else:
            self._repo = Repo.init(self.repo_path)
            # Create initial commit
            readme = self.repo_path / "README.md"
            readme.write_text("# Griot Contract Registry\n\nGit-backed contract storage.\n")
            self._repo.index.add(["README.md"])
            self._repo.index.commit("Initial commit")

        # Ensure we're on the right branch
        if self._repo.active_branch.name != self.branch:
            if self.branch in [b.name for b in self._repo.branches]:
                self._repo.heads[self.branch].checkout()
            else:
                self._repo.create_head(self.branch).checkout()

    async def close(self) -> None:
        """Close Git storage."""
        self._repo = None

    async def health_check(self) -> bool:
        """Check Git repository health."""
        try:
            return self._repo is not None and self.repo_path.exists()
        except Exception:
            return False

    def _contract_path(self, contract_id: str) -> Path:
        """Get path to contract YAML file."""
        return self.repo_path / "contracts" / f"{contract_id}.yaml"

    def _metadata_path(self, contract_id: str) -> Path:
        """Get path to contract metadata JSON file."""
        return self.repo_path / "contracts" / f"{contract_id}.meta.json"

    def _save_contract(self, contract: Contract) -> None:
        """Save contract to filesystem."""
        contract_path = self._contract_path(contract.id)
        metadata_path = self._metadata_path(contract.id)

        # Save contract YAML
        contract_data = {
            "id": contract.id,
            "name": contract.name,
            "description": contract.description,
            "version": contract.version,
            "owner": contract.owner,
            "status": contract.status,
            "fields": [f.model_dump() for f in contract.fields],
        }
        contract_path.write_text(yaml.dump(contract_data, default_flow_style=False))

        # Save metadata
        metadata = {
            "created_at": contract.created_at.isoformat(),
            "updated_at": contract.updated_at.isoformat(),
            "tags": contract.tags,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def _load_contract(self, contract_id: str) -> Contract | None:
        """Load contract from filesystem."""
        contract_path = self._contract_path(contract_id)
        metadata_path = self._metadata_path(contract_id)

        if not contract_path.exists():
            return None

        contract_data = yaml.safe_load(contract_path.read_text())
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}

        return Contract(
            id=contract_data["id"],
            name=contract_data["name"],
            description=contract_data.get("description"),
            version=contract_data["version"],
            owner=contract_data["owner"],
            status=contract_data.get("status", "active"),
            fields=contract_data["fields"],
            tags=metadata.get("tags", []),
            created_at=datetime.fromisoformat(metadata["created_at"]) if "created_at" in metadata else datetime.now(timezone.utc),
            updated_at=datetime.fromisoformat(metadata["updated_at"]) if "updated_at" in metadata else datetime.now(timezone.utc),
        )

    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create contract with initial commit."""
        now = datetime.now(timezone.utc)
        new_contract = Contract(
            id=contract.id,
            name=contract.name,
            description=contract.description,
            version="1.0.0",
            owner=contract.owner,
            status="active",
            fields=contract.fields,
            tags=contract.tags or [],
            created_at=now,
            updated_at=now,
        )

        self._save_contract(new_contract)

        # Git add and commit
        rel_contract = f"contracts/{contract.id}.yaml"
        rel_metadata = f"contracts/{contract.id}.meta.json"
        self.repo.index.add([rel_contract, rel_metadata])
        commit = self.repo.index.commit(f"Create contract: {contract.id}")

        # Tag this version
        self.repo.create_tag(
            f"{contract.id}/v1.0.0",
            commit,
            message=f"Version 1.0.0 of {contract.id}",
        )

        return new_contract

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get contract from Git."""
        if version:
            # Checkout specific version from tag
            tag_name = f"{contract_id}/v{version}"
            if tag_name in [t.name for t in self.repo.tags]:
                # Read from specific tag
                tag = self.repo.tags[tag_name]
                blob = tag.commit.tree / "contracts" / f"{contract_id}.yaml"
                contract_data = yaml.safe_load(blob.data_stream.read().decode())

                meta_blob = tag.commit.tree / "contracts" / f"{contract_id}.meta.json"
                metadata = json.loads(meta_blob.data_stream.read().decode()) if meta_blob else {}

                return Contract(
                    id=contract_data["id"],
                    name=contract_data["name"],
                    description=contract_data.get("description"),
                    version=contract_data["version"],
                    owner=contract_data["owner"],
                    status=contract_data.get("status", "active"),
                    fields=contract_data["fields"],
                    tags=metadata.get("tags", []),
                    created_at=datetime.fromisoformat(metadata["created_at"]) if "created_at" in metadata else datetime.now(timezone.utc),
                    updated_at=datetime.fromisoformat(metadata["updated_at"]) if "updated_at" in metadata else datetime.now(timezone.utc),
                )
            return None

        return self._load_contract(contract_id)

    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get contract YAML from Git."""
        contract = await self.get_contract(contract_id, version)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")
        return self._contract_path(contract_id).read_text()

    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
        is_breaking: bool = False,
        breaking_changes: list[dict[str, Any]] | None = None,
    ) -> Contract:
        """Update contract with new commit (T-373 enhanced).

        Includes breaking change information in commit message.
        """
        contract = self._load_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")

        # Bump version - force major for breaking changes
        parts = contract.version.split(".")
        if is_breaking:
            new_version = f"{int(parts[0]) + 1}.0.0"
        else:
            new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"

        updated = Contract(
            id=contract.id,
            name=update.name if update.name else contract.name,
            description=update.description if update.description is not None else contract.description,
            version=new_version,
            owner=update.owner if update.owner else contract.owner,
            status=contract.status,
            fields=update.fields if update.fields else contract.fields,
            tags=update.tags if update.tags is not None else contract.tags,
            created_at=contract.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        self._save_contract(updated)

        # Git add and commit
        rel_contract = f"contracts/{contract_id}.yaml"
        rel_metadata = f"contracts/{contract_id}.meta.json"
        self.repo.index.add([rel_contract, rel_metadata])

        # T-373: Include breaking change info in commit message
        commit_msg = f"Update contract: {contract_id} to v{new_version}"
        if is_breaking:
            commit_msg = f"BREAKING: {commit_msg}"
            if breaking_changes:
                commit_msg += f"\n\nBreaking changes:\n"
                for bc in breaking_changes:
                    commit_msg += f"- {bc.get('description', 'Unknown change')}\n"

        commit = self.repo.index.commit(commit_msg)

        # Tag new version with breaking change annotation
        tag_message = f"Version {new_version} of {contract_id}"
        if is_breaking:
            tag_message = f"BREAKING: {tag_message}"

        self.repo.create_tag(
            f"{contract_id}/v{new_version}",
            commit,
            message=tag_message,
        )

        return updated

    async def deprecate_contract(self, contract_id: str) -> None:
        """Deprecate contract."""
        contract = self._load_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")

        contract.status = "deprecated"
        contract.updated_at = datetime.now(timezone.utc)
        self._save_contract(contract)

        rel_contract = f"contracts/{contract_id}.yaml"
        rel_metadata = f"contracts/{contract_id}.meta.json"
        self.repo.index.add([rel_contract, rel_metadata])
        self.repo.index.commit(f"Deprecate contract: {contract_id}")

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List contracts from Git."""
        contracts_dir = self.repo_path / "contracts"
        all_contracts = []

        for yaml_file in contracts_dir.glob("*.yaml"):
            contract_id = yaml_file.stem
            contract = self._load_contract(contract_id)
            if contract:
                if status and contract.status != status:
                    continue
                if owner and contract.owner != owner:
                    continue
                all_contracts.append(contract)

        # Sort by updated_at descending
        all_contracts.sort(key=lambda c: c.updated_at, reverse=True)

        total = len(all_contracts)
        contracts = all_contracts[offset : offset + limit]

        return ContractList(contracts=contracts, total=total, limit=limit, offset=offset)

    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> VersionList:
        """List versions from Git tags."""
        prefix = f"{contract_id}/v"
        versions = []

        for tag in self.repo.tags:
            if tag.name.startswith(prefix):
                version = tag.name[len(prefix):]
                commit = tag.commit
                versions.append(
                    VersionInfo(
                        version=version,
                        created_at=datetime.fromtimestamp(commit.committed_date, timezone.utc),
                        commit_sha=commit.hexsha[:8],
                        message=tag.tag.message if tag.tag else None,
                    )
                )

        versions.sort(key=lambda v: v.created_at, reverse=True)
        total = len(versions)
        versions = versions[offset : offset + limit]

        return VersionList(versions=versions, total=total, limit=limit, offset=offset)

    async def diff_contracts(
        self,
        from_contract: Contract,
        to_contract: Contract,
    ) -> ContractDiff:
        """Diff two contracts."""
        from_fields = {f.name: f for f in from_contract.fields}
        to_fields = {f.name: f for f in to_contract.fields}

        added = [f for name, f in to_fields.items() if name not in from_fields]
        removed = [f for name, f in from_fields.items() if name not in to_fields]
        modified = []

        for name in set(from_fields) & set(to_fields):
            f1, f2 = from_fields[name], to_fields[name]
            if f1 != f2:
                modified.append(FieldChange(field=name, old=f1.model_dump(), new=f2.model_dump()))

        breaking = len(removed) > 0 or any(
            m.old.get("nullable") and not m.new.get("nullable") for m in modified
        )

        return ContractDiff(
            from_version=from_contract.version,
            to_version=to_contract.version,
            added_fields=added,
            removed_fields=removed,
            modified_fields=modified,
            breaking_changes=breaking,
        )

    async def record_validation(
        self,
        report: ValidationReport,
    ) -> ValidationRecord:
        """Record validation in validations file."""
        validations_path = self.repo_path / "validations.json"
        validations = []
        if validations_path.exists():
            validations = json.loads(validations_path.read_text())

        record = ValidationRecord(
            id=str(uuid4()),
            contract_id=report.contract_id,
            contract_version=report.contract_version,
            passed=report.passed,
            error_count=report.error_count,
            row_count=report.row_count,
            timestamp=datetime.now(timezone.utc),
            source=report.source,
        )

        validations.append(record.model_dump(mode="json"))
        validations_path.write_text(json.dumps(validations, indent=2, default=str))

        self.repo.index.add(["validations.json"])
        self.repo.index.commit(f"Record validation for {report.contract_id}")

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
        """List validations."""
        validations_path = self.repo_path / "validations.json"
        if not validations_path.exists():
            return ValidationList(validations=[], total=0, limit=limit, offset=offset)

        all_validations = json.loads(validations_path.read_text())
        filtered = []

        for v in all_validations:
            if contract_id and v["contract_id"] != contract_id:
                continue
            if passed is not None and v["passed"] != passed:
                continue
            ts = datetime.fromisoformat(v["timestamp"].replace("Z", "+00:00"))
            if from_date and ts < from_date:
                continue
            if to_date and ts > to_date:
                continue
            filtered.append(ValidationRecord(**v))

        filtered.sort(key=lambda v: v.timestamp, reverse=True)
        total = len(filtered)
        validations = filtered[offset : offset + limit]

        return ValidationList(validations=validations, total=total, limit=limit, offset=offset)

    async def search(
        self,
        query: str,
        field_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResults:
        """Search contracts."""
        contracts_dir = self.repo_path / "contracts"
        results = []
        query_lower = query.lower()

        for yaml_file in contracts_dir.glob("*.yaml"):
            contract = self._load_contract(yaml_file.stem)
            if not contract:
                continue

            # Search in name, description
            matches = []
            if query_lower in contract.name.lower():
                matches.append(f"name: {contract.name}")
            if contract.description and query_lower in contract.description.lower():
                matches.append(f"description match")

            # Search in fields
            for field in contract.fields:
                if field_filter and field.name != field_filter:
                    continue
                if query_lower in field.name.lower():
                    matches.append(f"field: {field.name}")
                if field.description and query_lower in field.description.lower():
                    matches.append(f"field {field.name} description")

            if matches:
                results.append(
                    SearchResult(
                        contract_id=contract.id,
                        contract_name=contract.name,
                        version=contract.version,
                        matches=matches,
                        score=len(matches),
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        total = len(results)
        results = results[offset : offset + limit]

        return SearchResults(results=results, total=total, query=query, limit=limit, offset=offset)
