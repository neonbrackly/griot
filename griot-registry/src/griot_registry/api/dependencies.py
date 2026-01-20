"""Common FastAPI dependencies for API endpoints."""

from typing import Annotated

from fastapi import Depends, Request

from griot_registry.config import Settings
from griot_registry.services.contracts import ContractService
from griot_registry.services.validation import ValidationService
from griot_registry.storage.base import StorageBackend


def get_storage(request: Request) -> StorageBackend:
    """Get storage backend from app state."""
    return request.app.state.storage


def get_contract_service(request: Request) -> ContractService:
    """Get contract service from app state."""
    return request.app.state.contract_service


def get_validation_service(request: Request) -> ValidationService:
    """Get validation service from app state."""
    return request.app.state.validation_service


def get_settings_from_app(request: Request) -> Settings:
    """Get settings from app state."""
    return request.app.state.settings


# Type aliases for dependency injection
Storage = Annotated[StorageBackend, Depends(get_storage)]
ContractSvc = Annotated[ContractService, Depends(get_contract_service)]
ValidationSvc = Annotated[ValidationService, Depends(get_validation_service)]
AppSettings = Annotated[Settings, Depends(get_settings_from_app)]
