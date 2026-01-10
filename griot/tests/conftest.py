"""
Griot Test Suite - Shared Fixtures and Configuration

Provides common fixtures for testing across all Griot components.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Generator

import pytest

# Add griot-core to path for testing
GRIOT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GRIOT_ROOT / "griot-core" / "src"))


# =============================================================================
# SAMPLE CONTRACT FIXTURES
# =============================================================================


@pytest.fixture
def sample_customer_data() -> list[dict[str, Any]]:
    """Sample valid customer data for testing."""
    return [
        {
            "customer_id": "CUST-000001",
            "email": "alice@example.com",
            "age": 30,
            "status": "active",
        },
        {
            "customer_id": "CUST-000002",
            "email": "bob@example.com",
            "age": 25,
            "status": "active",
        },
        {
            "customer_id": "CUST-000003",
            "email": "charlie@example.com",
            "age": 45,
            "status": "inactive",
        },
    ]


@pytest.fixture
def sample_invalid_customer_data() -> list[dict[str, Any]]:
    """Sample invalid customer data for testing validation errors."""
    return [
        {
            "customer_id": "invalid-id",  # Wrong pattern
            "email": "not-an-email",  # Invalid email format
            "age": -5,  # Below minimum
            "status": "unknown",  # Not in enum
        },
        {
            "customer_id": "CUST-000001",
            "email": "valid@example.com",
            "age": 200,  # Above maximum
            "status": "active",
        },
    ]


@pytest.fixture
def large_dataset() -> Generator[list[dict[str, Any]], None, None]:
    """Generate a large dataset for performance testing."""
    data = [
        {
            "customer_id": f"CUST-{i:06d}",
            "email": f"user{i}@example.com",
            "age": (i % 80) + 18,
            "status": ["active", "inactive", "suspended"][i % 3],
        }
        for i in range(100_000)
    ]
    yield data


# =============================================================================
# YAML CONTRACT FIXTURES
# =============================================================================


@pytest.fixture
def sample_contract_yaml() -> str:
    """Sample contract in YAML format."""
    return """
name: Customer
description: Customer profile contract
version: "1.0.0"
fields:
  customer_id:
    type: string
    description: Unique customer identifier
    primary_key: true
    pattern: "^CUST-\\d{6}$"
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
    unit: years
  status:
    type: string
    description: Account status
    enum: [active, inactive, suspended]
"""


# =============================================================================
# HELPER FIXTURES
# =============================================================================


@pytest.fixture
def temp_contract_file(tmp_path: Path, sample_contract_yaml: str) -> Path:
    """Create a temporary contract YAML file."""
    contract_path = tmp_path / "customer.yaml"
    contract_path.write_text(sample_contract_yaml)
    return contract_path
