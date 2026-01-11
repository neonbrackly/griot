"""
Integration tests for CLI push command with breaking changes (T-391).

Tests the griot push command's breaking change validation, including:
- Detection of breaking changes before push
- Blocking push when breaking changes detected
- --allow-breaking flag to force push
- --dry-run with breaking change reporting
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from griot_cli.main import cli


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def base_contract_yaml() -> str:
    """Original contract YAML for breaking change tests."""
    return """
id: test-customer-contract
name: Customer
description: Customer profile contract
version: "1.0.0"
status: active
fields:
  customer_id:
    type: string
    description: Unique customer identifier
    primary_key: true
    pattern: '^CUST-\\d{6}$'
  email:
    type: string
    description: Customer email address
    format: email
    max_length: 255
  age:
    type: integer
    description: Customer age in years
    ge: 0
    le: 150
  status:
    type: string
    description: Account status
    enum: [active, inactive, suspended]
"""


@pytest.fixture
def breaking_contract_yaml() -> str:
    """Modified contract YAML with breaking changes."""
    return """
id: test-customer-contract
name: Customer
description: Customer profile contract
version: "2.0.0"
status: active
fields:
  customer_id:
    type: string
    description: Unique customer identifier
    primary_key: true
    pattern: '^CUST-\\d{6}$'
  email:
    type: string
    description: Customer email address
    format: email
    max_length: 100
  status:
    type: string
    description: Account status
    enum: [active, inactive]
  new_required:
    type: string
    description: New required field
"""


@pytest.fixture
def non_breaking_contract_yaml() -> str:
    """Modified contract YAML with only non-breaking changes."""
    return """
id: test-customer-contract
name: Customer
description: Updated customer profile contract
version: "1.1.0"
status: active
fields:
  customer_id:
    type: string
    description: Unique customer identifier (updated description)
    primary_key: true
    pattern: '^CUST-\\d{6}$'
  email:
    type: string
    description: Customer email address
    format: email
    max_length: 500
  age:
    type: integer
    description: Customer age in years
    ge: 0
    le: 150
  status:
    type: string
    description: Account status
    enum: [active, inactive, suspended, pending]
  new_optional:
    type: string
    description: New optional field
    nullable: true
"""


@pytest.fixture
def new_contract_yaml() -> str:
    """New contract YAML without existing version in registry."""
    return """
name: NewProduct
description: New product contract
version: "1.0.0"
status: draft
fields:
  product_id:
    type: string
    description: Unique product identifier
    primary_key: true
  name:
    type: string
    description: Product name
"""


def mock_registry_response(base_contract_data: dict[str, Any]) -> MagicMock:
    """Create a mock response for registry API calls."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(base_contract_data).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    return mock_response


# =============================================================================
# T-391: Breaking Change Detection Integration Tests
# =============================================================================


class TestPushBreakingChangeDetection:
    """Tests for breaking change detection in push command."""

    def test_push_blocks_breaking_changes(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push should be blocked when breaking changes are detected."""
        # Write the breaking contract to a temp file
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(breaking_contract_yaml)

        # Parse base contract for mock registry response
        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # First call: fetch existing contract
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                ["push", str(contract_file), "--registry", "http://localhost:8000"],
            )

        # Should fail with exit code 1 (breaking changes blocked)
        assert result.exit_code == 1
        assert "BREAKING" in result.output.upper()

    def test_push_with_allow_breaking_proceeds(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push with --allow-breaking should proceed despite breaking changes."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # First call: fetch existing, Second call: push
            fetch_response = mock_registry_response(base_data)
            push_response = mock_registry_response({"version": "2.0.0"})
            mock_urlopen.side_effect = [fetch_response, push_response]

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "--allow-breaking",
                    "-m", "Breaking change approved",
                ],
            )

        # Should succeed (exit code 0)
        assert result.exit_code == 0
        assert "Pushed" in result.output or "breaking change" in result.output.lower()

    def test_push_non_breaking_succeeds(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        non_breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push with only non-breaking changes should succeed."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(non_breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            fetch_response = mock_registry_response(base_data)
            push_response = mock_registry_response({"version": "1.1.0"})
            mock_urlopen.side_effect = [fetch_response, push_response]

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "-m", "Non-breaking update",
                ],
            )

        # Should succeed
        assert result.exit_code == 0

    def test_push_new_contract_succeeds(
        self,
        runner: CliRunner,
        new_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push of a new contract (no existing version) should succeed."""
        contract_file = tmp_path / "product.yaml"
        contract_file.write_text(new_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # New contract without ID skips fetch, goes directly to POST
            # Only one HTTP call: POST to create
            mock_urlopen.return_value = mock_registry_response({"id": "new-product", "version": "1.0.0"})

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "-m", "Initial version",
                ],
            )

        # Should succeed (no breaking changes for new contract)
        assert result.exit_code == 0


# =============================================================================
# T-391: Dry Run Tests
# =============================================================================


class TestPushDryRun:
    """Tests for --dry-run with breaking change detection."""

    def test_dry_run_shows_breaking_changes(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Dry run should show breaking changes without pushing."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "--dry-run",
                ],
            )

        # Should show dry run info and breaking changes
        assert result.exit_code == 0  # dry-run always exits 0
        assert "dry run" in result.output.lower()
        assert "breaking" in result.output.lower()
        assert "BLOCKED" in result.output or "blocked" in result.output.lower()

    def test_dry_run_with_allow_breaking_shows_would_proceed(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Dry run with --allow-breaking should show push would proceed."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "--dry-run",
                    "--allow-breaking",
                ],
            )

        # Should show would proceed
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
        assert "proceed" in result.output.lower() or "allow" in result.output.lower()

    def test_dry_run_no_breaking_changes(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        non_breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Dry run with non-breaking changes should show success."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(non_breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                    "--dry-run",
                ],
            )

        # Should show no breaking changes
        assert result.exit_code == 0
        assert "no breaking" in result.output.lower()


# =============================================================================
# T-391: Breaking Change Types in Output Tests
# =============================================================================


class TestBreakingChangeOutput:
    """Tests for breaking change details in output."""

    def test_field_removed_shown_in_output(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Field removal should be shown in breaking change output."""
        base_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
  removed_field:
    type: string
    description: This will be removed
"""
        new_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
"""
        contract_file = tmp_path / "test.yaml"
        contract_file.write_text(new_yaml)

        import yaml
        base_data = yaml.safe_load(base_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        assert result.exit_code == 1
        assert "field_removed" in result.output.lower() or "removed" in result.output.lower()

    def test_type_change_shown_in_output(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Type change should be shown in breaking change output."""
        base_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
  value:
    type: string
    description: String value
"""
        new_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
  value:
    type: integer
    description: Now an integer
"""
        contract_file = tmp_path / "test.yaml"
        contract_file.write_text(new_yaml)

        import yaml
        base_data = yaml.safe_load(base_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        assert result.exit_code == 1
        assert "type" in result.output.lower()

    def test_enum_values_removed_shown_in_output(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Enum value removal should be shown in breaking change output."""
        base_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
  status:
    type: string
    enum: [active, inactive, pending]
"""
        new_yaml = """
id: test-contract
name: TestContract
fields:
  id:
    type: string
    primary_key: true
  status:
    type: string
    enum: [active, inactive]
"""
        contract_file = tmp_path / "test.yaml"
        contract_file.write_text(new_yaml)

        import yaml
        base_data = yaml.safe_load(base_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        assert result.exit_code == 1
        assert "enum" in result.output.lower()


# =============================================================================
# T-391: Error Handling Tests
# =============================================================================


class TestPushErrorHandling:
    """Tests for error handling in push command."""

    def test_push_without_registry_url(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push without registry URL should fail gracefully."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(base_contract_yaml)

        # Clear any environment variables
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(
                cli,
                ["push", str(contract_file)],
            )

        assert result.exit_code == 2
        assert "registry" in result.output.lower()

    def test_push_nonexistent_file(
        self,
        runner: CliRunner,
    ) -> None:
        """Push with nonexistent file should fail."""
        result = runner.invoke(
            cli,
            ["push", "/nonexistent/path/contract.yaml", "--registry", "http://localhost:8000"],
        )

        assert result.exit_code != 0

    def test_push_registry_unreachable(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push when registry is unreachable should handle gracefully."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            import urllib.error
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        # Should handle the error (either continue without check or fail gracefully)
        # The implementation skips breaking change check if registry is unreachable
        # So it should try to push and fail
        assert "error" in result.output.lower() or result.exit_code != 0


# =============================================================================
# T-391: Exit Code Tests
# =============================================================================


class TestPushExitCodes:
    """Tests for push command exit codes."""

    def test_exit_code_0_on_success(
        self,
        runner: CliRunner,
        new_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Successful push should exit with code 0."""
        contract_file = tmp_path / "product.yaml"
        contract_file.write_text(new_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            # New contract without ID skips fetch, goes directly to POST
            mock_urlopen.return_value = mock_registry_response({"id": "new-product", "version": "1.0.0"})

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        assert result.exit_code == 0

    def test_exit_code_1_on_breaking_changes(
        self,
        runner: CliRunner,
        base_contract_yaml: str,
        breaking_contract_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Push blocked by breaking changes should exit with code 1."""
        contract_file = tmp_path / "customer.yaml"
        contract_file.write_text(breaking_contract_yaml)

        import yaml
        base_data = yaml.safe_load(base_contract_yaml)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_registry_response(base_data)

            result = runner.invoke(
                cli,
                [
                    "push",
                    str(contract_file),
                    "--registry", "http://localhost:8000",
                ],
            )

        assert result.exit_code == 1

    def test_exit_code_2_on_error(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Errors should exit with code 2."""
        contract_file = tmp_path / "invalid.yaml"
        contract_file.write_text("invalid: yaml: content: [")

        result = runner.invoke(
            cli,
            [
                "push",
                str(contract_file),
                "--registry", "http://localhost:8000",
            ],
        )

        assert result.exit_code == 2
