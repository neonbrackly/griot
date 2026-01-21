"""Test fixtures for griot-registry tests."""

from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from griot_registry.config import Settings, get_settings
from griot_registry.server import create_app
from griot_registry.storage.base import StorageBackend


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with auth disabled."""
    return Settings(
        auth_enabled=False,  # Disable auth for tests
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="griot_test",
    )


@pytest.fixture
def mock_storage() -> StorageBackend:
    """Create a mock storage backend."""
    storage = MagicMock(spec=StorageBackend)
    now = datetime.now()

    # Contract repository mocks
    storage.contracts = MagicMock()
    storage.contracts.create = AsyncMock(return_value={
        "id": "test-contract",
        "name": "Test Contract",
        "version": "1.0.0",
        "status": "draft",
        "apiVersion": "v1.0.0",
        "kind": "DataContract",
        "schema": [],
        "_meta": {"created_at": "2026-01-20T00:00:00Z"}
    })
    storage.contracts.get = AsyncMock(return_value={
        "id": "test-contract",
        "name": "Test Contract",
        "version": "1.0.0",
        "status": "draft",
        "apiVersion": "v1.0.0",
        "kind": "DataContract",
        "schema": [],
    })
    storage.contracts.list = AsyncMock(return_value=([], 0))
    storage.contracts.update = AsyncMock()
    storage.contracts.delete = AsyncMock()
    storage.contracts.search = AsyncMock(return_value=[])
    storage.contracts.full_text_search = AsyncMock(return_value={
        "items": [],
        "total": 0,
    })

    # Run repository mocks
    storage.runs = MagicMock()
    storage.runs.create = AsyncMock(return_value={
        "id": "run-123",
        "contract_id": "test-contract",
        "status": "pending",
        "created_at": now,
    })
    storage.runs.get = AsyncMock(return_value={
        "id": "run-123",
        "contract_id": "test-contract",
        "status": "pending",
        "created_at": now,
    })
    storage.runs.update_status = AsyncMock(return_value={
        "id": "run-123",
        "contract_id": "test-contract",
        "status": "running",
        "created_at": now,
    })
    storage.runs.list = AsyncMock(return_value=([], 0))

    # Issue repository mocks
    storage.issues = MagicMock()
    storage.issues.create = AsyncMock(return_value={
        "id": "issue-123",
        "contract_id": "test-contract",
        "title": "Test Issue",
        "status": "open",
        "severity": "warning",
        "created_at": now,
    })
    storage.issues.get = AsyncMock(return_value={
        "id": "issue-123",
        "contract_id": "test-contract",
        "title": "Test Issue",
        "status": "open",
        "severity": "warning",
        "created_at": now,
    })
    # update takes (issue_id, updates_dict)
    storage.issues.update = AsyncMock(return_value={
        "id": "issue-123",
        "contract_id": "test-contract",
        "title": "Updated Issue",
        "status": "open",
        "severity": "warning",
        "created_at": now,
    })
    # resolve takes (issue_id, resolution, resolved_by)
    storage.issues.resolve = AsyncMock(return_value={
        "id": "issue-123",
        "contract_id": "test-contract",
        "title": "Test Issue",
        "status": "resolved",
        "severity": "warning",
        "resolution": "Fixed",
        "resolved_by": "anonymous",
        "resolved_at": now,
        "created_at": now,
    })
    storage.issues.list = AsyncMock(return_value=([], 0))

    # Comment repository mocks
    storage.comments = MagicMock()
    storage.comments.create = AsyncMock(return_value={
        "id": "comment-123",
        "contract_id": "test-contract",
        "content": "Test comment",
        "created_at": now,
        "created_by": "anonymous",
    })
    storage.comments.get = AsyncMock(return_value={
        "id": "comment-123",
        "contract_id": "test-contract",
        "content": "Test comment",
        "created_at": now,
        "created_by": "anonymous",
    })
    # update takes (comment_id, content, updated_by)
    storage.comments.update = AsyncMock(return_value={
        "id": "comment-123",
        "contract_id": "test-contract",
        "content": "Updated comment",
        "updated_at": now,
        "created_at": now,
        "created_by": "anonymous",
    })
    storage.comments.delete = AsyncMock(return_value=True)
    # add_reaction takes (comment_id, reaction, user_id)
    storage.comments.add_reaction = AsyncMock(return_value={
        "id": "comment-123",
        "contract_id": "test-contract",
        "content": "Test comment",
        "reactions": {"thumbsup": ["anonymous"]},
        "created_at": now,
        "created_by": "anonymous",
    })
    # list takes (contract_id, thread_id, limit, offset)
    storage.comments.list = AsyncMock(return_value=([], 0))

    # Approval repository mocks - using correct method names
    storage.approvals = MagicMock()
    # create_request takes (contract_id, requested_by, approvers, notes)
    storage.approvals.create_request = AsyncMock(return_value={
        "id": "approval-123",
        "contract_id": "test-contract",
        "requested_by": "anonymous",
        "approvers": ["approver1", "approver2"],
        "notes": "Please approve",
        "status": "pending",
        "approvals": [],
        "rejections": [],
        "created_at": now,
    })
    # get_request takes (request_id)
    storage.approvals.get_request = AsyncMock(return_value={
        "id": "approval-123",
        "contract_id": "test-contract",
        "requested_by": "anonymous",
        "approvers": ["approver1", "approver2"],
        "status": "pending",
        "approvals": [],
        "rejections": [],
        "created_at": now,
    })
    # list_pending takes (approver, contract_id)
    storage.approvals.list_pending = AsyncMock(return_value=[])
    # approve takes (request_id, approver, comments)
    storage.approvals.approve = AsyncMock(return_value={
        "id": "approval-123",
        "contract_id": "test-contract",
        "requested_by": "anonymous",
        "approvers": ["approver1", "approver2"],
        "status": "approved",
        "approvals": [{"approver": "anonymous", "approved_at": now}],
        "rejections": [],
        "created_at": now,
    })
    # reject takes (request_id, rejector, reason)
    storage.approvals.reject = AsyncMock(return_value={
        "id": "approval-123",
        "contract_id": "test-contract",
        "requested_by": "anonymous",
        "approvers": ["approver1", "approver2"],
        "status": "rejected",
        "approvals": [],
        "rejections": [{"rejector": "anonymous", "reason": "Needs changes", "rejected_at": now}],
        "created_at": now,
    })

    # Validation repository mocks
    storage.validations = MagicMock()
    storage.validations.create = AsyncMock(return_value={
        "id": "validation-123",
        "contract_id": "test-contract",
        "passed": True,
        "recorded_at": now,
    })
    storage.validations.list = AsyncMock(return_value=([], 0))
    storage.validations.get_stats = AsyncMock(return_value={
        "contract_id": "test-contract",
        "period_days": 30,
        "total_runs": 10,
        "passed_runs": 9,
        "failed_runs": 1,
        "pass_rate": 0.9,
        "total_rows": 1000,
        "total_errors": 10,
        "avg_duration_ms": 150.0,
    })

    # Schema catalog mocks
    storage.schema_catalog = MagicMock()
    storage.schema_catalog.find_schemas = AsyncMock(return_value=[])
    # get_contracts_by_schema returns just the list of contract IDs
    storage.schema_catalog.get_contracts_by_schema = AsyncMock(return_value=["test-contract"])
    # rebuild_catalog returns the count of schemas indexed
    storage.schema_catalog.rebuild_catalog = AsyncMock(return_value=5)

    # Health check
    storage.health_check = AsyncMock(return_value={"status": "healthy"})
    storage.close = AsyncMock()

    return storage


@pytest.fixture
def app(test_settings: Settings, mock_storage: StorageBackend) -> FastAPI:
    """Create FastAPI test app with mock storage and auth disabled."""
    # Create app with test settings
    app = create_app(settings=test_settings)

    # Override the settings dependency
    app.dependency_overrides[get_settings] = lambda: test_settings

    # Set up state that would normally be set in lifespan
    app.state.storage = mock_storage
    app.state.settings = test_settings

    # Create mock services
    from griot_registry.services.contracts import ContractService
    from griot_registry.services.validation import ValidationService

    app.state.contract_service = ContractService(mock_storage, test_settings)
    app.state.validation_service = ValidationService(test_settings)

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create sync test client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
