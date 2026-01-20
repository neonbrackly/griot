"""Griot Registry - Central registry API for Griot data contracts.

This package provides:
- REST API for contract storage and management
- MongoDB storage backend with schema catalog
- Python client for programmatic access
- JWT and API key authentication
- Contract validation using griot-core

Example usage with the client:
    from griot_registry.client import RegistryClient
    from griot_core import Contract

    async with RegistryClient("http://localhost:8000", api_key="key") as client:
        # Push a contract
        contract = Contract.from_yaml("contract.yaml")
        await client.push(contract)

        # Pull a contract
        contract = await client.pull("my-contract-id")

For synchronous usage:
    from griot_registry.client import SyncRegistryClient

    with SyncRegistryClient("http://localhost:8000") as client:
        contract = client.pull("my-contract-id")
"""

from griot_registry.server import create_app
from griot_registry.client import (
    RegistryClient,
    SyncRegistryClient,
    RegistryClientError,
    ContractNotFoundError,
    ValidationError,
    BreakingChangeError,
)

__version__ = "0.2.0"

__all__ = [
    # App factory
    "create_app",
    # Client
    "RegistryClient",
    "SyncRegistryClient",
    # Client exceptions
    "RegistryClientError",
    "ContractNotFoundError",
    "ValidationError",
    "BreakingChangeError",
    # Version
    "__version__",
]
