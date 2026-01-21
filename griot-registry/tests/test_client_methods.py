"""Tests for the new client methods in griot-registry.

Tests cover:
- Runs: create_run, get_run, update_run_status, list_runs
- Issues: create_issue, get_issue, update_issue, resolve_issue, list_issues
- Comments: create_comment, get_comment, update_comment, delete_comment, add_reaction, list_contract_comments
- Approvals: create_approval_request, list_pending_approvals, get_approval_request, approve_request, reject_request
- Schema Catalog: get_contracts_by_schema, rebuild_schema_catalog
- Validation: get_validation_stats
- Search: advanced_search
"""

import pytest
from fastapi.testclient import TestClient


class TestRunsAPI:
    """Tests for the runs API endpoints."""

    def test_create_run(self, client: TestClient, mock_storage):
        """Test POST /api/v1/runs creates a new run."""
        response = client.post(
            "/api/v1/runs",
            json={"contract_id": "test-contract"},
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["contract_id"] == "test-contract"

    def test_get_run(self, client: TestClient, mock_storage):
        """Test GET /api/v1/runs/{run_id} returns run details."""
        response = client.get("/api/v1/runs/run-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "run-123"

    def test_update_run_status(self, client: TestClient, mock_storage):
        """Test PATCH /api/v1/runs/{run_id} updates run status."""
        response = client.patch(
            "/api/v1/runs/run-123",
            json={"status": "running"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"

    def test_list_runs(self, client: TestClient, mock_storage):
        """Test GET /api/v1/runs lists runs."""
        response = client.get("/api/v1/runs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestIssuesAPI:
    """Tests for the issues API endpoints."""

    def test_create_issue(self, client: TestClient, mock_storage):
        """Test POST /api/v1/issues creates a new issue."""
        response = client.post(
            "/api/v1/issues",
            json={
                "contract_id": "test-contract",
                "title": "Test Issue",
                "severity": "warning",
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Issue"

    def test_get_issue(self, client: TestClient, mock_storage):
        """Test GET /api/v1/issues/{issue_id} returns issue details."""
        response = client.get("/api/v1/issues/issue-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "issue-123"

    def test_update_issue(self, client: TestClient, mock_storage):
        """Test PATCH /api/v1/issues/{issue_id} updates issue."""
        response = client.patch(
            "/api/v1/issues/issue-123",
            json={"title": "Updated Issue"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Issue"

    def test_resolve_issue(self, client: TestClient, mock_storage):
        """Test POST /api/v1/issues/{issue_id}/resolve resolves issue."""
        response = client.post(
            "/api/v1/issues/issue-123/resolve",
            json={"resolution": "Fixed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_list_issues(self, client: TestClient, mock_storage):
        """Test GET /api/v1/issues lists issues."""
        response = client.get("/api/v1/issues")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestCommentsAPI:
    """Tests for the comments API endpoints."""

    def test_create_comment(self, client: TestClient, mock_storage):
        """Test POST /api/v1/comments creates a new comment."""
        response = client.post(
            "/api/v1/comments",
            json={
                "contract_id": "test-contract",
                "content": "Test comment",
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["content"] == "Test comment"

    def test_get_comment(self, client: TestClient, mock_storage):
        """Test GET /api/v1/comments/{comment_id} returns comment."""
        response = client.get("/api/v1/comments/comment-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "comment-123"

    def test_update_comment(self, client: TestClient, mock_storage):
        """Test PATCH /api/v1/comments/{comment_id} updates comment."""
        response = client.patch(
            "/api/v1/comments/comment-123",
            json={"content": "Updated comment"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated comment"

    def test_delete_comment(self, client: TestClient, mock_storage):
        """Test DELETE /api/v1/comments/{comment_id} deletes comment."""
        response = client.delete("/api/v1/comments/comment-123")
        assert response.status_code == 204

    def test_add_reaction(self, client: TestClient, mock_storage):
        """Test POST /api/v1/comments/{comment_id}/reactions adds reaction."""
        response = client.post(
            "/api/v1/comments/comment-123/reactions",
            json={"reaction": "thumbsup"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "reactions" in data

    def test_list_contract_comments(self, client: TestClient, mock_storage):
        """Test GET /api/v1/contracts/{contract_id}/comments lists comments."""
        response = client.get("/api/v1/contracts/test-contract/comments")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestApprovalsAPI:
    """Tests for the approvals API endpoints."""

    def test_create_approval_request(self, client: TestClient, mock_storage):
        """Test POST /api/v1/approvals creates approval request."""
        # Per the approvals.py API, ApprovalRequestCreate requires:
        # contract_id, approvers (list[str]), notes (optional)
        response = client.post(
            "/api/v1/approvals",
            json={
                "contract_id": "test-contract",
                "approvers": ["approver1", "approver2"],
                "notes": "Please approve this contract",
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["contract_id"] == "test-contract"

    def test_list_pending_approvals(self, client: TestClient, mock_storage):
        """Test GET /api/v1/approvals/pending lists pending approvals."""
        response = client.get("/api/v1/approvals/pending")
        assert response.status_code == 200
        data = response.json()
        # Response is ApprovalRequestList which has "items" field
        assert "items" in data

    def test_get_approval_request(self, client: TestClient, mock_storage):
        """Test GET /api/v1/approvals/{request_id} returns approval."""
        response = client.get("/api/v1/approvals/approval-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "approval-123"

    def test_approve_request(self, client: TestClient, mock_storage, app):
        """Test POST /api/v1/approvals/{request_id}/approve approves request."""
        from unittest.mock import AsyncMock, patch
        from datetime import datetime
        now = datetime.now()

        # Modify mock to include anonymous in approvers list
        mock_storage.approvals.get_request.return_value = {
            "id": "approval-123",
            "contract_id": "test-contract",
            "requested_by": "someone",
            "approvers": ["anonymous", "approver2"],  # Include the test user
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "created_at": now,
        }

        # Mock the contract service's update_status to avoid the actual implementation
        app.state.contract_service.update_status = AsyncMock()

        response = client.post(
            "/api/v1/approvals/approval-123/approve",
            json={"comments": "Looks good"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"

    def test_reject_request(self, client: TestClient, mock_storage):
        """Test POST /api/v1/approvals/{request_id}/reject rejects request."""
        # Modify mock to include anonymous in approvers list
        mock_storage.approvals.get_request.return_value = {
            "id": "approval-123",
            "contract_id": "test-contract",
            "requested_by": "someone",
            "approvers": ["anonymous", "approver2"],  # Include the test user
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "created_at": "2026-01-20T00:00:00Z",
        }
        response = client.post(
            "/api/v1/approvals/approval-123/reject",
            json={"reason": "Needs changes"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"


class TestSchemaCatalogAPI:
    """Tests for the schema catalog API endpoints."""

    def test_get_contracts_by_schema(self, client: TestClient, mock_storage):
        """Test GET /api/v1/schemas/contracts/{schema_name} returns contracts."""
        response = client.get("/api/v1/schemas/contracts/test_schema")
        assert response.status_code == 200
        data = response.json()
        assert data["schema_name"] == "test_schema"
        assert "contract_ids" in data

    def test_rebuild_schema_catalog(self, client: TestClient, mock_storage):
        """Test POST /api/v1/schemas/rebuild rebuilds catalog."""
        response = client.post("/api/v1/schemas/rebuild")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "schemas_indexed" in data


class TestValidationsAPI:
    """Tests for the validations API endpoints."""

    def test_get_validation_stats(self, client: TestClient, mock_storage):
        """Test GET /api/v1/validations/stats/{contract_id} returns stats."""
        response = client.get("/api/v1/validations/stats/test-contract")
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == "test-contract"
        assert "pass_rate" in data


class TestSearchAPI:
    """Tests for the search API endpoints."""

    def test_advanced_search(self, client: TestClient, mock_storage):
        """Test GET /api/v1/search/advanced with filters."""
        response = client.get(
            "/api/v1/search/advanced",
            params={"query": "test", "status": "active"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestHealthAPI:
    """Tests for health endpoints."""

    def test_health_check(self, client: TestClient, mock_storage):
        """Test GET /api/v1/health returns health status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_liveness_probe(self, client: TestClient, mock_storage):
        """Test GET /api/v1/health/live returns alive status."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_probe(self, client: TestClient, mock_storage):
        """Test GET /api/v1/health/ready returns ready status."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
