"""PostgreSQL storage backend using SQLAlchemy async."""

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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

# Define database metadata and tables
metadata = MetaData()

contracts_table = Table(
    "contracts",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("description", Text),
    Column("owner", String(255)),
    Column("status", String(50), default="draft"),
    Column("latest_version", String(50), default="1.0.0"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

contract_versions_table = Table(
    "contract_versions",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("contract_id", String(255), nullable=False, index=True),
    Column("version", String(50), nullable=False),
    Column("name", String(255), nullable=False),
    Column("description", Text),
    Column("owner", String(255)),
    Column("status", String(50), default="draft"),
    Column("fields", JSONB, nullable=False),
    Column("change_type", String(50)),
    Column("change_notes", Text),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("created_by", String(255)),
)

validations_table = Table(
    "validations",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("contract_id", String(255), nullable=False, index=True),
    Column("contract_version", String(50)),
    Column("passed", Boolean, nullable=False),
    Column("row_count", Integer, nullable=False),
    Column("error_count", Integer, default=0),
    Column("error_rate", Float, default=0.0),
    Column("duration_ms", Float),
    Column("environment", String(50)),
    Column("pipeline_id", String(255)),
    Column("run_id", String(255)),
    Column("sample_errors", JSONB),
    Column("recorded_at", DateTime(timezone=True), server_default=func.now()),
)


class PostgresStorage(StorageBackend):
    """PostgreSQL storage backend.

    Stores contracts and validations in PostgreSQL with full-text search
    support and efficient querying.

    Tables:
        - contracts: Contract metadata and latest version info
        - contract_versions: Full version history with field definitions
        - validations: Validation results and history
    """

    def __init__(self, dsn: str) -> None:
        """Initialize PostgreSQL storage.

        Args:
            dsn: PostgreSQL connection string (asyncpg format).
                 Example: postgresql+asyncpg://user:pass@host:5432/dbname
        """
        self.dsn = dsn
        self.engine: AsyncEngine | None = None
        self.async_session: sessionmaker | None = None

    async def initialize(self) -> None:
        """Initialize database connection and create tables if needed."""
        self.engine = create_async_engine(
            self.dsn,
            echo=False,
            pool_size=5,
            max_overflow=10,
        )

        # Create tables if they don't exist
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None

    async def health_check(self) -> bool:
        """Check database connection."""
        if self.engine is None:
            raise RuntimeError("Database not initialized")

        async with self.engine.connect() as conn:
            await conn.execute(select(1))
        return True

    def _get_session(self) -> AsyncSession:
        """Get a database session."""
        if self.async_session is None:
            raise RuntimeError("Database not initialized")
        return self.async_session()

    # =========================================================================
    # Contract CRUD
    # =========================================================================
    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract."""
        async with self._get_session() as session:
            now = datetime.now(timezone.utc)
            version = "1.0.0"

            # Insert into contracts table
            await session.execute(
                contracts_table.insert().values(
                    id=contract.id,
                    name=contract.name,
                    description=contract.description,
                    owner=contract.owner,
                    status="draft",
                    latest_version=version,
                    created_at=now,
                    updated_at=now,
                )
            )

            # Insert initial version
            fields_json = [f.model_dump(exclude_none=True) for f in contract.fields]
            await session.execute(
                contract_versions_table.insert().values(
                    id=uuid4(),
                    contract_id=contract.id,
                    version=version,
                    name=contract.name,
                    description=contract.description,
                    owner=contract.owner,
                    status="draft",
                    fields=fields_json,
                    change_type="major",
                    change_notes="Initial version",
                    created_at=now,
                )
            )

            await session.commit()

            return Contract(
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

    async def get_contract(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> Contract | None:
        """Get a contract, optionally at a specific version."""
        async with self._get_session() as session:
            if version is not None:
                # Get specific version
                result = await session.execute(
                    select(contract_versions_table).where(
                        contract_versions_table.c.contract_id == contract_id,
                        contract_versions_table.c.version == version,
                    )
                )
                row = result.fetchone()
                if row is None:
                    return None

                return self._row_to_contract(row)
            else:
                # Get latest version
                result = await session.execute(
                    select(contracts_table).where(contracts_table.c.id == contract_id)
                )
                meta_row = result.fetchone()
                if meta_row is None:
                    return None

                latest_version = meta_row.latest_version

                result = await session.execute(
                    select(contract_versions_table).where(
                        contract_versions_table.c.contract_id == contract_id,
                        contract_versions_table.c.version == latest_version,
                    )
                )
                row = result.fetchone()
                if row is None:
                    return None

                return self._row_to_contract(row)

    async def get_contract_yaml(
        self,
        contract_id: str,
        version: str | None = None,
    ) -> str:
        """Get contract as YAML string."""
        import yaml

        contract = await self.get_contract(contract_id, version)
        if contract is None:
            return ""

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
        return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)

    async def update_contract(
        self,
        contract_id: str,
        update: ContractUpdate,
    ) -> Contract:
        """Update contract, creating a new version."""
        async with self._get_session() as session:
            # Get current contract
            result = await session.execute(
                select(contracts_table).where(contracts_table.c.id == contract_id)
            )
            meta_row = result.fetchone()
            if meta_row is None:
                raise ValueError(f"Contract {contract_id} not found")

            current_version = meta_row.latest_version
            new_version = self._bump_version(current_version, update.change_type)

            # Get current version for field defaults
            current = await self.get_contract(contract_id)
            if current is None:
                raise ValueError(f"Contract {contract_id} not found")

            now = datetime.now(timezone.utc)
            new_name = update.name if update.name else current.name
            new_desc = update.description if update.description else current.description
            new_fields = update.fields if update.fields else current.fields

            # Update contracts table
            await session.execute(
                contracts_table.update()
                .where(contracts_table.c.id == contract_id)
                .values(
                    name=new_name,
                    description=new_desc,
                    latest_version=new_version,
                    updated_at=now,
                )
            )

            # Insert new version
            fields_json = [f.model_dump(exclude_none=True) for f in new_fields]
            await session.execute(
                contract_versions_table.insert().values(
                    id=uuid4(),
                    contract_id=contract_id,
                    version=new_version,
                    name=new_name,
                    description=new_desc,
                    owner=current.owner,
                    status=current.status,
                    fields=fields_json,
                    change_type=update.change_type,
                    change_notes=update.change_notes,
                    created_at=now,
                )
            )

            await session.commit()

            return Contract(
                id=contract_id,
                name=new_name,
                description=new_desc,
                owner=current.owner,
                version=new_version,
                status=current.status,
                fields=new_fields,
                created_at=current.created_at,
                updated_at=now,
            )

    async def deprecate_contract(self, contract_id: str) -> None:
        """Mark contract as deprecated."""
        async with self._get_session() as session:
            result = await session.execute(
                contracts_table.update()
                .where(contracts_table.c.id == contract_id)
                .values(status="deprecated", updated_at=datetime.now(timezone.utc))
            )
            if result.rowcount == 0:
                raise ValueError(f"Contract {contract_id} not found")

            # Also update the latest version status
            result = await session.execute(
                select(contracts_table.c.latest_version).where(
                    contracts_table.c.id == contract_id
                )
            )
            row = result.fetchone()
            if row:
                await session.execute(
                    contract_versions_table.update()
                    .where(
                        contract_versions_table.c.contract_id == contract_id,
                        contract_versions_table.c.version == row.latest_version,
                    )
                    .values(status="deprecated")
                )

            await session.commit()

    async def list_contracts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        owner: str | None = None,
    ) -> ContractList:
        """List contracts with filtering."""
        async with self._get_session() as session:
            # Build query
            query = select(contracts_table)
            count_query = select(func.count()).select_from(contracts_table)

            if status:
                query = query.where(contracts_table.c.status == status)
                count_query = count_query.where(contracts_table.c.status == status)
            if owner:
                query = query.where(contracts_table.c.owner == owner)
                count_query = count_query.where(contracts_table.c.owner == owner)

            # Get total count
            result = await session.execute(count_query)
            total = result.scalar() or 0

            # Get paginated results
            query = query.order_by(contracts_table.c.name).limit(limit).offset(offset)
            result = await session.execute(query)
            rows = result.fetchall()

            # Fetch full contracts with fields
            contracts = []
            for row in rows:
                contract = await self.get_contract(row.id)
                if contract:
                    contracts.append(contract)

            return ContractList(items=contracts, total=total, limit=limit, offset=offset)

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
        async with self._get_session() as session:
            # Get total count
            count_query = (
                select(func.count())
                .select_from(contract_versions_table)
                .where(contract_versions_table.c.contract_id == contract_id)
            )
            result = await session.execute(count_query)
            total = result.scalar() or 0

            # Get versions
            query = (
                select(contract_versions_table)
                .where(contract_versions_table.c.contract_id == contract_id)
                .order_by(contract_versions_table.c.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(query)
            rows = result.fetchall()

            versions = [
                VersionSummary(
                    version=row.version,
                    created_at=row.created_at,
                    created_by=row.created_by,
                    change_type=row.change_type,
                    change_notes=row.change_notes,
                    is_breaking=row.change_type == "major",
                )
                for row in rows
            ]

            return VersionList(items=versions, total=total)

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
        """Store a validation result."""
        async with self._get_session() as session:
            record_id = uuid4()
            now = datetime.now(timezone.utc)

            sample_errors_json = [e.model_dump() for e in report.sample_errors]

            await session.execute(
                validations_table.insert().values(
                    id=record_id,
                    contract_id=report.contract_id,
                    contract_version=report.contract_version,
                    passed=report.passed,
                    row_count=report.row_count,
                    error_count=report.error_count,
                    error_rate=report.error_rate,
                    duration_ms=report.duration_ms,
                    environment=report.environment,
                    pipeline_id=report.pipeline_id,
                    run_id=report.run_id,
                    sample_errors=sample_errors_json,
                    recorded_at=now,
                )
            )

            await session.commit()

            return ValidationRecord(
                id=record_id,
                contract_id=report.contract_id,
                contract_version=report.contract_version,
                passed=report.passed,
                row_count=report.row_count,
                error_count=report.error_count,
                recorded_at=now,
            )

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
        async with self._get_session() as session:
            query = select(validations_table)
            count_query = select(func.count()).select_from(validations_table)

            conditions = []
            if contract_id:
                conditions.append(validations_table.c.contract_id == contract_id)
            if passed is not None:
                conditions.append(validations_table.c.passed == passed)
            if from_date:
                conditions.append(validations_table.c.recorded_at >= from_date)
            if to_date:
                conditions.append(validations_table.c.recorded_at <= to_date)

            if conditions:
                query = query.where(*conditions)
                count_query = count_query.where(*conditions)

            # Get total
            result = await session.execute(count_query)
            total = result.scalar() or 0

            # Get paginated results
            query = (
                query.order_by(validations_table.c.recorded_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(query)
            rows = result.fetchall()

            records = [
                ValidationRecord(
                    id=row.id,
                    contract_id=row.contract_id,
                    contract_version=row.contract_version,
                    passed=row.passed,
                    row_count=row.row_count,
                    error_count=row.error_count,
                    recorded_at=row.recorded_at,
                )
                for row in rows
            ]

            return ValidationList(items=records, total=total, limit=limit, offset=offset)

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
        """Search contracts using PostgreSQL LIKE (full-text search can be added)."""
        async with self._get_session() as session:
            hits: list[SearchHit] = []
            search_pattern = f"%{query}%"

            # Search in contract metadata
            if not field_filter:
                meta_query = select(contracts_table).where(
                    or_(
                        contracts_table.c.name.ilike(search_pattern),
                        contracts_table.c.description.ilike(search_pattern),
                    )
                )
                result = await session.execute(meta_query)
                rows = result.fetchall()

                for row in rows:
                    if query.lower() in row.name.lower():
                        hits.append(SearchHit(
                            contract_id=row.id,
                            contract_name=row.name,
                            match_type="name",
                            snippet=row.name,
                        ))
                    elif row.description and query.lower() in row.description.lower():
                        hits.append(SearchHit(
                            contract_id=row.id,
                            contract_name=row.name,
                            match_type="description",
                            snippet=self._snippet(row.description, query),
                        ))

            # Search in fields (requires loading all contracts and checking)
            # For better performance, consider adding a denormalized search table
            all_contracts = await self.list_contracts(limit=1000, offset=0)
            for contract in all_contracts.items:
                for field in contract.fields:
                    if field_filter and field.name != field_filter:
                        continue

                    if query.lower() in field.name.lower():
                        hits.append(SearchHit(
                            contract_id=contract.id,
                            contract_name=contract.name,
                            field_name=field.name,
                            match_type="field",
                            snippet=f"{field.name}: {field.description}",
                        ))
                    elif query.lower() in field.description.lower():
                        hits.append(SearchHit(
                            contract_id=contract.id,
                            contract_name=contract.name,
                            field_name=field.name,
                            match_type="field",
                            snippet=self._snippet(field.description, query),
                        ))

            # Remove duplicates and paginate
            seen = set()
            unique_hits = []
            for hit in hits:
                key = (hit.contract_id, hit.field_name, hit.match_type)
                if key not in seen:
                    seen.add(key)
                    unique_hits.append(hit)

            total = len(unique_hits)
            items = unique_hits[offset : offset + limit]

            return SearchResults(query=query, items=items, total=total)

    # =========================================================================
    # Helpers
    # =========================================================================
    def _row_to_contract(self, row: Any) -> Contract:
        """Convert a database row to a Contract."""
        fields = [FieldDefinition(**f) for f in row.fields]
        return Contract(
            id=row.contract_id,
            name=row.name,
            description=row.description,
            owner=row.owner,
            version=row.version,
            status=row.status,
            fields=fields,
            created_at=row.created_at,
            updated_at=row.created_at,  # Use version's created_at
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
        else:
            return f"{parts[0]}.{parts[1]}.{parts[2] + 1}"

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
