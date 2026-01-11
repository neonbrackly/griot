"""PostgreSQL storage backend for griot-registry."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from griot_registry.schemas import (
    Contract,
    ContractCreate,
    ContractDiff,
    ContractList,
    ContractUpdate,
    FieldChange,
    FieldSchema,
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
    from sqlalchemy.ext.asyncio import AsyncEngine


class PostgresStorage(StorageBackend):
    """PostgreSQL storage backend using SQLAlchemy async.

    Stores contracts in PostgreSQL with JSONB fields for flexible schema.
    Uses three tables: contracts, contract_versions, and validations.
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize PostgreSQL storage.

        Args:
            connection_string: PostgreSQL connection URL.
                Example: postgresql+asyncpg://user:pass@host:5432/dbname
        """
        self.connection_string = connection_string
        self._engine: AsyncEngine | None = None
        self._metadata = None
        self._contracts_table = None
        self._versions_table = None
        self._validations_table = None

    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            from sqlalchemy import (
                Boolean,
                Column,
                DateTime,
                Integer,
                MetaData,
                String,
                Table,
                Text,
            )
            from sqlalchemy.dialects.postgresql import JSONB
            from sqlalchemy.ext.asyncio import create_async_engine
        except ImportError as e:
            raise ImportError(
                "SQLAlchemy and asyncpg are required for PostgreSQL storage. "
                "Install with: pip install griot-registry[postgres]"
            ) from e

        self._engine = create_async_engine(self.connection_string, echo=False)
        self._metadata = MetaData()

        # Define tables
        self._contracts_table = Table(
            "contracts",
            self._metadata,
            Column("id", String(255), primary_key=True),
            Column("name", String(255), nullable=False),
            Column("description", Text),
            Column("version", String(50), nullable=False),
            Column("owner", String(255), nullable=False),
            Column("status", String(50), nullable=False, default="active"),
            Column("fields", JSONB, nullable=False),
            Column("tags", JSONB, nullable=False, default=[]),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )

        self._versions_table = Table(
            "contract_versions",
            self._metadata,
            Column("id", String(36), primary_key=True),
            Column("contract_id", String(255), nullable=False, index=True),
            Column("version", String(50), nullable=False),
            Column("fields", JSONB, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("message", Text),
        )

        self._validations_table = Table(
            "validations",
            self._metadata,
            Column("id", String(36), primary_key=True),
            Column("contract_id", String(255), nullable=False, index=True),
            Column("contract_version", String(50), nullable=False),
            Column("passed", Boolean, nullable=False),
            Column("error_count", Integer, nullable=False, default=0),
            Column("row_count", Integer),
            Column("timestamp", DateTime(timezone=True), nullable=False),
            Column("source", String(255)),
            Column("errors", JSONB),
        )

        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(self._metadata.create_all)

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("PostgreSQL storage not initialized. Call initialize() first.")
        return self._engine

    async def close(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            from sqlalchemy import text

            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract."""
        from sqlalchemy import insert

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

        async with self.engine.begin() as conn:
            # Insert contract
            await conn.execute(
                insert(self._contracts_table).values(
                    id=new_contract.id,
                    name=new_contract.name,
                    description=new_contract.description,
                    version=new_contract.version,
                    owner=new_contract.owner,
                    status=new_contract.status,
                    fields=[f.model_dump() for f in new_contract.fields],
                    tags=new_contract.tags,
                    created_at=now,
                    updated_at=now,
                )
            )

            # Insert initial version
            await conn.execute(
                insert(self._versions_table).values(
                    id=str(uuid4()),
                    contract_id=new_contract.id,
                    version="1.0.0",
                    fields=[f.model_dump() for f in new_contract.fields],
                    created_at=now,
                    message="Initial version",
                )
            )

        return new_contract

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract by ID, optionally at a specific version."""
        from sqlalchemy import select

        if version:
            # Get specific version
            async with self.engine.connect() as conn:
                # Get version data
                result = await conn.execute(
                    select(self._versions_table).where(
                        self._versions_table.c.contract_id == contract_id,
                        self._versions_table.c.version == version,
                    )
                )
                version_row = result.fetchone()
                if not version_row:
                    return None

                # Get contract metadata
                result = await conn.execute(
                    select(self._contracts_table).where(
                        self._contracts_table.c.id == contract_id
                    )
                )
                contract_row = result.fetchone()
                if not contract_row:
                    return None

                return Contract(
                    id=contract_row.id,
                    name=contract_row.name,
                    description=contract_row.description,
                    version=version_row.version,
                    owner=contract_row.owner,
                    status=contract_row.status,
                    fields=[FieldSchema(**f) for f in version_row.fields],
                    tags=contract_row.tags or [],
                    created_at=version_row.created_at,
                    updated_at=version_row.created_at,
                )

        # Get latest version
        async with self.engine.connect() as conn:
            result = await conn.execute(
                select(self._contracts_table).where(
                    self._contracts_table.c.id == contract_id
                )
            )
            row = result.fetchone()
            if not row:
                return None

            return Contract(
                id=row.id,
                name=row.name,
                description=row.description,
                version=row.version,
                owner=row.owner,
                status=row.status,
                fields=[FieldSchema(**f) for f in row.fields],
                tags=row.tags or [],
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get contract as YAML string."""
        import yaml

        contract = await self.get_contract(contract_id, version)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")

        data = {
            "id": contract.id,
            "name": contract.name,
            "description": contract.description,
            "version": contract.version,
            "owner": contract.owner,
            "status": contract.status,
            "fields": [f.model_dump() for f in contract.fields],
        }
        return yaml.dump(data, default_flow_style=False)

    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
        is_breaking: bool = False,
        breaking_changes: list[dict[str, Any]] | None = None,
    ) -> Contract:
        """Update a contract (T-373 enhanced).

        Tracks breaking changes in version history.
        """
        from sqlalchemy import insert, update as sql_update

        contract = await self.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract not found: {contract_id}")

        # Bump version - force major for breaking changes
        parts = contract.version.split(".")
        if is_breaking:
            new_version = f"{int(parts[0]) + 1}.0.0"
        else:
            new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
        now = datetime.now(timezone.utc)

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
            updated_at=now,
        )

        # T-373: Build version message with breaking change info
        message = f"Updated to version {new_version}"
        if is_breaking:
            message = f"BREAKING: {message}"

        async with self.engine.begin() as conn:
            # Update contract
            await conn.execute(
                sql_update(self._contracts_table)
                .where(self._contracts_table.c.id == contract_id)
                .values(
                    name=updated.name,
                    description=updated.description,
                    version=new_version,
                    owner=updated.owner,
                    fields=[f.model_dump() for f in updated.fields],
                    tags=updated.tags,
                    updated_at=now,
                )
            )

            # Insert new version with breaking change info
            version_data = {
                "id": str(uuid4()),
                "contract_id": contract_id,
                "version": new_version,
                "fields": [f.model_dump() for f in updated.fields],
                "created_at": now,
                "message": message,
            }

            # T-373: Store breaking change details in metadata if available
            if is_breaking and breaking_changes:
                version_data["metadata"] = {
                    "is_breaking": True,
                    "breaking_changes": breaking_changes,
                }

            await conn.execute(
                insert(self._versions_table).values(**version_data)
            )

        return updated

    async def deprecate_contract(self, contract_id: str) -> None:
        """Mark a contract as deprecated."""
        from sqlalchemy import update as sql_update

        async with self.engine.begin() as conn:
            await conn.execute(
                sql_update(self._contracts_table)
                .where(self._contracts_table.c.id == contract_id)
                .values(status="deprecated", updated_at=datetime.now(timezone.utc))
            )

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List contracts with optional filtering."""
        from sqlalchemy import func, select

        query = select(self._contracts_table)

        if status:
            query = query.where(self._contracts_table.c.status == status)
        if owner:
            query = query.where(self._contracts_table.c.owner == owner)

        query = query.order_by(self._contracts_table.c.updated_at.desc())

        async with self.engine.connect() as conn:
            # Get total count
            count_query = select(func.count()).select_from(self._contracts_table)
            if status:
                count_query = count_query.where(self._contracts_table.c.status == status)
            if owner:
                count_query = count_query.where(self._contracts_table.c.owner == owner)
            total = (await conn.execute(count_query)).scalar() or 0

            # Get paginated results
            result = await conn.execute(query.limit(limit).offset(offset))
            contracts = [
                Contract(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    version=row.version,
                    owner=row.owner,
                    status=row.status,
                    fields=[FieldSchema(**f) for f in row.fields],
                    tags=row.tags or [],
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row in result.fetchall()
            ]

        return ContractList(contracts=contracts, total=total, limit=limit, offset=offset)

    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> VersionList:
        """List versions of a contract."""
        from sqlalchemy import func, select

        async with self.engine.connect() as conn:
            # Count total
            count_query = (
                select(func.count())
                .select_from(self._versions_table)
                .where(self._versions_table.c.contract_id == contract_id)
            )
            total = (await conn.execute(count_query)).scalar() or 0

            # Get versions
            query = (
                select(self._versions_table)
                .where(self._versions_table.c.contract_id == contract_id)
                .order_by(self._versions_table.c.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await conn.execute(query)

            versions = [
                VersionInfo(
                    version=row.version,
                    created_at=row.created_at,
                    message=row.message,
                )
                for row in result.fetchall()
            ]

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
        """Record a validation result."""
        from sqlalchemy import insert

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

        async with self.engine.begin() as conn:
            await conn.execute(
                insert(self._validations_table).values(
                    id=record.id,
                    contract_id=record.contract_id,
                    contract_version=record.contract_version,
                    passed=record.passed,
                    error_count=record.error_count,
                    row_count=record.row_count,
                    timestamp=record.timestamp,
                    source=record.source,
                    errors=report.errors if hasattr(report, "errors") else None,
                )
            )

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
        """List validation records with filtering."""
        from sqlalchemy import func, select

        query = select(self._validations_table)

        if contract_id:
            query = query.where(self._validations_table.c.contract_id == contract_id)
        if passed is not None:
            query = query.where(self._validations_table.c.passed == passed)
        if from_date:
            query = query.where(self._validations_table.c.timestamp >= from_date)
        if to_date:
            query = query.where(self._validations_table.c.timestamp <= to_date)

        query = query.order_by(self._validations_table.c.timestamp.desc())

        async with self.engine.connect() as conn:
            # Get total
            count_query = select(func.count()).select_from(self._validations_table)
            if contract_id:
                count_query = count_query.where(self._validations_table.c.contract_id == contract_id)
            if passed is not None:
                count_query = count_query.where(self._validations_table.c.passed == passed)
            if from_date:
                count_query = count_query.where(self._validations_table.c.timestamp >= from_date)
            if to_date:
                count_query = count_query.where(self._validations_table.c.timestamp <= to_date)
            total = (await conn.execute(count_query)).scalar() or 0

            # Get paginated results
            result = await conn.execute(query.limit(limit).offset(offset))
            validations = [
                ValidationRecord(
                    id=row.id,
                    contract_id=row.contract_id,
                    contract_version=row.contract_version,
                    passed=row.passed,
                    error_count=row.error_count,
                    row_count=row.row_count,
                    timestamp=row.timestamp,
                    source=row.source,
                )
                for row in result.fetchall()
            ]

        return ValidationList(validations=validations, total=total, limit=limit, offset=offset)

    async def search(
        self,
        query: str,
        field_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResults:
        """Search contracts using PostgreSQL ILIKE."""
        from sqlalchemy import or_, select

        search_query = select(self._contracts_table).where(
            or_(
                self._contracts_table.c.name.ilike(f"%{query}%"),
                self._contracts_table.c.description.ilike(f"%{query}%"),
                self._contracts_table.c.id.ilike(f"%{query}%"),
            )
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(search_query)
            rows = result.fetchall()

        results = []
        query_lower = query.lower()

        for row in rows:
            matches = []
            if query_lower in row.name.lower():
                matches.append(f"name: {row.name}")
            if row.description and query_lower in row.description.lower():
                matches.append("description match")

            # Search in fields
            for field in row.fields:
                if field_filter and field.get("name") != field_filter:
                    continue
                if query_lower in field.get("name", "").lower():
                    matches.append(f"field: {field['name']}")
                if field.get("description") and query_lower in field["description"].lower():
                    matches.append(f"field {field['name']} description")

            if matches:
                results.append(
                    SearchResult(
                        contract_id=row.id,
                        contract_name=row.name,
                        version=row.version,
                        matches=matches,
                        score=len(matches),
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        total = len(results)
        results = results[offset : offset + limit]

        return SearchResults(results=results, total=total, query=query, limit=limit, offset=offset)
