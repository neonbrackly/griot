"""MongoDB storage backend implementation.

This module implements all repository interfaces using MongoDB as the storage engine.
Uses motor for async MongoDB operations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from griot_core import Contract, load_contract_from_dict, lint_contract

from griot_registry.storage.base import (
    StorageBackend,
    ContractRepository,
    SchemaCatalogRepository,
    ValidationRecordRepository,
    RunRepository,
    IssueRepository,
    CommentRepository,
    ApprovalRepository,
)


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


class MongoContractRepository(ContractRepository):
    """MongoDB implementation of ContractRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._contracts = db.contracts
        self._versions = db.contract_versions

    async def create(
        self,
        entity: Contract,
        created_by: str | None = None,
        **kwargs: Any,
    ) -> Contract:
        """Create a new contract."""
        now = _utc_now()

        # Convert griot-core Contract to dict (ODCS format with camelCase)
        doc = entity.to_dict()

        # Add registry metadata
        doc["_meta"] = {
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
        }

        # Insert into contracts collection
        await self._contracts.insert_one(doc)

        # Create initial version record
        await self._versions.insert_one({
            "contract_id": entity.id,
            "version": entity.version,
            "snapshot": doc.copy(),
            "change_type": "major",
            "change_notes": "Initial version",
            "is_breaking": False,
            "breaking_changes": [],
            "created_at": now,
            "created_by": created_by,
        })

        return entity

    async def get(self, entity_id: str, **kwargs: Any) -> Contract | None:
        """Get latest version of a contract by ID."""
        doc = await self._contracts.find_one({"id": entity_id})
        if not doc:
            return None

        # Remove MongoDB fields and registry metadata
        doc.pop("_id", None)
        doc.pop("_meta", None)

        # Use griot-core to parse
        return load_contract_from_dict(doc)

    async def get_version(
        self,
        contract_id: str,
        version: str,
    ) -> Contract | None:
        """Get a specific version of a contract."""
        version_doc = await self._versions.find_one({
            "contract_id": contract_id,
            "version": version,
        })
        if not version_doc:
            return None

        doc = version_doc["snapshot"]
        doc.pop("_id", None)
        doc.pop("_meta", None)

        return load_contract_from_dict(doc)

    async def update(
        self,
        entity_id: str,
        entity: Contract,
        change_type: str = "minor",
        change_notes: str | None = None,
        is_breaking: bool = False,
        breaking_changes: list[dict[str, Any]] | None = None,
        updated_by: str | None = None,
        **kwargs: Any,
    ) -> Contract:
        """Update a contract, creating a new version."""
        now = _utc_now()

        doc = entity.to_dict()
        # Don't include _meta in doc - we'll set specific fields instead
        # to avoid conflict between $set and preserving created_at

        # Build the update document
        set_doc = {**doc}  # Contract fields
        set_doc["_meta.updated_at"] = now
        set_doc["_meta.updated_by"] = updated_by

        # Update contracts collection (latest version)
        result = await self._contracts.update_one(
            {"id": entity_id},
            {"$set": set_doc},
        )

        if result.matched_count == 0:
            raise ValueError(f"Contract '{entity_id}' not found")

        # Add version record
        await self._versions.insert_one({
            "contract_id": entity_id,
            "version": entity.version,
            "snapshot": doc.copy(),
            "change_type": change_type,
            "change_notes": change_notes,
            "is_breaking": is_breaking,
            "breaking_changes": breaking_changes or [],
            "created_at": now,
            "created_by": updated_by,
        })

        return entity

    async def delete(self, entity_id: str, **kwargs: Any) -> bool:
        """Delete a contract (soft delete by setting status to retired)."""
        result = await self._contracts.update_one(
            {"id": entity_id},
            {"$set": {"status": "retired", "_meta.updated_at": _utc_now()}},
        )
        return result.matched_count > 0

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        schema_name: str | None = None,
        owner: str | None = None,
        **filters: Any,
    ) -> tuple[list[Contract], int]:
        """List contracts with pagination and filtering."""
        query: dict[str, Any] = {}

        if status:
            query["status"] = status
        if schema_name:
            query["schema.name"] = schema_name
        if owner:
            query["team.name"] = owner

        cursor = (
            self._contracts.find(query)
            .skip(offset)
            .limit(limit)
            .sort("_meta.updated_at", -1)
        )

        contracts = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("_meta", None)
            contracts.append(load_contract_from_dict(doc))

        total = await self._contracts.count_documents(query)

        return contracts, total

    async def exists(self, entity_id: str) -> bool:
        """Check if a contract exists."""
        count = await self._contracts.count_documents({"id": entity_id})
        return count > 0

    async def list_versions(
        self,
        contract_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List version history for a contract."""
        query = {"contract_id": contract_id}

        cursor = (
            self._versions.find(query, {"snapshot": 0})  # Exclude full snapshot
            .skip(offset)
            .limit(limit)
            .sort("created_at", -1)
        )

        versions = []
        async for doc in cursor:
            doc.pop("_id", None)
            versions.append(doc)

        total = await self._versions.count_documents(query)

        return versions, total

    async def update_status(
        self,
        contract_id: str,
        new_status: str,
        updated_by: str | None = None,
    ) -> Contract:
        """Update contract status."""
        now = _utc_now()

        result = await self._contracts.find_one_and_update(
            {"id": contract_id},
            {
                "$set": {
                    "status": new_status,
                    "_meta.updated_at": now,
                    "_meta.updated_by": updated_by,
                }
            },
            return_document=True,
        )

        if not result:
            raise ValueError(f"Contract '{contract_id}' not found")

        result.pop("_id", None)
        result.pop("_meta", None)

        return load_contract_from_dict(result)

    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Full-text search across contracts."""
        cursor = (
            self._contracts.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}},
            )
            .sort([("score", {"$meta": "textScore"})])
            .limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append({
                "contract_id": doc["id"],
                "contract_name": doc.get("name", ""),
                "version": doc.get("version", ""),
                "status": doc.get("status", ""),
                "score": doc.get("score", 0),
            })

        return results


class MongoSchemaCatalogRepository(SchemaCatalogRepository):
    """MongoDB implementation of SchemaCatalogRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._catalog = db.schema_catalog
        self._contracts = db.contracts

    async def find_schemas(
        self,
        name: str | None = None,
        physical_name: str | None = None,
        field_name: str | None = None,
        has_pii: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find schemas across all contracts."""
        query: dict[str, Any] = {}

        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if physical_name:
            query["physical_name"] = {"$regex": physical_name, "$options": "i"}
        if field_name:
            query["field_names"] = field_name
        if has_pii is not None:
            query["has_pii"] = has_pii

        cursor = self._catalog.find(query).limit(limit)

        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)

        return results

    async def get_contracts_by_schema(
        self,
        schema_name: str,
    ) -> list[str]:
        """Get contract IDs that contain a schema with given name."""
        cursor = self._catalog.find(
            {"name": schema_name},
            {"contract_id": 1},
        )

        contract_ids = []
        async for doc in cursor:
            contract_ids.append(doc["contract_id"])

        return list(set(contract_ids))

    async def rebuild_catalog(self) -> int:
        """Rebuild the entire schema catalog from contracts."""
        # Clear existing catalog
        await self._catalog.delete_many({})

        count = 0
        async for doc in self._contracts.find():
            contract_id = doc.get("id", "")
            contract_name = doc.get("name", "")
            contract_version = doc.get("version", "")
            contract_status = doc.get("status", "")

            for schema in doc.get("schema", []):
                entry = self._build_catalog_entry(
                    schema,
                    contract_id,
                    contract_name,
                    contract_version,
                    contract_status,
                )
                await self._catalog.insert_one(entry)
                count += 1

        return count

    async def update_for_contract(self, contract: Contract) -> None:
        """Update catalog entries for a specific contract."""
        # Remove old entries
        await self._catalog.delete_many({"contract_id": contract.id})

        # Add new entries
        for schema in contract.schemas:
            entry = self._build_catalog_entry_from_schema(
                schema,
                contract.id,
                contract.name,
                contract.version,
                contract.status.value,
            )
            await self._catalog.insert_one(entry)

    def _build_catalog_entry(
        self,
        schema: dict[str, Any],
        contract_id: str,
        contract_name: str,
        contract_version: str,
        contract_status: str,
    ) -> dict[str, Any]:
        """Build a catalog entry from a schema dict."""
        properties = schema.get("properties", [])
        field_names = [p.get("name", "") for p in properties]

        # Check for PII in any field
        has_pii = False
        for prop in properties:
            custom_props = prop.get("customProperties", {})
            privacy = custom_props.get("privacy", {})
            if isinstance(privacy, dict) and privacy.get("is_pii"):
                has_pii = True
                break

        # Find primary key
        pk_field = None
        for prop in properties:
            if prop.get("primary_key"):
                pk_field = prop.get("name")
                break

        return {
            "schema_id": schema.get("id", ""),
            "name": schema.get("name", ""),
            "physical_name": schema.get("physicalName", ""),
            "logical_type": schema.get("logicalType", "object"),
            "physical_type": schema.get("physicalType", "table"),
            "description": schema.get("description", ""),
            "business_name": schema.get("businessName", ""),
            "contract_id": contract_id,
            "contract_name": contract_name,
            "contract_version": contract_version,
            "contract_status": contract_status,
            "field_names": field_names,
            "field_count": len(field_names),
            "has_pii": has_pii,
            "primary_key_field": pk_field,
            "updated_at": _utc_now(),
        }

    def _build_catalog_entry_from_schema(
        self,
        schema,
        contract_id: str,
        contract_name: str,
        contract_version: str,
        contract_status: str,
    ) -> dict[str, Any]:
        """Build a catalog entry from a griot-core Schema object."""
        fields = schema.fields
        field_names = list(fields.keys())

        has_pii = any(f.is_pii for f in fields.values())

        pk_field = None
        for fname, finfo in fields.items():
            if finfo.primary_key:
                pk_field = fname
                break

        return {
            "schema_id": schema.id or "",
            "name": schema.name,
            "physical_name": schema.physical_name or "",
            "logical_type": schema.logical_type,
            "physical_type": schema.physical_type or "table",
            "description": schema.description or "",
            "business_name": schema.business_name or "",
            "contract_id": contract_id,
            "contract_name": contract_name,
            "contract_version": contract_version,
            "contract_status": contract_status,
            "field_names": field_names,
            "field_count": len(field_names),
            "has_pii": has_pii,
            "primary_key_field": pk_field,
            "updated_at": _utc_now(),
        }


class MongoValidationRecordRepository(ValidationRecordRepository):
    """MongoDB implementation of ValidationRecordRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._validations = db.validation_records

    async def record(self, validation: dict[str, Any]) -> dict[str, Any]:
        """Record a validation result."""
        validation["_id"] = _generate_id()
        validation["id"] = validation["_id"]
        validation["recorded_at"] = _utc_now()

        await self._validations.insert_one(validation)

        validation.pop("_id", None)
        return validation

    async def list(
        self,
        contract_id: str | None = None,
        schema_name: str | None = None,
        passed: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List validation records with filtering."""
        query: dict[str, Any] = {}

        if contract_id:
            query["contract_id"] = contract_id
        if schema_name:
            query["schema_name"] = schema_name
        if passed is not None:
            query["passed"] = passed
        if from_date:
            query["recorded_at"] = {"$gte": from_date}
        if to_date:
            query.setdefault("recorded_at", {})["$lte"] = to_date

        cursor = (
            self._validations.find(query)
            .skip(offset)
            .limit(limit)
            .sort("recorded_at", -1)
        )

        records = []
        async for doc in cursor:
            doc.pop("_id", None)
            records.append(doc)

        total = await self._validations.count_documents(query)

        return records, total

    async def get_stats(
        self,
        contract_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get validation statistics for a contract."""
        from_date = _utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        from_date = from_date - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "contract_id": contract_id,
                    "recorded_at": {"$gte": from_date},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_runs": {"$sum": 1},
                    "passed_runs": {"$sum": {"$cond": ["$passed", 1, 0]}},
                    "failed_runs": {"$sum": {"$cond": ["$passed", 0, 1]}},
                    "total_rows": {"$sum": "$row_count"},
                    "total_errors": {"$sum": "$error_count"},
                    "avg_duration_ms": {"$avg": "$duration_ms"},
                }
            },
        ]

        result = await self._validations.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "contract_id": contract_id,
                "period_days": days,
                "total_runs": 0,
                "passed_runs": 0,
                "failed_runs": 0,
                "pass_rate": 0.0,
                "total_rows": 0,
                "total_errors": 0,
                "avg_duration_ms": 0.0,
            }

        stats = result[0]
        stats.pop("_id", None)
        stats["contract_id"] = contract_id
        stats["period_days"] = days
        stats["pass_rate"] = (
            stats["passed_runs"] / stats["total_runs"]
            if stats["total_runs"] > 0
            else 0.0
        )

        return stats


class MongoRunRepository(RunRepository):
    """MongoDB implementation of RunRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._runs = db.runs

    async def create(self, run: dict[str, Any]) -> dict[str, Any]:
        """Create a new run record."""
        run["_id"] = _generate_id()
        run["id"] = run["_id"]
        run["created_at"] = _utc_now()
        run["status"] = run.get("status", "pending")

        await self._runs.insert_one(run)

        run.pop("_id", None)
        return run

    async def get(self, run_id: str) -> dict[str, Any] | None:
        """Get a run by ID."""
        doc = await self._runs.find_one({"id": run_id})
        if doc:
            doc.pop("_id", None)
        return doc

    async def update_status(
        self,
        run_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update run status and optionally set result."""
        update: dict[str, Any] = {
            "status": status,
            "updated_at": _utc_now(),
        }

        if status in ("completed", "failed"):
            update["completed_at"] = _utc_now()

        if result:
            update["result"] = result

        doc = await self._runs.find_one_and_update(
            {"id": run_id},
            {"$set": update},
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Run '{run_id}' not found")

        doc.pop("_id", None)
        return doc

    async def list(
        self,
        contract_id: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List runs with filtering."""
        query: dict[str, Any] = {}

        if contract_id:
            query["contract_id"] = contract_id
        if status:
            query["status"] = status
        if from_date:
            query["created_at"] = {"$gte": from_date}
        if to_date:
            query.setdefault("created_at", {})["$lte"] = to_date

        cursor = (
            self._runs.find(query)
            .skip(offset)
            .limit(limit)
            .sort("created_at", -1)
        )

        runs = []
        async for doc in cursor:
            doc.pop("_id", None)
            runs.append(doc)

        total = await self._runs.count_documents(query)

        return runs, total


class MongoIssueRepository(IssueRepository):
    """MongoDB implementation of IssueRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._issues = db.issues

    async def create(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Create a new issue."""
        issue["_id"] = _generate_id()
        issue["id"] = issue["_id"]
        issue["created_at"] = _utc_now()
        issue["status"] = issue.get("status", "open")

        await self._issues.insert_one(issue)

        issue.pop("_id", None)
        return issue

    async def get(self, issue_id: str) -> dict[str, Any] | None:
        """Get an issue by ID."""
        doc = await self._issues.find_one({"id": issue_id})
        if doc:
            doc.pop("_id", None)
        return doc

    async def update(self, issue_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update an issue."""
        updates["updated_at"] = _utc_now()

        doc = await self._issues.find_one_and_update(
            {"id": issue_id},
            {"$set": updates},
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Issue '{issue_id}' not found")

        doc.pop("_id", None)
        return doc

    async def resolve(
        self,
        issue_id: str,
        resolution: str,
        resolved_by: str,
    ) -> dict[str, Any]:
        """Mark an issue as resolved."""
        return await self.update(
            issue_id,
            {
                "status": "resolved",
                "resolution": resolution,
                "resolved_by": resolved_by,
                "resolved_at": _utc_now(),
            },
        )

    async def list(
        self,
        contract_id: str | None = None,
        run_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List issues with filtering."""
        query: dict[str, Any] = {}

        if contract_id:
            query["contract_id"] = contract_id
        if run_id:
            query["run_id"] = run_id
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity

        cursor = (
            self._issues.find(query)
            .skip(offset)
            .limit(limit)
            .sort("created_at", -1)
        )

        issues = []
        async for doc in cursor:
            doc.pop("_id", None)
            issues.append(doc)

        total = await self._issues.count_documents(query)

        return issues, total


class MongoCommentRepository(CommentRepository):
    """MongoDB implementation of CommentRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._comments = db.comments

    async def create(self, comment: dict[str, Any]) -> dict[str, Any]:
        """Create a new comment."""
        comment["_id"] = _generate_id()
        comment["id"] = comment["_id"]
        comment["created_at"] = _utc_now()
        comment["reactions"] = {}

        await self._comments.insert_one(comment)

        comment.pop("_id", None)
        return comment

    async def get(self, comment_id: str) -> dict[str, Any] | None:
        """Get a comment by ID."""
        doc = await self._comments.find_one({"id": comment_id})
        if doc:
            doc.pop("_id", None)
        return doc

    async def update(
        self,
        comment_id: str,
        content: str,
        updated_by: str,
    ) -> dict[str, Any]:
        """Update a comment's content."""
        doc = await self._comments.find_one_and_update(
            {"id": comment_id},
            {
                "$set": {
                    "content": content,
                    "updated_at": _utc_now(),
                    "updated_by": updated_by,
                }
            },
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Comment '{comment_id}' not found")

        doc.pop("_id", None)
        return doc

    async def delete(self, comment_id: str) -> bool:
        """Delete a comment."""
        result = await self._comments.delete_one({"id": comment_id})
        return result.deleted_count > 0

    async def list(
        self,
        contract_id: str,
        thread_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List comments for a contract."""
        query: dict[str, Any] = {"contract_id": contract_id}

        if thread_id:
            query["thread_id"] = thread_id

        cursor = (
            self._comments.find(query)
            .skip(offset)
            .limit(limit)
            .sort("created_at", 1)  # Oldest first for conversations
        )

        comments = []
        async for doc in cursor:
            doc.pop("_id", None)
            comments.append(doc)

        total = await self._comments.count_documents(query)

        return comments, total

    async def add_reaction(
        self,
        comment_id: str,
        reaction: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Add a reaction to a comment."""
        doc = await self._comments.find_one_and_update(
            {"id": comment_id},
            {"$addToSet": {f"reactions.{reaction}": user_id}},
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Comment '{comment_id}' not found")

        doc.pop("_id", None)
        return doc


class MongoApprovalRepository(ApprovalRepository):
    """MongoDB implementation of ApprovalRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._approvals = db.approvals

    async def create_request(
        self,
        contract_id: str,
        requested_by: str,
        approvers: list[str],
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Create an approval request."""
        request = {
            "_id": _generate_id(),
            "id": None,  # Will be set below
            "contract_id": contract_id,
            "requested_by": requested_by,
            "approvers": approvers,
            "notes": notes,
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "created_at": _utc_now(),
        }
        request["id"] = request["_id"]

        await self._approvals.insert_one(request)

        request.pop("_id", None)
        return request

    async def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Get an approval request by ID."""
        doc = await self._approvals.find_one({"id": request_id})
        if doc:
            doc.pop("_id", None)
        return doc

    async def approve(
        self,
        request_id: str,
        approver: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        """Record an approval."""
        approval_entry = {
            "approver": approver,
            "comments": comments,
            "approved_at": _utc_now(),
        }

        # Add approval and check if all approvers have approved
        doc = await self._approvals.find_one_and_update(
            {"id": request_id},
            {
                "$push": {"approvals": approval_entry},
                "$set": {"updated_at": _utc_now()},
            },
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Approval request '{request_id}' not found")

        # Check if fully approved
        approved_by = {a["approver"] for a in doc.get("approvals", [])}
        required = set(doc.get("approvers", []))

        if required.issubset(approved_by):
            await self._approvals.update_one(
                {"id": request_id},
                {"$set": {"status": "approved", "completed_at": _utc_now()}},
            )
            doc["status"] = "approved"

        doc.pop("_id", None)
        return doc

    async def reject(
        self,
        request_id: str,
        rejector: str,
        reason: str,
    ) -> dict[str, Any]:
        """Record a rejection."""
        rejection_entry = {
            "rejector": rejector,
            "reason": reason,
            "rejected_at": _utc_now(),
        }

        doc = await self._approvals.find_one_and_update(
            {"id": request_id},
            {
                "$push": {"rejections": rejection_entry},
                "$set": {
                    "status": "rejected",
                    "updated_at": _utc_now(),
                    "completed_at": _utc_now(),
                },
            },
            return_document=True,
        )

        if not doc:
            raise ValueError(f"Approval request '{request_id}' not found")

        doc.pop("_id", None)
        return doc

    async def list_pending(
        self,
        approver: str | None = None,
        contract_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List pending approval requests."""
        query: dict[str, Any] = {"status": "pending"}

        if approver:
            query["approvers"] = approver
        if contract_id:
            query["contract_id"] = contract_id

        cursor = self._approvals.find(query).sort("created_at", -1)

        requests = []
        async for doc in cursor:
            doc.pop("_id", None)
            requests.append(doc)

        return requests


class MongoDBStorage(StorageBackend):
    """MongoDB storage backend implementation.

    Provides access to all repositories and handles initialization.
    """

    def __init__(
        self,
        connection_string: str,
        database_name: str = "griot_registry",
    ):
        self._connection_string = connection_string
        self._database_name = database_name
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

        # Repositories (initialized in initialize())
        self._contracts: MongoContractRepository | None = None
        self._schema_catalog: MongoSchemaCatalogRepository | None = None
        self._validations: MongoValidationRecordRepository | None = None
        self._runs: MongoRunRepository | None = None
        self._issues: MongoIssueRepository | None = None
        self._comments: MongoCommentRepository | None = None
        self._approvals: MongoApprovalRepository | None = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        return self._db

    @property
    def contracts(self) -> MongoContractRepository:
        if self._contracts is None:
            raise RuntimeError("Storage not initialized")
        return self._contracts

    @property
    def schema_catalog(self) -> MongoSchemaCatalogRepository:
        if self._schema_catalog is None:
            raise RuntimeError("Storage not initialized")
        return self._schema_catalog

    @property
    def validations(self) -> MongoValidationRecordRepository:
        if self._validations is None:
            raise RuntimeError("Storage not initialized")
        return self._validations

    @property
    def runs(self) -> MongoRunRepository:
        if self._runs is None:
            raise RuntimeError("Storage not initialized")
        return self._runs

    @property
    def issues(self) -> MongoIssueRepository:
        if self._issues is None:
            raise RuntimeError("Storage not initialized")
        return self._issues

    @property
    def comments(self) -> MongoCommentRepository:
        if self._comments is None:
            raise RuntimeError("Storage not initialized")
        return self._comments

    @property
    def approvals(self) -> MongoApprovalRepository:
        if self._approvals is None:
            raise RuntimeError("Storage not initialized")
        return self._approvals

    async def initialize(self) -> None:
        """Initialize MongoDB connection, indexes, and repositories."""
        self._client = AsyncIOMotorClient(self._connection_string)
        self._db = self._client[self._database_name]

        # Initialize repositories
        self._contracts = MongoContractRepository(self._db)
        self._schema_catalog = MongoSchemaCatalogRepository(self._db)
        self._validations = MongoValidationRecordRepository(self._db)
        self._runs = MongoRunRepository(self._db)
        self._issues = MongoIssueRepository(self._db)
        self._comments = MongoCommentRepository(self._db)
        self._approvals = MongoApprovalRepository(self._db)

        # Create indexes
        await self._create_indexes()

    async def _create_indexes(self) -> None:
        """Create all required indexes for optimal performance."""
        # Contracts collection
        contracts = self._db.contracts
        await contracts.create_index("id", unique=True)
        await contracts.create_index("status")
        await contracts.create_index("name")
        await contracts.create_index("schema.name")
        await contracts.create_index("schema.physicalName")
        await contracts.create_index("team.name")
        await contracts.create_index([("_meta.updated_at", -1)])

        # Full-text search index
        await contracts.create_index([
            ("name", "text"),
            ("description.purpose", "text"),
            ("schema.name", "text"),
            ("schema.description", "text"),
            ("schema.properties.name", "text"),
            ("schema.properties.description", "text"),
        ])

        # Contract versions collection
        versions = self._db.contract_versions
        await versions.create_index([("contract_id", 1), ("version", 1)], unique=True)
        await versions.create_index([("contract_id", 1), ("created_at", -1)])
        await versions.create_index("is_breaking")

        # Schema catalog collection
        catalog = self._db.schema_catalog
        await catalog.create_index("name")
        await catalog.create_index("physical_name")
        await catalog.create_index("contract_id")
        await catalog.create_index("field_names")
        await catalog.create_index("has_pii")

        # Validation records collection
        validations = self._db.validation_records
        await validations.create_index("contract_id")
        await validations.create_index([("contract_id", 1), ("recorded_at", -1)])
        await validations.create_index("passed")

        # Runs collection
        runs = self._db.runs
        await runs.create_index("id", unique=True)
        await runs.create_index("contract_id")
        await runs.create_index("status")
        await runs.create_index([("created_at", -1)])

        # Issues collection
        issues = self._db.issues
        await issues.create_index("id", unique=True)
        await issues.create_index("contract_id")
        await issues.create_index("run_id")
        await issues.create_index("status")
        await issues.create_index("severity")

        # Comments collection
        comments = self._db.comments
        await comments.create_index("id", unique=True)
        await comments.create_index("contract_id")
        await comments.create_index("thread_id")
        await comments.create_index([("contract_id", 1), ("created_at", 1)])

        # Approvals collection
        approvals = self._db.approvals
        await approvals.create_index("id", unique=True)
        await approvals.create_index("contract_id")
        await approvals.create_index("status")
        await approvals.create_index("approvers")

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    async def health_check(self) -> dict[str, Any]:
        """Check MongoDB health."""
        try:
            await self._db.command("ping")
            return {
                "status": "healthy",
                "database": self._database_name,
                "collections": await self._db.list_collection_names(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }
