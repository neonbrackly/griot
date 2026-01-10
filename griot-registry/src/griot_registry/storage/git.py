"""Git-backed storage backend using GitPython."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from griot_registry.schemas import (
    ConstraintChange,
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    FieldConstraints,
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


class GitStorage(StorageBackend):
    """Git-backed storage backend.

    Stores contracts as YAML files in a Git repository. Each contract
    change creates a commit, providing a complete audit trail.

    Directory structure:
        repo_path/
        ├── contracts/
        │   └── {contract_id}/
        │       ├── contract.yaml      # Current contract definition
        │       └── metadata.json      # Version and status info
        └── validations/
            └── {contract_id}/
                └── {timestamp}_{uuid}.json

    Versioning:
        - Each contract update is a git commit
        - Tags mark versions: {contract_id}/v{version}
        - Branch history provides full audit trail
    """

    def __init__(self, repo_path: str, branch: str = "main") -> None:
        """Initialize Git storage.

        Args:
            repo_path: Path to Git repository.
            branch: Branch to use for contract storage.
        """
        self.repo_path = Path(repo_path)
        self.branch = branch
        self.repo: Repo | None = None
        self.contracts_dir = self.repo_path / "contracts"
        self.validations_dir = self.repo_path / "validations"

    async def initialize(self) -> None:
        """Initialize or open the Git repository."""
        if self.repo_path.exists():
            try:
                self.repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                # Directory exists but is not a git repo, initialize it
                self.repo = Repo.init(self.repo_path)
        else:
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.init(self.repo_path)

        # Create directories
        self.contracts_dir.mkdir(exist_ok=True)
        self.validations_dir.mkdir(exist_ok=True)

        # Checkout/create branch
        if self.branch not in [h.name for h in self.repo.heads]:
            if self.repo.heads:
                self.repo.create_head(self.branch)
            # If no heads exist, first commit will create the branch
        else:
            self.repo.heads[self.branch].checkout()

        # Initial commit if empty repo
        if not self.repo.heads:
            # Create .gitkeep files
            (self.contracts_dir / ".gitkeep").touch()
            (self.validations_dir / ".gitkeep").touch()
            self.repo.index.add([
                str(self.contracts_dir / ".gitkeep"),
                str(self.validations_dir / ".gitkeep"),
            ])
            self.repo.index.commit("Initial commit: create directory structure")

    async def close(self) -> None:
        """Close the Git repository."""
        if self.repo:
            self.repo.close()
            self.repo = None

    async def health_check(self) -> bool:
        """Check if the Git repository is healthy."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")
        if self.repo.bare:
            raise RuntimeError("Git repository is bare")
        return True

    # =========================================================================
    # Contract CRUD
    # =========================================================================
    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract with an initial commit."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        contract_dir = self.contracts_dir / contract.id
        contract_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        version = "1.0.0"

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

        # Save contract YAML
        contract_file = contract_dir / "contract.yaml"
        self._save_contract_yaml(contract_file, full_contract)

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
        metadata_file = contract_dir / "metadata.json"
        self._save_json(metadata_file, metadata)

        # Git commit
        self.repo.index.add([str(contract_file), str(metadata_file)])
        commit = self.repo.index.commit(f"Create contract: {contract.id} v{version}")

        # Create version tag
        self.repo.create_tag(f"{contract.id}/v{version}", commit, message=f"Version {version}")

        return full_contract

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract, optionally at a specific version."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        contract_dir = self.contracts_dir / contract_id
        if not contract_dir.exists():
            return None

        if version is not None:
            # Get contract at specific version from git history
            tag_name = f"{contract_id}/v{version}"
            try:
                tag = self.repo.tags[tag_name]
                commit = tag.commit
                # Get file content at that commit
                contract_path = f"contracts/{contract_id}/contract.yaml"
                try:
                    blob = commit.tree / contract_path
                    content = blob.data_stream.read().decode("utf-8")
                    return self._parse_contract_yaml(content)
                except KeyError:
                    return None
            except (IndexError, KeyError):
                return None

        # Get current version
        contract_file = contract_dir / "contract.yaml"
        if not contract_file.exists():
            return None

        return self._load_contract_yaml(contract_file)

    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get contract as raw YAML string."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        if version is not None:
            tag_name = f"{contract_id}/v{version}"
            try:
                tag = self.repo.tags[tag_name]
                commit = tag.commit
                contract_path = f"contracts/{contract_id}/contract.yaml"
                try:
                    blob = commit.tree / contract_path
                    return blob.data_stream.read().decode("utf-8")
                except KeyError:
                    return ""
            except (IndexError, KeyError):
                return ""

        contract_file = self.contracts_dir / contract_id / "contract.yaml"
        if not contract_file.exists():
            return ""
        return contract_file.read_text()

    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
    ) -> Contract:
        """Update contract with a new commit and version tag."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        contract_dir = self.contracts_dir / contract_id
        metadata_file = contract_dir / "metadata.json"
        metadata = self._load_json(metadata_file)

        if metadata is None:
            raise ValueError(f"Contract {contract_id} not found")

        current_version = metadata["latest_version"]
        new_version = self._bump_version(current_version, update.change_type)

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

        # Save updated contract
        contract_file = contract_dir / "contract.yaml"
        self._save_contract_yaml(contract_file, updated)

        # Update metadata
        metadata["latest_version"] = new_version
        metadata["versions"].append({
            "version": new_version,
            "created_at": now.isoformat(),
            "change_type": update.change_type,
            "change_notes": update.change_notes,
        })
        self._save_json(metadata_file, metadata)

        # Git commit
        self.repo.index.add([str(contract_file), str(metadata_file)])
        commit_msg = f"Update contract: {contract_id} v{new_version}"
        if update.change_notes:
            commit_msg += f"\n\n{update.change_notes}"
        commit = self.repo.index.commit(commit_msg)

        # Create version tag
        self.repo.create_tag(
            f"{contract_id}/v{new_version}",
            commit,
            message=f"Version {new_version}",
        )

        return updated

    async def deprecate_contract(self, contract_id: str) -> None:
        """Mark contract as deprecated with a commit."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        contract_dir = self.contracts_dir / contract_id
        metadata_file = contract_dir / "metadata.json"
        metadata = self._load_json(metadata_file)

        if metadata is None:
            raise ValueError(f"Contract {contract_id} not found")

        metadata["status"] = "deprecated"
        self._save_json(metadata_file, metadata)

        # Update contract status
        contract = await self.get_contract(contract_id)
        if contract:
            contract.status = "deprecated"
            contract_file = contract_dir / "contract.yaml"
            self._save_contract_yaml(contract_file, contract)
            self.repo.index.add([str(contract_file), str(metadata_file)])
        else:
            self.repo.index.add([str(metadata_file)])

        self.repo.index.commit(f"Deprecate contract: {contract_id}")

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List all contracts."""
        contracts: list[Contract] = []

        for contract_dir in sorted(self.contracts_dir.iterdir()):
            if not contract_dir.is_dir() or contract_dir.name.startswith("."):
                continue

            contract = await self.get_contract(contract_dir.name)
            if contract is None:
                continue

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
        """List all versions from metadata and git tags."""
        metadata_file = self.contracts_dir / contract_id / "metadata.json"
        metadata = self._load_json(metadata_file)

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

        for name in from_fields:
            if name not in to_fields:
                continue

            from_f = from_fields[name]
            to_f = to_fields[name]

            if from_f.type != to_f.type:
                type_changes.append(TypeChange(
                    field=name,
                    from_type=from_f.type,
                    to_type=to_f.type,
                    is_breaking=True,
                ))

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
        """Store a validation result (not committed to git by default)."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

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
        validation_file = validation_dir / filename
        self._save_json(validation_file, report_data)

        # Optionally commit validation records (configurable)
        # self.repo.index.add([str(validation_file)])
        # self.repo.index.commit(f"Record validation: {report.contract_id}")

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
        """List validation history."""
        records: list[ValidationRecord] = []

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
        """Search contracts."""
        query_lower = query.lower()
        hits: list[SearchHit] = []

        for contract_dir in self.contracts_dir.iterdir():
            if not contract_dir.is_dir() or contract_dir.name.startswith("."):
                continue

            contract = await self.get_contract(contract_dir.name)
            if contract is None:
                continue

            if not field_filter and query_lower in contract.name.lower():
                hits.append(SearchHit(
                    contract_id=contract.id,
                    contract_name=contract.name,
                    match_type="name",
                    snippet=contract.name,
                ))

            if not field_filter and contract.description and query_lower in contract.description.lower():
                hits.append(SearchHit(
                    contract_id=contract.id,
                    contract_name=contract.name,
                    match_type="description",
                    snippet=self._snippet(contract.description, query),
                ))

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
    # Git-specific methods
    # =========================================================================
    def get_commit_history(
        self,
        contract_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get commit history for a contract."""
        if self.repo is None:
            raise RuntimeError("Git repository not initialized")

        contract_path = f"contracts/{contract_id}"
        commits = []

        for commit in self.repo.iter_commits(paths=contract_path, max_count=limit):
            commits.append({
                "sha": commit.hexsha,
                "message": commit.message,
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
            })

        return commits

    # =========================================================================
    # Helpers
    # =========================================================================
    def _save_json(self, path: Path, data: dict[str, Any]) -> None:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def _save_contract_yaml(self, path: Path, contract: Contract) -> None:
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
        with open(path) as f:
            data = yaml.safe_load(f)
        return self._parse_contract_yaml_data(data)

    def _parse_contract_yaml(self, content: str) -> Contract:
        data = yaml.safe_load(content)
        return self._parse_contract_yaml_data(data)

    def _parse_contract_yaml_data(self, data: dict[str, Any]) -> Contract:
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
        parts = [int(p) for p in version.split(".")]
        if len(parts) != 3:
            parts = [1, 0, 0]

        if change_type == "major":
            return f"{parts[0] + 1}.0.0"
        elif change_type == "minor":
            return f"{parts[0]}.{parts[1] + 1}.0"
        else:
            return f"{parts[0]}.{parts[1]}.{parts[2] + 1}"

    def _version_tuple(self, version: str) -> tuple[int, int, int]:
        parts = version.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def _compare_constraints(
        self,
        field_name: str,
        from_f: FieldDefinition,
        to_f: FieldDefinition,
        changes: list[ConstraintChange],
    ) -> None:
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
        if from_val is None and to_val is not None:
            return True
        if from_val is not None and to_val is None:
            return False
        if constraint in ("min_length", "ge", "gt"):
            return to_val > from_val
        if constraint in ("max_length", "le", "lt"):
            return to_val < from_val
        if constraint == "pattern":
            return True
        if constraint == "enum":
            return not set(to_val).issuperset(set(from_val))
        return True

    def _snippet(self, text: str, query: str, context: int = 50) -> str:
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
