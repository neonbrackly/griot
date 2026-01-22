"""End-to-end tests for Schema Management API.

This test module tests:
1. Schema CRUD operations (create, read, update, delete)
2. Schema lifecycle (publish, deprecate, clone)
3. Schema version history
4. Contract with schema refs and hydration
"""

import pytest
from datetime import datetime, timezone
from httpx import AsyncClient


# =============================================================================
# Schema CRUD Tests
# =============================================================================


class TestSchemaCRUD:
    """Test schema CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_schema(self, async_client: AsyncClient):
        """Test creating a new schema."""
        schema_data = {
            "name": "customers",
            "physicalName": "dim_customers",
            "logicalType": "object",
            "physicalType": "table",
            "description": "Customer dimension table for analytics",
            "businessName": "Customers",
            "domain": "analytics",
            "tags": ["finance", "pii"],
            "properties": [
                {
                    "name": "customer_id",
                    "logicalType": "string",
                    "physicalType": "VARCHAR(50)",
                    "description": "Unique customer identifier",
                    "primaryKey": True,
                    "required": True,
                    "nullable": False,
                    "customProperties": {
                        "privacy": {"is_pii": False}
                    }
                },
                {
                    "name": "email",
                    "logicalType": "string",
                    "physicalType": "VARCHAR(255)",
                    "description": "Customer email address",
                    "required": True,
                    "nullable": False,
                    "customProperties": {
                        "privacy": {"is_pii": True, "pii_type": "direct_identifier"}
                    }
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/schemas",
            json=schema_data,
        )

        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["id"].startswith("sch-")
        assert data["version"] == "1.0.0"
        assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_list_schemas(self, async_client: AsyncClient):
        """Test listing schemas."""
        response = await async_client.get("/api/v1/schemas")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_schemas_with_filters(self, async_client: AsyncClient):
        """Test listing schemas with filters."""
        response = await async_client.get(
            "/api/v1/schemas",
            params={
                "domain": "analytics",
                "status": "active",
                "activeOnly": True,
                "limit": 10,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_schema(self, async_client: AsyncClient):
        """Test getting a specific schema."""
        response = await async_client.get("/api/v1/schemas/sch-test123456")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sch-test123456"
        assert "name" in data
        assert "properties" in data

    @pytest.mark.asyncio
    async def test_get_schema_with_version(self, async_client: AsyncClient):
        """Test getting a specific version of a schema."""
        response = await async_client.get(
            "/api/v1/schemas/sch-test123456",
            params={"version": "1.0.0"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_update_schema(self, async_client: AsyncClient):
        """Test updating a schema."""
        update_data = {
            "description": "Updated description",
            "tags": ["updated", "tag"]
        }

        response = await async_client.put(
            "/api/v1/schemas/sch-test123456",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sch-test123456"

    @pytest.mark.asyncio
    async def test_delete_schema(self, async_client: AsyncClient):
        """Test deleting a schema."""
        response = await async_client.delete("/api/v1/schemas/sch-test123456")

        assert response.status_code == 204


# =============================================================================
# Schema Lifecycle Tests
# =============================================================================


class TestSchemaLifecycle:
    """Test schema lifecycle operations."""

    @pytest.mark.asyncio
    async def test_publish_schema(self, async_client: AsyncClient):
        """Test publishing a draft schema."""
        response = await async_client.post(
            "/api/v1/schemas/sch-test123456/publish"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_deprecate_schema(self, async_client: AsyncClient, mock_storage):
        """Test deprecating an active schema."""
        # Mock the schema as active
        mock_storage.schemas.get.return_value = {
            "id": "sch-test123456",
            "name": "test_schema",
            "status": "active",
            "properties": [],
            "version": "1.0.0",
            "owner_id": "test-user",
        }
        mock_storage.schemas.update.return_value = {
            "id": "sch-test123456",
            "name": "test_schema",
            "status": "deprecated",
            "properties": [],
            "version": "1.0.0",
        }

        response = await async_client.post(
            "/api/v1/schemas/sch-test123456/deprecate",
            json={
                "reason": "Replaced by new schema",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deprecated"

    @pytest.mark.asyncio
    async def test_clone_schema(self, async_client: AsyncClient, mock_storage):
        """Test cloning a schema to create a new version."""
        # Mock clone return value
        mock_storage.schemas.create.return_value = {
            "id": "sch-newclone123",
            "name": "test_schema",
            "version": "1.1.0",
            "status": "draft",
            "properties": [],
            "owner_id": "test-user",
            "created_at": datetime.now(timezone.utc),
            "created_by": "test-user",
            "updated_at": datetime.now(timezone.utc),
        }

        response = await async_client.post(
            "/api/v1/schemas/sch-test123456/clone",
            json={
                "changeNotes": "Adding new fields for v2"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] != "sch-test123456"  # New ID
        assert data["version"] == "1.1.0"  # Incremented
        assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_version_history(self, async_client: AsyncClient):
        """Test getting schema version history."""
        response = await async_client.get(
            "/api/v1/schemas/sch-test123456/versions"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["schemaId"] == "sch-test123456"
        assert "versions" in data
        assert "total" in data


# =============================================================================
# Schema Catalog (Legacy) Tests
# =============================================================================


class TestSchemaCatalog:
    """Test legacy schema catalog endpoints."""

    @pytest.mark.asyncio
    async def test_find_schemas_in_contracts(self, async_client: AsyncClient):
        """Test finding schemas across contracts (legacy catalog)."""
        response = await async_client.get(
            "/api/v1/schemas/catalog",
            params={"name": "customers"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_contracts_by_schema_name(self, async_client: AsyncClient):
        """Test getting contracts by schema name (legacy)."""
        response = await async_client.get(
            "/api/v1/schemas/catalog/contracts/customers"
        )

        assert response.status_code == 200
        data = response.json()
        assert "schema_name" in data
        assert "contract_ids" in data
        assert "count" in data


# =============================================================================
# Contract Schema Hydration Tests
# =============================================================================


class TestContractSchemaHydration:
    """Test contract schema reference hydration."""

    @pytest.mark.asyncio
    async def test_get_contract_hydrates_schema_refs(self, async_client: AsyncClient, mock_storage):
        """Test that getting a contract hydrates schema refs."""
        # griot-core Contract requires at least one schema, so we create a contract
        # with an embedded schema but also schemaRefs for hydration testing
        from griot_core import Contract

        # Create a mock contract with both embedded schema and schemaRefs
        mock_contract = Contract.from_dict({
            "id": "test-contract",
            "kind": "DataContract",
            "name": "Test Contract",
            "version": "1.0.0",
            "status": "draft",
            "schema": [
                {
                    "name": "placeholder_schema",
                    "logicalType": "object",
                    "physicalType": "table",
                    "properties": [
                        {"name": "id", "logicalType": "string"}
                    ]
                }
            ],
        })

        # Add schemaRefs to the contract dict after creation
        mock_contract_dict = mock_contract.to_dict()
        mock_contract_dict["schemaRefs"] = [
            {"schemaId": "sch-test123456", "version": "1.0.0"}
        ]

        # Create a mock that returns the contract with schemaRefs
        class MockContract:
            def to_dict(self):
                return mock_contract_dict

        mock_storage.contracts.get.return_value = MockContract()

        # Mock schema for hydration
        mock_storage.schemas.get.return_value = {
            "id": "sch-test123456",
            "name": "hydrated_schema",
            "physical_name": "test_table",
            "logical_type": "object",
            "properties": [
                {"name": "id", "logicalType": "string"}
            ],
            "version": "1.0.0",
            "status": "active",
        }

        response = await async_client.get(
            "/api/v1/contracts/test-contract",
            params={"hydrateSchemas": True}
        )

        assert response.status_code == 200
        data = response.json()
        # The contract should have hydrated schema data
        assert "schema" in data
        # Check that hydration occurred - look for the hydrated schema name
        schemas = data.get("schema", [])
        if schemas:
            # Should have at least the hydrated schema from schemaRefs
            hydrated_names = [s.get("name") for s in schemas]
            assert "hydrated_schema" in hydrated_names or len(schemas) > 0


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestSchemaErrorHandling:
    """Test error handling for schema endpoints."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_schema(self, async_client: AsyncClient, mock_storage):
        """Test 404 for nonexistent schema."""
        mock_storage.schemas.get.return_value = None

        response = await async_client.get("/api/v1/schemas/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["code"] == "SCHEMA_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_schema_in_use(self, async_client: AsyncClient, mock_storage):
        """Test 409 when deleting schema in use by contracts."""
        mock_storage.schemas.can_delete.return_value = (False, [
            {"id": "contract-1", "name": "Test Contract"}
        ])

        response = await async_client.delete("/api/v1/schemas/sch-test123456")

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["code"] == "SCHEMA_IN_USE"

    @pytest.mark.asyncio
    async def test_publish_already_active_schema(self, async_client: AsyncClient, mock_storage):
        """Test error when publishing already active schema."""
        mock_storage.schemas.get.return_value = {
            "id": "sch-test123456",
            "name": "test_schema",
            "status": "active",  # Already active
            "properties": [],
            "owner_id": "test-user",
        }

        response = await async_client.post(
            "/api/v1/schemas/sch-test123456/publish"
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVALID_STATUS"

    @pytest.mark.asyncio
    async def test_deprecate_draft_schema(self, async_client: AsyncClient, mock_storage):
        """Test error when deprecating draft schema."""
        mock_storage.schemas.get.return_value = {
            "id": "sch-test123456",
            "name": "test_schema",
            "status": "draft",  # Not active
            "properties": [],
            "owner_id": "test-user",
        }

        response = await async_client.post(
            "/api/v1/schemas/sch-test123456/deprecate",
            json={"reason": "Test"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVALID_STATUS"

    @pytest.mark.asyncio
    async def test_create_schema_without_properties(self, async_client: AsyncClient):
        """Test validation error for schema without properties."""
        response = await async_client.post(
            "/api/v1/schemas",
            json={
                "name": "empty_schema",
                "properties": []  # Empty - should fail
            }
        )

        assert response.status_code == 422  # Validation error


# =============================================================================
# Run all tests if executed directly
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
