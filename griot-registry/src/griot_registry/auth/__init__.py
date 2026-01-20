"""Authentication and authorization for griot-registry.

This module provides:

- JWT token authentication for user sessions
- API key authentication for service-to-service communication
- Role-based authorization helpers
- Unified authentication dependencies for FastAPI routes

Example::

    from griot_registry.auth import CurrentUser, RequireEditor

    @router.post("/contracts")
    async def create_contract(user: CurrentUser, ...):
        pass  # user is guaranteed to be authenticated

    @router.put("/contracts/{id}")
    async def update_contract(user: RequireEditor, ...):
        pass  # user is guaranteed to have editor or admin role
"""

from griot_registry.auth.models import (
    AuthMethod,
    LoginRequest,
    RefreshRequest,
    TokenPayload,
    TokenResponse,
    User,
    UserRole,
)
from griot_registry.auth.jwt import (
    JWTAuth,
    JWTUser,
    get_current_user_jwt,
    get_jwt_auth,
)
from griot_registry.auth.api_key import (
    ApiKeyUser,
    get_api_key_header,
    get_current_user_api_key,
)
from griot_registry.auth.dependencies import (
    CurrentUser,
    OptionalUser,
    RequireAdmin,
    RequireEditor,
    RequireViewer,
    get_current_user,
    get_optional_user,
    require_admin,
    require_editor,
    require_role,
    require_viewer,
)

__all__ = [
    # Models
    "AuthMethod",
    "LoginRequest",
    "RefreshRequest",
    "TokenPayload",
    "TokenResponse",
    "User",
    "UserRole",
    # JWT auth
    "JWTAuth",
    "JWTUser",
    "get_current_user_jwt",
    "get_jwt_auth",
    # API key auth
    "ApiKeyUser",
    "get_api_key_header",
    "get_current_user_api_key",
    # Unified dependencies
    "CurrentUser",
    "OptionalUser",
    "RequireAdmin",
    "RequireEditor",
    "RequireViewer",
    "get_current_user",
    "get_optional_user",
    "require_admin",
    "require_editor",
    "require_role",
    "require_viewer",
]
